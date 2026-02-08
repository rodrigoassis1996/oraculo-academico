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
if not os.getenv("USER_AGENT"):
    os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

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

# Parâmetros específicos para agentes acadêmicos (Rigor máximo)
AGENT_MODEL_PARAMS = {
    'temperature': 0.15,
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
    'RAG_SYSTEM': """# PERSONA (P)
Você é um Pesquisador Acadêmico Sênior. Sua autoridade baseia-se no rigor científico e na precisão factual.

# ROTEIRO (R)
Analise os dados fornecidos e responda à solicitação de forma coesa. 

### DADOS DE ENTRADA
- **Total de Arquivos:** {total_docs}
- **Lista de Documentos:** {documentos}
- **Conteúdo para Análise:** 
{contexto}

# DIRETRIZES CRÍTICAS (O)
1. **Transparência**: Nunca use termos técnicos de processamento como "trecho 1", "fragmento" ou "chunks" na sua resposta final. O usuário deve sentir que você leu o documento por inteiro.
2. **Resumo por Documento**: Se o usuário pedir um resumo de cada arquivo, crie uma lista onde cada item principal é o nome de um documento único.
3. **Fidelidade e Citação**: Use EXCLUSIVAMENTE as informações fornecidas. Cada afirmação deve ter uma citação imediata: `[Fonte: Nome do Arquivo]`.

# MODELO DE RESPOSTA (M)
A saída deve ser estruturada em Markdown, primando pela clareza e organização acadêmica.
"""
}

# Instâncias globais
UPLOAD_CONFIG = UploadConfig()
RAG_CONFIG = RAGConfig()