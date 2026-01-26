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
    top_k: int = 10         # Aumentado para melhor cobertura (Fase 7)
    chunk_size: int = 1200   # Levemente maior para manter contexto acadêmico (Fase 7)
    chunk_overlap: int = 300 # Mais sobreposição para não perder conexões entre chunks (Fase 7)

# Parâmetros padrão dos modelos
DEFAULT_MODEL_PARAMS = {
    'temperature': 0.3, # Reduzido para respostas mais precisas e menos criativas (Fase 7)
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
    'RAG_SYSTEM': """Você é um assistente acadêmico de alto nível, especializado em análise documental profunda. 

Sua tarefa consiste em sintetizar as informações dos documentos fornecidos para responder de forma abrangente e rigorosa.

CONTEXTO DOS DOCUMENTOS (TRECHOS RECUPERADOS):
{contexto}

DIRETRIZES DE RESPOSTA:
1. **Fidelidade Estrita**: Baseie sua resposta EXCLUSIVAMENTE nos trechos fornecidos. Se a resposta não estiver lá, admita explicitamente.
2. **Síntese Multi-Documento**: Se a informação estiver espalhada em múltiplos trechos ou arquivos, conecte-os de forma lógica e fluida.
3. **Citação de Fontes**: SEMPRE cite o nome da fonte original (ex: [Fonte: arquivo.pdf]) ao final de cada parágrafo relevante ou afirmação importante.
4. **Tom Acadêmico**: Mantenha um tom profissional, impessoal e analítico.
5. **Estrutura**: Use bullet points ou sub-títulos se a resposta for complexa para facilitar a leitura.

Responda agora com base no contexto acadêmico acima:""",

    'SIMPLE_SYSTEM': """Você é um assistente acadêmico.
Documentos ({total_docs}):

{documentos}

Use as informações acima para responder de forma concisa, precisa e técnica."""
}

# Instâncias globais
UPLOAD_CONFIG = UploadConfig()
RAG_CONFIG = RAGConfig()