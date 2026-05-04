import React, { useState } from 'react';
import { AppSidebar } from '../../components/layout/AppSidebar';
import { ProjectCard } from '../../components/ui/ProjectCard';
import type { Projeto } from '../../types';

const mockProjetos: Projeto[] = [
    {
        id: 1,
        titulo: 'Análise de Redes Neurais Convolucionais em Imagens Médicas',
        etapaAtual: 1,
        status: 'Etapa 1: Contexto',
        dataCriacao: '2024-03-15T10:00:00Z',
        dataUltimaModificacao: '2024-03-20T15:30:00Z'
    },
    {
        id: 2,
        titulo: 'Impacto da LGPD no Tratamento de Dados Acadêmicos',
        etapaAtual: 2,
        status: 'Etapa 2: Revisão',
        dataCriacao: '2024-02-10T09:00:00Z',
        dataUltimaModificacao: '2024-02-25T11:20:00Z'
    },
    {
        id: 3,
        titulo: 'Sustentabilidade Urbana e Mobilidade Elétrica',
        etapaAtual: 4,
        status: 'Etapa 4: Escrita',
        dataCriacao: '2024-01-05T14:00:00Z',
        dataUltimaModificacao: '2024-03-01T16:45:00Z'
    }
];

const DashboardPage: React.FC = () => {
    const [filtro, setFiltro] = useState<'Todos' | 'Em andamento' | 'Finalizados'>('Todos');
    const [search, setSearch] = useState('');

    const projetosFiltrados = mockProjetos.filter(p => {
        const matchesSearch = p.titulo.toLowerCase().includes(search.toLowerCase());
        if (filtro === 'Todos') return matchesSearch;
        if (filtro === 'Em andamento') return matchesSearch && p.status !== 'Rascunho'; // Exemplo
        return matchesSearch;
    });

    return (
        <div className="flex min-h-screen academic-gradient">
            <AppSidebar activeRoute="projetos" />
            
            <main className="flex-1 md:ml-64 min-h-screen flex flex-col">
                {/* Topbar */}
                <header className="h-20 bg-white/80 backdrop-blur-md border-b border-gray-100 flex items-center justify-between px-8 sticky top-0 z-30">
                    <div className="flex items-center gap-4">
                        <span className="text-gray-900 font-bold text-lg font-display">Olá, Pesquisador</span>
                    </div>
                    
                    <div className="flex items-center gap-6">
                        <div className="hidden lg:flex items-center bg-gray-50 border border-gray-100 rounded-xl px-4 py-2 w-96 group focus-within:bg-white focus-within:ring-2 focus-within:ring-primary-fixed/20 transition-all">
                            <span className="material-symbols-outlined text-gray-400 text-lg">search</span>
                            <input 
                                type="text" 
                                placeholder="Buscar projetos..." 
                                className="bg-transparent border-none focus:ring-0 text-sm ml-2 w-full text-gray-600 placeholder:text-gray-400"
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                            />
                        </div>
                        
                        <div className="flex items-center gap-3">
                            <button className="w-10 h-10 flex items-center justify-center rounded-xl text-gray-500 hover:bg-gray-50 transition-colors relative">
                                <span className="material-symbols-outlined">notifications</span>
                                <span className="absolute top-2 right-2 w-2 h-2 bg-secondary rounded-full border-2 border-white"></span>
                            </button>
                            <div className="w-10 h-10 rounded-xl bg-primary-container flex items-center justify-center text-primary-fixed-dim font-bold">
                                P
                            </div>
                        </div>
                    </div>
                </header>

                {/* Content Area */}
                <div className="p-8 max-w-7xl mx-auto w-full space-y-8">
                    {/* Page Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 font-display tracking-tight">Meus Projetos</h1>
                            <p className="text-gray-500 mt-1">Gerencie e acompanhe o progresso de suas pesquisas acadêmicas.</p>
                        </div>
                        <button className="flex items-center justify-center gap-2 bg-primary-fixed-dim text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-primary-fixed/20 transition-all active:scale-95">
                            <span className="material-symbols-outlined">add</span>
                            Novo Projeto
                        </button>
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex border-b border-gray-200">
                        {(['Todos', 'Em andamento', 'Finalizados'] as const).map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setFiltro(tab)}
                                className={`px-6 py-4 text-sm font-semibold transition-all relative ${
                                    filtro === tab ? 'text-primary-fixed-dim' : 'text-gray-500 hover:text-gray-700'
                                }`}
                            >
                                {tab}
                                {filtro === tab && (
                                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-fixed-dim"></div>
                                )}
                            </button>
                        ))}
                    </div>

                    {/* Project Grid */}
                    {projetosFiltrados.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                            {projetosFiltrados.map((projeto) => (
                                <ProjectCard key={projeto.id} projeto={projeto} onClick={() => console.log('Click projeto:', projeto.id)} />
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
                            <div className="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center text-gray-300">
                                <span className="material-symbols-outlined text-4xl">folder_off</span>
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-gray-900">Nenhum projeto encontrado</h3>
                                <p className="text-gray-500 max-w-xs mx-auto">Tente ajustar seus filtros ou inicie um novo projeto agora mesmo.</p>
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default DashboardPage;
