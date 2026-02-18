import pytest
from unittest.mock import MagicMock
import os

@pytest.fixture
def mock_env(monkeypatch):
    """Garante que as variáveis de ambiente necessárias estejam presentes."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("USER_AGENT", "test-agent")

@pytest.fixture
def mock_langchain_openai(mocker):
    """Mock para ChatOpenAI."""
    mock_chat = mocker.patch("langchain_openai.ChatOpenAI")
    instance = mock_chat.return_value
    instance.stream.return_value = [MagicMock(content="Resposta simulada")]
    return mock_chat

@pytest.fixture
def mock_embeddings(mocker):
    """Mock para HuggingFaceEmbeddings."""
    mock_emb = mocker.patch("langchain_huggingface.HuggingFaceEmbeddings")
    return mock_emb

@pytest.fixture
def mock_chroma(mocker):
    """Mock para ChromaDB."""
    mock_client = mocker.patch("chromadb.PersistentClient")
    mock_vectorstore = mocker.patch("langchain_community.vectorstores.Chroma")
    return mock_client, mock_vectorstore
@pytest.fixture
def mock_auth_manager(mocker):
    """Mock para o AuthManager."""
    mock_auth = mocker.patch("services.google_docs.auth.AuthManager")
    return mock_auth.return_value

@pytest.fixture
def mock_google_docs_client(mocker, mock_auth_manager):
    """Mock para o cliente da API do Google Docs."""
    mock_client = mocker.patch("services.google_docs.client.GoogleDocsClient")
    instance = mock_client.return_value
    instance.auth_manager = mock_auth_manager
    instance.get_document.return_value = {"body": {"content": []}}
    return instance

@pytest.fixture
def mock_docs_manager(mocker, mock_google_docs_client):
    """Mock para o DocumentManager."""
    mock_manager = mocker.patch("services.google_docs.document_manager.DocumentManager")
    instance = mock_manager.return_value
    return instance

@pytest.fixture
def mock_mm(mock_auth_manager):
    """Mock do ModelManager central."""
    mm = MagicMock()
    mm.get_historico_langchain.return_value = []
    mm.rag_manager.get_contexto_para_prompt.return_value = "Contexto de teste acadêmico."
    mm.auth_manager = mock_auth_manager
    mm.session_state = {}
    return mm
