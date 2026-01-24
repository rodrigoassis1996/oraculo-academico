# services/rag_manager.py
"""Gerenciador RAG - Embeddings, Vector Store e Retrieval."""

import streamlit as st
from typing import List, Optional
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings as ChromaSettings

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from services.text_processor import TextProcessor, TextChunk, ChunkConfig

@dataclass
class RAGConfig:
    """Configurações do RAG."""
    embedding_model: str = "all-MiniLM-L6-v2"  # Modelo leve e eficiente
    collection_name: str = "oraculo_docs"
    top_k: int = 5  # Quantos chunks recuperar
    chunk_size: int = 1000
    chunk_overlap: int = 200

class RAGManager:
    """
    Gerenciador de RAG (Retrieval Augmented Generation).
    Responsável por embeddings, armazenamento e recuperação.
    """

    def __init__(self, config: RAGConfig = None):
        self.config = config or RAGConfig()
        self.text_processor = TextProcessor(
            ChunkConfig(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
        )
        self._init_session_state()
        self._init_embeddings()
        self._init_vector_store()

    def _init_session_state(self):
        """Inicializa session state."""
        if 'rag_chunks' not in st.session_state:
            st.session_state['rag_chunks'] = []
        if 'rag_initialized' not in st.session_state:
            st.session_state['rag_initialized'] = False

    def _init_embeddings(self):
        """Inicializa modelo de embeddings."""
        # Cache do modelo para não recarregar
        if 'embedding_model' not in st.session_state:
            st.session_state['embedding_model'] = HuggingFaceEmbeddings(
                model_name=self.config.embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        self.embeddings = st.session_state['embedding_model']

    def _init_vector_store(self):
        """Inicializa vector store."""
        # Cliente ChromaDB em memória (efêmero)
        if 'chroma_client' not in st.session_state:
            st.session_state['chroma_client'] = chromadb.EphemeralClient(
                settings=ChromaSettings(anonymized_telemetry=False)
            )
        self.chroma_client = st.session_state['chroma_client']
        
        # Vector store
        if 'vector_store' not in st.session_state:
            st.session_state['vector_store'] = None
        self.vector_store = st.session_state['vector_store']

    @property
    def is_initialized(self) -> bool:
        """Verifica se o RAG está inicializado com documentos."""
        return st.session_state.get('rag_initialized', False)

    @property
    def total_chunks(self) -> int:
        """Total de chunks indexados."""
        return len(st.session_state.get('rag_chunks', []))

    # ==================== INDEXAÇÃO ====================

    def indexar_documentos(
        self,
        documentos: List[tuple],  # [(nome, conteudo), ...]
        progress_callback=None
    ) -> dict:
        """
        Indexa múltiplos documentos no vector store.
        
        Args:
            documentos: Lista de tuplas (nome, conteudo)
            progress_callback: Função para atualizar progresso
            
        Returns:
            Estatísticas da indexação
        """
        # Limpa índice anterior
        self.limpar_indice()
        
        todos_chunks = []
        documentos_langchain = []
        
        total_docs = len(documentos)
        
        for i, (nome, conteudo) in enumerate(documentos):
            if progress_callback:
                progress_callback((i + 1) / (total_docs + 1), f"Processando {nome}...")
            
            # Valida conteúdo
            is_valid, msg = self.text_processor.validar_conteudo_extraido(conteudo)
            if not is_valid:
                st.warning(f"⚠️ {nome}: {msg}")
                continue
            
            # Cria chunks
            chunks = self.text_processor.criar_chunks(conteudo, nome)
            todos_chunks.extend(chunks)
            
            # Converte para formato LangChain
            for chunk in chunks:
                doc = Document(
                    page_content=chunk.conteudo,
                    metadata={
                        "source": chunk.documento_origem,
                        "chunk_index": chunk.indice
                    }
                )
                documentos_langchain.append(doc)
        
        if not documentos_langchain:
            raise ValueError("Nenhum documento válido para indexar.")
        
        if progress_callback:
            progress_callback(0.9, "Criando embeddings...")
        
        # Cria vector store com os documentos
        self.vector_store = Chroma.from_documents(
            documents=documentos_langchain,
            embedding=self.embeddings,
            collection_name=self.config.collection_name,
            client=self.chroma_client
        )
        
        # Salva no session state
        st.session_state['vector_store'] = self.vector_store
        st.session_state['rag_chunks'] = todos_chunks
        st.session_state['rag_initialized'] = True
        
        if progress_callback:
            progress_callback(1.0, "Concluído!")
        
        # Estatísticas
        stats = self.text_processor.get_estatisticas(todos_chunks)
        stats['documentos_indexados'] = len(set(c.documento_origem for c in todos_chunks))
        
        return stats

    # ==================== RECUPERAÇÃO ====================

    def buscar_relevantes(
        self, 
        query: str, 
        top_k: int = None
    ) -> List[Document]:
        """
        Busca chunks mais relevantes para a query.
        
        Args:
            query: Pergunta do usuário
            top_k: Número de chunks a retornar
            
        Returns:
            Lista de Documents relevantes
        """
        if not self.is_initialized or self.vector_store is None:
            return []
        
        k = top_k or self.config.top_k
        
        # Busca por similaridade
        docs = self.vector_store.similarity_search(query, k=k)
        
        return docs

    def buscar_com_scores(
        self, 
        query: str, 
        top_k: int = None
    ) -> List[tuple]:
        """
        Busca chunks com scores de similaridade.
        
        Returns:
            Lista de (Document, score)
        """
        if not self.is_initialized or self.vector_store is None:
            return []
        
        k = top_k or self.config.top_k
        
        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
        
        return docs_with_scores

    def get_contexto_para_prompt(self, query: str, top_k: int = None) -> str:
        """
        Retorna contexto formatado para incluir no prompt.
        
        Args:
            query: Pergunta do usuário
            
        Returns:
            String formatada com os chunks relevantes
        """
        docs = self.buscar_relevantes(query, top_k)
        
        if not docs:
            return ""
        
        contexto_partes = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Desconhecido')
            contexto_partes.append(
                f"[Trecho {i} - Fonte: {source}]\n{doc.page_content}"
            )
        
        return "\n\n---\n\n".join(contexto_partes)

    # ==================== GERENCIAMENTO ====================

    def limpar_indice(self):
        """Limpa o índice atual."""
        # Reseta collection no ChromaDB
        try:
            self.chroma_client.delete_collection(self.config.collection_name)
        except:
            pass  # Collection pode não existir
        
        st.session_state['vector_store'] = None
        st.session_state['rag_chunks'] = []
        st.session_state['rag_initialized'] = False
        self.vector_store = None

    def get_estatisticas(self) -> dict:
        """Retorna estatísticas do índice atual."""
        chunks = st.session_state.get('rag_chunks', [])
        return self.text_processor.get_estatisticas(chunks)