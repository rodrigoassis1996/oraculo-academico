# tests/unit/test_structure_extraction.py

import pytest
from unittest.mock import MagicMock
from agents.orchestrator import OrchestratorAgent

class TestStructureExtraction:
    
    @pytest.fixture
    def mock_mm(self):
        mm = MagicMock()
        mm.session_state = {}
        return mm

    @pytest.fixture
    def agent(self, mock_mm):
        # We don't need a real LLM for the regex fallback tests
        agent = OrchestratorAgent(mock_mm)
        
        # Mock LLM and place it in session_state so the property .llm returns it
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM failure simulator")
        mock_mm.session_state['llm'] = mock_llm
        
        return agent

    def test_extract_from_numbered_list(self, agent):
        """Test extraction from a numbered list format."""
        text = """
        Aqui está a estrutura:
        1. Introdução
        2. Estado da Arte
        3. Metodologia: O que faremos
        4. Resultados Preliminares | Análise
        5. Conclusão
        """
        
        data = agent.extrair_estrutura_da_mensagem(text)
        
        assert data is not None
        assert data["titulo"] == "Trabalho Acadêmico"
        secoes = data["secoes"]
        assert len(secoes) == 5
        assert secoes[0]["titulo"] == "Introdução"
        assert secoes[0]["key"] == "INTRODUÇÃO"
        assert secoes[2]["titulo"] == "Metodologia"
        assert secoes[2]["key"] == "METODOLOGIA"
        assert secoes[3]["titulo"] == "Resultados Preliminares"

    def test_extract_from_markdown_and_subitems(self, agent):
        """Test extraction with markdown bold and sub-items."""
        text = """
        1. **Introdução**
        2. **Desenvolvimento**
           2.1 Sub-item de teste
        3. **Conclusão**
        """
        
        data = agent.extrair_estrutura_da_mensagem(text)
        
        assert data is not None
        secoes = data["secoes"]
        assert len(secoes) == 4
        assert secoes[0]["titulo"] == "Introdução"
        assert secoes[0]["key"] == "INTRODUÇÃO"
        assert secoes[2]["titulo"] == "Sub-item de teste"

    def test_extract_from_markdown_headers(self, agent):
        """Test extraction from ### headers."""
        text = """
        ### Introdução
        ### Fundamentação Teórica
        ### Conclusão
        """
        
        data = agent.extrair_estrutura_da_mensagem(text)
        
        assert data is not None
        assert len(data["secoes"]) == 3
        assert data["secoes"][0]["key"] == "INTRODUÇÃO"

    def test_extract_combined_garbage(self, agent):
        """Test skip garbage and long text."""
        text = """
        Blah blah.
        1. Intro
        Algum texto longo que não é título pois tem mais de 100 caracteres e blá blá blá blá blá blá blá blá blá blá blá blá blá blá blá blá blá blá blá blá.
        2. Fim
        """
        
        data = agent.extrair_estrutura_da_mensagem(text)
        assert len(data["secoes"]) == 2
        assert data["secoes"][1]["titulo"] == "Fim"
