import os
from time import sleep
from dotenv import load_dotenv

import tempfile

import streamlit as st

from langchain_community.document_loaders import (
    WebBaseLoader, 
    YoutubeLoader, 
    CSVLoader, 
    PyPDFLoader, 
    TextLoader)
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory

from fake_useragent import UserAgent

load_dotenv()

CONFIG_MODELOS = {
    #'Groq': 
    #    {'modelos': ['llama-3.1-8b-instant', 'meta-llama/llama-guard-4-12b', 'llama-3.3-70b-versatile'],
    #     'chat': ChatGroq}, 
    'OpenAI': 
        {'modelos': ['gpt-5-mini-2025-08-07', 'o4-mini-2025-04-16', 'gpt-5-pro-2025-10-06','gpt-oss-120b'],
         'chat': ChatOpenAI}
}

# Função para carregar o modelo com base no provedor, modelo e api_key fornecidos
def carrega_modelo(tipo_arquivo, arquivo, provedor='OpenAI', modelo='o4-mini-2025-04-16', api_key=os.getenv("OPENAI_API_KEY")):
    
    documento = carrega_arquivos(tipo_arquivo, arquivo)

    system_message = '''
    Você é um assistente acadêmico especializado em responder perguntas com base em um documento {} fornecido pelo usuário:

    ####
    {}
    ####

    Utilize as informações contidas nos documentos para fornecer respostas precisas e relevantes às perguntas feitas pelo usuário.

    Se o documento não contiver informações suficientes para responder à pergunta, informe educadamente ao usuário que você não possui as informações necessárias.

    Seja claro, conciso e acadêmico em suas respostas.

    Se a informação do documento for algo como "Just a moment... Enable JavaScript and cookies to continue", sugira ao usuário carregar o oráculo novamente.

    '''.format(tipo_arquivo, documento)

    print(system_message)
    
    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])

    chat = CONFIG_MODELOS[provedor]['chat'](model=modelo, api_key=api_key, temperature=1)
    chain = template | chat

    st.session_state['chain'] = chain

def carrega_site(url):
    documento = ''
    for i in range(5):
        try: 
            os.environ['USER_AGENT'] = UserAgent().random
            loader = WebBaseLoader(url, raise_for_status=True)
            lista_documentos = loader.load()
            documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
            break
        except:
            print(f'Erro ao carregar o site, tentando novamente ({i+1})...')
            sleep(3)
    if documento == '':
        st.error('Não foi possível carregar o site.')
        st.stop()
    return documento

def carrega_csv(caminho):
    loader = CSVLoader(caminho)
    lista_documentos = loader.load()

    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_pdf(caminho):
    loader = PyPDFLoader(caminho)
    lista_documentos = loader.load()

    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_txt(caminho):
    loader = TextLoader(caminho)
    lista_documentos = loader.load()

    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

# url = "KO6a3QYpZbo"
# def carrega_youtube(video_id):
#     os.environ["USER_AGENT"] = "Mozilla/5.0"
#     loader = YoutubeLoader(url, add_video_info=False, language=["pt"])
#     lista_documentos = loader.load()

#     documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
#     return documento

# documento = carrega_youtube(url)
# print(documento)

def carrega_arquivos(tipo_arquivo, arquivo):
    if tipo_arquivo == 'Site':
        documento = carrega_site(arquivo)
    # if tipo_arquivo == 'Yotube':
        # documento = carrega_Youtube(arquivo)
    if tipo_arquivo == 'PDF':
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_pdf(nome_temp)
    if tipo_arquivo == 'CSV':
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_csv(nome_temp)
    if tipo_arquivo == 'TXT':
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_txt(nome_temp)
    return documento