import React from 'react';
import type { Projeto } from '../../types';
import { StatusBadge } from './ProjectCard';

interface ProjectTableRowProps {
  projeto: Projeto;
  isAlternate: boolean;
  onClick?: () => void;
}

export const ProjectTableRow: React.FC<ProjectTableRowProps> = ({
  projeto,
  isAlternate,
  onClick
}) => {
  const formataData = (dataStr: string | null) => {
    if (!dataStr) return '';
    try {
      return new Date(dataStr).toLocaleDateString('pt-BR');
    } catch {
      return dataStr;
    }
  };

  const dataExibida = projeto.dataUltimaModificacao || projeto.dataCriacao;

  return (
    <div
      onClick={onClick}
      className={`flex items-center h-[52px] px-6 hover:bg-gray-50 transition-colors cursor-pointer rounded-lg group ${
        isAlternate ? 'bg-[#f7f9fc]' : 'bg-white'
      }`}
    >
      {/* Coluna STATUS */}
      <div className="w-[200px] flex-shrink-0 flex items-center">
        <StatusBadge status={projeto.status} />
      </div>

      {/* Coluna PROJETO */}
      <div className="flex-1 min-w-0 pr-8">
        <h3 className="font-body text-[#111827] text-[0.9rem] font-semibold truncate text-left">
          {projeto.titulo}
        </h3>
      </div>

      {/* Coluna ÚLTIMA ATIVIDADE */}
      <div className="w-[160px] flex-shrink-0 flex justify-end items-center gap-1.5">
        <span className="material-symbols-outlined text-[12px] text-gray-400 select-none">
          schedule
        </span>
        <span className="text-[#9ca3af] text-[0.8rem]">
          {formataData(dataExibida)}
        </span>
      </div>
    </div>
  );
};
