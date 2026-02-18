# tests/unit/test_orchestrator.py
"""Testes unitários para o Agente Orquestrador."""

import pytest
from unittest.mock import MagicMock, patch
from agents.orchestrator import OrchestratorAgent

@pytest.fixture
def mock_mm():
    """Mock do ModelManager."""
    mm = MagicMock()
    mm.get_historico_langchain.return_value = []
    mm.rag_manager.get_contexto_para_prompt.return_value = "Trechos de teste."
    return mm

def test_llm_initialization_validation(mock_mm):
    """Valida se o erro é lançado quando o LLM não está inicializado e funciona quando está."""
    # Cenário 1: LLM Ausente
    mock_mm.session_state = {'llm': None, 'documentos': []}
    agent = OrchestratorAgent(mock_mm)
    assert agent.llm is None
    with pytest.raises(ValueError, match="LLM não inicializado no ModelManager"):
        # A execução deve falhar logo no início ao acessar self.llm no route_request
        next(agent.route_request("objetivo"))

    # Cenário 2: LLM Presente
    mock_llm = MagicMock()
    mock_mm.session_state = {'llm': mock_llm, 'documentos': []}
    agent = OrchestratorAgent(mock_mm)
    assert agent.llm == mock_llm
    # Verifica se o route_request acessa o llm
    with patch('agents.orchestrator.ChatPromptTemplate.from_messages') as mock_prompt:
         mock_chain = MagicMock()
         mock_prompt.return_value.__or__.return_value = mock_chain
         try:
             gen = agent.route_request("objetivo")
             next(gen)
         except StopIteration:
             pass 
         except Exception as e:
             if isinstance(e, ValueError) and "LLM não inicializado" in str(e):
                 pytest.fail("Lançou ValueError mesmo com LLM presente")
