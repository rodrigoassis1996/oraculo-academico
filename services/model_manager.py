# services/model_manager.py
"""Gerenciador de modelos e chains com suporte a RAG."""

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from config.settings import CONFIG_MODELOS, DEFAULT_MODEL_PARAMS, PROMPTS, RAG_CONFIG
from services.rag_manager import RAGManager
from services.google_docs.auth import AuthManager
from services.google_docs.client import GoogleDocsClient
from services.google_docs.formatter import AcademicFormatter
from services.google_docs.document_manager import DocumentManager
from agents.orchestrator import OrchestratorAgent

class ModelManager:

    """Gerencia criação de chains e memória de conversação com RAG."""

    def __init__(self):
        self._init_session_state()
        self.rag_manager = RAGManager()
        self._init_google_docs()
        self.orchestrator = OrchestratorAgent(self, docs_manager=self.docs_manager)

    def _init_google_docs(self):
        """Inicializa componentes do Google Docs."""
        try:
            import os
            credentials_path = os.path.join(os.getcwd(), "credentials.json")
            if os.path.exists(credentials_path):
                auth = AuthManager(credentials_path)
                client = GoogleDocsClient(auth)
                formatter = AcademicFormatter(style="ABNT")
                self.docs_manager = DocumentManager(client, formatter)
            else:
                self.docs_manager = None
        except Exception:
            self.docs_manager = None


    def _init_session_state(self) -> None:
        """Inicializa keys no session_state."""
        if 'chain' not in st.session_state:
            st.session_state['chain'] = None
        if 'mensagens' not in st.session_state:
            st.session_state['mensagens'] = []  # Lista simples de mensagens
        if 'usar_rag' not in st.session_state:
            st.session_state['usar_rag'] = True

    @property
    def chain(self):
        return st.session_state.get('chain')

    @property
    def mensagens(self) -> list:
        return st.session_state.get('mensagens', [])

    @property
    def usar_rag(self) -> bool:
        return st.session_state.get('usar_rag', True)

    def adicionar_mensagem(self, role: str, content: str):
        """Adiciona mensagem ao histórico."""
        st.session_state['mensagens'].append({
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
        
        # Indexa documentos no RAG
        stats = self.rag_manager.indexar_documentos(
            documentos, 
            progress_callback=progress_callback
        )
        
        # Cria o modelo LLM usando parâmetros padronizados
        llm = config['chat'](
            model=modelo,
            api_key=api_key,
            **DEFAULT_MODEL_PARAMS
        )
        
        st.session_state['llm'] = llm
        st.session_state['chain'] = "RAG_MODE"
        st.session_state['usar_rag'] = True
        st.session_state['rag_stats'] = stats
        
        return stats

    def gerar_resposta_rag(self, pergunta: str):
        """Gera resposta usando RAG ou Agente Orquestrador com streaming."""
        llm = st.session_state.get('llm')
        if not llm:
            raise ValueError("LLM não inicializado.")
        
        # Se houver documentos, usamos a lógica do Orquestrador
        if st.session_state.get('documentos'):
            yield from self.orchestrator.planejar_documento(pergunta)
            return

        # Recupera contexto relevante

        contexto = self.rag_manager.get_contexto_para_prompt(pergunta)
        
        if not contexto:
            contexto = "Nenhum contexto relevante encontrado nos documentos."
        
        system_message = PROMPTS['RAG_SYSTEM']
        
        # Recupera metadados para o prompt customizado do usuário
        docs_atuais = st.session_state.get('documentos', [])
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
        st.session_state['chain'] = chain
        st.session_state['usar_rag'] = False
        
        return chain

    def limpar_memoria(self) -> None:
        """Limpa histórico."""
        st.session_state['mensagens'] = []

    def limpar_chain(self) -> None:
        """Remove chain atual."""
        st.session_state['chain'] = None
        st.session_state['llm'] = None
        self.rag_manager.limpar_indice()

    def reset_completo(self) -> None:
        """Limpa tudo."""
        self.limpar_chain()
        self.limpar_memoria()