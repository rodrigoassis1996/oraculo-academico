import React from 'react';

interface UserMenuDropdownProps {
  isAdmin: boolean;
  nomeUsuario: string;
  emailUsuario: string;
  onFechar: () => void;
  onLogout?: () => void;
}

export const UserMenuDropdown: React.FC<UserMenuDropdownProps> = ({
  isAdmin,
  nomeUsuario,
  emailUsuario,
  onFechar,
  onLogout
}) => {
  const obterIniciais = (nome: string) => {
    const partes = nome.trim().split(/\s+/);
    if (partes.length === 0 || !partes[0]) return '';
    if (partes.length === 1) return partes[0].substring(0, 2).toUpperCase();
    return (partes[0][0] + (partes[partes.length - 1]?.[0] || '')).toUpperCase();
  };

  return (
    <div className="absolute right-0 top-[calc(100%+8px)] w-64 bg-white rounded-2xl shadow-xl border border-gray-100 z-50 overflow-hidden text-left">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-sm flex-shrink-0 select-none">
          {obterIniciais(nomeUsuario)}
        </div>
        <div className="flex flex-col min-w-0">
          <span className="font-semibold text-sm text-gray-900 truncate">
            {nomeUsuario}
          </span>
          <span className="text-xs text-gray-500 truncate">
            {emailUsuario}
          </span>
        </div>
      </div>

      {/* Ações */}
      <div className="p-2 flex flex-col gap-0.5">
        <div
          onClick={onFechar}
          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
        >
          <span className="text-base select-none" role="img" aria-label="perfil">👤</span>
          <span>Meu Perfil</span>
        </div>
        <div
          onClick={onFechar}
          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
        >
          <span className="text-base select-none" role="img" aria-label="configuracoes">⚙️</span>
          <span>Preferências da Conta</span>
        </div>
      </div>

      {/* Admin Section */}
      {isAdmin && (
        <>
          <div className="border-t border-gray-100 my-1" />
          <div className="px-4 pt-2 pb-1">
            <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
              Administração
            </span>
          </div>
          <div className="p-2 pt-0 flex flex-col gap-0.5">
            <div
              onClick={onFechar}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
            >
              <span className="text-base select-none" role="img" aria-label="ia">🧠</span>
              <span>Motor da IA (Blocos & Pontos)</span>
            </div>
            <div
              onClick={onFechar}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
            >
              <span className="text-base select-none" role="img" aria-label="seguranca">🛡️</span>
              <span>Gestão de Usuários</span>
            </div>
            <div
              onClick={onFechar}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
            >
              <span className="text-base select-none" role="img" aria-label="logs">📊</span>
              <span>Logs do Sistema</span>
            </div>
          </div>
        </>
      )}

      {/* Logout */}
      <div className="border-t border-gray-100 my-1" />
      <div className="p-2 flex flex-col">
        <div
          onClick={() => {
            onLogout?.();
            onFechar();
          }}
          className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg cursor-pointer transition-colors"
        >
          <span className="text-base select-none" role="img" aria-label="sair">🚪</span>
          <span>Sair da conta</span>
        </div>
      </div>
    </div>
  );
};
