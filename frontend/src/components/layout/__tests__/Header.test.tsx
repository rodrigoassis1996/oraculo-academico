import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Header } from '../Header';
import { useAppStore } from '../../../store/useAppStore';

// Mock do store para controlar o estado durante os testes
vi.mock('../../../store/useAppStore', () => ({
    useAppStore: vi.fn(),
}));

describe('Header Component', () => {
    it('deve renderizar o título do projeto', () => {
        (useAppStore as any).mockReturnValue({
            agenteAtivo: 'ORCHESTRATOR',
            sessionId: 'test-session',
        });

        render(<Header />);
        expect(screen.getByText('Oráculo Acadêmico')).toBeDefined();
    });

    it('deve exibir o agente ativo correto', () => {
        (useAppStore as any).mockReturnValue({
            agenteAtivo: 'ESTRUTURADOR',
            sessionId: 'test-session',
        });

        render(<Header />);
        expect(screen.getByText('ESTRUTURADOR')).toBeDefined();
    });
});
