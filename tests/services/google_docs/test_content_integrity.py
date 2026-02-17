# tests/services/google_docs/test_content_integrity.py

import pytest
from unittest.mock import MagicMock
from services.google_docs.formatter import AcademicFormatter

class TestContentIntegrity:
    
    @pytest.fixture
    def formatter(self):
        return AcademicFormatter(style="ABNT")

    def test_heading_level_1_is_uppercase(self, formatter):
        """ABNT Level 1 headings must be UPPERCASE."""
        text = "introdução ao tema"
        requests = formatter.format_heading(text, level=1, index=1)
        
        # Find the insertText request
        insert_req = next(r for r in requests if "insertText" in r)
        assert insert_req["insertText"]["text"] == "INTRODUÇÃO AO TEMA\n"

    def test_font_family_is_times_new_roman(self, formatter):
        """All text styles must use Times New Roman for ABNT."""
        text = "Texto de teste"
        
        # Check Heading font
        heading_reqs = formatter.format_heading(text, level=1, index=1)
        style_req = next(r for r in heading_reqs if "updateTextStyle" in r)
        assert style_req["updateTextStyle"]["textStyle"]["weightedFontFamily"]["fontFamily"] == "Times New Roman"
        
        # Check Paragraph font
        para_reqs = formatter.format_paragraph(text, index=1)
        para_style_req = next(r for r in para_reqs if "updateTextStyle" in r)
        assert para_style_req["updateTextStyle"]["textStyle"]["weightedFontFamily"]["fontFamily"] == "Times New Roman"

    def test_font_size_standard_rules(self, formatter):
        """Header 0 (Title) is 14pt, others are 12pt."""
        # Main Title
        title_reqs = formatter.format_heading("Título", level=0, index=1)
        title_style = next(r for r in title_reqs if "updateTextStyle" in r)
        assert title_style["updateTextStyle"]["textStyle"]["fontSize"]["magnitude"] == 14
        
        # Regular Heading
        h1_reqs = formatter.format_heading("Seção", level=1, index=1)
        h1_style = next(r for r in h1_reqs if "updateTextStyle" in r)
        assert h1_style["updateTextStyle"]["textStyle"]["fontSize"]["magnitude"] == 12
        
        # Paragraph
        p_reqs = formatter.format_paragraph("Parágrafo", index=1)
        p_style = next(r for r in p_reqs if "updateTextStyle" in r)
        assert p_style["updateTextStyle"]["textStyle"]["fontSize"]["magnitude"] == 12

    def test_abnt_margins_calculation(self, formatter):
        """ABNT margins must be 3cm (top/left) and 2cm (bottom/right)."""
        requests = formatter.get_document_style_requests()
        doc_style = next(r for r in requests if "updateDocumentStyle" in r)
        margins = doc_style["updateDocumentStyle"]["documentStyle"]
        
        # 1 cm = 28.35 PT
        pt = 28.35
        assert margins["marginTop"]["magnitude"] == pytest.approx(3 * pt)
        assert margins["marginLeft"]["magnitude"] == pytest.approx(3 * pt)
        assert margins["marginBottom"]["magnitude"] == pytest.approx(2 * pt)
        assert margins["marginRight"]["magnitude"] == pytest.approx(2 * pt)

    def test_heading_alignment_rules(self, formatter):
        """Level 0 is CENTER, others are START (API equivalent for LEFT)."""
        # Title
        title_reqs = formatter.format_heading("Título", level=0, index=1)
        title_p_style = next(r for r in title_reqs if "updateParagraphStyle" in r)
        assert title_p_style["updateParagraphStyle"]["paragraphStyle"]["alignment"] == "CENTER"
        
        # Heading 1
        h1_reqs = formatter.format_heading("Seção", level=1, index=1)
        h1_p_style = next(r for r in h1_reqs if "updateParagraphStyle" in r)
        assert h1_p_style["updateParagraphStyle"]["paragraphStyle"]["alignment"] == "START"
