import pytest
from services.model_manager import ModelManager

@pytest.fixture
def mock_model_manager(mocker, mock_langchain_openai, mock_embeddings, mock_chroma):
    """Cria instância do ModelManager com mocks."""
    return ModelManager(session_state={})

def test_model_manager_init(mock_langchain_openai, mock_embeddings, mock_chroma):
    """Valida inicialização do session state via ModelManager."""
    # Instancia sem passar state para forçar criação dos defaults
    mm = ModelManager() 
    assert 'mensagens' in mm.session_state
    assert mm.session_state['usar_rag'] is True

def test_adicionar_mensagem(mock_model_manager):
    """Testa adição de mensagens ao histórico."""
    mock_model_manager.adicionar_mensagem("human", "Ola")
    assert len(mock_model_manager.session_state['mensagens']) == 1
    assert mock_model_manager.session_state['mensagens'][0]['role'] == "human"

def test_limpar_memoria(mock_model_manager):
    """Testa limpeza do histórico."""
    mock_model_manager.adicionar_mensagem("human", "Ola")
    mock_model_manager.limpar_memoria()
    assert len(mock_model_manager.session_state['mensagens']) == 0
