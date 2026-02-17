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

# --- Hotfix para instâncias obsoletas no session_state ---
if not hasattr(st.session_state['model_manager'].orchestrator, 'create_google_doc_from_structure'):
    del st.session_state['model_manager']
    st.session_state['model_manager'] = ModelManager()
    st.rerun()

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
        
        # --- EXIBIÇÃO DO LINK DO GOOGLE DOCS ---
        doc_id = st.session_state.get('active_doc_id')
        if doc_id:
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            st.success(f"📝 **Documento em edição:** [Abrir no Google Docs]({doc_url})")


        # --- CONTAINER DE SCROLL ---
        chat_container = st.container(height=400, border=False)

        # 1. Renderiza histórico DENTRO do container de scroll
        with chat_container:
            for msg in model_manager.mensagens:
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])
            
            # --- LOGICA DE BOTÕES DE FEEDBACK (DENTRO DO SCROLL) ---
            if st.session_state.get('agente_ativo') == 'AGUARDANDO_APROVACAO':
                st.info("💡 **Dica:** Você pode aprovar a estrutura acima ou solicitar ajustes específicos.")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("✅ Aprovar Estrutura", use_container_width=True, key="btn_aprovar"):
                        model_manager.adicionar_mensagem('human', "Estrutura aprovada!")
                        
                        # Tenta encontrar a última proposta de estrutura/análise da IA
                        ultima_resposta = ""
                        for msg in reversed(model_manager.mensagens):
                            if msg['role'] == 'ai':
                                # Se encontrarmos uma mensagem que pareça ser uma proposta, paramos nela
                                content = msg['content']
                                if "###" in content or "Estrutura" in content or "Sugestão" in content:
                                    ultima_resposta = content
                                    break
                                # Caso contrário, guardamos a última mensagem da IA como backup
                                if not ultima_resposta:
                                    ultima_resposta = content
                        
                        # Extrai a estrutura real via LLM se houver resposta anterior
                        if ultima_resposta:
                            with st.spinner("Analisando proposta de estrutura..."):
                                structure = model_manager.orchestrator.extrair_estrutura_da_mensagem(ultima_resposta)
                        else:
                            structure = None
                        
                        if structure and structure.get("secoes"):
                            # Tenta criar o Doc (reutiliza se já existir)
                            doc_id = model_manager.orchestrator.create_google_doc_from_structure(structure)
                            if doc_id:
                                st.success(f"Excelente! O documento foi preparado com {len(structure['secoes'])} seções.")
                                st.markdown(f"**Link**: [Clique aqui para abrir](https://docs.google.com/document/d/{doc_id})")
                                st.info("Como deseja prosseguir?")
                            else:
                                st.error("Não foi possível criar o documento no Google Docs. Verifique as credenciais.")
                        else:
                            st.warning("⚠️ Não identifiquei uma proposta de estrutura clara na última mensagem. Por favor, peça para o Oráculo 'estruturar o documento' primeiro.")
                        
                        st.session_state['agente_ativo'] = 'ORCHESTRATOR'
                        st.rerun()
                        
                with col2:
                    if st.button("❌ Ajustar Estrutura", use_container_width=True, key="btn_ajustar"):
                        st.warning("⚠️ Descreva os ajustes desejados no campo de texto abaixo.")
                        
                with col3:
                    if st.button("🔄 Ignorar/Mudar de Assunto", use_container_width=True, key="btn_ignorar"):
                        st.session_state['agente_ativo'] = 'ORCHESTRATOR'
                        st.rerun()

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
