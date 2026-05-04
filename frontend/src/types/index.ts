/** 
 * Rótulos de status exibidos nos cards do dashboard 
 */
export type StatusEtapa =
    | 'Rascunho'
    | 'Etapa 1: Contexto'
    | 'Etapa 2: Revisão'
    | 'Etapa 3: Metodologia'
    | 'Etapa 4: Escrita'
    | 'Revisão';

/** 
 * Perfil do usuário autenticado via OAuth Google 
 */
export interface Usuario {
    id: number;
    nome: string;
    email: string;
    fotoPerfil: string | null;
    role: 'pesquisador' | 'admin';
}

/** 
 * Projeto de pesquisa pertencente a um usuário 
 */
export interface Projeto {
    id: number;
    titulo: string;
    etapaAtual: 1 | 2 | 3 | 4 | 5;
    status: StatusEtapa;
    dataCriacao: string;
    dataUltimaModificacao: string | null;
}

// ============================================================
// Tipos Legados V1.0 — mantidos para compatibilidade do store
// e das queries existentes. Serão migrados na V2.0.
// ============================================================

export interface Documento {
    id: string;
    nome: string;
    tipo: string;
    tamanho_bytes?: number;
    tamanho_chars?: number;
    data_upload?: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [key: string]: any;
}

export interface Mensagem {
    role: string;
    content: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [key: string]: any;
}

export interface SessionInfo {
    session_id: string;
    rag_stats?: {
        total_chunks?: number;
        documentos_indexados?: number;
        media_chars_chunk?: number;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        [key: string]: any;
    };
    rag_error?: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [key: string]: any;
}
