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
