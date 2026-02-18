import { create } from 'zustand';
import type { Documento, Mensagem, SessionInfo } from '../types';

interface AppState {
    sessionId: string | null;
    documentos: Documento[];
    mensagens: Mensagem[];
    agenteAtivo: string;
    activeDocId: string | null;
    ragStats: SessionInfo['rag_stats'] | null;
    isLoading: boolean;
    uploadCount: number;
    isUploading: boolean;

    // Actions
    setSessionId: (id: string) => void;
    setDocumentos: (docs: Documento[]) => void;
    addDocumento: (doc: Documento) => void;
    removeDocumento: (docId: string) => void;
    setMensagens: (messages: Mensagem[]) => void;
    addMensagem: (message: Mensagem) => void;
    setAgenteAtivo: (agente: string) => void;
    setActiveDocId: (id: string | null) => void;
    setRagStats: (stats: SessionInfo['rag_stats'] | null) => void;
    setIsLoading: (loading: boolean) => void;
    incrementUpload: () => void;
    decrementUpload: () => void;
    reset: () => void;
}

export const useAppStore = create<AppState>((set) => ({
    sessionId: null,
    documentos: [],
    mensagens: [],
    agenteAtivo: 'ORCHESTRATOR',
    activeDocId: null,
    ragStats: null,
    isLoading: false,
    uploadCount: 0,
    isUploading: false,

    setSessionId: (id) => set({ sessionId: id }),
    setDocumentos: (docs) => set({ documentos: docs }),
    addDocumento: (doc) => set((state) => ({ documentos: [...state.documentos, doc] })),
    removeDocumento: (docId) => set((state) => ({
        documentos: state.documentos.filter((d) => d.id !== docId)
    })),
    setMensagens: (messages) => set({ mensagens: messages }),
    addMensagem: (message) => set((state) => ({ mensagens: [...state.mensagens, message] })),
    setAgenteAtivo: (agente) => set({ agenteAtivo: agente }),
    setActiveDocId: (id) => set({ activeDocId: id }),
    setRagStats: (stats) => set({ ragStats: stats }),
    setIsLoading: (loading) => set({ isLoading: loading }),
    incrementUpload: () => set((state) => ({ uploadCount: state.uploadCount + 1, isUploading: true })),
    decrementUpload: () => set((state) => {
        const newCount = Math.max(0, state.uploadCount - 1);
        return { uploadCount: newCount, isUploading: newCount > 0 };
    }),

    reset: () => set({
        sessionId: null,
        documentos: [],
        mensagens: [],
        agenteAtivo: 'ORCHESTRATOR',
        activeDocId: null,
        ragStats: null,
        isLoading: false,
        uploadCount: 0,
        isUploading: false,
    }),
}));
