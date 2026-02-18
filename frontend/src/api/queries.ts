import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import type { SessionInfo } from '../types';

export const useSession = (sessionId?: string) => {
    return useQuery({
        queryKey: ['session', sessionId],
        queryFn: async () => {
            if (!sessionId) {
                const { data } = await apiClient.post<SessionInfo>('/session');
                return data;
            }
            const { data } = await apiClient.get<SessionInfo>(`/session/${sessionId}`);
            return data;
        },
        enabled: true,
    });
};

export const useUploadDocument = () => {
    return useMutation({
        mutationFn: async ({ sessionId, file }: { sessionId: string; file: File }) => {
            const formData = new FormData();
            formData.append('session_id', sessionId);
            formData.append('file', file);
            const { data } = await apiClient.post('/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return data;
        },
    });
};

export const useChat = () => {
    return useMutation({
        mutationFn: async ({ sessionId, message }: { sessionId: string; message: string }) => {
            const response = await fetch(`${apiClient.defaults.baseURL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: sessionId, message }),
            });

            if (!response.ok) throw new Error('Falha na resposta do chat');
            return response; // Retorna o objeto Response completo
        },
    });
};
