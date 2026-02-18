# tests/services/google_docs/test_index_aware_search.py
import pytest
from unittest.mock import MagicMock
from services.google_docs.client import GoogleDocsClient

@pytest.fixture
def client(mock_auth_manager):
    # Mock do serviço para evitar chamadas reais
    mock_service = MagicMock()
    client = GoogleDocsClient(mock_auth_manager)
    client.service = mock_service
    return client

def test_find_text_in_simple_paragraphs(client):
    """Verifica se encontra índices corretos em parágrafos simples."""
    # Simulando a estrutura de resposta do Google Docs
    mock_doc = {
        "body": {
            "content": [
                {
                    "startIndex": 1,
                    "paragraph": {
                        "elements": [{"textRun": {"content": "Título do Trabalho\n"}}]
                    }
                },
                {
                    "startIndex": 20,
                    "paragraph": {
                        "elements": [{"textRun": {"content": "O marcador está aqui: {{*INTRODUCAO*}}\n"}}]
                    }
                }
            ]
        }
    }
    client.get_document = MagicMock(return_value=mock_doc)
    
    results = client.find_text("doc-id", "{{*INTRODUCAO*}}")
    
    # O marcador começa após "O marcador está aqui: " (22 caracteres)
    # 20 (startIndex) + 22 = 42
    assert len(results) == 1
    start, end = results[0]
    assert start == 42
    assert end == 42 + len("{{*INTRODUCAO*}}")

def test_find_text_in_tables(client):
    """Verifica se encontra texto dentro de células de tabela."""
    mock_doc = {
        "body": {
            "content": [
                {
                    "startIndex": 1,
                    "table": {
                        "tableRows": [
                            {
                                "tableCells": [
                                    {
                                        "content": [
                                            {
                                                "startIndex": 10,
                                                "paragraph": {
                                                    "elements": [{"textRun": {"content": "Tabela: {{*METODOLOGIA*}}"}}]
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
    }
    client.get_document = MagicMock(return_value=mock_doc)
    
    results = client.find_text("doc-id", "{{*METODOLOGIA*}}")
    
    # 10 (startIndex da para dentro da célula) + 8 (len("Tabela: ")) = 18
    assert len(results) == 1
    assert results[0][0] == 18
