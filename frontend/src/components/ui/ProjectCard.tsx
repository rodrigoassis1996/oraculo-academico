import React from 'react';
import type { Projeto, StatusEtapa } from '../../types';

export const StatusBadge: React.FC<{ status: StatusEtapa }> = ({ status }) => {
    let bgClass = '';
    let textClass = '';
    let dotClass = '';

    switch (status) {
        case 'Rascunho':
            bgClass = 'bg-gray-100';
            textClass = 'text-gray-600';
            dotClass = 'bg-gray-400';
            break;
        case 'Etapa 1: Contexto':
            bgClass = 'bg-blue-50';
            textClass = 'text-blue-700';
            dotClass = 'bg-blue-500';
            break;
        case 'Etapa 2: Revisão':
            bgClass = 'bg-purple-50';
            textClass = 'text-purple-700';
            dotClass = 'bg-purple-500';
            break;
        case 'Etapa 3: Metodologia':
            bgClass = 'bg-amber-50';
            textClass = 'text-amber-700';
            dotClass = 'bg-amber-500';
            break;
        case 'Etapa 4: Escrita':
            bgClass = 'bg-emerald-50';
            textClass = 'text-emerald-700';
            dotClass = 'bg-emerald-500';
            break;
        case 'Revisão':
            bgClass = 'bg-blue-50';
            textClass = 'text-blue-700';
            dotClass = 'bg-blue-500';
            break;
        default:
            bgClass = 'bg-gray-100';
            textClass = 'text-gray-600';
            dotClass = 'bg-gray-400';
    }

    return (
        <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full ${bgClass} ${textClass} text-xs font-medium mb-4`}>
            <span className={`w-1.5 h-1.5 rounded-full ${dotClass}`}></span>
            [{status}]
        </div>
    );
};

export interface ProjectCardProps {
    projeto: Projeto;
    onClick?: () => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ projeto, onClick }) => {
    const formataData = (dataStr: string) => {
        try {
            return new Date(dataStr).toLocaleDateString('pt-BR');
        } catch {
            return dataStr;
        }
    };

    return (
        <div
            onClick={onClick}
            className="group bg-white rounded-xl p-6 flex flex-col justify-between h-64 shadow-[0_4px_12px_rgba(0,0,0,0.03)] border border-gray-100 hover:shadow-[0_8px_24px_rgba(0,0,0,0.08)] hover:-translate-y-1 transition-all duration-300 cursor-pointer"
        >
            <div>
                <StatusBadge status={projeto.status} />
                <h3 className="font-display text-xl font-bold text-gray-900 leading-tight line-clamp-3">
                    {projeto.titulo}
                </h3>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-50 flex justify-between items-center text-sm text-gray-500">
                <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[18px]">schedule</span>
                    {formataData(projeto.dataCriacao)}
                </div>
            </div>
        </div>
    );
};
