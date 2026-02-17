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
        Returns list of (start, end) indices for all matches.
        Note: This requires reading the full document content first as the API 
        doesn't provide a direct 'find' endpoint.
        """
        doc = self.get_document(doc_id)
        full_text = ""
        # Extract plain text from document content
        results = []
        
        # Simple text extraction for search (recursive would be better for complex docs)
        def extract_text(elements):
            text = ""
            for element in elements:
                if 'paragraph' in element:
                    for part in element['paragraph']['elements']:
                        if 'textRun' in part:
                            text += part['textRun']['content']
                elif 'table' in element:
                    for row in element['table']['tableRows']:
                        for cell in row['tableCells']:
                            text += extract_text(cell['content'])
            return text

        full_text = extract_text(doc.get('body').get('content'))
        
        start_idx = 0
        while True:
            idx = full_text.find(query, start_idx)
            if idx == -1:
                break
            results.append((idx + 1, idx + len(query) + 1)) # Docs API index is 1-based (mostly)
            # Actually, Docs API indices can be tricky. Heading/TOC etc affect them.
            # For simplicity in Phase 1, we assume a relatively flat structure.
            start_idx = idx + len(query)
            
        return results
