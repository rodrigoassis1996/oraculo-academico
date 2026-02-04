# agents/orchestrator.py
"""Implementação do Agente Orquestrador Acadêmico."""

from typing import Generator, List
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from agents.prompts import ORCHESTRATOR_SYSTEM_PROMPT
from config.settings import AGENT_MODEL_PARAMS

class OrchestratorAgent:
    """Agente responsável por coordenar o processo de pesquisa e escrita acadêmica."""

    def __init__(self, model_manager):
        self.mm = model_manager

    @property
    def llm(self):
        """Acessa o LLM dinamicamente do session_state."""
        return st.session_state.get('llm')


    def get_prompt_template(self) -> ChatPromptTemplate:
        """Retorna o template de prompt especializado para o orquestrador."""
        docs_atuais = st.session_state.get('documentos', [])
        nomes_docs = ", ".join([d.nome for d in docs_atuais])
        
        # O orquestrador precisa de contexto, vamos pegar do RAGManager via ModelManager
        contexto = "O usuário subiu os seguintes documentos: " + nomes_docs
        
        return ChatPromptTemplate.from_messages([
            ('system', ORCHESTRATOR_SYSTEM_PROMPT),
            ('placeholder', '{chat_history}'),
            ('user', '{input}')
        ])

    def planejar_documento(self, objetivo: str) -> Generator[str, None, None]:
        """Gera um plano de escrita acadêmica baseado no objetivo do usuário."""
        if not self.llm:
            raise ValueError("LLM não inicializado no ModelManager.")

        # Recupera contexto relevante para o objetivo do usuário
        contexto_rag = self.mm.rag_manager.get_contexto_para_prompt(objetivo)
        
        template = self.get_prompt_template()
        chain = template | self.llm
        
        # Adiciona uma instrução específica de planejamento ao input
        input_rich = f"OBJETIVO DO USUÁRIO: {objetivo}\n\nCONTEXTO DOS DOCUMENTOS:\n{contexto_rag}\n\nPor favor, aja como Orquestrador e proponha o plano de trabalho."

        for chunk in chain.stream({
            'input': input_rich,
            'chat_history': self.mm.get_historico_langchain()
        }):
            yield chunk.content
