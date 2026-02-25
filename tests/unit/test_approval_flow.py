"""
Testes unitários para o fluxo de aprovação da estrutura e escrita de conteúdo.
Cobre a nova arquitetura: Estruturador → Doc com esqueleto → Orquestrador → escrita com aprovação.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from agents.orchestrator import OrchestratorAgent


def _make_orchestrator(session_state=None, mensagens=None):
    """Helper para criar OrchestratorAgent com mocks."""
    mm = MagicMock()
    mm.session_state = session_state or {
        'agente_ativo': 'ORCHESTRATOR',
        'active_doc_id': None,
        'last_active_section': None,
        'current_structure': None,
        'pending_section': None,
        'sections_queue': [],
        'completed_sections': [],
        'mensagens': [],
    }
    mm.mensagens = mensagens or []
    mm.get_historico_langchain.return_value = []
    
    docs_manager = MagicMock()
    orch = OrchestratorAgent(mm, docs_manager=docs_manager)
    return orch, mm, docs_manager


class TestApprovalReusesSavedStructure:
    """Testa que _handle_approval_flow prioriza a estrutura salva em session_state."""

    def test_approval_reuses_saved_structure(self):
        """Deve usar current_structure do session_state ao invés de re-extrair."""
        estrutura = {
            'titulo': 'Artigo Teste',
            'secoes': [
                {'key': 'sec_1', 'titulo': 'Introdução'},
                {'key': 'sec_2', 'titulo': 'Metodologia'},
            ]
        }
        orch, mm, docs = _make_orchestrator(
            session_state={
                'agente_ativo': 'AGUARDANDO_APROVACAO',
                'active_doc_id': None,
                'last_active_section': None,
                'current_structure': estrutura,
                'pending_section': None,
                'sections_queue': [],
                'completed_sections': [],
            }
        )
        
        docs.create_academic_document.return_value = 'doc_abc123'
        orch.create_google_doc_from_structure = MagicMock(return_value='doc_abc123')
        
        result = orch._handle_approval_flow()
        
        assert result == 'doc_abc123'
        orch.create_google_doc_from_structure.assert_called_once_with(estrutura)
        assert mm.session_state['active_doc_id'] == 'doc_abc123'

    def test_approval_transitions_to_orchestrator(self):
        """Após criar doc, deve transicionar para ORCHESTRATOR (não ESTRUTURADOR)."""
        estrutura = {
            'titulo': 'Artigo',
            'secoes': [{'key': 'sec_1', 'titulo': 'Intro'}]
        }
        orch, mm, docs = _make_orchestrator(
            session_state={
                'agente_ativo': 'AGUARDANDO_APROVACAO',
                'active_doc_id': None,
                'last_active_section': None,
                'current_structure': estrutura,
                'pending_section': None,
                'sections_queue': [],
                'completed_sections': [],
            }
        )
        orch.create_google_doc_from_structure = MagicMock(return_value='doc_xyz')
        
        orch._handle_approval_flow()
        
        assert mm.session_state['agente_ativo'] == 'ORCHESTRATOR'

    def test_approval_populates_sections_queue(self):
        """Deve popular sections_queue com as seções da estrutura aprovada."""
        secoes = [
            {'key': 'sec_1', 'titulo': 'Introdução'},
            {'key': 'sec_2', 'titulo': 'Revisão'},
            {'key': 'sec_3', 'titulo': 'Conclusão'},
        ]
        orch, mm, docs = _make_orchestrator(
            session_state={
                'agente_ativo': 'AGUARDANDO_APROVACAO',
                'active_doc_id': None,
                'last_active_section': None,
                'current_structure': {'titulo': 'Test', 'secoes': secoes},
                'pending_section': None,
                'sections_queue': [],
                'completed_sections': [],
            }
        )
        orch.create_google_doc_from_structure = MagicMock(return_value='doc_123')
        
        orch._handle_approval_flow()
        
        assert len(mm.session_state['sections_queue']) == 3
        assert mm.session_state['completed_sections'] == []


class TestApprovalFallback:
    """Testa o fallback quando current_structure não está salva."""

    def test_approval_fallback_to_extraction(self):
        """Deve tentar extrair da última mensagem quando current_structure é None."""
        orch, mm, docs = _make_orchestrator(
            session_state={
                'agente_ativo': 'AGUARDANDO_APROVACAO',
                'active_doc_id': None,
                'last_active_section': None,
                'current_structure': None,
                'pending_section': None,
                'sections_queue': [],
                'completed_sections': [],
            },
            mensagens=[
                {'role': 'ai', 'content': '### 1. Introdução\n### 2. Metodologia\n### 3. Conclusão'}
            ]
        )
        orch.create_google_doc_from_structure = MagicMock(return_value='doc_fallback')
        
        result = orch._handle_approval_flow()
        
        assert result == 'doc_fallback'

    def test_approval_fails_gracefully_no_ai_msg(self):
        """Deve retornar ERROR_FAIL_DOC quando não há mensagem da IA."""
        orch, mm, docs = _make_orchestrator(
            session_state={
                'agente_ativo': 'AGUARDANDO_APROVACAO',
                'active_doc_id': None,
                'last_active_section': None,
                'current_structure': None,
                'pending_section': None,
                'sections_queue': [],
                'completed_sections': [],
            },
            mensagens=[]
        )
        
        result = orch._handle_approval_flow()
        
        assert result == 'ERROR_FAIL_DOC'
        assert mm.session_state['agente_ativo'] == 'ESTRUTURADOR'


class TestContentApproval:
    """Testa o fluxo de aprovação de conteúdo de seções."""

    def test_content_approval_writes_to_doc(self):
        """Ao aprovar conteúdo, deve escrever no Google Doc."""
        orch, mm, docs = _make_orchestrator(
            session_state={
                'agente_ativo': 'AGUARDANDO_APROVACAO_CONTEUDO',
                'active_doc_id': 'doc_123',
                'last_active_section': None,
                'current_structure': {'titulo': 'Art', 'secoes': []},
                'pending_section': {
                    'key': 'sec_1',
                    'titulo': 'Introdução',
                    'content': '### Introdução\n\nConteúdo da introdução...'
                },
                'sections_queue': [{'key': 'sec_2', 'titulo': 'Metodologia'}],
                'completed_sections': [],
            }
        )
        
        result = orch._handle_content_approval("Sim, aprovo!")
        
        assert result == 'CONTENT_APPROVED'
        docs.write_section.assert_called_once()
        assert 'sec_1' in mm.session_state['completed_sections']
        assert mm.session_state['pending_section'] is None

    def test_content_rejection_keeps_pending(self):
        """Ao rejeitar conteúdo, deve retornar CONTENT_REJECTED."""
        orch, mm, docs = _make_orchestrator(
            session_state={
                'agente_ativo': 'AGUARDANDO_APROVACAO_CONTEUDO',
                'active_doc_id': 'doc_123',
                'last_active_section': None,
                'current_structure': None,
                'pending_section': {
                    'key': 'sec_1',
                    'titulo': 'Introdução',
                    'content': 'Conteúdo original'
                },
                'sections_queue': [],
                'completed_sections': [],
            }
        )
        
        result = orch._handle_content_approval("Não está bom, detalhe mais sobre smart cities")
        
        assert result == 'CONTENT_REJECTED'
        docs.write_section.assert_not_called()


class TestStateTransitions:
    """Testa as transições de estado ao longo do ciclo completo."""

    def test_state_transitions_full_cycle(self):
        """ORCHESTRATOR → ESTRUTURADOR → AGUARDANDO_APROVACAO → ORCHESTRATOR"""
        orch, mm, docs = _make_orchestrator()
        
        # Simula: classificação como ESCRITA → ESTRUTURADOR
        llm_mock = MagicMock()
        llm_mock.invoke.return_value = MagicMock(content='ESCRITA')
        type(orch).llm = PropertyMock(return_value=llm_mock)
        
        orch.classificar_e_atualizar_estado("Quero escrever um artigo")
        assert mm.session_state['agente_ativo'] == 'ESTRUTURADOR'

    def test_no_duplicate_doc_creation(self):
        """Não deve criar doc duplicado na segunda classificação."""
        estrutura = {
            'titulo': 'Art', 
            'secoes': [{'key': 's1', 'titulo': 'Intro'}]
        }
        orch, mm, docs = _make_orchestrator(
            session_state={
                'agente_ativo': 'ORCHESTRATOR',
                'active_doc_id': 'already_created',
                'last_active_section': None,
                'current_structure': estrutura,
                'pending_section': None,
                'sections_queue': [],
                'completed_sections': [],
                'last_input_classified': None,
            }
        )
        
        llm_mock = MagicMock()
        llm_mock.invoke.return_value = MagicMock(content='APROVACAO')
        type(orch).llm = PropertyMock(return_value=llm_mock)
        
        # Quando já tem doc criado e input não é _is_approval,
        # não deve tentar criar outro
        orch.classificar_e_atualizar_estado("continue escrevendo")
        
        # Não deve ter chamado _handle_approval_flow porque 
        # o estado não era AGUARDANDO_APROVACAO
        assert mm.session_state.get('active_doc_id') == 'already_created'
