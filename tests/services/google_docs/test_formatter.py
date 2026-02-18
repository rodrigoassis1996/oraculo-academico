# tests/services/google_docs/test_formatter.py

import pytest
from services.google_docs.formatter import AcademicFormatter

class TestAcademicFormatter:
    
    @pytest.fixture
    def abnt_formatter(self):
        return AcademicFormatter(style="ABNT")

    def test_abnt_config_values(self, abnt_formatter):
        """Verifies ABNT configuration defaults."""
        assert abnt_formatter.config["font_family"] == "Times New Roman"
        assert abnt_formatter.config["margins"]["top"] == 3
        assert abnt_formatter.config["line_spacing"] == 1.5

    def test_get_document_style_requests(self, abnt_formatter):
        """Verifies margin request generation."""
        requests = abnt_formatter.get_document_style_requests()
        assert len(requests) == 1
        assert "updateDocumentStyle" in requests[0]
        # 3cm * 28.35 = 85.05
        assert requests[0]["updateDocumentStyle"]["documentStyle"]["marginTop"]["magnitude"] == pytest.approx(85.05)

    def test_format_heading_requests(self, abnt_formatter):
        """Verifies heading request structure and uppercase level 1."""
        requests = abnt_formatter.format_heading("Introdução", level=1, index=10)
        assert len(requests) == 3
        assert requests[0]["insertText"]["text"] == "INTRODUÇÃO\n"
        assert requests[1]["updateTextStyle"]["textStyle"]["bold"] is True
        assert requests[2]["updateParagraphStyle"]["paragraphStyle"]["namedStyleType"] == "HEADING_1"

    def test_format_paragraph_requests(self, abnt_formatter):
        """Verifies paragraph request structure and indentation."""
        requests = abnt_formatter.format_paragraph("Um parágrafo de teste.", index=50)
        assert len(requests) == 3
        assert requests[0]["insertText"]["text"] == "Um parágrafo de teste.\n"
        assert requests[2]["updateParagraphStyle"]["paragraphStyle"]["alignment"] == "JUSTIFIED"
        assert requests[2]["updateParagraphStyle"]["paragraphStyle"]["indentFirstLine"]["magnitude"] == 35.4

    def test_abnt_citation_uppercase(self, abnt_formatter):
        """Verifies ABNT citations use uppercase for authors."""
        citation = {"author": "Silva", "year": "2023"}
        formatted = abnt_formatter.format_citation(citation)
        assert formatted == "(SILVA, 2023)"

    def test_create_section_placeholder(self, abnt_formatter):
        """Verifica se o placeholder é criado no novo formato {{*KEY*}}."""
        placeholder = abnt_formatter.create_section_placeholder("INTRODUCAO")
        assert placeholder == "{{*INTRODUCAO*}}"
