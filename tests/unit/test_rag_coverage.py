# tests/unit/test_rag_coverage.py
"""Testes unitários para a funcionalidade de cobertura total do RAGManager."""

import pytest
from unittest.mock import MagicMock, patch
from services.rag_manager import RAGManager, RAGConfig
from langchain_core.documents import Document

@pytest.fixture
def rag_manager():
    """Fixture para o RAGManager com mocks."""
    with patch('services.rag_manager.HuggingFaceEmbeddings'), \
         patch('services.rag_manager.chromadb.PersistentClient'):
        return RAGManager()

def test_buscar_em_todos_os_documentos(rag_manager):
    """Verifica se o método busca em cada documento individualmente."""
    # Mock do chroma_client e do vector_store
    mock_collection = MagicMock()
    mock_collection.get.return_value = {
        'metadatas': [{'source': 'doc1.pdf'}, {'source': 'doc2.pdf'}, {'source': 'doc1.pdf'}]
    }
    rag_manager.chroma_client.get_collection.return_value = mock_collection
    
    rag_manager.vector_store = MagicMock()
    rag_manager.vector_store.similarity_search.side_effect = [
        [Document(page_content="c1", metadata={"source": "doc1.pdf"})],
        [Document(page_content="c2", metadata={"source": "doc2.pdf"})]
    ]
    
    with patch('streamlit.session_state', {'rag_initialized': True}):
        res = rag_manager.buscar_em_todos_os_documentos("query", k_por_doc=1)
        
        assert len(res) == 2
        assert res[0].page_content == "c1"
        assert res[1].page_content == "c2"
        # Verifica se chamou search com filtro para cada source único
        assert rag_manager.vector_store.similarity_search.call_count == 2
        
        # Verifica se os filtros foram aplicados corretamente
        calls = rag_manager.vector_store.similarity_search.call_args_list
        filters = [c.kwargs.get('filter') for c in calls]
        assert {"source": "doc1.pdf"} in filters
        assert {"source": "doc2.pdf"} in filters

def test_get_contexto_para_prompt_with_cobertura(rag_manager):
    """Verifica se o contexto usa a busca global quando solicitado."""
    with patch.object(RAGManager, 'buscar_em_todos_os_documentos') as mock_global:
        mock_global.return_value = [Document(page_content="c1", metadata={"source": "doc1.pdf"})]
        
        rag_manager.get_contexto_para_prompt("query", cobertura_total=True)
        mock_global.assert_called_once_with("query")
