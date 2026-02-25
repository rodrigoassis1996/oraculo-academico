# tests/services/google_docs/test_document_manager.py

import pytest
from unittest.mock import MagicMock, patch
from services.google_docs.document_manager import DocumentManager
from services.google_docs.client import GoogleDocsClient
from services.google_docs.formatter import AcademicFormatter

class TestDocumentManager:
    
    @pytest.fixture
    def mock_client(self):
        return MagicMock(spec=GoogleDocsClient)
        
    @pytest.fixture
    def mock_formatter(self):
        formatter = MagicMock(spec=AcademicFormatter)
        formatter.create_section_placeholder.side_effect = lambda k: f"{{{{*{k}*}}}}"
        formatter.create_section_markers.side_effect = lambda k: (f"[[START:{k}]]", f"[[END:{k}]]")
        formatter.get_document_style_requests.return_value = [{"updateDocumentStyle": {}}]
        formatter.format_paragraph.side_effect = lambda text, idx: [{"insertText": {"location": {"index": idx}, "text": f"{text}\n"}}]
        formatter.format_heading.side_effect = lambda text, level, index: [{"insertText": {"location": {"index": index}, "text": f"{text}\n"}}]
        return formatter
        
    @pytest.fixture
    def doc_manager(self, mock_client, mock_formatter):
        return DocumentManager(mock_client, mock_formatter)

    def test_create_academic_document_applies_styles(self, doc_manager, mock_client):
        """Document creation applies initial styles and structure."""
        mock_client.create_document.return_value = "doc123"
        
        structure = {
            "titulo": "Teste",
            "secoes": [{"key": "INTRO", "titulo": "Introdução"}]
        }
        
        doc_manager.create_academic_document("Teste", structure)
        
        assert mock_client.create_document.called
        # Verify batchUpdate was called with style requests + initial structure
        args, _ = mock_client.batch_update.call_args
        requests = args[1]
        assert any("updateDocumentStyle" in r for r in requests)
        assert any("insertText" in r and "Teste" in r["insertText"]["text"] for r in requests)

    def test_write_section_replaces_with_multiple_paragraphs(self, doc_manager, mock_client):
        """Content replaces placeholder and handles multiple paragraphs."""
        # find_text is called first for START/END markers, then for placeholder
        def find_text_side_effect(doc_id, query):
            if "[[" in query: return [] # No markers
            return [(10, 20)] # Found placeholder
            
        mock_client.find_text.side_effect = find_text_side_effect
        content = "Parágrafo 1\nParágrafo 2"
        
        doc_manager.write_section("doc123", "INTRO", content, mode="replace")
        
        mock_client.delete_range.assert_called_with("doc123", 10, 20)
        # Verify batch_update was called with formatted paragraphs
        assert mock_client.batch_update.called

    def test_get_section_content_extraction(self, doc_manager, mock_client):
        """Correctly extracts content between specific markers."""
        # Content with markers
        content = "Título\n[[START:INTRO]]Conteúdo da introdução[[END:INTRO]]\nFim"
        # Since get_full_content uses get_document, we mock both
        mock_client.get_document.return_value = {
            'body': {
                'content': [{'paragraph': {'elements': [{'textRun': {'content': content}}]}}]
            }
        }
        
        extracted = doc_manager.get_section_content("doc123", "INTRO")
        assert extracted == "Conteúdo da introdução"

    def test_finalize_removes_placeholders(self, doc_manager, mock_client):
        """Finalization cleanup works as expected."""
        mock_client.get_document.return_value = {
            'body': {
                'content': [{'paragraph': {'elements': [{'textRun': {'content': 'Texto {{*INTRO*}}'}}]}}]
            }
        }
        mock_client.find_text.return_value = [(6, 15)]
        
        doc_manager.finalize_document("doc123")
        mock_client.delete_range.assert_called()
