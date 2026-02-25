import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import json
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError
from services.google_docs.auth import AuthManager
from services.google_docs.client import GoogleDocsClient
from services.google_docs.exceptions import TokenRevokedError, AuthenticationError
from agents.orchestrator import OrchestratorAgent

@pytest.fixture
def mock_creds():
    creds = MagicMock()
    creds.valid = False
    creds.expired = True
    creds.refresh_token = "fake_refresh_token"
    creds.to_json.return_value = '{"token": "new_token"}'
    return creds

@pytest.fixture
def auth_manager(tmp_path):
    creds_file = tmp_path / "credentials.json"
    creds_file.write_text('{"type": "authorized_user", "client_id": "id", "client_secret": "secret"}')
    token_file = tmp_path / "token.json"
    token_file.write_text('{"token": "old_token", "refresh_token": "fake_refresh"}')
    
    return AuthManager(str(creds_file), token_path=str(token_file))

class TestOAuthResilience:

    def test_auth_refresh_success(self, auth_manager, mock_creds):
        """Verifica se o AuthManager faz o refresh com sucesso e salva o novo token."""
        with patch("google.oauth2.credentials.Credentials.from_authorized_user_file", return_value=mock_creds):
            with patch("google.auth.transport.requests.Request", return_value=MagicMock()):
                creds = auth_manager.get_credentials()
                
                mock_creds.refresh.assert_called_once()
                assert creds == mock_creds
                assert os.path.exists(auth_manager.token_path)
                with open(auth_manager.token_path, "r") as f:
                    assert "new_token" in f.read()

    def test_auth_invalid_grant(self, auth_manager, mock_creds):
        """Verifica se lança TokenRevokedError em caso de invalid_grant."""
        mock_creds.refresh.side_effect = RefreshError("invalid_grant: Token has been expired or revoked")
        
        with patch("google.oauth2.credentials.Credentials.from_authorized_user_file", return_value=mock_creds):
            with patch("google.auth.transport.requests.Request", return_value=MagicMock()):
                # O token_path deve existir antes
                assert os.path.exists(auth_manager.token_path)
                
                with pytest.raises(TokenRevokedError):
                    auth_manager.get_credentials()
                
                # Deve ter removido o arquivo de token inválido
                assert not os.path.exists(auth_manager.token_path)

    def test_client_retry_401(self, auth_manager):
        """Verifica se o GoogleDocsClient tenta refresh em erro 401."""
        client = GoogleDocsClient(auth_manager)
        
        # Mock de erro 401
        response = MagicMock()
        response.status = 401
        err = HttpError(resp=response, content=b"Unauthorized")
        
        request = MagicMock()
        # Na primeira chamada falha com 401, na segunda (após retry) falha de novo 
        # (pois o _execute_with_retry do discovery não reconstrói a request automaticamente no mock)
        request.execute.side_effect = err
        
        with patch.object(auth_manager, "get_credentials") as mock_get_creds:
            with pytest.raises(HttpError) as excinfo:
                client._execute_with_retry(request)
            
            assert excinfo.value.resp.status == 401
            # Verificamos que o refresh foi tentado
            assert auth_manager._credentials is None
            mock_get_creds.assert_called()

    def test_orchestrator_handles_revocation(self):
        """Verifica se o Orquestrador gera a mensagem de reautorização ao pegar TokenRevokedError."""
        mm = MagicMock()
        mock_llm = MagicMock()
        mm.session_state = {
            'agente_ativo': 'AGUARDANDO_APROVACAO',
            'current_structure': {'titulo': 'Teste', 'secoes': []},
            'mensagens': [],
            'llm': mock_llm
        }
        mm.auth_manager.get_authorization_url.return_value = "http://auth-url"
        
        # O route_request usa self.llm (que vem do model_manager)
        # Precisamos garantir que mm.session_state.get('llm') retorne algo
        
        orchestrator = OrchestratorAgent(mm, docs_manager=MagicMock())
        
        # Simula erro de token revogado no docs_manager
        orchestrator.docs_manager.create_academic_document.side_effect = TokenRevokedError("Expulso")
        
        # Simula que o classificador detectou aprovação de estrutura
        with patch.object(orchestrator, "classificar_e_atualizar_estado", return_value="AUTH_REVOKED"):
            generator = orchestrator.route_request("sim")
            response = list(generator)
            
            # A resposta deve conter o link de autorização
            full_msg = "".join(response)
            assert "Google Docs expirou ou foi revogada" in full_msg
            assert "http://auth-url" in full_msg
