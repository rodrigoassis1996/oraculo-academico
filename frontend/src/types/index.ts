export type TipoArquivo = 'PDF' | 'DOCX' | 'CSV' | 'TXT' | 'SITE';

export type Documento = {
    id: string;
    nome: string;
    tipo: TipoArquivo;
    tamanho_bytes: number;
    tamanho_chars: number;
    data_upload: string;
};

export type Mensagem = {
    role: 'human' | 'ai';
    content: string;
};

export type SessionInfo = {
    session_id: string;
    total_docs: number;
    agente_ativo: string;
    active_doc_id?: string;
    rag_stats?: {
        total_chunks: number;
        total_chars: number;
        media_chars_chunk: number;
        documentos_indexados: number;
        documentos_pulpados?: number;
    };
};

export const VERSION = '1.0.0';
