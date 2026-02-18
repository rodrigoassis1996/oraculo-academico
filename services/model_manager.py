# services/model_manager.py
"""Gerenciador de modelos e chains com suporte a RAG."""

from typing import Dict, Any, Optional, List
import os

try:
    import streamlit as st
except ImportError:
    st = None

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from config.settings import CONFIG_MODELOS, DEFAULT_MODEL_PARAMS, PROMPTS
from services.rag_manager import RAGManager
from services.google_docs.auth import AuthManager
from services.google_docs.client import GoogleDocsClient
from services.google_docs.formatter import AcademicFormatter
from services.google_docs.document_manager import DocumentManager
from agents.orchestrator import OrchestratorAgent

class ModelManager:
    """Gerencia criação de chains e memória de conversação com RAG."""

    def __init__(self, session_state: Optional[Dict[str, Any]] = None):
        self.session_state = session_state
        
        # Se estiver no Streamlit e nenhum estado for passado, usa o session_state do st
        if self.session_state is None and st is not None:
            self._init_st_session_state()
            self.session_state = st.session_state
        elif self.session_state is None:
            # Caso contrário, usa um dicionário local para modo standalone/API
            self.session_state = {
                'chain': None,
                'mensagens': [],
                'usar_rag': True,
                'llm': None,
                'documentos': []
            }

        # Reutiliza RAGManager e DocsManager do session_state se existirem,
        # para não perder documentos indexados entre requisições
        if self.session_state.get('_rag_manager'):
            self.rag_manager = self.session_state['_rag_manager']
        else:
            self.rag_manager = RAGManager(session_state=self.session_state)
            self.session_state['_rag_manager'] = self.rag_manager
        
        if '_docs_manager' in self.session_state:
            self.docs_manager = self.session_state['_docs_manager']
        else:
            self._init_google_docs()
            self.session_state['_docs_manager'] = self.docs_manager
        
        self.orchestrator = OrchestratorAgent(self, docs_manager=self.docs_manager)

    def _init_st_session_state(self) -> None:
        """Inicializa keys no session_state do Streamlit."""
        if 'chain' not in st.session_state:
            st.session_state['chain'] = None
        if 'mensagens' not in st.session_state:
            st.session_state['mensagens'] = []
        if 'usar_rag' not in st.session_state:
            st.session_state['usar_rag'] = True
        if 'llm' not in st.session_state:
            st.session_state['llm'] = None
        if 'documentos' not in st.session_state:
            st.session_state['documentos'] = []

    def _init_google_docs(self):
        """Inicializa componentes do Google Docs."""
        try:
            cwd = os.getcwd()
            credentials_path = os.path.join(cwd, "credentials.json")
            if os.path.exists(credentials_path):
                auth = AuthManager(credentials_path)
                client = GoogleDocsClient(auth)
                formatter = AcademicFormatter(style="ABNT")
                self.docs_manager = DocumentManager(client, formatter)
            else:
                self.docs_manager = None
        except Exception:
            self.docs_manager = None

    @property
    def chain(self):
        return self.session_state.get('chain')

    @property
    def mensagens(self) -> list:
        return self.session_state.get('mensagens', [])

    @property
    def usar_rag(self) -> bool:
        return self.session_state.get('usar_rag', True)

    def adicionar_mensagem(self, role: str, content: str):
        """Adiciona mensagem ao histórico."""
        if 'mensagens' not in self.session_state:
            self.session_state['mensagens'] = []
        self.session_state['mensagens'].append({
            'role': role,
            'content': content
        })

    def get_historico_langchain(self) -> list:
        """Retorna histórico no formato LangChain."""
        historico = []
        for msg in self.mensagens:
            if msg['role'] == 'human':
                historico.append(HumanMessage(content=msg['content']))
            else:
                historico.append(AIMessage(content=msg['content']))
        return historico

    def criar_chain_rag(
        self,
        documentos: list,
        provedor: str = 'OpenAI',
        modelo: str = 'gpt-4o-mini-2024-07-18',
        api_key: str = None,
        progress_callback=None
    ):
        """Cria chain com RAG."""
        config = CONFIG_MODELOS.get(provedor)
        if not config:
            raise ValueError(f"Provedor '{provedor}' não configurado.")
        
        api_key = api_key or config.get('default_api_key')
        if not api_key:
            raise ValueError(f"API key não fornecida para {provedor}.")
        
        # Converte objetos DocumentoCarregado (ou similares) para tuplas (nome, conteudo, doc_hash)
        # Isso garante compatibilidade com o RAGManager que espera tuplas
        docs_para_indexar = []
        for d in documentos:
            if hasattr(d, 'get_conteudo'):
                # É um objeto DocumentoCarregado
                docs_para_indexar.append((d.nome, d.get_conteudo(), d.hash))
            else:
                # Já é uma tupla ou outro formato
                docs_para_indexar.append(d)

        # Indexa documentos no RAG
        stats = self.rag_manager.indexar_documentos(
            docs_para_indexar, 
            progress_callback=progress_callback
        )
        
        # Cria o modelo LLM
        llm = config['chat'](
            model=modelo,
            api_key=api_key,
            **DEFAULT_MODEL_PARAMS
        )
        
        self.session_state['llm'] = llm
        self.session_state['chain'] = "RAG_MODE"
        self.session_state['usar_rag'] = True
        self.session_state['rag_stats'] = stats
        self.session_state['documentos'] = documentos
        
        return stats

    def gerar_resposta_rag(self, pergunta: str):
        """Gera resposta usando RAG ou Agente Orquestrador com streaming."""
        llm = self.session_state.get('llm')
        if not llm:
            raise ValueError("LLM não inicializado. Chame criar_chain_rag ou criar_chain_simples primeiro.")
        
        # Se houver documentos, usamos a lógica do Orquestrador
        if self.session_state.get('documentos'):
            yield from self.orchestrator.planejar_documento(pergunta)
            return

        # Recupera contexto relevante
        contexto = self.rag_manager.get_contexto_para_prompt(pergunta)
        
        if not contexto:
            contexto = "Nenhum contexto relevante encontrado nos documentos."
        
        system_message = PROMPTS['RAG_SYSTEM']
        
        # Recupera metadados para o prompt customizado
        docs_atuais = self.session_state.get('documentos', [])
        nomes_docs = ", ".join([d.nome for d in docs_atuais])
        
        template = ChatPromptTemplate.from_messages([
            ('system', system_message.format(
                contexto=contexto,
                total_docs=len(docs_atuais),
                documentos=nomes_docs
            )),
            ('placeholder', '{chat_history}'),
            ('user', '{input}')
        ])
        
        chain = template | llm
        
        for chunk in chain.stream({
            'input': pergunta,
            'chat_history': self.get_historico_langchain()
        }):
            yield chunk.content

    def criar_chain_simples(
        self,
        documentos_conteudo: str,
        total_documentos: int,
        provedor: str = 'OpenAI',
        modelo: str = 'gpt-4o-mini-2024-07-18',
        api_key: str = None
    ):
        """Cria chain simples (sem RAG)."""
        config = CONFIG_MODELOS.get(provedor)
        if not config:
            raise ValueError(f"Provedor '{provedor}' não configurado.")
        
        api_key = api_key or config.get('default_api_key')
        if not api_key:
            raise ValueError(f"API key não fornecida para {provedor}.")
        
        system_message = PROMPTS['SIMPLE_SYSTEM'].format(
            total_docs=total_documentos, 
            documentos=documentos_conteudo
        )
        
        template = ChatPromptTemplate.from_messages([
            ('system', system_message),
            ('placeholder', '{chat_history}'),
            ('user', '{input}')
        ])
        
        chat = config['chat'](
            model=modelo,
            api_key=api_key,
            **DEFAULT_MODEL_PARAMS
        )
        
        chain = template | chat
        self.session_state['chain'] = chain
        self.session_state['usar_rag'] = False
        self.session_state['llm'] = chat
        
        return chain

    def limpar_memoria(self) -> None:
        """Limpa histórico."""
        self.session_state['mensagens'] = []

    def limpar_chain(self) -> None:
        """Remove chain atual."""
        self.session_state['chain'] = None
        self.session_state['llm'] = None
        self.rag_manager.limpar_indice()

    def reset_completo(self) -> None:
        """Limpa tudo."""
        self.limpar_chain()
        self.limpar_memoria()
