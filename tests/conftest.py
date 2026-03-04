import pytest
from unittest.mock import MagicMock
import os
import sys

# Mocks para evitar carregamento pesado de bibliotecas durante a descoberta de testes.
# Reduz o tempo de 'collecting' de ~40s para <2s.
# Eles são desativados se o usuário rodar explicitamente testes E2E.
is_e2e = any(arg in ["-m", "e2e"] for arg in sys.argv) or any("tests/e2e" in arg for arg in sys.argv)

if not is_e2e:
    mock_heavy_libs = [
        "langchain_huggingface",
        "chromadb",
        "chromadb.config",
        "langchain_chroma",
        "torch",
        "transformers",
    ]

    for lib in mock_heavy_libs:
        if lib not in sys.modules:
            sys.modules[lib] = MagicMock()
else:
    print("[CONFTEST] Executando em modo E2E. Mocks de performance desativados (coleta pode ser lenta).")

@pytest.fixture(autouse=True, scope="session")
def global_mocks(session_mocker):
    """
    Mocks globais para garantir que bibliotecas pesadas não sejam carregadas nos testes unitários.
    """
    if not is_e2e:
        # Patching via string evita que o 'import' real ocorra aqui.
        session_mocker.patch("langchain_huggingface.HuggingFaceEmbeddings")
        session_mocker.patch("chromadb.PersistentClient")
        session_mocker.patch("langchain_openai.ChatOpenAI")
        
        # Mock para Langchain Chroma para suportar as duas versões possíveis
        try:
            session_mocker.patch("langchain_chroma.Chroma")
        except Exception:
            try:
                session_mocker.patch("langchain_community.vectorstores.Chroma")
            except Exception:
                pass

def pytest_collection_modifyitems(config, items):
    """
    Pula testes marcados como e2e por padrão, a menos que selecionados via -m e2e
    ou se estivermos rodando especificamente a pasta de e2e.
    """
    marker_opt = config.getoption("-m")
    
    # Se o usuário pediu e2e explicitamente ou se estamos em modo is_e2e (via argv), não pulamos.
    if marker_opt == "e2e" or is_e2e:
        return
        
    skip_e2e = pytest.mark.skip(reason="Usar 'pytest -m e2e' para rodar testes pesados")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)

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
