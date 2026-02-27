# tests/unit/test_persistence_logic.py
import pytest
from unittest.mock import MagicMock, patch
from agents.orchestrator import OrchestratorAgent

@pytest.fixture
def orchestrator(mock_mm, mock_docs_manager, mock_auth_manager):
    # Mock do LLM para evitar chamadas reais
    mock_llm = MagicMock()
    
    # Simula estado da sessão com estrutura aprovada e LLM presente
    mock_mm.session_state = {
        'agente_ativo': 'ESTRUTURADOR',
        'active_doc_id': 'doc-123',
        'llm': mock_llm,
        'current_structure': {
            'secoes': [
                {'key': 'INTRODUCAO', 'titulo': 'Introdução'},
                {'key': 'METODOLOGIA', 'titulo': 'Metodologia'},
                {'key': 'CONCLUSAO', 'titulo': 'Conclusão'}
            ]
        }
    }
    # Adicionando o auth_manager ao mock_mm para evitar erros de inicialização
    mock_mm.auth_manager = mock_auth_manager
    # Mock do stream para retornar o que queremos testar
    mock_llm.stream.return_value = [] 
    
    agent = OrchestratorAgent(mock_mm)
    agent.docs_manager = mock_docs_manager
    agent.google_client = MagicMock() # Mock extra para o cliente interno
    return agent



def test_detect_section_key_fuzzy(orchestrator):
    """Valida a detecção robusta de chaves mesmo com títulos levemente diferentes ou acentos."""
    
    # 1. Match exato com acento
    assert orchestrator._detect_section_key("", "### Introdução") == 'INTRODUCAO'
    
    # 2. Match sem acento (Normalização)
    assert orchestrator._detect_section_key("", "### INTRODUCAO") == 'INTRODUCAO'
    
    # 3. Match via Key direta
    assert orchestrator._detect_section_key("", "Aqui está o conteúdo da CONCLUSAO") == 'CONCLUSAO'
    
    # 4. Match via Substring de Início de bloco
    assert orchestrator._detect_section_key("", "Introdução do Estudo sobre IA") == 'INTRODUCAO'

def test_limpar_conteudo_para_doc(orchestrator):
    """Verifica se o limpador remove conversas iniciais."""
    text = "Com certeza! Segue a redação:\n### Introdução\nO texto acadêmico propriamente dito."
    clean = orchestrator._limpar_conteudo_para_doc(text)
    
    # Deve manter o texto mas remover o header e a conversa
    assert "###" not in clean
    assert "Com certeza" not in clean
    assert "O texto acadêmico" in clean
