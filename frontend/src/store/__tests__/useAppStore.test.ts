import { describe, it, expect, beforeEach } from 'vitest';
import { useAppStore } from '../useAppStore';

describe('useAppStore', () => {
    beforeEach(() => {
        useAppStore.getState().reset();
    });

    it('deve inicializar com o estado padrão', () => {
        const state = useAppStore.getState();
        expect(state.sessionId).toBeNull();
        expect(state.documentos).toEqual([]);
        expect(state.mensagens).toEqual([]);
        expect(state.agenteAtivo).toBe('ORCHESTRATOR');
    });

    it('deve adicionar um documento corretamente', () => {
        const doc = {
            id: '1',
            nome: 'Teste.pdf',
            tipo: 'PDF' as const,
            tamanho_bytes: 100,
            tamanho_chars: 1000,
            data_upload: new Date().toISOString(),
        };

        useAppStore.getState().addDocumento(doc);
        expect(useAppStore.getState().documentos).toHaveLength(1);
        expect(useAppStore.getState().documentos[0].nome).toBe('Teste.pdf');
    });

    it('deve adicionar uma mensagem corretamente', () => {
        const msg = { role: 'human' as const, content: 'Olá' };
        useAppStore.getState().addMensagem(msg);
        expect(useAppStore.getState().mensagens).toHaveLength(1);
        expect(useAppStore.getState().mensagens[0].content).toBe('Olá');
    });
});
