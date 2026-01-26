# services/upload_manager.py
"""Gerenciador de upload com suporte a múltiplos documentos."""

import os
import sys
import tempfile
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from time import sleep
from typing import List, Optional, Tuple

import streamlit as st
from fake_useragent import UserAgent
import docx2txt

from langchain_community.document_loaders import (
WebBaseLoader, CSVLoader, PyPDFLoader, TextLoader
)

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

    def __init__(self):
        self.config = UPLOAD_CONFIG
        self.tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.tmp'))
        self.content_dir = os.path.join(self.tmp_dir, 'content')
        
        # Cria diretórios necessários
        os.makedirs(self.content_dir, exist_ok=True)
        self._init_session_state()

    def _init_session_state(self) -> None:
        """Inicializa keys no session_state."""
        if 'documentos' not in st.session_state:
            st.session_state['documentos'] = []  # Lista de DocumentoCarregado

    @property
    def documentos(self) -> List[DocumentoCarregado]:
        """Retorna lista de documentos carregados."""
        return st.session_state.get('documentos', [])

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

    # ==================== VALIDAÇÕES ====================

    def validar_tamanho(self, arquivo) -> Tuple[bool, str]:
        """Valida se arquivo não excede limite."""
        if arquivo is None:
            return False, "Nenhum arquivo selecionado."
        
        tamanho = arquivo.size
        if tamanho > self.config.MAX_SIZE_BYTES:
            tamanho_mb = tamanho / (1024 * 1024)
            return False, (
                f"❌ Arquivo muito grande ({tamanho_mb:.1f}MB). "
                f"Limite: {self.config.MAX_SIZE_MB}MB."
            )
        return True, f"✅ Tamanho válido ({tamanho / (1024 * 1024):.2f}MB)"

    def validar_limite_arquivos(self) -> Tuple[bool, str]:
        """Valida se não excedeu limite de arquivos."""
        if self.total_documentos >= self.config.MAX_ARQUIVOS:
            return False, f"❌ Limite de {self.config.MAX_ARQUIVOS} arquivos atingido."
        return True, ""

    def validar_arquivo(self, arquivo, tipo: TipoArquivo) -> Tuple[bool, List[str]]:
        """Executa todas as validações."""
        erros = []
        
        # Valida limite de arquivos
        valid_limite, msg_limite = self.validar_limite_arquivos()
        if not valid_limite:
            erros.append(msg_limite)
        
        # Valida tamanho (para arquivos, não URLs)
        if tipo != TipoArquivo.SITE:
            valid_size, msg_size = self.validar_tamanho(arquivo)
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

    def _carregar_com_temp_file(self, arquivo, suffix: str, loader_class=None) -> str:
        """Carrega arquivo via script de execução usando arquivo temporário."""
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(arquivo.read())
            temp_path = temp.name
        
        try:
            return self._executar_ingestao(["--file", temp_path, "--suffix", suffix])
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _carregar_docx(self, arquivo) -> str:
        """Carrega arquivo DOCX via script de execução."""
        return self._carregar_com_temp_file(arquivo, '.docx')

    def _gerar_hash(self, texto: str) -> str:
        """Gera hash MD5 do conteúdo."""
        return hashlib.md5(texto.encode('utf-8')).hexdigest()


    # ==================== MÉTODOS PRINCIPAIS ====================

    def carregar_documento(
        self, 
        tipo: TipoArquivo, 
        arquivo_ou_url,
        nome: str = None
    ) -> Tuple[bool, str]:
        """
        Carrega documento e adiciona à lista.
        Returns: (sucesso, mensagem)
        """
        try:
            # Determina nome do documento
            if tipo == TipoArquivo.SITE:
                nome_doc = nome or arquivo_ou_url[:50]
                tamanho_bytes = 0
            else:
                nome_doc = arquivo_ou_url.name
                tamanho_bytes = arquivo_ou_url.size
                arquivo_ou_url.seek(0)  # Reset para leitura
            
            # Carrega conteúdo baseado no tipo
            if tipo.value == TipoArquivo.SITE.value:
                conteudo = self._carregar_site(arquivo_ou_url)
            elif tipo.value == TipoArquivo.PDF.value:
                conteudo = self._carregar_com_temp_file(arquivo_ou_url, '.pdf', PyPDFLoader)
            elif tipo.value == TipoArquivo.CSV.value:
                conteudo = self._carregar_com_temp_file(arquivo_ou_url, '.csv', CSVLoader)
            elif tipo.value == TipoArquivo.TXT.value:
                conteudo = self._carregar_com_temp_file(arquivo_ou_url, '.txt', TextLoader)
            elif tipo.value == TipoArquivo.DOCX.value:
                conteudo = self._carregar_docx(arquivo_ou_url)
            else:
                return False, f"Tipo {tipo} não suportado (valor: {tipo.value if hasattr(tipo, 'value') else tipo})."
            
            # Valida conteúdo
            if not conteudo or len(conteudo.strip()) < 10:
                return False, "⚠️ Documento sem conteúdo extraível."
            
            # Smart Persistence: Gera hash para deduplicação
            content_hash = self._gerar_hash(conteudo)
            cache_id = f"{content_hash}.txt"
            caminho_cache = os.path.join(self.content_dir, cache_id)
            
            ja_existia = os.path.exists(caminho_cache)
            if not ja_existia:
                with open(caminho_cache, 'w', encoding='utf-8') as f:
                    f.write(conteudo)

            # Cria objeto do documento
            doc = DocumentoCarregado(
                id=f"{content_hash}_{datetime.now().timestamp()}", # ID único para a sessão
                nome=nome_doc,
                tipo=tipo,
                caminho_cache=caminho_cache,
                hash=content_hash,
                tamanho_bytes=tamanho_bytes,
                tamanho_chars=len(conteudo)
            )
            
            # Evita duplicatas exatas na lista da sessão atual
            if any(d.caminho_cache == caminho_cache for d in self.documentos):
                return True, f"💡 '{nome_doc}' já está na lista (conteúdo idêntico detectado)."

            # Adiciona à lista
            st.session_state['documentos'].append(doc)
            
            status_msg = "carregado" if not ja_existia else "reutilizado do cache"
            return True, f"✅ '{nome_doc}' {status_msg} ({doc.tamanho_formatado}, {len(conteudo):,} chars)"
            
        except Exception as e:
            return False, f"❌ Erro ao carregar: {str(e)}"

    def remover_documento(self, doc_id: str) -> bool:
        """Remove documento da lista da sessão (mantém cache físico para reuso)."""
        docs = st.session_state['documentos']
        for i, doc in enumerate(docs):
            if doc.id == doc_id:
                docs.pop(i)
                return True
        return False

    def limpar_documentos(self) -> None:
        """Limpa lista de documentos da sessão atual (mantém arquivos no disco)."""
        st.session_state['documentos'] = []
    
    def purgar_fisico(self) -> None:
        """Remove fisicamente todos os arquivos de cache do disco."""
        import shutil
        if os.path.exists(self.content_dir):
            shutil.rmtree(self.content_dir)
            os.makedirs(self.content_dir, exist_ok=True)
        self.limpar_documentos()