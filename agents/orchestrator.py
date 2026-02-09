# agents/orchestrator.py
"""Implementação do Agente Orquestrador Acadêmico com triagem Maestro e gerenciamento de estado."""

from typing import Generator, List
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from agents.prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT, 
    ESTRUTURADOR_SYSTEM_PROMPT, 
    QA_SYSTEM_PROMPT
)
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class OrchestratorAgent:
    """Agente Maestro que orquestra a triagem e delegação para especialistas."""

    def __init__(self, model_manager):
        self.mm = model_manager
        if 'agente_ativo' not in st.session_state:
            st.session_state['agente_ativo'] = 'ORCHESTRATOR'

    @property
    def llm(self):
        """Acessa o LLM dinamicamente do session_state."""
        return st.session_state.get('llm')

    def route_request(self, input_usuario: str) -> Generator[str, None, None]:
        """Realiza a triagem, troca de estado se necessário e delega para o especialista."""
        if not self.llm:
            raise ValueError("LLM não inicializado no ModelManager.")

        # 1. Classificação de Intenção (Fase Silenciosa)
        # Delegamos para o método de classificação que já possui as proteções de estado
        self.classificar_e_atualizar_estado(input_usuario)
        
        # 2. Seleção do Prompt baseado no Estado Atual
        agente_atual = st.session_state['agente_ativo']
        prompt_sistema = self._get_prompt_por_agente(agente_atual)
        
        # 3. Detecção de Necessidade de Cobertura Total (Global)
        is_global = self._is_global_query(input_usuario, agente_atual)
        
        # 4. Recuperação de Contexto (RAG)
        contexto_rag = self.mm.rag_manager.get_contexto_para_prompt(
            input_usuario, 
            cobertura_total=is_global
        )
        
        # 5. Execução da Chain
        template = ChatPromptTemplate.from_messages([
            ('system', prompt_sistema),
            ('placeholder', '{chat_history}'),
            ('user', '{input}')
        ])
        
        chain = template | self.llm
        
        input_rich = input_usuario
        if contexto_rag and contexto_rag != "Nenhum contexto relevante encontrado nos documentos.":
             label = "CONTEXTO GLOBAL (Todos os docs)" if is_global else "CONTEXTO DOS DOCUMENTOS"
             input_rich = f"{label}:\n{contexto_rag}\n\nSOLICITAÇÃO: {input_usuario}"

        for chunk in chain.stream({
            'input': input_rich,
            'chat_history': self.mm.get_historico_langchain()
        }):
            yield chunk.content
        
        # Se o agente for o Estruturador, entramos no estado de guarda para aprovação
        if st.session_state['agente_ativo'] == 'ESTRUTURADOR':
            st.session_state['agente_ativo'] = 'AGUARDANDO_APROVACAO'

    def _is_global_query(self, input_usuario: str, agente_ativo: str) -> bool:
        """Detecta se a pergunta exige análise de todos os documentos."""
        # Regra 1: Se o agente for o Estruturador, ele precisa de visão global para propor capítulos.
        if agente_ativo == 'ESTRUTURADOR':
            return True
            
        # Regra 2: Keywords que indicam visão geral
        keywords_globais = [
            "todos", "cada um", "resumo geral", "comparativo", 
            "quais são os artigos", "lista de artigos", "panorama"
        ]
        input_lower = input_usuario.lower()
        if any(kw in input_lower for kw in keywords_globais):
            return True
            
        return False

    def classificar_e_atualizar_estado(self, input_usuario: str):
        """Usa o LLM para classificar a intenção e atualizar o st.session_state['agente_ativo']."""
        # Proteção 1: Se estivermos em loop de refinamento ou estruturando, mantemos o estado
        # até que o usuário aprove ou mude explicitamente (via botões na UI)
        estado_atual = st.session_state.get('agente_ativo')
        if estado_atual in ['AGUARDANDO_APROVACAO', 'ESTRUTURADOR']:
            st.session_state['agente_ativo'] = 'ESTRUTURADOR'
            return

        # Só classifica se for uma nova mensagem (prevenção de loop de tokens no rerun)
        last_classified = st.session_state.get('last_input_classified')
        if last_classified == input_usuario:
            return

        prompt_classificador = """Analise o histórico e o último input e classifique em uma palavra:
- ESCRITA: Quer criar documento novo (tese, artigo, etc).
- CONSULTA: Quer dados, dúvidas ou resumos dos arquivos.
- ORCHESTRATOR: Indefinido, saudação ou ambíguo.

Resposta (apenas a palavra):"""
        
        historico_resumo = "\n".join([f"{m['role']}: {m['content'][:100]}..." for m in self.mm.mensagens[-3:]])
        
        mensagens = [
            SystemMessage(content=prompt_classificador),
            HumanMessage(content=f"Histórico:\n{historico_resumo}\n\nInput: {input_usuario}")
        ]
        
        try:
            # Chamada síncrona/rápida para classificação
            resposta = self.llm.invoke(mensagens).content.strip().upper()
            st.session_state['last_input_classified'] = input_usuario
            
            if "ESCRITA" in resposta:
                st.session_state['agente_ativo'] = 'ESTRUTURADOR'
            elif "CONSULTA" in resposta:
                st.session_state['agente_ativo'] = 'QA'
            else:
                st.session_state['agente_ativo'] = 'ORCHESTRATOR'
        except Exception:
            pass

    def _get_prompt_por_agente(self, agente: str) -> str:
        if agente == 'ESTRUTURADOR':
            return ESTRUTURADOR_SYSTEM_PROMPT
        elif agente == 'QA':
            return QA_SYSTEM_PROMPT
        return ORCHESTRATOR_SYSTEM_PROMPT

    def planejar_documento(self, objetivo: str) -> Generator[str, None, None]:
        """Mantido por compatibilidade."""
        yield from self.route_request(objetivo)
