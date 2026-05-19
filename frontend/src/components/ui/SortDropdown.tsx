import React from 'react';
import type { OrdemOpcao } from '../../types';

interface SortDropdownProps {
  valorAtual: OrdemOpcao;
  onSelecionar: (opcao: OrdemOpcao) => void;
  onFechar: () => void;
}

interface OpcaoOrdenacao {
  valor: OrdemOpcao;
  label: string;
  icone: string;
}

const opcoes: OpcaoOrdenacao[] = [
  { valor: 'recentes', label: 'Mais recentes', icone: 'arrow_downward' },
  { valor: 'antigos', label: 'Mais antigos', icone: 'arrow_upward' },
  { valor: 'nome-az', label: 'Nome (A → Z)', icone: 'sort_by_alpha' },
  { valor: 'nome-za', label: 'Nome (Z → A)', icone: 'sort_by_alpha' },
  { valor: 'etapa', label: 'Etapa atual', icone: 'account_tree' }
];

export const SortDropdown: React.FC<SortDropdownProps> = ({
  valorAtual,
  onSelecionar,
  onFechar
}) => {
  return (
    <div className="absolute top-[calc(100%+6px)] left-0 w-[220px] z-[100] bg-white rounded-[10px] shadow-[0_20px_25px_-5px_rgba(0,43,91,0.06),0_8px_10px_-6px_rgba(0,43,91,0.06)] border border-gray-100 py-1 flex flex-col text-left overflow-hidden">
      <div className="px-4 pt-3 pb-2">
        <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">
          Ordenar Por
        </span>
      </div>

      <div className="flex flex-col">
        {opcoes.map((opcao) => {
          const isSelected = valorAtual === opcao.valor;
          return (
            <div
              key={opcao.valor}
              onClick={() => {
                onSelecionar(opcao.valor);
                onFechar();
              }}
              className={`flex items-center justify-between px-4 py-2 cursor-pointer transition-colors ${
                isSelected ? 'bg-amber-50' : 'hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-3">
                {/* Custom Radio Button */}
                {isSelected ? (
                  <div className="w-4 h-4 rounded-full border-2 border-amber-500 flex items-center justify-center flex-shrink-0">
                    <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                  </div>
                ) : (
                  <div className="w-4 h-4 rounded-full border-2 border-gray-300 flex-shrink-0" />
                )}

                <span
                  className={`text-sm ${
                    isSelected ? 'text-gray-900 font-medium' : 'text-gray-700'
                  }`}
                >
                  {opcao.label}
                </span>
              </div>

              {/* Icon */}
              <span
                className={`material-symbols-outlined text-[18px] select-none ${
                  isSelected ? 'text-amber-500' : 'text-gray-400'
                }`}
              >
                {opcao.icone}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
