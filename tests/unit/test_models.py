import pytest
import streamlit as st
from services.model_manager import ModelManager

@pytest.fixture
def mock_model_manager(mocker, mock_langchain_openai, mock_embeddings, mock_chroma):
    """Cria instância do ModelManager com mocks."""
    mocker.patch("streamlit.session_state", {})
    return ModelManager()

def test_model_manager_init(mock_model_manager):
    """Valida inicialização do session state via ModelManager."""
    # Como mockamos o session_state como um dict vazio {}, 
    # as chaves devem ter sido criadas no __init__
    assert 'mensagens' in st.session_state
    assert st.session_state['usar_rag'] is True

def test_adicionar_mensagem(mock_model_manager):
    """Testa adição de mensagens ao histórico."""
    mock_model_manager.adicionar_mensagem("human", "Ola")
    assert len(st.session_state['mensagens']) == 1
    assert st.session_state['mensagens'][0]['role'] == "human"

def test_limpar_memoria(mock_model_manager):
    """Testa limpeza do histórico."""
    mock_model_manager.adicionar_mensagem("human", "Ola")
    mock_model_manager.limpar_memoria()
    assert len(st.session_state['mensagens']) == 0
