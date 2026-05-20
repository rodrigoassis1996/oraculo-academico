import { create } from 'zustand';
import apiClient from '../lib/apiClient';

interface Usuario {
  id: number;
  nome: string;
  email: string;
  fotoPerfil: string | null;
  role: string;
}

interface AuthState {
  usuario: Usuario | null;
  isAuthenticated: boolean;
  isChecking: boolean;
  verificarAutenticacao: () => Promise<void>;
  iniciarLoginGoogle: () => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  usuario: null,
  isAuthenticated: false,
  isChecking: true,

  verificarAutenticacao: async () => {
    set({ isChecking: true });
    try {
      const response = await apiClient.get<Usuario>('/api/v2/auth/me');
      set({ usuario: response.data, isAuthenticated: true, isChecking: false });
    } catch {
      set({ usuario: null, isAuthenticated: false, isChecking: false });
    }
  },

  iniciarLoginGoogle: async () => {
    try {
      const response = await apiClient.get<{ url: string }>('/api/v2/auth/google/url');
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Erro ao obter URL de autenticação do Google:', error);
    }
  },

  logout: async () => {
    try {
      await apiClient.post('/api/v2/auth/logout');
    } catch (error) {
      console.error('Erro ao realizar logout:', error);
    } finally {
      set({ usuario: null, isAuthenticated: false });
    }
  },
}));
