import React, { useState } from 'react';
import type { StatusEtapa } from '../../types';

interface StatusFilterPanelProps {
  statusSelecionados: StatusEtapa[];
  onAplicar: (status: StatusEtapa[]) => void;
  onFechar: () => void;
}

interface OpcaoStatus {
  label: string;
  valor: StatusEtapa | null;
  dotClass?: string;
}

const opcoes: OpcaoStatus[] = [
  { label: 'Todas', valor: null },
  { label: 'Rascunho', valor: 'Rascunho', dotClass: 'bg-gray-400' },
  { label: 'Etapa 1: Contexto', valor: 'Etapa 1: Contexto', dotClass: 'bg-blue-500' },
  { label: 'Etapa 2: Revisão', valor: 'Etapa 2: Revisão', dotClass: 'bg-purple-500' },
  { label: 'Etapa 3: Metodologia', valor: 'Etapa 3: Metodologia', dotClass: 'bg-amber-500' },
  { label: 'Etapa 4: Escrita', valor: 'Etapa 4: Escrita', dotClass: 'bg-emerald-500' }
];

export const StatusFilterPanel: React.FC<StatusFilterPanelProps> = ({
  statusSelecionados,
  onAplicar,
  onFechar
}) => {
  const [selecionadosLocal, setSelecionadosLocal] = useState<StatusEtapa[]>(statusSelecionados);

  return (
    <div className="absolute top-[calc(100%+6px)] right-0 w-[240px] z-[100] bg-white rounded-[10px] shadow-[0_20px_25px_-5px_rgba(0,43,91,0.06),0_8px_10px_-6px_rgba(0,43,91,0.06)] border border-gray-100 flex flex-col text-left overflow-hidden">
      <div className="px-4 pt-3 pb-2">
        <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
          Filtrar por Status
        </span>
      </div>
      
      <div className="flex flex-col">
        {opcoes.map((opcao) => {
          const isSelected = opcao.valor === null 
            ? selecionadosLocal.length === 0 
            : selecionadosLocal.includes(opcao.valor);
          return (
            <div
              key={opcao.label}
              onClick={() => {
                if (opcao.valor === null) {
                  setSelecionadosLocal([]);
                } else {
                  if (selecionadosLocal.includes(opcao.valor)) {
                    setSelecionadosLocal(selecionadosLocal.filter((s) => s !== opcao.valor));
                  } else {
                    setSelecionadosLocal([...selecionadosLocal, opcao.valor]);
                  }
                }
              }}
              className={`flex items-center gap-3 px-4 py-2 cursor-pointer transition-colors ${
                isSelected ? 'bg-amber-50' : 'hover:bg-gray-50'
              }`}
            >
              {/* Custom Checkbox */}
              {isSelected ? (
                <div className="w-4 h-4 bg-amber-500 rounded flex items-center justify-center flex-shrink-0">
                  <span className="material-symbols-outlined text-white text-[14px] font-bold select-none">
                    check
                  </span>
                </div>
              ) : (
                <div className="w-4 h-4 border border-gray-300 rounded flex-shrink-0" />
              )}

              {/* Dot */}
              {opcao.dotClass && (
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${opcao.dotClass}`} />
              )}

              {/* Label */}
              <span
                className={`text-sm ${
                  isSelected ? 'text-gray-900 font-medium' : 'text-gray-700'
                }`}
              >
                {opcao.label}
              </span>
            </div>
          );
        })}
      </div>

      <div className="h-px bg-gray-100 my-2" />

      <div className="px-4 pb-4 pt-2 flex items-center justify-between">
        <button
          onClick={() => setSelecionadosLocal([])}
          className="text-sm text-gray-500 font-medium hover:text-gray-900 transition-colors"
        >
          Limpar
        </button>
        <button
          onClick={() => {
            onAplicar(selecionadosLocal);
            onFechar();
          }}
          className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold rounded-lg transition-colors"
        >
          Aplicar
        </button>
      </div>
    </div>
  );
};
