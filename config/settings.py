# config/settings.py
"""Configurações centralizadas do projeto."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Type
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# from langchain_groq import ChatGroq  # Descomente quando usar

load_dotenv()

class TipoArquivo(Enum):
    """Tipos de arquivo suportados pelo sistema."""
    SITE = "Site"
    # YOUTUBE = "Youtube"  # Descomente quando implementar
    PDF = "PDF"
    CSV = "CSV"
    TXT = "TXT"
    DOCX = "DOCX"

@dataclass
class UploadConfig:
    """Configurações de upload."""
    MAX_SIZE_MB: int = 10
    MAX_SIZE_BYTES: int = field(init=False)
    MAX_ARQUIVOS: int = 10
    EXTENSOES: Dict[TipoArquivo, List[str]] = field(default_factory=dict)

    def __post_init__(self):
        self.MAX_SIZE_BYTES = self.MAX_SIZE_MB * 1024 * 1024
        self.EXTENSOES = {
            TipoArquivo.PDF: [".pdf"],
            TipoArquivo.CSV: [".csv"],
            TipoArquivo.TXT: [".txt"],
            TipoArquivo.DOCX: [".docx"],
        }

@dataclass
class RAGConfig:
    """Configurações do RAG."""
    embedding_model: str = "all-MiniLM-L6-v2"
    collection_name: str = "oraculo_docs"
    top_k: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200

# Parâmetros padrão dos modelos
DEFAULT_MODEL_PARAMS = {
    'temperature': 0.7,
    'max_tokens': None,
}

# Configuração de modelos LLM
CONFIG_MODELOS = {
    'OpenAI': {
        'modelos': ['gpt-4o-mini-2024-07-18', 'o4-mini-2025-04-16', 'gpt-4o'],
        'chat': ChatOpenAI,
        'default_api_key': os.getenv("OPENAI_API_KEY")
    }
}

# Prompts centralizados
PROMPTS = {
    'RAG_SYSTEM': """Você é um assistente acadêmico especializado. 
Responda à pergunta baseando-se EXCLUSIVAMENTE no contexto fornecido.

CONTEXTO DOS DOCUMENTOS:
{contexto}

INSTRUÇÕES:
1. Use apenas informações do contexto acima.
2. Se não encontrar a informação, diga claramente.
3. Cite a fonte (nome do documento) quando possível.
4. Seja claro, preciso e acadêmico.""",

    'SIMPLE_SYSTEM': """Você é um assistente acadêmico.
Documentos ({total_docs}):

{documentos}

Use as informações acima para responder de forma concisa e precisa."""
}

# Instâncias globais
UPLOAD_CONFIG = UploadConfig()
RAG_CONFIG = RAGConfig()