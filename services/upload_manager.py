# services/upload_manager.py
"""Gerenciador de upload com suporte a múltiplos documentos."""

import os
import sys
import tempfile
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

try:
    import streamlit as st
except ImportError:
    st = None

from fake_useragent import UserAgent

from config.settings import TipoArquivo, UPLOAD_CONFIG

@dataclass
class DocumentoCarregado:
    """Representa um documento carregado no sistema."""
    id: str
    nome: str
    tipo: TipoArquivo
    caminho_cache: str  # Caminho para o arquivo de texto em .tmp/
    hash: str          # Hash MD5 do conteúdo
    tamanho_bytes: int
    tamanho_chars: int
    data_upload: datetime = field(default_factory=datetime.now)

    def get_conteudo(self) -> str:
        """Lê o conteúdo do arquivo de cache."""
        if not os.path.exists(self.caminho_cache):
            return ""
        with open(self.caminho_cache, 'r', encoding='utf-8') as f:
            return f.read()

    @property
    def tamanho_formatado(self) -> str:
        """Retorna tamanho em formato legível."""
        if self.tamanho_bytes < 1024:
            return f"{self.tamanho_bytes} B"
        elif self.tamanho_bytes < 1024 * 1024:
            return f"{self.tamanho_bytes / 1024:.1f} KB"
        else:
            return f"{self.tamanho_bytes / (1024 * 1024):.2f} MB"

class UploadManager:
    """
    Gerenciador de uploads com suporte a múltiplos documentos.
    """

    def __init__(self, external_state: Optional[List[DocumentoCarregado]] = None):
        self.config = UPLOAD_CONFIG
        self.tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.tmp'))
        self.content_dir = os.path.join(self.tmp_dir, 'content')
        
        # Cria diretórios necessários
        os.makedirs(self.content_dir, exist_ok=True)
        
        # Estado interno ou externo
        self._internal_docs = []
        self._external_state = external_state
        
        # Tenta inicializar com session_state se disponível e nenhum estado externo fornecido
        if self._external_state is None and st is not None:
             if 'documentos' not in st.session_state:
                 st.session_state['documentos'] = []
             self._external_state = st.session_state['documentos']

    @property
    def documentos(self) -> List[DocumentoCarregado]:
        """Retorna lista de documentos carregados."""
        if self._external_state is not None:
            return self._external_state
        return self._internal_docs

    @property
    def total_documentos(self) -> int:
        """Retorna quantidade de documentos."""
        return len(self.documentos)

    @property
    def conteudo_combinado(self) -> str:
        """Combina conteúdo de todos os documentos (lendo do cache)."""
        if not self.documentos:
            return ""
        
        partes = []
        for doc in self.documentos:
            partes.append(f"=== DOCUMENTO: {doc.nome} ({doc.tipo.value}) ===\n{doc.get_conteudo()}")
        
        return "\n\n".join(partes)

    def detectar_tipo_arquivo(self, nome_arquivo: str) -> Optional[TipoArquivo]:
        """
        Detecta o tipo do arquivo baseado na extensão.
        """
        ext = os.path.splitext(nome_arquivo)[1].lower()
        
        mapping = {
            ".pdf": TipoArquivo.PDF,
            ".docx": TipoArquivo.DOCX,
            ".csv": TipoArquivo.CSV,
            ".txt": TipoArquivo.TXT
        }
        
        return mapping.get(ext)

    # ==================== VALIDAÇÕES ====================

    def validar_tamanho(self, tamanho_bytes: int) -> Tuple[bool, str]:
        """Valida se tamanho não excede limite."""
        if tamanho_bytes > self.config.MAX_SIZE_BYTES:
            tamanho_mb = tamanho_bytes / (1024 * 1024)
            return False, (
                f"❌ Arquivo muito grande ({tamanho_mb:.1f}MB). "
                f"Limite: {self.config.MAX_SIZE_MB}MB."
            )
        return True, f"✅ Tamanho válido ({tamanho_bytes / (1024 * 1024):.2f}MB)"

    def validar_limite_arquivos(self) -> Tuple[bool, str]:
        """Valida se não excedeu limite de arquivos."""
        if self.total_documentos >= self.config.MAX_ARQUIVOS:
            return False, f"❌ Limite de {self.config.MAX_ARQUIVOS} arquivos atingido."
        return True, ""

    def validar_arquivo(self, tamanho_bytes: int, tipo: TipoArquivo) -> Tuple[bool, List[str]]:
        """Executa todas as validações."""
        erros = []
        
        # Valida limite de arquivos
        valid_limite, msg_limite = self.validar_limite_arquivos()
        if not valid_limite:
            erros.append(msg_limite)
        
        # Valida tamanho (para arquivos, não URLs)
        if tipo != TipoArquivo.SITE:
            valid_size, msg_size = self.validar_tamanho(tamanho_bytes)
            if not valid_size:
                erros.append(msg_size)
        
        return len(erros) == 0, erros

    # ==================== LOADERS ====================

    def _executar_ingestao(self, args: List[str]) -> str:
        """Executa o script de ingestão e retorna o resultado."""
        import subprocess
        
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'execution', 'document_ingestion.py'))
        cmd = [sys.executable, script_path] + args
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr or e.stdout or "Nenhuma mensagem de erro capturada."
            raise RuntimeError(f"Erro no script de ingestão: {err_msg.strip()}")

    def _carregar_site(self, url: str) -> str:
        """Carrega conteúdo de URL via script de execução."""
        return self._executar_ingestao(["--url", url])

    def _carregar_do_arquivo(self, file_path: str, suffix: str) -> str:
        """Carrega arquivo via script de execução."""
        return self._executar_ingestao(["--file", file_path, "--suffix", suffix])

    def _gerar_hash(self, texto: str) -> str:
        """Gera hash MD5 do conteúdo."""
        return hashlib.md5(texto.encode('utf-8')).hexdigest()

    # ==================== MÉTODOS PRINCIPAIS ====================

    def carregar_documento_de_dados(
        self, 
        tipo: TipoArquivo, 
        dados: bytes,
        nome_arquivo: str
    ) -> Tuple[bool, str]:
        """Carrega documento a partir de bytes (útil para API)."""
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(nome_arquivo)[1], delete=False) as temp:
            temp.write(dados)
            temp_path = temp.name
        
        try:
            return self.carregar_documento_de_caminho(tipo, temp_path, nome_arquivo)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def carregar_documento_de_caminho(
        self, 
        tipo: TipoArquivo, 
        caminho_arquivo: str,
        nome_original: str = None
    ) -> Tuple[bool, str]:
        """Carrega documento a partir de um caminho no disco."""
        try:
            nome_doc = nome_original or os.path.basename(caminho_arquivo)
            tamanho_bytes = os.path.getsize(caminho_arquivo)
            
            # Validações
            success, errors = self.validar_arquivo(tamanho_bytes, tipo)
            if not success:
                return False, " | ".join(errors)

            # Ingestão
            suffix = os.path.splitext(nome_doc)[1]
            conteudo = self._carregar_do_arquivo(caminho_arquivo, suffix)
            
            return self._registrar_documento(tipo, conteudo, nome_doc, tamanho_bytes)
        except Exception as e:
            return False, f"❌ Erro ao carregar: {str(e)}"

    def carregar_documento_url(self, url: str, nome: str = None) -> Tuple[bool, str]:
        """Carrega documento a partir de uma URL."""
        try:
            nome_doc = nome or url[:50]
            conteudo = self._carregar_site(url)
            return self._registrar_documento(TipoArquivo.SITE, conteudo, nome_doc, 0)
        except Exception as e:
            return False, f"❌ Erro ao carregar URL: {str(e)}"

    def _registrar_documento(self, tipo: TipoArquivo, conteudo: str, nome_doc: str, tamanho_bytes: int) -> Tuple[bool, str]:
        """Lógica comum de registro após extração de texto."""
        if not conteudo or len(conteudo.strip()) < 10:
            return False, "⚠️ Documento sem conteúdo extraível."
        
        content_hash = self._gerar_hash(conteudo)
        cache_id = f"{content_hash}.txt"
        caminho_cache = os.path.join(self.content_dir, cache_id)
        
        ja_existia = os.path.exists(caminho_cache)
        if not ja_existia:
            with open(caminho_cache, 'w', encoding='utf-8') as f:
                f.write(conteudo)

        doc = DocumentoCarregado(
            id=f"{content_hash}_{datetime.now().timestamp()}",
            nome=nome_doc,
            tipo=tipo,
            caminho_cache=caminho_cache,
            hash=content_hash,
            tamanho_bytes=tamanho_bytes,
            tamanho_chars=len(conteudo)
        )
        
        if any(d.caminho_cache == caminho_cache for d in self.documentos):
            return True, f"💡 '{nome_doc}' já está na lista (conteúdo idêntico)."

        if self._external_state is not None:
            self._external_state.append(doc)
        else:
            self._internal_docs.append(doc)
        
        status_msg = "carregado" if not ja_existia else "reutilizado do cache"
        return True, f"✅ '{nome_doc}' {status_msg} ({doc.tamanho_formatado})"

    def carregar_documento(self, tipo: TipoArquivo, arquivo_ou_url, nome: str = None) -> Tuple[bool, str]:
        """Interface legada para compatibilidade com Streamlit."""
        if tipo == TipoArquivo.SITE:
            return self.carregar_documento_url(arquivo_ou_url, nome)
        
        # Assume que arquivo_ou_url é um UploadedFile do Streamlit ou objeto similar com .read()
        try:
            dados = arquivo_ou_url.read()
            # Se for UploadedFile, ele tem .name
            nome_original = nome or getattr(arquivo_ou_url, 'name', 'arquivo_sem_nome')
            return self.carregar_documento_de_dados(tipo, dados, nome_original)
        except Exception as e:
            return False, f"❌ Erro na interface legada: {str(e)}"

    def remover_documento(self, doc_id: str) -> bool:
        """Remove documento da lista."""
        docs = self.documentos
        for i, doc in enumerate(docs):
            if doc.id == doc_id:
                docs.pop(i)
                return True
        return False

    def limpar_documentos(self) -> None:
        """Limpa lista de documentos."""
        if self._external_state is not None:
            self._external_state.clear()
        else:
            self._internal_docs.clear()
    
    def purgar_fisico(self) -> None:
        """Remove fisicamente todos os arquivos de cache."""
        import shutil
        if os.path.exists(self.content_dir):
            shutil.rmtree(self.content_dir)
            os.makedirs(self.content_dir, exist_ok=True)
        self.limpar_documentos()
