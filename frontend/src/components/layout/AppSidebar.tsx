import React from 'react';

export interface AppSidebarProps {
    activeRoute: string;
}

export const AppSidebar: React.FC<AppSidebarProps> = ({ activeRoute }) => {
    const navItems = [
        { id: 'projetos', label: 'Projetos', icon: 'dashboard' },
        { id: 'pesquisas', label: 'Pesquisas', icon: 'science' },
        { id: 'biblioteca', label: 'Biblioteca', icon: 'local_library' },
        { id: 'configuracoes', label: 'Configurações', icon: 'settings' },
    ];

    return (
        <nav className="hidden md:flex flex-col bg-white border-r border-gray-200 h-screen w-64 fixed left-0 top-0 pt-24 pb-8 z-40">
            <div className="px-6 mb-8">
                <span className="font-display font-bold text-xl text-primary-fixed-dim tracking-tight">Oráculo Acadêmico</span>
            </div>
            <div className="flex-1 px-4 space-y-2">
                {navItems.map((item) => {
                    const isActive = activeRoute === item.id;
                    return (
                        <a
                            key={item.id}
                            href={`/${item.id}`}
                            className={`flex items-center gap-3 px-4 py-3 font-semibold text-sm transition-all ${
                                isActive
                                    ? 'text-gray-900 bg-amber-50/50 border-l-4 border-primary-fixed-dim rounded-r-xl'
                                    : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50 rounded-xl'
                            }`}
                        >
                            <span
                                className="material-symbols-outlined"
                                style={isActive ? { fontVariationSettings: "'FILL' 1" } : {}}
                            >
                                {item.icon}
                            </span>
                            {item.label}
                        </a>
                    );
                })}
            </div>
            <div className="px-4 mt-auto">
                <a className="flex items-center gap-3 px-4 py-3 text-gray-500 hover:text-gray-900 hover:bg-gray-50 rounded-xl transition-all duration-300 font-medium text-sm" href="/suporte">
                    <span className="material-symbols-outlined">help_outline</span>
                    Suporte
                </a>
            </div>
        </nav>
    );
};
