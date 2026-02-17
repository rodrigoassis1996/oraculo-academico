# services/google_docs/document_manager.py

from typing import Dict, Any, Optional, Literal, List
from .client import GoogleDocsClient
from .formatter import AcademicFormatter
from .exceptions import APIError

class DocumentManager:
    """
    High-level document operations for academic writing workflow.
    Integrates with OrchestratorAgent output format.
    """
    
    def __init__(self, client: GoogleDocsClient, formatter: AcademicFormatter):
        self.client = client
        self.formatter = formatter

    def create_academic_document(
        self, 
        title: str, 
        structure: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Creates new document with predefined academic structure and styles.
        Uses reverse-order insertion at index 1 to keep indices stable.
        """
        doc_id = self.client.create_document(title)
        
        # 1. Apply Document Styles (Margins)
        all_requests = self.formatter.get_document_style_requests()
        
        # 2. Prepare content in REVERSE order (bottom to top)
        # So we insert at index 1 and everything shifts down correctly.
        
        sections = structure.get('secoes', [])
        for section in reversed(sections):
            section_title = section.get('titulo', section['key'])
            placeholder = self.formatter.create_section_placeholder(section['key'])
            
            # Insert Placeholder first (becomes bottom)
            p_reqs = self.formatter.format_paragraph(f"{placeholder}\n", 1)
            all_requests.extend(p_reqs)
            
            # Insert Header at index 1 (pushes placeholder down)
            header_reqs = self.formatter.format_heading(section_title, level=1, index=1)
            all_requests.extend(header_reqs)

        # 3. Add Title last (at index 1, pushes everything else down)
        title_reqs = self.formatter.format_heading(title, level=0, index=1)
        all_requests.extend(title_reqs)
            
        self.client.batch_update(doc_id, all_requests)
        return doc_id
    def write_section(
        self,
        doc_id: str,
        section_key: str,
        content: str,
        mode: Literal["replace", "append"] = "replace"
    ) -> None:
        """
        Writes content to a specific section with proper ABNT formatting.
        """
        placeholder = self.formatter.create_section_placeholder(section_key)
        matches = self.client.find_text(doc_id, placeholder)
        
        if not matches:
            raise APIError(f"Marcador {placeholder} não encontrado no documento.")
            
        start, end = matches[0]
        
        if mode == "replace":
            # Remove placeholder
            self.client.delete_range(doc_id, start, end)
            
            # Insert styled content
            # We treat content as a series of paragraphs for now
            paragraphs = content.split('\n')
            current_idx = start
            all_requests = []
            
            for p in paragraphs:
                if not p.strip():
                    continue
                # For Phase 2, we assume the first line of a section might be a heading or just text
                # In refined logic, we'd distinguish headings. 
                # For now, let's just format all as paragraphs.
                reqs = self.formatter.format_paragraph(p, current_idx)
                all_requests.extend(reqs)
                current_idx += len(p) + 1 # +1 for newline
                
            self.client.batch_update(doc_id, all_requests)
        else:
            # Append logic (simplified: just add as paragraph at the end of section)
            # Finding the "end of section" is tricky without markers for section ends.
            # For now, append just after where the placeholder was.
            reqs = self.formatter.format_paragraph(content, end)
            self.client.batch_update(doc_id, reqs)

    def get_section_content(self, doc_id: str, section_key: str) -> str:
        """Retrieves current content of a section for context."""
        # Improved extraction: find text between this placeholder and the next (or end of doc)
        full_doc = self.client.get_document(doc_id)
        full_text = self.get_full_content(doc_id)
        
        placeholder = self.formatter.create_section_placeholder(section_key)
        start_idx = full_text.find(placeholder)
        if start_idx == -1:
            return ""
            
        # Find next placeholder
        import re
        next_matches = list(re.finditer(r'\{\{#.*?\#\}\}', full_text[start_idx + len(placeholder):]))
        
        if next_matches:
            end_idx = start_idx + len(placeholder) + next_matches[0].start()
        else:
            end_idx = len(full_text)
            
        return full_text[start_idx + len(placeholder):end_idx].strip()

    def get_full_content(self, doc_id: str) -> str:
        """Returns entire document as plain text."""
        doc = self.client.get_document(doc_id)
        full_text = ""
        for element in doc.get('body').get('content'):
            if 'paragraph' in element:
                for part in element['paragraph']['elements']:
                    if 'textRun' in part:
                        full_text += part['textRun']['content']
        return full_text

    def finalize_document(self, doc_id: str) -> None:
        """
        Removes all remaining placeholders.
        """
        full_text = self.get_full_content(doc_id)
        # Find all patterns like {{#...#}}
        import re
        placeholders = re.findall(r'\{\{#.*?\#\}\}', full_text)
        
        for p in placeholders:
            matches = self.client.find_text(doc_id, p)
            if matches:
                start, end = matches[0]
                self.client.delete_range(doc_id, start, end)
