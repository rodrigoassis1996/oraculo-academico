# services/google_docs/auth.py

import os
from typing import List, Optional
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from .exceptions import AuthenticationError

class AuthManager:
    """
    Handles Google API authentication.
    Supports both OAuth 2.0 (interactive) and Service Account (server-side).
    """
    
    DEFAULT_SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.readonly'
    ]

    def __init__(self, credentials_path: str, scopes: Optional[List[str]] = None, token_path: str = "token.json"):
        """
        Args:
            credentials_path: Path to credentials JSON file
            scopes: API scopes
            token_path: Path to store/load the OAuth token
        """
        self.credentials_path = credentials_path
        self.scopes = scopes or self.DEFAULT_SCOPES
        self.token_path = token_path
        self._credentials = None

    def get_credentials(self) -> Credentials:
        """Returns valid credentials, refreshing if necessary."""
        if self._credentials and self._credentials.valid:
            return self._credentials

        if not os.path.exists(self.credentials_path):
            raise AuthenticationError(f"Arquivo de credenciais não encontrado: {self.credentials_path}")

        # Tenta carregar como Service Account primeiro
        try:
            self._credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.scopes
            )
            return self._credentials
        except Exception:
            # Se falhar, assume que é OAuth 2.0
            return self._authenticate_oauth()

    def _authenticate_oauth(self) -> Credentials:
        """Handles OAuth 2.0 flow."""
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    raise AuthenticationError(f"Falha ao atualizar token OAuth: {str(e)}")
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    raise AuthenticationError(f"Falha no fluxo OAuth 2.0: {str(e)}")

            # Salva o token para a próxima vez
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self._credentials = creds
        return self._credentials

    def revoke(self) -> None:
        """Revokes current credentials (deletes token file)."""
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self._credentials = None
