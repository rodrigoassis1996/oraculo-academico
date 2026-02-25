import pytest
from unittest.mock import MagicMock
from services.google_docs.document_manager import DocumentManager
from services.google_docs.formatter import AcademicFormatter

def test_create_academic_document_empty_sections():
    """Verifica se a criação de documento com seções vazias não gera ranges vazios na API."""
    mock_client = MagicMock()
    mock_client.create_document.return_value = "fake_doc_id"
    
    formatter = AcademicFormatter(style="ABNT")
    manager = DocumentManager(mock_client, formatter)
    
    # Estrutura com títulos vazios ou strings vazias
    estrutura = {
        "titulo": "Teste de Range",
        "secoes": [
            {"key": "INTRO", "titulo": ""},
            {"key": "METODO", "titulo": "Metodologia"}
        ]
    }
    
    # 1. Deve executar sem erros de Python
    doc_id = manager.create_academic_document("Título Teste", estrutura)
    assert doc_id == "fake_doc_id"
    
    # 2. Verifica as requisições enviadas para batch_update
    all_requests = mock_client.batch_update.call_args[0][1]
    
    update_text_styles = [r for r in all_requests if "updateTextStyle" in r]
    update_paragraph_styles = [r for r in all_requests if "updateParagraphStyle" in r]
    
    # Verifica que todos os updateTextStyle têm range não-vazio
    for r in update_text_styles:
        range_data = r["updateTextStyle"]["range"]
        assert range_data["startIndex"] < range_data["endIndex"], f"Range vazio detectado em updateTextStyle: {r}"

    # Verifica que todos os updateParagraphStyle têm range não-vazio
    for r in update_paragraph_styles:
        range_data = r["updateParagraphStyle"]["range"]
        assert range_data["startIndex"] < range_data["endIndex"], f"Range vazio detectado em updateParagraphStyle: {r}"

def test_format_paragraph_empty_string():
    """Testa especificamente o formatador para parágrafo vazio."""
    formatter = AcademicFormatter(style="ABNT")
    # Texto vazio
    reqs = formatter.format_paragraph("", index=10)
    
    # Deve conter insertText e updateParagraphStyle, mas NÃO updateTextStyle
    has_insert = any("insertText" in r for r in reqs)
    has_text_style = any("updateTextStyle" in r for r in reqs)
    has_para_style = any("updateParagraphStyle" in r for r in reqs)
    
    assert has_insert
    assert not has_text_style, "Não deveria haver updateTextStyle para string vazia"
    assert has_para_style
    
    # Verifica range do parágrafo (deve incluir o \n)
    para_req = [r for r in reqs if "updateParagraphStyle" in r][0]
    assert para_req["updateParagraphStyle"]["range"]["startIndex"] == 10
    assert para_req["updateParagraphStyle"]["range"]["endIndex"] == 11 # 10 + 0 + 1
