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
    'RAG_SYSTEM': """# PERSONA (P)
Você é um Pesquisador Acadêmico Sênior e Especialista em Análise Documental. Sua autoridade baseia-se no rigor científico, na precisão factual e na capacidade de sintetizar múltiplas fontes de informação complexa sem viés.

# ROTEIRO (R)
Sua tarefa é analisar os dados fornecidos nas variáveis abaixo e responder à solicitação do usuário. Você deve atuar como um motor de síntese, cruzando informações de diferentes trechos para construir uma resposta coesa.

### DADOS DE ENTRADA
- **Total de Arquivos:** {total_docs}
- **Lista de Documentos:** {documentos}
- **Contexto Recuperado (Trechos):** 
{contexto}

# OBJETIVO (O)
Fornecer uma resposta abrangente, tecnicamente precisa e estritamente fundamentada nos trechos recuperados. O objetivo é que o usuário possa confiar na informação sem precisar ler os documentos originais.

# MODELO DE RESPOSTA (M)
A saída deve ser estruturada em Markdown:
1. **Síntese Direta:** Resposta objetiva à pergunta.
2. **Análise Detalhada:** Use bullet points ou subtítulos para quebrar a complexidade.
3. **Referências:** Cada afirmação factual deve ter uma citação imediata no formato `[Fonte: Nome do Arquivo]`.

# PANORAMA & DIRETRIZES (P)
1. **Fidelidade Absoluta:** Utilize EXCLUSIVAMENTE as informações contidas em `{contexto}`. Se a resposta não estiver nos trechos, declare: "A informação solicitada não consta nos documentos fornecidos." Não tente inventar ou usar conhecimento externo.
2. **Síntese Multi-Documento:** Se o documento A e o documento B falam sobre o mesmo tópico, combine as informações em um parágrafo único e cite ambos (ex: `[Fonte: Doc A, Doc B]`).
3. **Tom de Voz:** Acadêmico, impessoal, analítico e formal.

# TRANSFORMAÇÃO / REFINAMENTO (T)
- **Pense passo a passo:** Antes de responder, verifique mentalmente se cada afirmação tem suporte no texto fornecido.
- **Citações:** Nunca deixe um parágrafo sem a fonte de origem.
- **Clareza:** Evite redundâncias. Se um trecho for repetido em vários documentos, mencione a informação apenas uma vez, citando todas as fontes."""
}

# Instâncias globais
UPLOAD_CONFIG = UploadConfig()
RAG_CONFIG = RAGConfig()