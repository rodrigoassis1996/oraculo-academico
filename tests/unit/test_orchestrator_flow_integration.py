# tests/unit/test_orchestrator_flow_integration.py

import pytest
from unittest.mock import MagicMock, patch
from agents.orchestrator import OrchestratorAgent
from langchain_core.messages import AIMessage

class TestOrchestratorFlowIntegration:
    
    @pytest.fixture
    def mock_mm(self):
        mm = MagicMock()
        mm.session_state = {
            'llm': MagicMock(),
            'agente_ativo': 'ORCHESTRATOR',
            'active_doc_id': None,
            'current_structure': None,
            'last_input_classified': None
        }
        mm.get_historico_langchain.return_value = []
        mm.rag_manager.get_contexto_para_prompt.return_value = ""
        mm.mensagens = []
        return mm

    @pytest.fixture
    def docs_manager(self):
        return MagicMock()

    def test_approval_flow_creates_doc_and_auto_continues(self, mock_mm, docs_manager):
        """Testa se a aprovação cria o doc e muda o estado para Estruturador com auto-continuação."""
        # 1. Setup: Estado inicial aguardando aprovação com estrutura na memória
        mock_mm.session_state['agente_ativo'] = 'AGUARDANDO_APROVACAO'
        structure = {"titulo": "Tese", "secoes": [{"key": "S1", "titulo": "Intro"}]}
        mock_mm.session_state['current_structure'] = structure
        mock_mm.mensagens = [{'role': 'ai', 'content': '### Intro: Resumo'}]
        
        docs_manager.create_academic_document.return_value = "doc_123"
        
        agent = OrchestratorAgent(mock_mm, docs_manager=docs_manager)
        
        # Mock do LLM para a chain de escrita
        mock_llm = mock_mm.session_state['llm']
        mock_llm.invoke.return_value = AIMessage(content="CONTEUDO")
        mock_llm.stream.return_value = [MagicMock(content="Conteudo da seção")]

        with patch('agents.orchestrator.ChatPromptTemplate.from_messages') as mock_template_factory:
            # 2. Execução: Usuário envia "Aprovo"
            # O OrchestratorAgent irá chamar classificar_e_atualizar_estado
            # que por sua vez chama extrair_estrutura_da_mensagem
            
            # Precisamos mockar o extrair_estrutura_da_mensagem para não depender do LLM no teste de fluxo
            with patch.object(OrchestratorAgent, 'extrair_estrutura_da_mensagem', return_value=structure):
                mock_template = MagicMock()
                mock_template_factory.return_value = mock_template
                mock_chain = MagicMock()
                mock_template.__or__.return_value = mock_chain
                mock_chain.stream.return_value = [MagicMock(content="Texto gerado")]
                
                gen = agent.route_request("Aprovo")
                res = list(gen)
            
            # 3. Verificações
            # Verifica se o doc foi criado
            docs_manager.create_academic_document.assert_called_once_with(
                title="Tese", structure=structure
            )
            
            # Verifica se o estado mudou
            assert mock_mm.session_state['agente_ativo'] == 'ESTRUTURADOR'
            assert mock_mm.session_state['active_doc_id'] == "doc_123"
            
            # Verifica se o prompt injetado contém a instrução de auto-continuação
            # (Pegamos o input_rich passado para o template)
            # Como usamos generator e chain.stream, olhamos a chamada do chain.stream
            call_args = mock_chain.stream.call_args[0][0]
            assert "A estrutura foi APROVADA" in call_args['input']
            assert "Intro" in call_args['input']
