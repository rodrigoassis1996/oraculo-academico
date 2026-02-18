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

def test_detect_multiple_sections_and_save(orchestrator, mock_docs_manager):
    """Verifica se o orquestrador identifica múltiplos blocos ### e chama o salvamento para cada um."""
    
    # Resposta simulada com 2 blocos ###
    full_response = (
        "Com certeza, aqui está a introdução:\n\n"
        "### Introdução\n"
        "Este é o texto da introdução acadêmica.\n\n"
        "### Metodologia\n"
        "Aqui descrevemos o método científico aplicado."
    )
    
    # Precisamos mockar o chain.stream para retornar nosso texto simulado
    mock_chunk = MagicMock()
    mock_chunk.content = full_response
    
    with patch('agents.orchestrator.ChatPromptTemplate.from_messages') as mock_prompt:
        mock_chain = MagicMock()
        mock_chain.stream.return_value = [mock_chunk]
        
        # O Langchain usa prompt | llm, que chama prompt.__or__(llm)
        # Precisamos garantir que isso retorne nossa cadeia mockada
        mock_prompt.return_value.__or__.return_value = mock_chain
        
        # Executa o roteamento (dispara a lógica de persistência no final)
        # Consumimos o generator para garantir que o loop interno rode
        list(orchestrator.route_request("prossiga"))
        
    # Verifica se write_section foi chamado 2 vezes (uma para cada bloco)
    assert mock_docs_manager.write_section.call_count == 2
    
    # Verifica os argumentos das chamadas (posicionais conforme assinatura)
    calls = mock_docs_manager.write_section.call_args_list
    
    # Primeira chamada: INTRODUCAO
    # Signature: write_section(doc_id, section_key, content, title_hint=None)
    args_1, kwargs_1 = calls[0]
    assert args_1[1] == 'INTRODUCAO'
    assert 'texto da introdução' in args_1[2]
    assert kwargs_1.get('title_hint') == 'Introdução'
    
    # Segunda chamada: METODOLOGIA
    args_2, kwargs_2 = calls[1]
    assert args_2[1] == 'METODOLOGIA'
    assert 'método científico' in args_2[2]
    assert kwargs_2.get('title_hint') == 'Metodologia'

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
