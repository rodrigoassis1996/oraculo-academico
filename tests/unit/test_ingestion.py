import pytest
import os
from execution.document_ingestion import extract_from_url, extract_from_file

def test_extract_from_file_txt(tmp_path):
    """Testa extração de arquivo TXT."""
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("Hello World", encoding="utf-8")
    
    content = extract_from_file(str(p), ".txt")
    assert "Hello World" in content

def test_extract_from_file_unsupported():
    """Testa erro para extensão não suportada."""
    with pytest.raises(ValueError, match="não suportada"):
        extract_from_file("test.exe", ".exe")

def test_extract_from_url_mock(mocker):
    """Testa extração de URL com mock do Loader."""
    mock_loader = mocker.patch("execution.document_ingestion.WebBaseLoader")
    mock_instance = mock_loader.return_value
    mock_instance.load.return_value = [pytest.importorskip("langchain_core.documents").Document(page_content="Conteúdo da Web")]
    
    content = extract_from_url("http://example.com")
    assert "Conteúdo da Web" in content
