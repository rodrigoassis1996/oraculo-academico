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
            sessionId: 'test-session',
            activeDocId: null,
        });

        render(<Header />);
        expect(screen.getByText('Oráculo Acadêmico')).toBeDefined();
    });

    it('deve exibir o ID da sessão', () => {
        (useAppStore as any).mockReturnValue({
            sessionId: 'abcd1234-efgh-5678',
            activeDocId: null,
        });

        render(<Header />);
        expect(screen.getByText('abcd1234')).toBeDefined();
    });
});
