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
    with patch('streamlit.session_state', {'llm': None, 'documentos': []}):
        agent = OrchestratorAgent(mock_mm)
        assert agent.llm is None
        with pytest.raises(ValueError, match="LLM não inicializado no ModelManager"):
            # A execução deve falhar logo no início ao acessar self.llm no planejar_documento
            next(agent.planejar_documento("objetivo"))

    # Cenário 2: LLM Presente
    mock_llm = MagicMock()
    with patch('streamlit.session_state', {'llm': mock_llm, 'documentos': []}):
        agent = OrchestratorAgent(mock_mm)
        assert agent.llm == mock_llm
        # Verifica se o planejar_documento acessa o llm (ele deve tentar criar o chain)
        with patch.object(OrchestratorAgent, 'get_prompt_template', return_value=MagicMock()):
             # Basta verificar que não lança ValueError de imediato
             try:
                 gen = agent.planejar_documento("objetivo")
                 next(gen)
             except StopIteration:
                 pass # O gerador pode estar vazio no mock
             except Exception as e:
                 if isinstance(e, ValueError) and "LLM não inicializado" in str(e):
                     pytest.fail("Lançou ValueError mesmo com LLM presente")


def test_get_prompt_template_persona(mock_mm):
    """Verifica se a persona correta é carregada no template."""
    with patch('streamlit.session_state', {'documentos': []}):
        agent = OrchestratorAgent(mock_mm)
        template = agent.get_prompt_template()
        assert "Coordenador de Pesquisa" in template.messages[0].prompt.template
