# components/ui_upload.py
"""Componentes de UI para upload e RAG."""

import streamlit as st

from config.settings import TipoArquivo, UPLOAD_CONFIG
from services.upload_manager import UploadManager
from services.model_manager import ModelManager

def render_upload_widget(upload_manager: UploadManager, model_manager: ModelManager):
    """Renderiza widget de upload."""

    st.subheader("📄 Upload de Documentos")
    st.caption(f"Máx: {UPLOAD_CONFIG.MAX_ARQUIVOS} arquivos, {UPLOAD_CONFIG.MAX_SIZE_MB}MB cada")

    tipo_str = st.selectbox(
        "Tipo de fonte",
        options=[t.value for t in TipoArquivo],
        key="tipo_arquivo_select"
    )
    tipo = TipoArquivo(tipo_str)

    if tipo == TipoArquivo.SITE:
        arquivo = st.text_input("URL do site", key="url_input")
        arquivos = [arquivo] if arquivo else []
    else:
        extensoes_map = {
            TipoArquivo.PDF: ["pdf"],
            TipoArquivo.CSV: ["csv"],
            TipoArquivo.TXT: ["txt"],
            TipoArquivo.DOCX: ["docx"],
        }
        arquivos = st.file_uploader(
            f"Selecione arquivo(s) {tipo.value}",
            type=extensoes_map.get(tipo, []),
            accept_multiple_files=True,
            key="file_uploader_multi"
        )

    # Preview dos arquivos selecionados
    if arquivos and tipo != TipoArquivo.SITE:
        st.info(f"📎 {len(arquivos)} arquivo(s) selecionado(s)")

    # Botão adicionar
    if st.button("➕ Adicionar", use_container_width=True, disabled=not arquivos):
        for arq in arquivos:
            with st.spinner(f"Carregando {arq if tipo == TipoArquivo.SITE else arq.name}..."):
                sucesso, mensagem = upload_manager.carregar_documento(tipo, arq)
            if sucesso:
                st.success(mensagem)
            else:
                st.error(mensagem)

    st.divider()
    render_lista_documentos(upload_manager)

    st.divider()
    render_botoes_acao(upload_manager, model_manager)

def render_lista_documentos(upload_manager: UploadManager):
    """Renderiza lista de documentos carregados."""
    docs = upload_manager.documentos

    st.subheader(f"📚 Documentos ({len(docs)})")

    if not docs:
        st.info("Nenhum documento carregado.")
        return

    for doc in docs:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{doc.nome}**")
            st.caption(f"{doc.tipo.value} • {doc.tamanho_formatado} • {doc.tamanho_chars:,} chars")
        with col2:
            if st.button("🗑️", key=f"del_{doc.id}"):
                upload_manager.remover_documento(doc.id)
                st.rerun()

def render_botoes_acao(upload_manager: UploadManager, model_manager: ModelManager):
    """Renderiza botões de ação."""
    total = upload_manager.total_documentos

    # Opção de modo RAG
    usar_rag = st.toggle(
        "🧠 Usar RAG (recomendado para documentos grandes)",
        value=True,
        key="toggle_rag"
    )

    if usar_rag:
        st.caption("RAG divide os documentos em partes e busca apenas as relevantes para cada pergunta.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            f"🚀 Inicializar ({total})",
            disabled=total == 0,
            type="primary",
            use_container_width=True
        ):
            # Prepara documentos com hash para indexação incremental
            documentos = [(doc.nome, doc.get_conteudo(), doc.hash) for doc in upload_manager.documentos]
            
            if usar_rag:
                # Modo RAG
                progress = st.progress(0, text="Iniciando...")
                
                try:
                    stats = model_manager.criar_chain_rag(
                        documentos=documentos,
                        progress_callback=lambda p, t: progress.progress(p, text=t)
                    )
                    progress.empty()
                    st.success(
                        f"✅ RAG inicializado!\n\n"
                        f"📊 **{stats['total_chunks']}** chunks criados de "
                        f"**{stats['documentos_indexados']}** documento(s)"
                    )
                except Exception as e:
                    progress.empty()
                    st.error(f"❌ Erro: {e}")
            else:
                # Modo simples
                with st.spinner("Criando Oráculo..."):
                    try:
                        model_manager.criar_chain_simples(
                            documentos_conteudo=upload_manager.conteudo_combinado,
                            total_documentos=total
                        )
                        st.success(f"✅ Oráculo pronto com {total} doc(s)!")
                    except Exception as e:
                        st.error(f"❌ {e}")

    with col2:
        if st.button("🗑️ Limpar", disabled=total == 0, use_container_width=True):
            upload_manager.limpar_documentos()
            model_manager.reset_completo()
            st.rerun()

    # Zona de Perigo - Limpeza física
    with st.sidebar:
        st.divider()
        with st.expander("⚠️ Configurações Avançadas"):
            st.warning("A purga deleta fisicamente o banco de vetores e o cache de texto do disco.")
            if st.button("🔥 Purgar Dados Locais", use_container_width=True):
                # Executa purga nos dois managers e reseta sessão
                upload_manager.purgar_fisico()
                sucesso, msg = model_manager.rag_manager.purgar_fisicamente()
                if sucesso:
                    model_manager.reset_completo()
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


def render_status_documento():
    """Status na sidebar."""
    docs = st.session_state.get('documentos', [])
    chain = st.session_state.get('chain')
    usar_rag = st.session_state.get('usar_rag', False)
    rag_stats = st.session_state.get('rag_stats', {})

    if docs:
        st.success(f"📚 {len(docs)} documento(s)")
        for doc in docs:
            st.caption(f"• {doc.nome}")
        
        if chain:
            if usar_rag:
                chunks = rag_stats.get('total_chunks', 0)
                st.info(f"🧠 RAG ativo ({chunks} chunks)")
            else:
                st.info("🤖 Modo simples ativo")
    else:
        st.info("Nenhum documento")

def render_debug_chunks():
    """Visualiza os chunks criados (para debug/validação)."""

    if not st.session_state.get('rag_initialized'):
        st.info("RAG não inicializado.")
        return

    chunks = st.session_state.get('rag_chunks', [])
    stats = st.session_state.get('rag_stats', {})

    st.subheader(f"🔍 Validação de Chunks ({len(chunks)})")

    # Estatísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Chunks", stats.get('total_chunks', 0))
    with col2:
        st.metric("Total Chars", f"{stats.get('total_chars', 0):,}")
    with col3:
        st.metric("Média/Chunk", stats.get('media_chars_chunk', 0))

    # Lista de chunks
    st.divider()

    # Filtro por documento
    docs_unicos = list(set(c.documento_origem for c in chunks))
    doc_filtro = st.selectbox(
        "Filtrar por documento",
        options=["Todos"] + docs_unicos,
        key="filtro_doc_chunks"
    )

    # Filtra chunks
    if doc_filtro != "Todos":
        chunks_filtrados = [c for c in chunks if c.documento_origem == doc_filtro]
    else:
        chunks_filtrados = chunks

    st.write(f"Exibindo {len(chunks_filtrados)} chunks")

    # Exibe chunks em expanders
    for chunk in chunks_filtrados[:20]:  # Limita a 20 para performance
        with st.expander(f"Chunk {chunk.indice} - {chunk.documento_origem} ({chunk.total_chars} chars)"):
            st.text(chunk.conteudo)

    if len(chunks_filtrados) > 20:
        st.warning(f"Mostrando apenas 20 de {len(chunks_filtrados)} chunks.")