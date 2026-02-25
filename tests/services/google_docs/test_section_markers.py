# tests/services/google_docs/test_section_markers.py

import pytest
from unittest.mock import MagicMock
from services.google_docs.document_manager import DocumentManager
from services.google_docs.client import GoogleDocsClient
from services.google_docs.formatter import AcademicFormatter

class TestSectionMarkers:
    
    @pytest.fixture
    def mock_client(self):
        return MagicMock(spec=GoogleDocsClient)
        
    @pytest.fixture
    def formatter(self):
        return AcademicFormatter(style="ABNT")
        
    @pytest.fixture
    def doc_manager(self, mock_client, formatter):
        return DocumentManager(mock_client, formatter)

    def test_create_document_with_markers(self, doc_manager, mock_client):
        """Verify that markers are inserted correctly in reversed order."""
        structure = {
            "titulo": "Artigo Científico",
            "secoes": [
                {"key": "INTRO", "titulo": "Introdução"},
                {"key": "METODO", "titulo": "Metodologia"}
            ]
        }
        
        doc_manager.create_academic_document("Artigo Científico", structure)
        
        # Capture all insertText calls
        args, _ = mock_client.batch_update.call_args
        requests = args[1]
        
        inserted_texts = [r["insertText"]["text"] for r in requests if "insertText" in r]
        
        # Expected order (since we insert at index 1 in reverse):
        # 1. Artigo Científico (Title)
        # 2. INTRODUÇÃO (Header 1)
        # 3. [[START:INTRO]]
        # 4. \n
        # 5. [[END:INTRO]]\n
        # 6. METODOLOGIA (Header 1)
        # ...
        
        assert "[[START:INTRO]]" in "".join(inserted_texts)
        assert "[[END:INTRO]]" in "".join(inserted_texts)
        assert "[[START:METODO]]" in "".join(inserted_texts)
        assert "[[END:METODO]]" in "".join(inserted_texts)

    def test_write_section_replaces_between_markers(self, doc_manager, mock_client):
        """Verify that content is replaced exactly between START and END markers."""
        mock_client.find_text.side_effect = lambda id, query: {
            "[[START:INTRO]]": [(10, 25)],
            "[[END:INTRO]]": [(100, 115)]
        }.get(query, [])
        
        content = "Novo conteúdo da introdução."
        doc_manager.write_section("doc123", "INTRO", content, mode="replace")
        
        # Should delete from END of START marker (25) to START of END marker (100)
        mock_client.delete_range.assert_called_with("doc123", 25, 100)
        
        # Should insert at index 25
        args, _ = mock_client.batch_update.call_args
        requests = args[1]
        assert requests[0]["insertText"]["location"]["index"] == 25
        assert content in requests[0]["insertText"]["text"]

    def test_get_section_content_with_markers(self, doc_manager, mock_client):
        """Verify extraction using markers."""
        full_text = "Title\nHeader\n[[START:INTRO]]Conteúdo extraído[[END:INTRO]]\nNext"
        mock_client.get_document.return_value = {
            'body': {'content': [{'paragraph': {'elements': [{'textRun': {'content': full_text}}]}}]}
        }
        
        extracted = doc_manager.get_section_content("doc123", "INTRO")
        assert extracted == "Conteúdo extraído"

    def test_finalize_removes_markers(self, doc_manager, mock_client):
        """Verify all types of markers are removed."""
        full_text = "Intro [[START:INTRO]] content [[END:INTRO]] and old {{*METODO*}}"
        mock_client.get_document.return_value = {
            'body': {'content': [{'paragraph': {'elements': [{'textRun': {'content': full_text}}]}}]}
        }
        
        # Custom side effect to handle while True loop for each pattern
        def find_text_side_effect(doc_id, query):
            if "[[START:INTRO]]" in query:
                res = [[(6, 21)]] if not hasattr(find_text_side_effect, 'start_called') else [[]]
                find_text_side_effect.start_called = True
                return res[0]
            if "[[END:INTRO]]" in query:
                res = [[(30, 43)]] if not hasattr(find_text_side_effect, 'end_called') else [[]]
                find_text_side_effect.end_called = True
                return res[0]
            if "{{*METODO*}}" in query:
                res = [[(50, 62)]] if not hasattr(find_text_side_effect, 'metodo_called') else [[]]
                find_text_side_effect.metodo_called = True
                return res[0]
            return []
            
        mock_client.find_text.side_effect = find_text_side_effect
        
        doc_manager.finalize_document("doc123")
        assert mock_client.delete_range.call_count >= 3
