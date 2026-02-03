import pytest
from unittest.mock import MagicMock
from services.rag_manager import RAGManager, RAGConfig

@pytest.fixture
def mock_rag_manager(mocker, mock_embeddings, mock_chroma):
    """Cria instância do RAGManager com mocks."""
    # Mock do Streamlit session state
    mocker.patch("streamlit.session_state", {})
    return RAGManager()

def test_rag_manager_init(mock_rag_manager):
    """Valida inicialização do RAGManager."""
    assert mock_rag_manager.config.collection_name == "oraculo_docs"

def test_indexar_documentos_vazio(mock_rag_manager):
    """Testa comportamento com lista vazia."""
    with pytest.raises(ValueError, match="Nenhum documento válido"):
        mock_rag_manager.indexar_documentos([])

def test_buscar_relevantes_vazio(mock_rag_manager):
    """Testa busca sem inicialização."""
    assert mock_rag_manager.buscar_relevantes("pergunta") == []
