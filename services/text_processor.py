# services/text_processor.py
"""Processador de texto para RAG - chunking, limpeza e validação."""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter

@dataclass
class ChunkConfig:
    """Configurações de chunking."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: List[str] = None

    def __post_init__(self):
        if self.separators is None:
            self.separators = ["\n\n", "\n", ". ", " ", ""]

@dataclass
class TextChunk:
    """Representa um chunk de texto processado."""
    conteudo: str
    indice: int
    documento_origem: str
    total_chars: int


class TextProcessor:
    """
    Processador de texto para preparação de documentos para RAG.
    Inclui limpeza, chunking e validação.
    """

    def __init__(self, config: ChunkConfig = None):
        self.config = config or ChunkConfig()
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=self.config.separators,
            length_function=len,
        )

    # ==================== LIMPEZA ====================

    def limpar_texto(self, texto: str) -> str:
        """
        Limpa e normaliza texto extraído.
        Remove caracteres problemáticos e normaliza espaços.
        """
        if not texto:
            return ""
        
        # Remove caracteres nulos e de controle (exceto newlines e tabs)
        texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', texto)
        
        # Normaliza quebras de linha excessivas
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        
        # Remove espaços múltiplos (mantém newlines)
        texto = re.sub(r'[^\S\n]+', ' ', texto)
        
        # Remove espaços no início/fim de linhas
        texto = '\n'.join(line.strip() for line in texto.split('\n'))
        
        # Remove linhas vazias consecutivas
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        
        return texto.strip()

    def remover_cabecalhos_rodapes(self, texto: str) -> str:
        """
        Remove padrões comuns de cabeçalhos/rodapés de PDFs.
        """
        # Remove números de página isolados
        texto = re.sub(r'^\s*\d+\s*$', '', texto, flags=re.MULTILINE)
        
        # Remove padrões comuns de cabeçalho (ex: "Página X de Y")
        texto = re.sub(r'[Pp]ágina\s+\d+\s*(de\s+\d+)?', '', texto)
        texto = re.sub(r'[Pp]age\s+\d+\s*(of\s+\d+)?', '', texto)
        
        return texto

    def processar_texto(self, texto: str, limpar: bool = True) -> str:
        """Pipeline completo de processamento de texto."""
        if limpar:
            texto = self.limpar_texto(texto)
            texto = self.remover_cabecalhos_rodapes(texto)
        return texto

    # ==================== CHUNKING ====================

    def criar_chunks(
        self, 
        texto: str, 
        documento_nome: str,
        processar: bool = True
    ) -> List[TextChunk]:
        """
        Divide texto em chunks otimizados para RAG.
        
        Args:
            texto: Texto completo do documento
            documento_nome: Nome do documento de origem
            processar: Se deve aplicar limpeza antes do chunking
            
        Returns:
            Lista de TextChunk
        """
        if processar:
            texto = self.processar_texto(texto)
        
        if not texto:
            return []
        
        # Divide em chunks
        chunks_raw = self._splitter.split_text(texto)
        
        # Cria objetos TextChunk
        chunks = []
        for i, chunk_texto in enumerate(chunks_raw):
            chunk = TextChunk(
                conteudo=chunk_texto,
                indice=i,
                documento_origem=documento_nome,
                total_chars=len(chunk_texto)
            )
            chunks.append(chunk)
        
        return chunks

    def criar_chunks_multiplos_docs(
        self,
        documentos: List[Tuple[str, str]]  # [(nome, conteudo), ...]
    ) -> List[TextChunk]:
        """
        Cria chunks de múltiplos documentos.
        
        Args:
            documentos: Lista de tuplas (nome_documento, conteudo)
            
        Returns:
            Lista consolidada de TextChunks
        """
        todos_chunks = []
        
        for nome, conteudo in documentos:
            chunks = self.criar_chunks(conteudo, nome)
            todos_chunks.extend(chunks)
        
        return todos_chunks

    # ==================== VALIDAÇÃO ====================

    def validar_conteudo_extraido(self, texto: str) -> Tuple[bool, str]:
        """
        Valida se o conteúdo extraído é utilizável.
        
        Returns:
            (is_valid, mensagem)
        """
        if not texto:
            return False, "Nenhum conteúdo extraído."
        
        texto_limpo = self.limpar_texto(texto)
        
        # Muito curto
        if len(texto_limpo) < 50:
            return False, "Conteúdo muito curto (< 50 caracteres)."
        
        # Detecta possíveis problemas de extração
        problemas = []
        
        # PDF protegido ou escaneado (muito pouco texto legível)
        palavras = texto_limpo.split()
        if len(palavras) < 10:
            problemas.append("Poucas palavras extraídas (possível PDF escaneado ou protegido)")
        
        # Muitos caracteres estranhos
        chars_estranhos = len(re.findall(r'[^\w\s\.,;:!?\-\(\)\[\]\"\'áéíóúàèìòùâêîôûãõäëïöüç]', texto_limpo, re.IGNORECASE))
        ratio_estranhos = chars_estranhos / len(texto_limpo) if texto_limpo else 0
        if ratio_estranhos > 0.1:
            problemas.append("Muitos caracteres não reconhecidos (possível problema de encoding)")
        
        # Texto de bloqueio JavaScript
        if "enable javascript" in texto_limpo.lower() or "just a moment" in texto_limpo.lower():
            problemas.append("Conteúdo bloqueado por JavaScript")
        
        if problemas:
            return False, " | ".join(problemas)
        
        return True, "Conteúdo válido"

    # ==================== ESTATÍSTICAS ====================

    def get_estatisticas(self, chunks: List[TextChunk]) -> dict:
        """Retorna estatísticas dos chunks gerados."""
        if not chunks:
            return {
                "total_chunks": 0,
                "total_chars": 0,
                "media_chars_chunk": 0,
                "documentos": []
            }
        
        total_chars = sum(c.total_chars for c in chunks)
        docs_unicos = list(set(c.documento_origem for c in chunks))
        
        return {
            "total_chunks": len(chunks),
            "total_chars": total_chars,
            "media_chars_chunk": total_chars // len(chunks),
            "documentos": docs_unicos
        }