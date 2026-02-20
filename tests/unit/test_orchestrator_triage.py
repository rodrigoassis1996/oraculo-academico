# tests/unit/test_orchestrator_triage.py
"""Testes unitários focados na lógica de triagem e troca de estado do Orquestrador."""

import pytest
from unittest.mock import MagicMock, patch
from agents.orchestrator import OrchestratorAgent
from agents.prompts import ORCHESTRATOR_SYSTEM_PROMPT, ESTRUTURADOR_SYSTEM_PROMPT

@pytest.fixture
def mock_mm():
    """Mock do ModelManager."""
    mm = MagicMock()
    mm.get_historico_langchain.return_value = []
    mm.rag_manager.get_contexto_para_prompt.return_value = "Trechos de teste."
    mm.mensagens = []
    return mm

def test_route_request_calls_llm_with_orchestrator_prompt(mock_mm):
    """Verifica se o route_request usa o prompt do orquestrador inicialmente."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "ORCHESTRATOR"
    mock_llm.invoke.return_value = mock_response
    
    class MockChunk:
        def __init__(self, content): self.content = content
        @property
        def content(self): return self._content # use property to be safe
        @content.setter
        def content(self, val): self._content = val
        def __str__(self): return self._content

    mock_mm.session_state = {'llm': mock_llm, 'agente_ativo': 'ORCHESTRATOR'}
    agent = OrchestratorAgent(mock_mm)
    
    # Patch direto na classe para garantir que capture a chamada
    with patch('agents.orchestrator.ChatPromptTemplate.from_messages') as mock_template_factory:
        mock_template = MagicMock()
        mock_template_factory.return_value = mock_template
        mock_chain = MagicMock()
        mock_template.__or__.return_value = mock_chain
        
        # O chunk deve ter .content sendo string
        chunk = MagicMock()
        chunk.content = "Maestro resp"
        mock_chain.stream.return_value = [chunk]
            
        # Força o classificador a retornar ORCHESTRATOR para este teste
        with patch.object(OrchestratorAgent, 'classificar_e_atualizar_estado'):
            gen = agent.route_request("Oi")
            list(gen) # Consome o gerador
        
        # Verifica se o template foi criado com o prompt do Orquestrador
        assert mock_template_factory.called, "ChatPromptTemplate.from_messages não foi chamado"
        args, _ = mock_template_factory.call_args
        assert args[0][0][1] == ORCHESTRATOR_SYSTEM_PROMPT

def test_state_transition_to_writing(mock_mm):
    """Verifica se o estado muda para ESTRUTURADOR quando a intenção é escrita."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "ESCRITA"
    mock_llm.invoke.return_value = mock_response
    
    mock_mm.session_state = {'llm': mock_llm, 'agente_ativo': 'ORCHESTRATOR'}
    agent = OrchestratorAgent(mock_mm)
    agent.classificar_e_atualizar_estado("Quero um artigo")
    assert mock_mm.session_state['agente_ativo'] == 'ESTRUTURADOR'

def test_prompt_selection_after_transition(mock_mm):
    """Verifica se o prompt do Estruturador é usado após a transição."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "ESCRITA"
    mock_llm.invoke.return_value = mock_response
    
    mock_mm.session_state = {'llm': mock_llm, 'agente_ativo': 'ESTRUTURADOR', 'documentos': ['doc1']}
    agent = OrchestratorAgent(mock_mm)
    
    with patch('agents.orchestrator.ChatPromptTemplate.from_messages') as mock_template_factory:
        mock_template = MagicMock()
        mock_template_factory.return_value = mock_template
        mock_chain = MagicMock()
        mock_template.__or__.return_value = mock_chain
        
        chunk = MagicMock()
        chunk.content = "" # String vazia para evitar TypeError no re
        mock_chain.stream.return_value = [chunk]
            
        with patch.object(OrchestratorAgent, 'classificar_e_atualizar_estado'):
            list(agent.route_request("Como estruturar?"))
        
        assert mock_template_factory.called
        args, _ = mock_template_factory.call_args
        assert args[0][0][1] == ESTRUTURADOR_SYSTEM_PROMPT

def test_is_global_query_detection(mock_mm):
    """Verifica a lógica de detecção de perguntas globais."""
    agent = OrchestratorAgent(mock_mm)
    
    # Por estado
    assert agent._is_global_query("oi", "ESTRUTURADOR") is True
    
    # Por keyword
    assert agent._is_global_query("Resumo de todos os artigos", "QA") is True
    assert agent._is_global_query("Quais são os artigos que tenho?", "ORCHESTRATOR") is True
    
    # Negativo
    assert agent._is_global_query("O que diz o texto A?", "QA") is False
