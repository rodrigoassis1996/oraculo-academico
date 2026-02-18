import os
import uuid
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from services.upload_manager import UploadManager, DocumentoCarregado
from services.model_manager import ModelManager
from config.settings import TipoArquivo

app = FastAPI(title="Oráculo Acadêmico API", version="1.0.0")

# Configurar CORS para o frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir ao domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Agent-Active"],
)

# Gerenciador de Sessões (Em memória para este exemplo/MVP)
# Em produção, usar Redis ou Banco de Dados
sessions: Dict[str, Dict[str, Any]] = {}

def get_session(session_id: str):
    if session_id not in sessions:
        # Inicializa estado da sessão
        state = {
            'mensagens': [],
            'documentos': [],
            'chain': None,
            'llm': None,
            'usar_rag': True,
            'agente_ativo': 'ORCHESTRATOR',
            'active_doc_id': None
        }
        sessions[session_id] = state
    return sessions[session_id]

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    message: str
    agent: str
    active_doc_id: Optional[str] = None

class SessionInfo(BaseModel):
    session_id: str
    total_docs: int
    agente_ativo: str
    active_doc_id: Optional[str] = None
    rag_stats: Optional[Dict[str, Any]] = None

@app.post("/api/v1/session", response_model=SessionInfo)
async def create_session():
    session_id = str(uuid.uuid4())
    state = get_session(session_id)
    return SessionInfo(
        session_id=session_id,
        total_docs=0,
        agente_ativo=state['agente_ativo']
    )

@app.get("/api/v1/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    state = get_session(session_id)
    return SessionInfo(
        session_id=session_id,
        total_docs=len(state['documentos']),
        agente_ativo=state['agente_ativo'],
        active_doc_id=state.get('active_doc_id'),
        rag_stats=state.get('rag_stats')
    )

@app.post("/api/v1/upload")
async def upload_document(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    state = get_session(session_id)
    up_manager = UploadManager(external_state=state['documentos'])
    
    content = await file.read()
    tipo = up_manager.detectar_tipo_arquivo(file.filename)
    if not tipo:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado.")
    
    success, message = up_manager.carregar_documento_de_dados(tipo, content, file.filename)
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    # Se documentos carregados, inicializamos a chain RAG no ModelManager
    mm = ModelManager(session_state=state)
    rag_stats = None
    rag_error = None
    try:
        rag_stats = mm.criar_chain_rag(state['documentos'])
    except Exception as e:
        error_msg = str(e)
        # Verifica se é erro de corrupção do Vector DB (HNSW/Compaction)
        if "hnsw" in error_msg.lower() or "compaction" in error_msg.lower() or "segment reader" in error_msg.lower():
            print(f"⚠️ Corrupção detectada no ChromaDB: {error_msg}")
            print("♻️  Iniciando protocolo de auto-recuperação (Purge & Retry)...")
            try:
                # Tenta limpar tudo e reindexar
                mm.rag_manager.purgar_fisicamente()
                rag_stats = mm.criar_chain_rag(state['documentos'])
                print("✅ Auto-recuperação concluída com sucesso!")
                rag_error = None
            except Exception as retry_e:
                print(f"❌ Falha na auto-recuperação: {retry_e}")
                rag_error = f"Erro crítico no banco de dados. Por favor, reinicie a aplicação. Detalhes: {retry_e}"
        else:
            print(f"Erro ao criar chain RAG: {error_msg}")
            rag_error = error_msg

    return {
        "success": True, 
        "message": message, 
        "total_docs": len(state['documentos']),
        "rag_stats": rag_stats,
        "rag_error": rag_error
    }

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    state = get_session(request.session_id)
    mm = ModelManager(session_state=state)
    
    if not state.get('llm'):
        # LLM não está pronto. Tenta re-inicializar se houver documentos no estado.
        if state['documentos']:
            try:
                mm.criar_chain_rag(state['documentos'])
            except Exception as e:
                print(f"[API] Erro ao criar chain RAG sob demanda: {e}")
                return StreamingResponse(
                    iter(["⏳ Os documentos ainda estão sendo processados. Aguarde a conclusão do carregamento e tente novamente."]),
                    media_type="text/plain",
                    headers={"X-Agent-Active": "ORCHESTRATOR"}
                )
        else:
            return StreamingResponse(
                iter(["⚠️ Nenhum documento carregado ainda. Por favor, faça o upload de documentos primeiro."]),
                media_type="text/plain",
                headers={"X-Agent-Active": "ORCHESTRATOR"}
            )

    mm.adicionar_mensagem("human", request.message)
    
    # Classifica o agente antes de iniciar o stream para que o frontend saiba quem responde em tempo real
    try:
        mm.orchestrator.classificar_e_atualizar_estado(request.message)
    except Exception as e:
        print(f"[API] Erro na classificação pré-stream: {e}")
    
    agente_ativo = state.get('agente_ativo', 'ORCHESTRATOR')

    def stream_response():
        full_reply = ""
        try:
            for chunk in mm.gerar_resposta_rag(request.message):
                full_reply += chunk
                yield chunk
            mm.adicionar_mensagem("ai", full_reply)
        except Exception as e:
            error_msg = f"\n\n⚠️ Ocorreu um erro durante a geração da resposta: {str(e)}"
            print(f"[API] Erro no stream: {e}")
            yield error_msg

    return StreamingResponse(
        stream_response(), 
        media_type="text/plain",
        headers={"X-Agent-Active": agente_ativo}
    )

@app.post("/api/v1/clear")
async def clear_session(session_id: str):
    if session_id in sessions:
        state = sessions[session_id]
        mm = ModelManager(session_state=state)
        mm.reset_completo()
        return {"success": True}
    return {"success": False, "detail": "Sessão não encontrada"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
