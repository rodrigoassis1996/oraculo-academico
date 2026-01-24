# execution/document_ingestion.py
"""
Script de execução para ingestão de documentos.
Segue a arquitetura de 3 camadas definida em AGENTS.md.
"""

import sys
import os
import argparse
from typing import Optional

# Adiciona o diretório raiz ao path para importar configurações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from services.upload_manager import UploadManager
from config.settings import TipoArquivo

load_dotenv()

def process_source(source: str, is_url: bool = False) -> Optional[str]:
    """
    Processa uma fonte (URL ou arquivo local) e retorna o conteúdo extraído.
    """
    manager = UploadManager()
    
    # Mock do session_state do Streamlit para o manager funcionar fora do Streamlit se necessário
    # No entanto, o UploadManager depende fortemente do st.session_state.
    # Vamos adaptar uma versão simplificada ou garantir que ele funcione via CLI.
    
    # Como o UploadManager original usa st.session_state, vamos extrair a lógica core
    # para ser independente se possível, ou usar try/except.
    
    tipo = TipoArquivo.SITE if is_url else None
    if not is_url:
        ext = os.path.splitext(source)[1].lower()
        if ext == '.pdf': tipo = TipoArquivo.PDF
        elif ext == '.csv': tipo = TipoArquivo.CSV
        elif ext == '.docx': tipo = TipoArquivo.DOCX
        elif ext == '.txt': tipo = TipoArquivo.TXT
        else:
            print(f"Erro: Extensão {ext} não suportada.")
            return None

    try:
        if is_url:
            print(f"Processando URL: {source}")
            conteudo = manager._carregar_site(source)
        else:
            print(f"Processando Arquivo: {source}")
            with open(source, 'rb') as f:
                # Criamos um objeto mock com .name e .read() e .size para o manager
                class MockFile:
                    def __init__(self, name, data, size):
                        self.name = name
                        self.data = data
                        self.size = size
                        self._pos = 0
                    def read(self): return self.data
                    def seek(self, pos): self._pos = pos
                
                data = f.read()
                mock_file = MockFile(os.path.basename(source), data, len(data))
                
                if tipo == TipoArquivo.PDF:
                    from langchain_community.document_loaders import PyPDFLoader
                    conteudo = manager._carregar_com_temp_file(mock_file, '.pdf', PyPDFLoader)
                elif tipo == TipoArquivo.CSV:
                    from langchain_community.document_loaders import CSVLoader
                    conteudo = manager._carregar_com_temp_file(mock_file, '.csv', CSVLoader)
                elif tipo == TipoArquivo.TXT:
                    from langchain_community.document_loaders import TextLoader
                    conteudo = manager._carregar_com_temp_file(mock_file, '.txt', TextLoader)
                elif tipo == TipoArquivo.DOCX:
                    conteudo = manager._carregar_docx(mock_file)
                else:
                    conteudo = None
        
        return conteudo
    except Exception as e:
        print(f"Erro ao processar: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingestão de documentos para o Oráculo Acadêmico")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL do site para processar")
    group.add_argument("--file", help="Caminho do arquivo local para processar")
    parser.add_argument("--output", help="Arquivo de saída (opcional)", default=None)

    args = parser.parse_args()

    content = None
    if args.url:
        content = process_source(args.url, is_url=True)
    elif args.file:
        content = process_source(args.file, is_url=False)

    if content:
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Conteúdo salvo em: {args.output}")
        else:
            print("\n--- CONTEÚDO EXTRAÍDO (Primeiros 500 chars) ---\n")
            print(content[:500] + "...")
            print("\n--- FIM ---")
    else:
        print("Falha ao extrair conteúdo.")
        sys.exit(1)
