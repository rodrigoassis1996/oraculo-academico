# services/google_docs/auth.py

import os
import json
import logging
from typing import List, Optional
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from .exceptions import AuthenticationError, TokenRevokedError

# Configuração de logging especializada para o módulo Docs
logger = logging.getLogger("google_docs.auth")

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
            logger.error(f"Arquivo de credenciais não encontrado: {self.credentials_path}")
            raise AuthenticationError(f"Arquivo de credenciais não encontrado: {self.credentials_path}")

        # Tenta carregar como Service Account primeiro
        try:
            # Verifica se o arquivo parece ser de Service Account (contém project_id)
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)
                if creds_data.get('type') == 'service_account':
                    self._credentials = service_account.Credentials.from_service_account_file(
                        self.credentials_path, scopes=self.scopes
                    )
                    logger.info("Autenticado via Service Account.")
                    return self._credentials
        except Exception as e:
            logger.debug(f"Falha ao tentar carregar como Service Account: {e}")

        # Se falhar ou não for service account, assume que é OAuth 2.0
        return self._authenticate_oauth()

    def _authenticate_oauth(self) -> Credentials:
        """Handles OAuth 2.0 credentials loading and refreshing."""
        creds = None
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
                logger.debug("Token carregado do arquivo.")
            except Exception as e:
                logger.warning(f"Erro ao carregar token.json: {e}")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Token expirado. Tentando refresh...")
                    creds.refresh(Request())
                    logger.info("Token renovado com sucesso.")
                    # Salva o token renovado
                    with open(self.token_path, 'w') as token:
                        token.write(creds.to_json())
                except RefreshError as e:
                    logger.error(f"Erro ao atualizar token OAuth: {e}")
                    if "invalid_grant" in str(e).lower():
                        logger.warning("Token revogado ou inválido (invalid_grant). Limpando token.json.")
                        self.revoke()
                        raise TokenRevokedError("O acesso ao Google Docs foi revogado ou expirou. É necessário reautorizar.")
                    raise AuthenticationError(f"Falha ao atualizar token OAuth: {str(e)}")
                except Exception as e:
                    logger.error(f"Erro inesperado no refresh: {e}")
                    raise AuthenticationError(f"Erro inesperado ao renovar token: {str(e)}")
            else:
                logger.warning("Nenhum token válido ou refresh token disponível.")
                raise TokenRevokedError("Autorização necessária para o Google Docs.")

        self._credentials = creds
        return self._credentials

    def get_authorization_url(self, redirect_uri: Optional[str] = None, state: Optional[str] = None) -> str:
        """Returns the authorization URL for the user to visit."""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path, self.scopes
        )
        if redirect_uri:
            flow.redirect_uri = redirect_uri
        
        auth_url, _ = flow.authorization_url(
            prompt='consent', 
            access_type='offline',
            state=state,
            include_granted_scopes='true'
        )
        return auth_url

    def save_credentials_from_code(self, code: str, redirect_uri: Optional[str] = None) -> Credentials:
        """Exchanges code for credentials and saves them."""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, self.scopes
            )
            if redirect_uri:
                flow.redirect_uri = redirect_uri
            
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            
            self._credentials = creds
            logger.info("Novas credenciais salvas com sucesso após fluxo de código.")
            return creds
        except Exception as e:
            logger.error(f"Erro ao processar código de autorização: {e}")
            raise AuthenticationError(f"Falha ao processar autorização: {str(e)}")

    def revoke(self) -> None:
        """Revokes current credentials (deletes token file)."""
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self._credentials = None
