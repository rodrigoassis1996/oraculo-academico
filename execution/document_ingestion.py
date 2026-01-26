# execution/document_ingestion.py
"""
Script de execução para extração de texto de documentos e URLs.
Segue a arquitetura de 3 camadas definida em AGENTS.md.
Independente do Streamlit e da camada de serviços.
"""

import os
import argparse
import tempfile
import sys
import io
from typing import Optional, List
from time import sleep

# Força o stdout a usar UTF-8 para evitar erros de encoding no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Loaders do LangChain
from langchain_community.document_loaders import (
    WebBaseLoader, 
    CSVLoader, 
    PyPDFLoader, 
    TextLoader
)
import docx2txt
from fake_useragent import UserAgent

def extract_from_url(url: str) -> str:
    """Extrai texto de uma URL com retry e fake user agent."""
    for tentativa in range(5):
        try:
            # Set User-Agent for WebBaseLoader
            os.environ['USER_AGENT'] = UserAgent().random
            loader = WebBaseLoader(url, raise_for_status=True)
            docs = loader.load()
            return '\n\n'.join([doc.page_content for doc in docs])
        except Exception as e:
            if tentativa < 4:
                sleep(2)
            else:
                raise RuntimeError(f"Falha ao carregar site: {e}")
    return ""

def extract_from_file(file_path: str, suffix: str) -> str:
    """Extrai texto de arquivo local baseado na extensão."""
    suffix = suffix.lower()
    
    if suffix == '.pdf':
        try:
            import pypdf
        except ImportError:
            raise ImportError("Biblioteca 'pypdf' não encontrada. Instale com 'pip install pypdf'.")
            
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        if not docs:
            return ""
        return '\n\n'.join([doc.page_content for doc in docs])
    
    elif suffix == '.csv':
        # Tenta múltiplos encodings para CSV
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        last_err = None
        for enc in encodings:
            try:
                loader = CSVLoader(file_path, encoding=enc)
                docs = loader.load()
                return '\n\n'.join([doc.page_content for doc in docs])
            except Exception as e:
                last_err = e
                continue
        raise RuntimeError(f"Não foi possível ler o arquivo CSV com nenhum dos encodings {encodings}. Erro final: {last_err}")

    
    elif suffix == '.txt':
        # Tenta múltiplos encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'utf-16']
        last_err = None
        for enc in encodings:
            try:
                loader = TextLoader(file_path, encoding=enc)
                docs = loader.load()
                return '\n\n'.join([doc.page_content for doc in docs])
            except Exception as e:
                last_err = e
                continue
        raise RuntimeError(f"Não foi possível ler o arquivo TXT com nenhum dos encodings {encodings}. Erro final: {last_err}")


    
    elif suffix == '.docx':
        return docx2txt.process(file_path)
    
    else:
        raise ValueError(f"Extensão {suffix} não suportada.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extração determinística de texto.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL para processar")
    group.add_argument("--file", help="Caminho do arquivo local")
    parser.add_argument("--suffix", help="Sufixo do arquivo (se --file for usado)", default=None)
    parser.add_argument("--output", help="Arquivo de saída (opcional)", default=None)

    args = parser.parse_args()

    try:
        content = ""
        if args.url:
            content = extract_from_url(args.url)
        elif args.file:
            suffix = args.suffix or os.path.splitext(args.file)[1]
            if not os.path.exists(args.file):
                print(f"ERRO: Arquivo não encontrado: {args.file}", file=sys.stderr)
                sys.exit(1)
            content = extract_from_file(args.file, suffix)

        if content:
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"SUCESSO: Conteúdo salvo em {args.output}")
            else:
                # Se não houver output, imprime para o stdout
                sys.stdout.write(content)
        else:
            print("ERRO: Nenhum conteúdo extraído.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        import traceback
        print(f"ERRO: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
