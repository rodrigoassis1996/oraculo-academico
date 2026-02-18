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
        mode: Literal["replace", "append"] = "replace",
        title_hint: Optional[str] = None
    ) -> None:
        """
        Writes content to a specific section with proper ABNT formatting.
        Converts markdown patterns to native Google Docs formatting.
        """
        import re
        
        placeholder = self.formatter.create_section_placeholder(section_key)
        matches = self.client.find_text(doc_id, placeholder)
        
        candidate_ranges = []
        
        if matches:
            candidate_ranges.append(matches[0])
            
        if title_hint:
            # Check by Title as well to catch duplicates/existing content
            print(f"[DOCS MANAGER] Verificando existência por título: '{title_hint}'")
            ranges = self.client.find_section_ranges_by_title(doc_id, title_hint)
            if ranges:
                print(f"[DOCS MANAGER] Encontrados {len(ranges)} ranges via título.")
                candidate_ranges.extend(ranges)
            else:
                print(f"[DOCS MANAGER] Nenhum range encontrado via título.")
                
        if not candidate_ranges:
            raise APIError(f"Não foi possível localizar a seção. Placeholder {placeholder} não encontrado e título '{title_hint}' não localizado.")

        # Merge Overlapping Ranges to avoid index errors during deletion
        # Sort by start index
        candidate_ranges.sort(key=lambda x: x[0])
        
        merged_ranges = []
        if candidate_ranges:
            curr_start, curr_end = candidate_ranges[0]
            for i in range(1, len(candidate_ranges)):
                next_start, next_end = candidate_ranges[i]
                if next_start <= curr_end:  # Overlap or Adjacent
                    curr_end = max(curr_end, next_end)
                else:
                    merged_ranges.append((curr_start, curr_end))
                    curr_start, curr_end = next_start, next_end
            merged_ranges.append((curr_start, curr_end))
            
        # Insertion point is the start of the first merged range (topmost)
        start = merged_ranges[0][0]
        
        if mode == "replace":
            # Remove all merged ranges in REVERSE order
            for r_start, r_end in reversed(merged_ranges):
                print(f"[DOCS MANAGER] Removendo range unificado: {r_start}-{r_end}")
                self.client.delete_range(doc_id, r_start, r_end)
            
            # Parse content lines and classify each one
            lines = content.split('\n')
            current_idx = start
            all_requests = []
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                
                # Detect markdown heading: ### Title or ## Title
                heading_match = re.match(r'^(#{2,3})\s+(.*)', stripped)
                if heading_match:
                    level_str = heading_match.group(1)
                    heading_text = heading_match.group(2).strip()
                    
                    # ANTI-DUPLICATION: Skip if heading matches the Section Title
                    if title_hint and heading_text.lower() == title_hint.strip().lower():
                        print(f"[DOCS MANAGER] Removendo título duplicado no conteúdo: '{heading_text}'")
                        continue

                    # ## = level 1 (section), ### = level 2 (subsection)
                    level = 1 if len(level_str) == 2 else 2
                    reqs = self.formatter.format_heading(heading_text, level=level, index=current_idx)
                    all_requests.extend(reqs)
                    current_idx += len(heading_text) + 1  # +1 for newline
                    continue
                
                # Strip markdown bold markers **text** → text
                clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
                # Strip markdown italic markers *text* → text
                clean_line = re.sub(r'\*(.*?)\*', r'\1', clean_line)
                # Strip bullet markers - text → text
                clean_line = re.sub(r'^[-•]\s+', '', clean_line)
                
                # ANTI-DUPLICATION: Skip if plain text matches the Section Title
                if title_hint and clean_line.strip().lower() == title_hint.strip().lower():
                    print(f"[DOCS MANAGER] Removendo título duplicado (texto): '{clean_line}'")
                    continue

                reqs = self.formatter.format_paragraph(clean_line, current_idx)
                all_requests.extend(reqs)
                current_idx += len(clean_line) + 1  # +1 for newline
                
            self.client.batch_update(doc_id, all_requests)
        else:
            # Append logic (simplified: add as paragraph at the end of section)
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
        # Busca por {{*KEY*}}
        next_matches = list(re.finditer(r'\{\{\*.*?\*\}\}', full_text[start_idx + len(placeholder):]))
        
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
        # Find all patterns like {{*...*}}
        import re
        placeholders = re.findall(r'\{\{\*.*?\*\}\}', full_text)
        
        for p in placeholders:
            matches = self.client.find_text(doc_id, p)
            if matches:
                start, end = matches[0]
                self.client.delete_range(doc_id, start, end)
