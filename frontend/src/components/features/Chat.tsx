import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Avatar, Space, Typography, Card } from 'antd';
import { Send, User, Bot, Sparkles } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { useChat, useSession } from '../../api/queries';
import { ABNTPreview } from '../common/ABNTPreview';
import ReactMarkdown from 'react-markdown';

const { Text } = Typography;

export const AgentChatInterface: React.FC = () => {
    const [input, setInput] = useState('');
    const { mensagens, addMensagem, sessionId, agenteAtivo, setIsLoading, isLoading, isUploading, setAgenteAtivo, setRagStats, setActiveDocId } = useAppStore();
    const chatMutation = useChat();
    const { refetch: refreshSession } = useSession(sessionId || undefined);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [mensagens]);

    const handleSend = async () => {
        if (!input.trim() || !sessionId || isLoading || isUploading) return;

        const userMsg = { role: 'human' as const, content: input };
        addMensagem(userMsg);
        setInput('');
        setIsLoading(true);

        try {
            const response = await chatMutation.mutateAsync({ sessionId, message: input });
            if (!response || !response.body) throw new Error('No stream returned');

            // Captura o agente ativo do header em tempo real
            const agenteHeader = response.headers.get('X-Agent-Active');
            if (agenteHeader) {
                setAgenteAtivo(agenteHeader);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantContent = '';

            addMensagem({ role: 'ai', content: '' }); // Mensagem vazia para iniciar o stream

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                assistantContent += chunk;

                // Atualiza a última mensagem (a que acabamos de criar)
                useAppStore.setState((state) => ({
                    mensagens: [
                        ...state.mensagens.slice(0, -1),
                        { role: 'ai', content: assistantContent }
                    ]
                }));
            }
        } catch (error) {
            console.error('Chat Error:', error);
        } finally {
            setIsLoading(false);
            // Refresh session state to get updated agent and RAG stats
            const { data: updatedSession } = await refreshSession();
            if (updatedSession) {
                setAgenteAtivo(updatedSession.agente_ativo);
                if (updatedSession.active_doc_id) {
                    setActiveDocId(updatedSession.active_doc_id);
                }
                if (updatedSession.rag_stats) {
                    setRagStats(updatedSession.rag_stats);
                }
            }
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-140px)] bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            {/* Messages Area */}
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50/30"
            >
                {mensagens.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full opacity-40">
                        <Sparkles size={48} className="text-primary-400 mb-4" />
                        <Text>Inicie uma conversa ou peça para estruturar seu trabalho.</Text>
                    </div>
                )}

                {mensagens.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex ${msg.role === 'human' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`flex max-w-[85%] ${msg.role === 'human' ? 'flex-row-reverse' : 'flex-row'}`}>
                            <Avatar
                                icon={msg.role === 'human' ? <User size={18} /> : <Bot size={18} />}
                                className={msg.role === 'human' ? 'bg-primary-600 ml-3' : 'bg-gray-800 mr-3'}
                            />
                            <div className="flex flex-col">
                                <Card
                                    className={`shadow-sm border-none ${msg.role === 'human'
                                        ? 'bg-primary-600 text-white rounded-tr-none'
                                        : 'bg-white text-gray-800 rounded-tl-none'
                                        }`}
                                    bodyStyle={{ padding: '12px 16px' }}
                                >
                                    {/* Se a mensagem parecer uma estrutura (heurística simples), renderiza o Preview */}
                                    {msg.role === 'ai' && msg.content.includes('###') ? (
                                        <ABNTPreview content={msg.content} />
                                    ) : (
                                        <div className="whitespace-pre-wrap leading-relaxed markdown-content">
                                            <ReactMarkdown>{msg.content || (isLoading && idx === mensagens.length - 1 ? 'Pensando...' : '')}</ReactMarkdown>
                                        </div>
                                    )}
                                </Card>
                                <Text className="text-[10px] text-gray-400 mt-1 px-2">
                                    {msg.role === 'human' ? 'Você' : `Agente ${agenteAtivo}`}
                                </Text>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-100">
                <Space.Compact className="w-full">
                    <Input
                        size="large"
                        placeholder={isUploading ? 'Aguarde o carregamento dos documentos...' : "Digite sua dúvida ou comando (ex: 'Crie uma introdução sobre IA...')"}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onPressEnter={handleSend}
                        disabled={isLoading || isUploading}
                        className="rounded-l-xl border-gray-200 focus:border-primary-400 shadow-none"
                    />
                    <Button
                        type="primary"
                        size="large"
                        icon={<Send size={18} />}
                        onClick={handleSend}
                        loading={isLoading}
                        disabled={isUploading}
                        className="rounded-r-xl h-[40px] px-6 shadow-md"
                    >
                        Enviar
                    </Button>
                </Space.Compact>
            </div>
        </div>
    );
};
