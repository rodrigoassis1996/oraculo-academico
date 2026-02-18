import React from 'react';
import { Button, message, Badge, Upload } from 'antd';
import {
    Plus,
    Trash2,
    Globe,
    FileCode,
    Files,
    FileText,
    Cpu
} from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { useUploadDocument } from '../../api/queries';

export const Sidebar: React.FC = () => {
    const { documentos, sessionId, removeDocumento, addDocumento, ragStats, setRagStats, incrementUpload, decrementUpload } = useAppStore();
    const uploadMutation = useUploadDocument();

    const handleUpload = async (options: any) => {
        const { file, onSuccess, onError } = options;
        if (!sessionId) return;

        const hide = message.loading(`Enviando ${file.name}...`, 0);
        incrementUpload();

        try {
            const result = await uploadMutation.mutateAsync({ sessionId, file: file as File });
            if (result.rag_stats) {
                setRagStats(result.rag_stats);
            }
            addDocumento({
                id: Math.random().toString(36),
                nome: file.name,
                tipo: 'PDF',
                tamanho_bytes: file.size,
                tamanho_chars: 0,
                data_upload: new Date().toISOString()
            });
            hide();
            if (result.rag_error) {
                message.warning(`Documento salvo, mas erro ao indexar: ${result.rag_error}`);
            } else {
                message.success(`${file.name} carregado com sucesso.`);
            }
            onSuccess(result);
        } catch (err) {
            hide();
            message.error(`Falha ao carregar ${file.name}.`);
            onError(err);
        } finally {
            decrementUpload();
        }
    };

    const getIcon = (tipo: string) => {
        switch (tipo) {
            case 'SITE': return <Globe size={16} />;
            case 'DOCX': return <FileCode size={16} />;
            default: return <FileText size={16} />;
        }
    };

    return (
        <aside
            className="w-[280px] bg-white border-r border-slate-200 fixed left-0 top-16 bottom-0 z-[900] flex flex-col pt-4"
        >
            <div className="px-6 pb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Files size={18} className="text-primary-600" />
                    <span className="font-bold text-slate-800 text-sm">Corpus Acadêmico</span>
                </div>
                <Badge
                    count={documentos.length}
                    showZero
                    color="#0284c7"
                    className="scale-90"
                />
            </div>

            <div className="flex-1 overflow-y-auto px-3">
                {documentos.length === 0 ? (
                    <div className="mx-3 mt-4 text-center py-12 px-4 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                        <FileText size={32} className="mx-auto text-slate-300 mb-3" />
                        <p className="text-xs text-slate-400 font-medium leading-relaxed">
                            Seu corpus está vazio.<br />Faça o upload de PDFs para começar.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-1">
                        {documentos.map(doc => (
                            <div
                                key={doc.id}
                                className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 group cursor-pointer transition-colors"
                            >
                                <div className="flex items-center gap-3 min-w-0">
                                    <div className="text-slate-400 group-hover:text-primary-600 transition-colors">
                                        {getIcon(doc.tipo)}
                                    </div>
                                    <span className="text-xs font-medium text-slate-600 truncate group-hover:text-slate-900 transition-colors">
                                        {doc.nome}
                                    </span>
                                </div>
                                <Button
                                    type="text"
                                    size="small"
                                    icon={<Trash2 size={14} />}
                                    danger
                                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        removeDocumento(doc.id);
                                    }}
                                />
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {ragStats && (
                <div className="px-3 pb-4">
                    <div className="bg-slate-900 rounded-2xl p-4 shadow-xl border border-slate-800">
                        <div className="flex items-center gap-2 mb-3">
                            <Cpu size={14} className="text-primary-400" />
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Status da Memória RAG</span>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="flex flex-col">
                                <span className="text-white text-lg font-mono font-bold leading-none">
                                    {ragStats.total_chunks ?? 0}
                                </span>
                                <span className="text-[9px] text-slate-500 font-bold uppercase mt-1">Chunks</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-white text-lg font-mono font-bold leading-none">
                                    {ragStats.documentos_indexados ?? 0}
                                </span>
                                <span className="text-[9px] text-slate-500 font-bold uppercase mt-1">Docs</span>
                            </div>
                            <div className="flex flex-col col-span-2 pt-2 border-t border-slate-800">
                                <div className="flex items-center justify-between">
                                    <span className="text-[9px] text-slate-500 font-bold uppercase">Média Chars/Chunk</span>
                                    <span className="text-primary-400 text-[10px] font-mono font-bold">
                                        {Math.round(ragStats.media_chars_chunk ?? 0)}
                                    </span>
                                </div>
                                <div className="w-full bg-slate-800 h-1 rounded-full mt-1 overflow-hidden">
                                    <div
                                        className="bg-primary-500 h-full transition-all duration-1000"
                                        style={{ width: `${Math.min(((ragStats.media_chars_chunk ?? 0) / 1500) * 100, 100)}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <div className="p-6 bg-slate-50/50 border-t border-slate-100 mt-auto">
                <Upload
                    customRequest={handleUpload}
                    showUploadList={false}
                    disabled={uploadMutation.isPending}
                    multiple
                >
                    <Button
                        type="primary"
                        icon={<Plus size={16} />}
                        block
                        className="h-10 font-bold rounded-xl shadow-lg shadow-primary-600/20"
                        loading={uploadMutation.isPending}
                    >
                        {uploadMutation.isPending ? 'Enviando...' : 'Adicionar Documento'}
                    </Button>
                </Upload>
            </div>
        </aside>
    );
};
