import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AgentChatInterface } from './Chat';
import { useAppStore } from '../../store/useAppStore';
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mock do Store do Zustand
vi.mock('../../store/useAppStore', () => ({
    useAppStore: Object.assign(vi.fn(), {
        getState: vi.fn(),
        setState: vi.fn(),
        subscribe: vi.fn(),
    }),
}));

// Mock das queries e mutações de API
vi.mock('../../api/queries', () => ({
    useChat: vi.fn(() => ({
        mutateAsync: vi.fn(() => Promise.resolve({
            body: {
                getReader: () => ({
                    read: vi.fn()
                        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode("Olá, como posso ajudar?") })
                        .mockResolvedValueOnce({ done: true })
                })
            },
            headers: {
                get: (header: string) => header === 'X-Agent-Active' ? 'ESTRUTURADOR' : null
            }
        }))
    })),
    useSession: vi.fn(() => ({
        refetch: vi.fn(() => Promise.resolve({ data: { agente_ativo: 'ESTRUTURADOR' } }))
    }))
}));

describe('Fluxo de Chat do Agente', () => {
    beforeEach(() => {
        // Reset do Store para cada teste
        (useAppStore as any).mockReturnValue({
            mensagens: [],
            addMensagem: vi.fn(),
            sessionId: 'test-session',
            agente_ativo: 'QA',
            setIsLoading: vi.fn(),
            isLoading: false,
            isUploading: false,
            setAgenteAtivo: vi.fn(),
            setRagStats: vi.fn(),
            setActiveDocId: vi.fn()
        });
    });

    it('deve enviar uma mensagem e processar a resposta do agente', async () => {
        const store = useAppStore();

        render(<AgentChatInterface />);

        const input = screen.getByPlaceholderText(/Digite sua dúvida/i);
        const button = screen.getByRole('button', { name: /Enviar/i });

        // Simula digitação e clique
        fireEvent.change(input, { target: { value: 'Olá Oráculo' } });
        fireEvent.click(button);

        // Verifica se a mensagem foi adicionada ao store
        expect(store.addMensagem).toHaveBeenCalledWith({ role: 'human', content: 'Olá Oráculo' });

        // Verifica se o estado de carregamento foi ativado
        expect(store.setIsLoading).toHaveBeenCalledWith(true);

        // Aguarda a resposta aparecer (aqui precisaríamos de um mock mais detalhado do store para o .getState)
        await waitFor(() => {
            expect(store.setIsLoading).toHaveBeenLastCalledWith(false);
        });
    });
});
