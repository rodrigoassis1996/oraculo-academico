# services/rag_manager.py
"""Gerenciador RAG - Embeddings, Vector Store e Retrieval."""


import os
import shutil
from typing import List, Optional
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings as ChromaSettings

from langchain_huggingface import HuggingFaceEmbeddings
try:
    from langchain_chroma import Chroma
except ImportError:
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

    def __init__(self, config: RAGConfig = None, session_state: dict = None):
        from config.settings import RAG_CONFIG
        self.config = config or RAG_CONFIG
        self._external_state = session_state if session_state is not None else {}
        
        self.text_processor = TextProcessor(
            ChunkConfig(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
        )
        self._init_session_state()
        self._init_embeddings()
        self._init_vector_store()
        self._lifecycle_purge()

    @property
    def session_state(self):
        """Retorna o estado da sessão atual."""
        return self._external_state

    def _lifecycle_purge(self):
        """Remove arquivos temporários e índices com mais de 48h."""
        import time
        current_time = time.time()
        max_age = 48 * 3600  # 48 horas em segundos
        
        base_tmp = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.tmp'))
        content_dir = os.path.join(base_tmp, 'content')
        
        if os.path.exists(content_dir):
            for f in os.listdir(content_dir):
                file_path = os.path.join(content_dir, f)
                if os.path.isfile(file_path):
                    if current_time - os.path.getmtime(file_path) > max_age:
                        try:
                            os.remove(file_path)
                        except:
                            pass


    def _init_session_state(self):
        """Inicializa session state."""
        if 'rag_chunks' not in self.session_state:
            self.session_state['rag_chunks'] = []
        if 'rag_initialized' not in self.session_state:
            self.session_state['rag_initialized'] = False

    def _init_embeddings(self):
        """Inicializa modelo de embeddings."""
        # Cache do modelo para não recarregar
        if 'embedding_model' not in self.session_state:
            # Bug fix: 'Cannot copy out of meta tensor' em versões recentes de torch/transformers
            # Forçamos o carregamento direto no CPU sem usar meta tensors se possível
            self.session_state['embedding_model'] = HuggingFaceEmbeddings(
                model_name=self.config.embedding_model,
                model_kwargs={
                    'device': 'cpu',
                    'trust_remote_code': True
                },
                encode_kwargs={'normalize_embeddings': True}
            )
        self.embeddings = self.session_state['embedding_model']

    def _init_vector_store(self):
        """Inicializa vector store persistente."""
        persist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.tmp', 'vector_db'))
        
        # Cliente ChromaDB persistente
        if 'chroma_client' not in self.session_state:
            try:
                self.session_state['chroma_client'] = chromadb.PersistentClient(
                    path=persist_dir,
                    settings=ChromaSettings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
            except Exception as e:
                # Se falhar a abertura (comum em corrupção de índice HNSW)
                print(f"⚠️ Erro ao carregar banco de vetores: {str(e)}")
                
                # Tenta limpar a pasta e reinicializar
                try:
                    if os.path.exists(persist_dir):
                        print(f"🧹 Tentando limpar índice corrompido em: {persist_dir}")
                        # No Windows, arquivos podem estar presos por outros processos.
                        # Tentamos remover recursivamente.
                        shutil.rmtree(persist_dir, ignore_errors=True)
                    
                    os.makedirs(persist_dir, exist_ok=True)
                    
                    self.session_state['chroma_client'] = chromadb.PersistentClient(
                        path=persist_dir,
                        settings=ChromaSettings(
                            anonymized_telemetry=False,
                            allow_reset=True
                        )
                    )
                except PermissionError:
                    print("⚠️ Pasta de vetores bloqueada (PermissionError). Usando Fallback em memória.")
                    self.session_state['chroma_client'] = chromadb.Client(
                        settings=ChromaSettings(anonymized_telemetry=False)
                    )
                except Exception as recovery_error:
                    print(f"❌ Falha crítica na recuperação: {str(recovery_error)}")
                    # Fallback para cliente em memória se falhar feio
                    self.session_state['chroma_client'] = chromadb.Client(
                        settings=ChromaSettings(anonymized_telemetry=False)
                    )

        self.chroma_client = self.session_state['chroma_client']

        
        # Vector store
        if 'vector_store' not in self.session_state:
            self.session_state['vector_store'] = None
        self.vector_store = self.session_state['vector_store']

    @property
    def is_initialized(self) -> bool:
        """Verifica se o RAG está inicializado com documentos."""
        return self.session_state.get('rag_initialized', False)

    @property
    def total_chunks(self) -> int:
        """Total de chunks indexados."""
        return len(self.session_state.get('rag_chunks', []))

    # ==================== INDEXAÇÃO ====================

    def indexar_documentos(
        self,
        documentos: List[tuple],  # [(nome, conteudo, hash), ...]
        incremental: bool = True,
        progress_callback=None
    ) -> dict:
        """
        Indexa múltiplos documentos no vector store de forma incremental.
        
        Args:
            documentos: Lista de tuplas (nome, conteudo, hash)
            incremental: Se True, pula documentos já indexados
            progress_callback: Função para atualizar progresso
            
        Returns:
            Estatísticas da indexação
        """
        if not incremental:
            self.limpar_indice()
        
        # Pega hashes atuais da UI para sincronização
        def get_val(obj, attr, index):
            if isinstance(obj, (list, tuple)):
                return obj[index]
            return getattr(obj, attr, None)

        def get_conteudo(obj):
            if hasattr(obj, 'get_conteudo'):
                return obj.get_conteudo()
            return get_val(obj, 'conteudo', 1)

        hashes_atuais = set(get_val(d, 'hash', 2) for d in documentos)
        
        # Pega coleção atual para verificar hashes
        try:
            collection = self.chroma_client.get_collection(self.config.collection_name)
            # Extrai hashes únicos já presentes na coleção
            existing_metadata = collection.get(include=['metadatas'])['metadatas']
            hashes_no_banco = set(m.get('hash') for m in existing_metadata if m.get('hash'))
            
            # Sincronização: Remove do banco o que não está mais na lista da UI
            hashes_para_deletar = hashes_no_banco - hashes_atuais
            if hashes_para_deletar:
                if progress_callback:
                    progress_callback(0.1, f"Limpando {len(hashes_para_deletar)} documentos antigos...")
                # Deleta usando o filtro de metadados
                collection.delete(where={"hash": {"$in": list(hashes_para_deletar)}})
                # Atualiza lista do que restou
                hashes_no_banco = hashes_no_banco - hashes_para_deletar
        except Exception as e:
            hashes_no_banco = set()
            print(f"Aviso na sincronização: {e}")

        todos_chunks = []
        documentos_langchain = []
        
        total_docs = len(documentos)
        docs_skipped = 0
        
        for i, d in enumerate(documentos):
            nome = get_val(d, 'nome', 0)
            conteudo = get_conteudo(d)
            doc_hash = get_val(d, 'hash', 2)
            
            if progress_callback:
                progress_callback((i + 1) / (total_docs + 1), f"Processando {nome}...")
            
            # Valida conteúdo
            is_valid, msg = self.text_processor.validar_conteudo_extraido(conteudo)
            if not is_valid:
                st.warning(f"⚠️ {nome}: {msg}")
                continue
            
            # Sempre gera chunks para o UI (processamento de texto é rápido)
            chunks = self.text_processor.criar_chunks(conteudo, nome)
            todos_chunks.extend(chunks)
            
            # Só adiciona no LangChain se NÃO estiver no banco
            if incremental and doc_hash in hashes_no_banco:
                docs_skipped += 1
            else:
                for chunk in chunks:
                    doc = Document(
                        page_content=chunk.conteudo,
                        metadata={
                            "source": chunk.documento_origem,
                            "chunk_index": chunk.indice,
                            "hash": doc_hash
                        }
                    )
                    documentos_langchain.append(doc)

        # Se não há documentos válidos (nem novos nem antigos), aí sim erro
        if not todos_chunks:
            raise ValueError("Nenhum documento válido para indexar.")

        # Se não há nada NOVO para indexar
        if not documentos_langchain:
            # Garante que o vector store está conectado
            self.vector_store = Chroma(
                collection_name=self.config.collection_name,
                embedding_function=self.embeddings,
                client=self.chroma_client
            )
            
            # Atualiza session state com os chunks carregados
            self.session_state['rag_chunks'] = todos_chunks
            self.session_state['vector_store'] = self.vector_store
            self.session_state['rag_initialized'] = True
            
            if progress_callback:
                progress_callback(1.0, "Documentos sincronizados com sucesso.")
            
            stats = self.text_processor.get_estatisticas(todos_chunks)
            stats['documentos_indexados'] = len(set(c.documento_origem for c in todos_chunks))
            stats['documentos_pulpados'] = docs_skipped
            stats['novos_documentos'] = 0
            
            return stats
        
        if progress_callback:
            progress_callback(0.9, "Atualizando embeddings...")
        
        # Adiciona novos documentos ao vector store existente ou cria um novo
        if self.vector_store and incremental:
            self.vector_store.add_documents(documentos_langchain)
        else:
            self.vector_store = Chroma.from_documents(
                documents=documentos_langchain,
                embedding=self.embeddings,
                collection_name=self.config.collection_name,
                client=self.chroma_client
            )
        
        # Atualiza session state com todos os chunks processados
        self.session_state['rag_chunks'] = todos_chunks

        self.session_state['vector_store'] = self.vector_store
        self.session_state['rag_initialized'] = True
        
        if progress_callback:
            progress_callback(1.0, "Concluído!")
        
        # Estatísticas
        chunks_finais = self.session_state['rag_chunks']
        stats = self.text_processor.get_estatisticas(chunks_finais)
        stats['documentos_indexados'] = len(set(c.documento_origem for c in chunks_finais))
        stats['documentos_pulpados'] = docs_skipped
        
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

    def buscar_em_todos_os_documentos(
        self, 
        query: str, 
        k_por_doc: int = 3
    ) -> List[Document]:
        """
        Busca chunks mais relevantes em CADA um dos documentos indexados.
        Garante cobertura total do corpus.
        """
        if not self.is_initialized or self.vector_store is None:
            return []
            
        # Pega a lista de todos os fontes (sources) unicos
        collection = self.chroma_client.get_collection(self.config.collection_name)
        metadata = collection.get(include=['metadatas'])['metadatas']
        sources = list(set(m.get('source') for m in metadata if m.get('source')))
        
        documentos_finais = []
        for source in sources:
            # Busca filtrando por source
            docs_doc = self.vector_store.similarity_search(
                query, 
                k=k_por_doc, 
                filter={"source": source}
            )
            documentos_finais.extend(docs_doc)
            
        return documentos_finais

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

    def get_contexto_para_prompt(self, query: str, top_k: int = None, cobertura_total: bool = False) -> str:
        """
        Retorna contexto formatado para incluir no prompt.
        
        Args:
            query: Pergunta do usuário
            top_k: Número de chunks a retornar (se cobertura_total=False)
            cobertura_total: Se True, busca em todos os documentos individualmente.
            
        Returns:
            String formatada com os chunks relevantes
        """
        if cobertura_total:
            docs = self.buscar_em_todos_os_documentos(query)
        else:
            docs = self.buscar_relevantes(query, top_k)
        
        if not docs:
            return ""
        
        contexto_partes = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Desconhecido')
            contexto_partes.append(
                f"--- CONTEÚDO DO DOCUMENTO: {source} (Fragmento {i}) ---\n{doc.page_content}"
            )
        
        return "\n\n".join(contexto_partes)

    # ==================== GERENCIAMENTO ====================

    def limpar_indice(self):
        """Limpa o índice atual."""
        # Reseta collection no ChromaDB
        try:
            self.chroma_client.delete_collection(self.config.collection_name)
        except:
            pass  # Collection pode não existir
        
        self.session_state['vector_store'] = None
        self.session_state['rag_chunks'] = []
        self.session_state['rag_initialized'] = False
        self.vector_store = None

    def get_estatisticas(self) -> dict:
        """Retorna estatísticas do índice atual."""
        chunks = self.session_state.get('rag_chunks', [])
        return self.text_processor.get_estatisticas(chunks)

    def purgar_fisicamente(self):
        """Deleta fisicamente todas as pastas de dados locais (usando reset para o Chroma)."""
        self.limpar_indice()
        
        # 1. Reset do ChromaDB (mais seguro que rm -rf no Windows com o arquivo aberto)
        try:
            self.chroma_client.reset()
        except Exception as e:
            print(f"Aviso: Erro ao resetar Chroma: {e}")

        # 2. Limpeza do cache de texto em .tmp/content/
        base_tmp = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.tmp'))
        content_dir = os.path.join(base_tmp, 'content')
        
        if os.path.exists(content_dir):
            try:
                shutil.rmtree(content_dir)
                os.makedirs(content_dir, exist_ok=True)
                return True, "✅ Dados locais purgados com sucesso."
            except Exception as e:
                return False, f"❌ Erro ao purgar cache de texto: {str(e)}"
        
        return True, "✅ Purga concluída."

