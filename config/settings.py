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

# Configuração de modelos LLM
CONFIG_MODELOS = {
'OpenAI': {
    'modelos': ['gpt-4o-mini-2024-07-18', 'o4-mini-2025-04-16', 'gpt-4o'],
    'chat': ChatOpenAI,
    'default_api_key': os.getenv("OPENAI_API_KEY")
},
# 'Groq': {
#     'modelos': ['llama-3.1-8b-instant', 'llama-3.3-70b-versatile'],
#     'chat': ChatGroq,
#     'default_api_key': os.getenv("GROQ_API_KEY")
# },
}

# Instância global de configuração de upload
UPLOAD_CONFIG = UploadConfig()