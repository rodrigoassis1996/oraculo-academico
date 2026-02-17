# services/google_docs/formatter.py

from typing import List, Dict, Any, Literal

class AcademicFormatter:
    """
    Formatting utilities for academic documents following ABNT/APA standards.
    """
    
    def __init__(self, style: Literal["ABNT", "APA"] = "ABNT"):
        self.style = style
        # ABNT Default Configs
        self.config = {
            "font_family": "Times New Roman",
            "font_size": 12,
            "line_spacing": 1.5,
            "alignment": "JUSTIFIED",
            "margins": {
                "top": 3,
                "bottom": 2,
                "left": 3,
                "right": 2
            }
        } if style == "ABNT" else {
            "font_family": "Arial",
            "font_size": 11,
            "line_spacing": 2.0,
            "alignment": "START",
            "margins": {"top": 2.54, "bottom": 2.54, "left": 2.54, "right": 2.54}
        }

    def get_document_style_requests(self) -> List[Dict[str, Any]]:
        """Returns requests to set up document margins and default styling."""
        # Convert cm to points (1 cm = 28.35 points)
        pt = 28.35
        return [
            {
                "updateDocumentStyle": {
                    "documentStyle": {
                        "marginTop": {"magnitude": self.config["margins"]["top"] * pt, "unit": "PT"},
                        "marginBottom": {"magnitude": self.config["margins"]["bottom"] * pt, "unit": "PT"},
                        "marginLeft": {"magnitude": self.config["margins"]["left"] * pt, "unit": "PT"},
                        "marginRight": {"magnitude": self.config["margins"]["right"] * pt, "unit": "PT"},
                    },
                    "fields": "marginTop,marginBottom,marginLeft,marginRight"
                }
            }
        ]

    def format_heading(self, text: str, level: int, index: int) -> List[Dict[str, Any]]:
        """Returns requests for a formatted heading at a specific index."""
        # Level 0: Main Title (Centered, Bold, 12pt/14pt)
        # Level 1: UPPERCASE, BOLD, 12pt
        # Level 2: Title Case, BOLD, 12pt
        # Level 3: Title Case, Normal, 12pt
        
        font_size = 14 if level == 0 else 12
        is_bold = level <= 2
        alignment = "CENTER" if level == 0 else "START"
        content = text.upper() if level == 1 else text
        
        requests = [
            {
                "insertText": {
                    "location": {"index": index},
                    "text": f"{content}\n"
                }
            },
            {
                "updateTextStyle": {
                    "range": {
                        "startIndex": index,
                        "endIndex": index + len(content)
                    },
                    "textStyle": {
                        "weightedFontFamily": {"fontFamily": self.config["font_family"]},
                        "fontSize": {"magnitude": font_size, "unit": "PT"},
                        "bold": is_bold
                    },
                    "fields": "weightedFontFamily,fontSize,bold"
                }
            },
            {
                "updateParagraphStyle": {
                    "range": {
                        "startIndex": index,
                        "endIndex": index + len(content)
                    },
                    "paragraphStyle": {
                        "alignment": alignment,
                        "namedStyleType": f"HEADING_{max(1, level)}", # Google doesn't have HEADING_0
                        "spaceAbove": {"magnitude": 12 if level > 0 else 24, "unit": "PT"},
                        "spaceBelow": {"magnitude": 12, "unit": "PT"}
                    },
                    "fields": "alignment,namedStyleType,spaceAbove,spaceBelow"
                }
            }
        ]
        return requests
    def format_paragraph(self, text: str, index: int) -> List[Dict[str, Any]]:
        """Returns requests for a formatted paragraph at a specific index."""
        requests = [
            {
                "insertText": {
                    "location": {"index": index},
                    "text": f"{text}\n"
                }
            },
            {
                "updateTextStyle": {
                    "range": {
                        "startIndex": index,
                        "endIndex": index + len(text)
                    },
                    "textStyle": {
                        "weightedFontFamily": {"fontFamily": self.config["font_family"]},
                        "fontSize": {"magnitude": self.config["font_size"], "unit": "PT"}
                    },
                    "fields": "weightedFontFamily,fontSize"
                }
            },
            {
                "updateParagraphStyle": {
                    "range": {
                        "startIndex": index,
                        "endIndex": index + len(text)
                    },
                    "paragraphStyle": {
                        "alignment": self.config["alignment"],
                        "lineSpacing": self.config["line_spacing"] * 100, # Google Docs uses percentage for line spacing
                        "indentFirstLine": {"magnitude": 35.4, "unit": "PT"} # ~1.25cm indent
                    },
                    "fields": "alignment,lineSpacing,indentFirstLine"
                }
            }
        ]
        return requests

    def format_citation(self, citation: Dict[str, Any]) -> str:
        """Formats citation according to style guide."""
        author = citation.get('author', 'Anon')
        year = citation.get('year', 'n.d.')
        if self.style == "ABNT":
            return f"({author.upper()}, {year})"
        return f"({author}, {year})"

    def create_section_placeholder(self, section_key: str) -> str:
        """Returns standardized placeholder string."""
        return f"{{{{#{section_key}#}}}}"
