# services/upload_manager.py
"""Gerenciador de upload com suporte a múltiplos documentos."""

import os
import tempfile
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
    conteudo: str
    tamanho_bytes: int
    tamanho_chars: int
    data_upload: datetime = field(default_factory=datetime.now)

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
        """Combina conteúdo de todos os documentos."""
        if not self.documentos:
            return ""
        
        partes = []
        for doc in self.documentos:
            partes.append(f"=== DOCUMENTO: {doc.nome} ({doc.tipo.value}) ===\n{doc.conteudo}")
        
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

    def _carregar_site(self, url: str) -> str:
        """Carrega conteúdo de URL."""
        for tentativa in range(5):
            try:
                os.environ['USER_AGENT'] = UserAgent().random
                loader = WebBaseLoader(url, raise_for_status=True)
                docs = loader.load()
                return '\n\n'.join([doc.page_content for doc in docs])
            except Exception as e:
                if tentativa < 4:
                    sleep(3)
                else:
                    raise RuntimeError(f"Falha ao carregar site: {e}")
        return ""

    def _carregar_com_temp_file(self, arquivo, suffix: str, loader_class) -> str:
        """Carrega arquivo via arquivo temporário."""
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(arquivo.read())
            temp_path = temp.name
        
        try:
            loader = loader_class(temp_path)
            docs = loader.load()
            return '\n\n'.join([doc.page_content for doc in docs])
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _carregar_docx(self, arquivo) -> str:
        """Carrega arquivo DOCX."""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp:
            temp.write(arquivo.read())
            temp_path = temp.name
        
        try:
            conteudo = docx2txt.process(temp_path)
            return conteudo
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

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
            if tipo == TipoArquivo.SITE:
                conteudo = self._carregar_site(arquivo_ou_url)
            elif tipo == TipoArquivo.PDF:
                conteudo = self._carregar_com_temp_file(arquivo_ou_url, '.pdf', PyPDFLoader)
            elif tipo == TipoArquivo.CSV:
                conteudo = self._carregar_com_temp_file(arquivo_ou_url, '.csv', CSVLoader)
            elif tipo == TipoArquivo.TXT:
                conteudo = self._carregar_com_temp_file(arquivo_ou_url, '.txt', TextLoader)
            elif tipo == TipoArquivo.DOCX:
                conteudo = self._carregar_docx(arquivo_ou_url)
            else:
                return False, f"Tipo {tipo} não suportado."
            
            # Valida conteúdo
            if not conteudo or len(conteudo.strip()) < 10:
                return False, "⚠️ Documento sem conteúdo extraível."
            
            # Cria objeto do documento
            doc = DocumentoCarregado(
                id=f"{nome_doc}_{datetime.now().timestamp()}",
                nome=nome_doc,
                tipo=tipo,
                conteudo=conteudo,
                tamanho_bytes=tamanho_bytes,
                tamanho_chars=len(conteudo)
            )
            
            # Adiciona à lista
            st.session_state['documentos'].append(doc)
            
            return True, f"✅ '{nome_doc}' carregado ({doc.tamanho_formatado}, {len(conteudo):,} chars)"
            
        except Exception as e:
            return False, f"❌ Erro ao carregar: {str(e)}"

    def remover_documento(self, doc_id: str) -> bool:
        """Remove documento da lista pelo ID."""
        docs = st.session_state['documentos']
        for i, doc in enumerate(docs):
            if doc.id == doc_id:
                docs.pop(i)
                return True
        return False

    def limpar_documentos(self) -> None:
        """Remove todos os documentos."""
        st.session_state['documentos'] = []