# 01_home.py
import streamlit as st
from services.upload_manager import UploadManager
from services.model_manager import ModelManager
from components.ui_upload import render_upload_widget, render_status_documento, render_debug_chunks

st.set_page_config(
    page_title='Oráculo Acadêmico',
    page_icon='👨🏾‍🎓',
    layout='wide'
)

# --- CSS: Ajustes finos de layout ---
st.markdown("""
<style>
/* Layout otimizado - previne scroll global mantendo elementos visíveis */
.block-container {
    padding-top: 2rem;  /* Aumentado para evitar corte do título */
    padding-bottom: 2rem;
}

/* Esconde footer padrão */
footer {visibility: hidden;}

/* Previne scroll global - permite apenas scroll interno do chat */
section.main > div {
    overflow-y: auto;
    max-height: 100vh;
}

section.main {
    overflow: hidden;
}

/* Ajuste para o container do Streamlit */
.stChatInput {
    padding-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Inicializa managers
if 'upload_manager' not in st.session_state:
    st.session_state['upload_manager'] = UploadManager()
if 'model_manager' not in st.session_state:
    st.session_state['model_manager'] = ModelManager()

upload_manager = st.session_state['upload_manager']
model_manager = st.session_state['model_manager']

# Mapeamento de nomes de agentes para exibição
AGENT_LABELS = {
    'ORCHESTRATOR': 'Maestro (Triagem)',
    'ESTRUTURADOR': 'Agente Estruturador',
    'QA': 'Agente de Pergunta e Resposta'
}

# ===================== SIDEBAR =====================
with st.sidebar:
    st.header('⚙️ Configurações')
    render_status_documento()
    st.divider()
    render_upload_widget(upload_manager, model_manager)

    st.divider()
    agente_ativo = st.session_state.get('agente_ativo', 'ORCHESTRATOR')
    label_agente = AGENT_LABELS.get(agente_ativo, agente_ativo)
    st.caption(f"🤖 **Agente Ativo:** {label_agente}")
    if st.button('🧹 Limpar Histórico', use_container_width=True):

        model_manager.limpar_memoria()
        st.rerun()

# ===================== MAIN =====================
st.title('👨🏾‍🎓 Oráculo Acadêmico')

# Info sobre documentos
if upload_manager.total_documentos > 0:
    docs_nomes = [doc.nome for doc in upload_manager.documentos]
    st.caption(f"📚 Baseado em: {', '.join(docs_nomes)}")

# Tabs
tab_chat, tab_debug = st.tabs(["💬 Chat", "🔍 Debug Chunks"])

# ===================== TAB DEBUG =====================
with tab_debug:
    render_debug_chunks()

# ===================== TAB CHAT =====================
with tab_chat:
    if model_manager.chain is None:
        st.info('👈 Arraste documento(s) para o painel lateral para começar automaticamente.')
    else:
        usar_rag = st.session_state.get('usar_rag', False)
        
        if usar_rag and st.session_state.get('rag_stats'):
            stats = st.session_state['rag_stats']
            agente_ativo = st.session_state.get('agente_ativo', 'ORCHESTRATOR')
            label_agente = AGENT_LABELS.get(agente_ativo, agente_ativo)
            st.info(f"🎓 **{label_agente}:** Processando solicitação acadêmica.")
            st.caption(f"🧠 RAG ativo: {stats.get('total_chunks', 0)} chunks")


        # --- CONTAINER DE SCROLL ---
        chat_container = st.container(height=350, border=False)

        # 1. Renderiza histórico DENTRO do container de scroll
        with chat_container:
            for msg in model_manager.mensagens:
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])
            
            # O st.container(height=...) rola automaticamente para o final
            pass

# 2. Input do Usuário (Nível raiz para o Streamlit fixar automaticamente)
if model_manager.chain is not None:
    if prompt := st.chat_input('Fale com o Oráculo Acadêmico'):
        # 1. Triagem Imediata para atualizar a UI
        if st.session_state.get('usar_rag'):
             model_manager.orchestrator.classificar_e_atualizar_estado(prompt)

        # 2. Adiciona ao histórico e marca para execução reativa
        model_manager.adicionar_mensagem('human', prompt)
        st.session_state['prompt_pendente'] = prompt
        st.rerun()

# 3. Execução de Prompt Pendente (para garantir que a UI rodou com o novo estado)
if 'prompt_pendente' in st.session_state:
    prompt = st.session_state.pop('prompt_pendente')
    with chat_container:
        with st.chat_message('ai'):
            usar_rag = st.session_state.get('usar_rag', False)
            if usar_rag:
                # O state já mudou, o stream usará o agente certo
                resposta = st.write_stream(model_manager.gerar_resposta_rag(prompt))
            else:
                resposta = st.write_stream(
                    model_manager.chain.stream({
                        'input': prompt,
                        'chat_history': model_manager.get_historico_langchain()
                    })
                )
    
    model_manager.adicionar_mensagem('ai', resposta)
    st.rerun()
