import React from 'react';

import { GraduationCap, ExternalLink } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export const Header: React.FC = () => {
    const { sessionId, activeDocId } = useAppStore();

    return (
        <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 px-6 flex items-center justify-between fixed top-0 left-0 right-0 z-[1000] h-16">
            <div className="flex items-center gap-3">
                <div className="bg-primary-600 p-2 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/20">
                    <GraduationCap className="text-white" size={24} />
                </div>
                <div className="flex flex-col">
                    <h1 className="text-lg font-bold text-slate-900 leading-tight">
                        Oráculo Acadêmico
                    </h1>
                    <span className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">
                        Assistente Especialista em Pesquisa
                    </span>
                </div>
            </div>

            <div className="flex items-center gap-6">
                {activeDocId && (
                    <a
                        href={`https://docs.google.com/document/d/${activeDocId}/edit`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 bg-blue-50 text-blue-600 px-4 py-2 rounded-xl border border-blue-100 font-bold text-sm hover:bg-blue-100 transition-colors shadow-sm"
                    >
                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                        <ExternalLink size={16} />
                        GOOGLE DOC ATIVO
                    </a>
                )}


                <div className="flex flex-col items-end">
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">
                        Sessão
                    </span>
                    <span className="text-xs font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                        {sessionId?.slice(0, 8) || '0cd9a26b'}
                    </span>
                </div>
            </div>
        </header>
    );
};
