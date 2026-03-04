# tests/unit/test_orchestrator.py
"""Testes unitários para o Agente Orquestrador."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
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
    
    # Patch direto na propriedade para garantir o valor None independente de mocks globais
    with patch.object(OrchestratorAgent, 'llm', new_callable=PropertyMock) as mock_prop:
        mock_prop.return_value = None
        assert agent.llm is None
        with pytest.raises(ValueError, match="LLM não inicializado no ModelManager"):
            next(agent.route_request("objetivo"))

    # Cenário 2: LLM Presente
    mock_llm = MagicMock()
    with patch.object(OrchestratorAgent, 'llm', new_callable=PropertyMock) as mock_prop:
        mock_prop.return_value = mock_llm
        agent = OrchestratorAgent(mock_mm)
        assert agent.llm == mock_llm
