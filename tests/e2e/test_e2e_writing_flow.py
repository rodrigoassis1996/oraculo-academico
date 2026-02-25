"""
Teste End-to-End REAL do fluxo completo de escrita de documentos.
Usa ChatOpenAI real, Google Docs API real, e PDFs reais do projeto.
Requer: OPENAI_API_KEY no .env, credentials.json e token.json válidos.

Para executar:
    .\.venv\Scripts\python.exe -m pytest tests/e2e/ -v -m e2e --tb=long
"""

import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).parent.parent.parent

# PDFs reais para teste
PDF_FILES = [
    ROOT_DIR / "arquivos" / "Estimating the Carbon Footprint of BLOOM, a 176B Parameter Language Model.pdf",
    ROOT_DIR / "arquivos" / "Generative AI And Sustainability.pdf",
]


@pytest.fixture(scope="module")
def client():
    """Cria TestClient do FastAPI para os testes."""
    from main_api import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def session_id(client):
    """Cria uma sessão e retorna o ID."""
    response = client.post("/api/v1/session")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    return data["session_id"]


def _upload_pdf(client, session_id: str, pdf_path: Path):
    """Helper para upload de um PDF."""
    assert pdf_path.exists(), f"PDF não encontrado: {pdf_path}"
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/v1/upload",
            data={"session_id": session_id},
            files={"file": (pdf_path.name, f, "application/pdf")},
        )
    assert response.status_code == 200, f"Upload falhou: {response.text}"
    return response.json()


def _send_chat(client, session_id: str, message: str) -> str:
    """Helper para enviar mensagem no chat e retornar a resposta completa."""
    response = client.post(
        "/api/v1/chat",
        json={"session_id": session_id, "message": message},
    )
    assert response.status_code == 200, f"Chat falhou: {response.text}"
    # TestClient retorna o streaming response como texto completo
    return response.text


def _get_session_state(client, session_id: str) -> dict:
    """Helper para obter o estado interno da sessão."""
    from main_api import sessions
    return sessions.get(session_id, {})


@pytest.mark.e2e
class TestWritingFlowE2E:
    """
    Teste E2E completo: upload → pedir artigo → aprovar estrutura → 
    gerar seções → aprovar cada seção → documento completo.
    """

    def test_full_writing_flow(self, client, session_id):
        """Fluxo completo de criação de documento acadêmico."""
        
        # ═══════════════════════════════════════════════════
        # PASSO 1: Upload dos PDFs reais
        # ═══════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("PASSO 1: Upload dos PDFs")
        print("=" * 60)
        
        for pdf_path in PDF_FILES:
            result = _upload_pdf(client, session_id, pdf_path)
            print(f"  OK Upload: {pdf_path.name} | total_docs: {result.get('total_docs')}")
            assert result["success"] is True
        
        # ═══════════════════════════════════════════════════
        # PASSO 2: Solicitar escrita de artigo
        # ═══════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("PASSO 2: Solicitando escrita de artigo")
        print("=" * 60)
        
        resposta = _send_chat(
            client, session_id,
            "Gostaria de escrever um artigo acadêmico sobre o impacto ambiental de modelos de linguagem de grande porte."
        )
        print(f"  Resposta ({len(resposta)} chars): {resposta[:200]}...")
        
        # Verifica que o estado transitou para AGUARDANDO_APROVACAO
        state = _get_session_state(client, session_id)
        assert state.get('agente_ativo') == 'AGUARDANDO_APROVACAO', \
            f"Estado esperado: AGUARDANDO_APROVACAO, obtido: {state.get('agente_ativo')}"
        
        # Verifica que uma estrutura foi detectada
        estrutura = state.get('current_structure')
        assert estrutura is not None, "Estrutura deveria ter sido detectada"
        secoes = estrutura.get('secoes', [])
        assert len(secoes) >= 2, f"Estrutura deveria ter pelo menos 2 seções, tem {len(secoes)}"
        print(f"  OK Estrutura detectada com {len(secoes)} seções:")
        for s in secoes:
            print(f"     - {s['key']}: {s['titulo']}")
        
        # ═══════════════════════════════════════════════════
        # PASSO 3: Aprovar a estrutura
        # ═══════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("PASSO 3: Aprovando estrutura")
        print("=" * 60)
        
        resposta = _send_chat(client, session_id, "Aprovo a estrutura!")
        print(f"  Resposta ({len(resposta)} chars): {resposta[:300]}...")
        
        state = _get_session_state(client, session_id)
        
        # Google Doc deve ter sido criado
        doc_id = state.get('active_doc_id')
        assert doc_id is not None, "Google Doc deveria ter sido criado"
        print(f"  OK Google Doc criado: {doc_id}")
        
        # Verificar que o doc foi criado com título correto
        # (o título é definido em create_google_doc_from_structure)
        
        # Verificar que a primeira seção já foi gerada no chat
        assert state.get('agente_ativo') == 'AGUARDANDO_APROVACAO_CONTEUDO', \
            f"Estado esperado: AGUARDANDO_APROVACAO_CONTEUDO, obtido: {state.get('agente_ativo')}"
        
        pending = state.get('pending_section')
        assert pending is not None, "Deveria haver uma seção pendente para aprovação"
        print(f"  OK Primeira seção gerada: {pending['titulo']}")
        
        # ═══════════════════════════════════════════════════
        # PASSO 4: Loop de aprovação de todas as seções
        # ═══════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("PASSO 4: Aprovando seções uma a uma")
        print("=" * 60)
        
        max_iterations = 20  # Safety limit
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            state = _get_session_state(client, session_id)
            
            if state.get('agente_ativo') != 'AGUARDANDO_APROVACAO_CONTEUDO':
                print(f"  Estado atual: {state.get('agente_ativo')} — saindo do loop.")
                break
            
            pending = state.get('pending_section')
            if not pending:
                print("  Nenhuma seção pendente — saindo do loop.")
                break
            
            completed = len(state.get('completed_sections', []))
            remaining = len(state.get('sections_queue', []))
            total = completed + remaining + 1  # +1 para a pendente
            
            print(f"\n  [{completed + 1}/{total}] Aprovando: {pending['titulo']}")
            print(f"    Conteúdo ({len(pending.get('content', ''))} chars): {pending.get('content', '')[:100]}...")
            
            resposta = _send_chat(client, session_id, "Aprovo esta seção, prossiga para a próxima.")
            print(f"    Resposta ({len(resposta)} chars): {resposta[:150]}...")
        
        # ═══════════════════════════════════════════════════
        # PASSO 5: Verificações finais
        # ═══════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("PASSO 5: Verificações finais")
        print("=" * 60)
        
        state = _get_session_state(client, session_id)
        completed_sections = state.get('completed_sections', [])
        remaining_queue = state.get('sections_queue', [])
        
        print(f"  Seções completadas: {len(completed_sections)}")
        print(f"  Seções restantes na fila: {len(remaining_queue)}")
        print(f"  Estado final: {state.get('agente_ativo')}")
        
        # Todas as seções devem ter sido completadas
        assert len(remaining_queue) == 0, \
            f"Deveria ter 0 seções restantes, mas tem {len(remaining_queue)}"
        assert len(completed_sections) == len(secoes), \
            f"Deveria ter {len(secoes)} seções completadas, tem {len(completed_sections)}"
        
        # O doc_id deve continuar ativo
        assert state.get('active_doc_id') == doc_id
        
        print(f"\n  FINISH TESTE E2E COMPLETO!")
        print(f"  📄 Documento: https://docs.google.com/document/d/{doc_id}/edit")
        print(f"  ⚠️  Lembre-se de apagar o documento de teste!")
