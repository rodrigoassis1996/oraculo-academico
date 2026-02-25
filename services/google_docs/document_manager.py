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
            start_marker, end_marker = self.formatter.create_section_markers(section['key'])
            
            # Insere marcadores e espaços em ordem inversa (da base para o topo)
            # Resultado final desejado: HEADING \n [[START]] \n \n [[END]]
            
            # 1. Marcador de Fim (fica embaixo)
            p_end = self.formatter.format_paragraph(f"{end_marker}\n", 1)
            all_requests.extend(p_end)
            
            # 2. Espaço vazio para conteúdo (no meio)
            p_empty = self.formatter.format_paragraph("", 1)
            all_requests.extend(p_empty)
            
            # 3. Marcador de Início (fica em cima do conteúdo)
            p_start = self.formatter.format_paragraph(f"{start_marker}", 1)
            all_requests.extend(p_start)
            
            # 4. Título da Seção (no index 1, empurra tudo para baixo)
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
        
        start_marker, end_marker = self.formatter.create_section_markers(section_key)
        start_matches = self.client.find_text(doc_id, start_marker)
        end_matches = self.client.find_text(doc_id, end_marker)
        
        if start_matches and end_matches:
            # Ponto de inserção é após o marcador de início
            # O conteúdo a deletar é entre o fim do START e o início do END
            start_pos = start_matches[0][1] # Fim do [[START:KEY]]
            end_pos = end_matches[0][0]     # Início do [[END:KEY]]
            
            print(f"[DOCS MANAGER] Usando marcadores: {start_pos} até {end_pos}")
            merged_ranges = [(start_pos, end_pos)]
        else:
            # Fallback para o sistema antigo de placeholder ou título (retrocompatibilidade)
            print(f"[DOCS MANAGER] Marcadores não encontrados para {section_key}. Usando fallback.")
            placeholder = self.formatter.create_section_placeholder(section_key)
            matches = self.client.find_text(doc_id, placeholder)
            candidate_ranges = []
            if matches: candidate_ranges.append(matches[0])
            if title_hint:
                ranges = self.client.find_section_ranges_by_title(doc_id, title_hint)
                if ranges: candidate_ranges.extend(ranges)
            
            if not candidate_ranges:
                raise APIError(f"Não foi possível localizar a seção. Marcadores ou placeholder {placeholder} não encontrados.")

            candidate_ranges.sort(key=lambda x: x[0])
            merged_ranges = []
            if candidate_ranges:
                curr_start, curr_end = candidate_ranges[0]
                for i in range(1, len(candidate_ranges)):
                    next_start, next_end = candidate_ranges[i]
                    if next_start <= curr_end: curr_end = max(curr_end, next_end)
                    else:
                        merged_ranges.append((curr_start, curr_end))
                        curr_start, curr_end = next_start, next_end
                merged_ranges.append((curr_start, curr_end))
            start_pos = merged_ranges[0][0]

        # Inserção começa no start_pos definido acima
        start = start_pos
        
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
        
        start_marker, end_marker = self.formatter.create_section_markers(section_key)
        full_text = self.get_full_content(doc_id)
        
        start_idx = full_text.find(start_marker)
        if start_idx == -1:
            return ""
            
        end_idx = full_text.find(end_marker, start_idx)
        if end_idx == -1:
            end_idx = len(full_text)
            
        return full_text[start_idx + len(start_marker):end_idx].strip()

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
        # Find all section markers [[START:...]] and [[END:...]]
        import re
        patterns = [r'\[\[START:.*?\]\]', r'\[\[END:.*?\]\]', r'\{\{\*.*?\*\}\}']
        
        for pattern in patterns:
            # We need to find and delete matches until no more are found, 
            # because deleting shifts the indexes.
            while True:
                full_text = self.get_full_content(doc_id)
                match = re.search(pattern, full_text)
                if not match:
                    break
                
                # Search for the exact coordinate in the doc structure
                # finding by text again to get fresh start/end
                matches = self.client.find_text(doc_id, match.group())
                if matches:
                    start, end = matches[0]
                    self.client.delete_range(doc_id, start, end)
                else:
                    break
