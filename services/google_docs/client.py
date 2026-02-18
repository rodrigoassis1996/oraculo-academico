# services/google_docs/client.py

import time
import random
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .auth import AuthManager
from .exceptions import APIError, DocumentNotFoundError

class GoogleDocsClient:
    """
    Low-level wrapper for Google Docs API with built-in rate limiting/retry.
    """
    
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self._docs_service = None
        self._drive_service = None
        self.max_retries = 5
        self.base_delay = 1.0 # seconds

    @property
    def docs_service(self):
        if not self._docs_service:
            creds = self.auth_manager.get_credentials()
            self._docs_service = build('docs', 'v1', credentials=creds)
        return self._docs_service

    @property
    def drive_service(self):
        if not self._drive_service:
            creds = self.auth_manager.get_credentials()
            self._drive_service = build('drive', 'v3', credentials=creds)
        return self._drive_service

    def _execute_with_retry(self, request):
        """Executes a request with exponential backoff for rate limits and transient errors."""
        for attempt in range(self.max_retries):
            try:
                return request.execute()
            except HttpError as e:
                if e.resp.status in [429, 503]:
                    if attempt == self.max_retries - 1:
                        raise e
                    delay = (self.base_delay * (2 ** attempt)) + (random.uniform(0, 1))
                    print(f"[GOOGLE API] Rate limit/Busy (Attempt {attempt+1}). Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    raise e
            except Exception as e:
                raise e

    def create_document(self, title: str) -> str:
        """Creates empty document, returns document_id."""
        try:
            body = {'title': title}
            req = self.docs_service.documents().create(body=body)
            doc = self._execute_with_retry(req)
            return doc.get('documentId')
        except Exception as e:
            raise APIError(f"Falha ao criar documento: {str(e)}")

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Retrieves full document structure and content."""
        try:
            req = self.docs_service.documents().get(documentId=doc_id)
            return self._execute_with_retry(req)
        except Exception as e:
            if "not found" in str(e).lower():
                raise DocumentNotFoundError(f"Documento {doc_id} não encontrado.")
            raise APIError(f"Falha ao obter documento: {str(e)}")

    def batch_update(self, doc_id: str, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Executes batch of update requests atomically."""
        if not requests:
            return {}
        try:
            body = {'requests': requests}
            req = self.docs_service.documents().batchUpdate(
                documentId=doc_id, body=body
            )
            return self._execute_with_retry(req)
        except Exception as e:
            raise APIError(f"Falha na operação em lote: {str(e)}")

    def insert_text(self, doc_id: str, text: str, index: int) -> None:
        """Inserts text at specified index."""
        requests = [
            {
                'insertText': {
                    'location': {'index': index},
                    'text': text
                }
            }
        ]
        self.batch_update(doc_id, requests)

    def delete_range(self, doc_id: str, start: int, end: int) -> None:
        """Deletes content between indices."""
        if start >= end:
            return
        requests = [
            {
                'deleteContentRange': {
                    'range': {
                        'startIndex': start,
                        'endIndex': end
                    }
                }
            }
        ]
        self.batch_update(doc_id, requests)

    def find_text(self, doc_id: str, query: str) -> List[tuple[int, int]]:
        """
        Returns list of (start, end) indices for all matches with CORRECT Google Docs indexes.
        """
        doc = self.get_document(doc_id)
        results = []
        import re

        def search_in_elements(elements):
            for element in elements:
                if 'paragraph' in element:
                    para_text = ""
                    para_start = element['startIndex']
                    for part in element['paragraph']['elements']:
                        if 'textRun' in part:
                            para_text += part['textRun']['content']
                    
                    # Search within this paragraph
                    for m in re.finditer(re.escape(query), para_text):
                        results.append((para_start + m.start(), para_start + m.end()))
                
                elif 'table' in element:
                    for row in element['table']['tableRows']:
                        for cell in row['tableCells']:
                            search_in_elements(cell['content'])
        
        search_in_elements(doc.get('body').get('content'))
        return results

    def find_section_ranges_by_title(self, doc_id: str, title: str) -> List[tuple[int, int]]:
        """
        Finds ALL content ranges (start, end) for a section by its Heading 1 title.
        Returns list of (start, end) tuples. Helpful for cleaning up duplicates.
        """
        import unicodedata
        
        def normalize_text(t: str) -> str:
            return ''.join(c for c in unicodedata.normalize('NFD', t) 
                          if unicodedata.category(c) != 'Mn').lower()

        doc = self.get_document(doc_id)
        content = doc.get('body', {}).get('content', [])
        
        target_title = normalize_text(title.strip())
        ranges = []
        
        i = 0
        while i < len(content):
            element = content[i]
            if 'paragraph' in element:
                p = element['paragraph']
                style = p.get('paragraphStyle', {}).get('namedStyleType', '')
                
                # Check if it's a Heading 1
                if style == 'HEADING_1':
                    text = ""
                    for part in p.get('elements', []):
                        if 'textRun' in part:
                            text += part['textRun']['content']
                    
                    # Normalize doc text: remove accents, hashes, whitespace
                    clean_text = text.replace('#', '').strip()
                    clean_text_norm = normalize_text(clean_text)
                    
                    # Check match
                    if clean_text_norm == target_title or target_title in clean_text_norm:
                        start_index = element['endIndex']
                        end_index = -1
                        
                        # Find the END (Next Heading 1 or End of Doc)
                        j = i + 1
                        while j < len(content):
                             next_el = content[j]
                             if 'paragraph' in next_el:
                                 next_style = next_el['paragraph'].get('paragraphStyle', {}).get('namedStyleType', '')
                                 if next_style == 'HEADING_1':
                                     # Found next section
                                     end_index = max(start_index, next_el['startIndex'] - 1)
                                     break
                             j += 1
                        
                        if end_index == -1:
                            # Last section
                            last_idx = content[-1]['endIndex']
                            end_index = last_idx - 1
                        
                        ranges.append((start_index, end_index))
            i += 1
                        
        return ranges
