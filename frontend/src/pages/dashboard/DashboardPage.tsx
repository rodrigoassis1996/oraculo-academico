import React, { useState, useEffect } from 'react';
import { AppSidebar } from '../../components/layout/AppSidebar';
import { ProjectCard } from '../../components/ui/ProjectCard';
import type { Projeto, StatusEtapa } from '../../types';

type DashboardEstado = 'populado' | 'vazio' | 'filtrado' | 'erro' | 'skeleton';
type ModalEstado = 'novo-projeto' | 'sucesso' | 'erro-modal' | null;
type FiltroStatus = StatusEtapa | null;

const mockProjetos: Projeto[] = [
    {
        id: 1, titulo: 'Conflitos Socioambientais em Terras Indígenas',
        etapaAtual: 1, status: 'Etapa 1: Contexto',
        dataCriacao: '2024-03-20T08:00:00Z', dataUltimaModificacao: null
    },
    {
        id: 2, titulo: 'Impacto da IA na Educação Superior',
        etapaAtual: 3, status: 'Etapa 3: Metodologia',
        dataCriacao: '2024-03-19T10:00:00Z', dataUltimaModificacao: null
    },
    {
        id: 3, titulo: 'Análise Comparativa de Algoritmos RAG',
        etapaAtual: 1, status: 'Rascunho',
        dataCriacao: '2023-10-12T00:00:00Z', dataUltimaModificacao: null
    },
    {
        id: 4, titulo: 'Governança Digital em Municípios',
        etapaAtual: 2, status: 'Etapa 2: Revisão',
        dataCriacao: '2024-03-19T00:00:00Z', dataUltimaModificacao: null
    },
    {
        id: 5, titulo: 'Impacto da LGPD na Pesquisa Científica',
        etapaAtual: 4, status: 'Etapa 4: Escrita',
        dataCriacao: '2024-03-17T00:00:00Z', dataUltimaModificacao: null
    },
    {
        id: 6, titulo: 'Inteligência Artificial e Ética Profissional',
        etapaAtual: 1, status: 'Rascunho',
        dataCriacao: '2023-10-05T00:00:00Z', dataUltimaModificacao: null
    },
    {
        id: 7, titulo: 'Urbanismo Sustentável em Metrópoles',
        etapaAtual: 2, status: 'Revisão',
        dataCriacao: '2023-09-28T00:00:00Z', dataUltimaModificacao: null
    },
    {
        id: 8, titulo: 'Avaliação de Políticas Públicas Locais',
        etapaAtual: 3, status: 'Etapa 3: Metodologia',
        dataCriacao: '2023-09-15T00:00:00Z', dataUltimaModificacao: null
    },
    {
        id: 9, titulo: 'Desafios da Mobilidade Urbana',
        etapaAtual: 1, status: 'Rascunho',
        dataCriacao: '2023-09-10T00:00:00Z', dataUltimaModificacao: null
    },
    {
        id: 10, titulo: 'Inovação Tecnológica na Saúde Pública',
        etapaAtual: 2, status: 'Etapa 2: Revisão',
        dataCriacao: '2023-09-02T00:00:00Z', dataUltimaModificacao: null
    },
    {
        id: 11, titulo: 'Sistemas de Informação em Cidades Inteligentes',
        etapaAtual: 4, status: 'Etapa 4: Escrita',
        dataCriacao: '2023-08-20T00:00:00Z', dataUltimaModificacao: null
    },
];

const DashboardPage: React.FC = () => {
    const [estado, setEstado] = useState<DashboardEstado>('populado');
    const [modal, setModal] = useState<ModalEstado>(null);
    const [filtroAtivo, setFiltroAtivo] = useState<FiltroStatus>(null);
    const [search, setSearch] = useState('');
    const [nomeProjeto, setNomeProjeto] = useState('');

    useEffect(() => {
        if (modal === 'sucesso') {
            const t = setTimeout(() => {
                setModal(null);
                setNomeProjeto('');
            }, 2500);
            return () => clearTimeout(t);
        }
    }, [modal]);

    const projetosFiltrados = mockProjetos.filter(p => {
        const matchSearch = p.titulo.toLowerCase().includes(search.toLowerCase());
        const matchFiltro = filtroAtivo === null || p.status === filtroAtivo;
        return matchSearch && matchFiltro;
    });

    const renderBoasVindas = () => {
        if (estado === 'erro') return null;

        return (
            <div className={`flex flex-col md:flex-row justify-between items-start md:items-end mb-12 w-full gap-6 ${estado === 'skeleton' ? 'sticky top-0 z-20 pb-4 pt-8 border-b border-gray-200/50 bg-gray-50/80 backdrop-blur-md' : ''}`}>
                <div>
                    <h1 className="font-display text-4xl md:text-5xl text-on-surface font-bold tracking-tight mb-3">
                        Bem-vinda, Ana.
                    </h1>
                    <p className="text-lg text-on-surface-variant font-body">
                        Aqui está o seu ambiente de pesquisa e estruturação acadêmica.
                    </p>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                    <div className="flex items-center bg-white border border-gray-200 rounded-xl px-4 py-2 w-64 group focus-within:ring-2 focus-within:ring-primary-fixed-dim/20 transition-all">
                        <span className="material-symbols-outlined text-gray-400 text-lg">search</span>
                        <input
                            type="text"
                            placeholder="Buscar..."
                            className="bg-transparent border-none focus:ring-0 text-sm ml-2 w-full text-gray-600 outline-none"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                        <span className="text-[10px] font-bold text-gray-300 ml-2 border border-gray-200 px-1 rounded">⌘K</span>
                    </div>

                    <button
                        onClick={() => {
                            if (filtroAtivo) {
                                setFiltroAtivo(null);
                                setEstado('populado');
                            } else {
                                setFiltroAtivo('Etapa 1: Contexto');
                                setEstado('filtrado');
                            }
                        }}
                        className={`flex items-center gap-2 px-4 h-10 border rounded-xl text-sm font-medium transition-colors shadow-sm ${filtroAtivo !== null
                                ? 'bg-amber-100 border-amber-400 text-amber-900 hover:bg-amber-200'
                                : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                            }`}
                    >
                        <span className="material-symbols-outlined text-lg">filter_list</span>
                        {filtroAtivo ? `Status: ${filtroAtivo}` : 'Status'}
                    </button>

                    <button className="flex items-center gap-2 px-4 h-10 bg-white border border-gray-200 rounded-xl text-gray-700 text-sm font-medium hover:bg-gray-50 transition-colors shadow-sm">
                        Mais recentes
                        <span className="material-symbols-outlined text-lg">expand_more</span>
                    </button>

                    <div className="flex bg-gray-100 rounded-xl p-1">
                        <button className="w-8 h-8 flex items-center justify-center bg-white rounded-lg shadow-sm text-primary-fixed-dim">
                            <span className="material-symbols-outlined text-xl">grid_view</span>
                        </button>
                        <button className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors">
                            <span className="material-symbols-outlined text-xl">view_list</span>
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    const renderConteudo = () => {
        if (estado === 'erro') {
            return (
                <div className="flex flex-col items-center justify-center mt-32 max-w-md mx-auto text-center">
                    <div className="w-20 h-20 flex items-center justify-center mb-6 text-amber-500">
                        <span className="material-symbols-outlined text-[80px]">warning</span>
                    </div>
                    <h1 className="font-display text-xl font-bold text-gray-900 mb-3">
                        Ops, algo não saiu como planejado
                    </h1>
                    <p className="text-gray-500 font-body mb-8">
                        Tivemos uma pequena falha técnica ao buscar seus projetos.
                        Não se preocupe, seus dados estão seguros.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
                        <button
                            onClick={() => setEstado('populado')}
                            className="w-full sm:w-auto px-6 py-2.5 bg-amber-400 text-white font-medium rounded-xl hover:bg-amber-500 transition-colors shadow-sm"
                        >
                            Tentar novamente
                        </button>
                        <button className="w-full sm:w-auto px-6 py-2.5 text-gray-500 hover:text-gray-900 font-medium rounded-xl hover:bg-gray-100 transition-colors">
                            Contatar suporte
                        </button>
                    </div>
                </div>
            );
        }

        if (estado === 'vazio') {
            return (
                <div className="flex flex-col items-center justify-center mt-32 mb-32 text-center px-4">
                    <span className="material-symbols-outlined text-[80px] text-gray-300 mb-6 w-20 h-20 flex items-center justify-center leading-none">
                        description
                    </span>
                    <h2 className="font-display text-xl font-bold text-gray-900 mb-3">
                        Nenhum projeto encontrado
                    </h2>
                    <p className="text-gray-500 max-w-md mx-auto mb-8 font-body">
                        Sua biblioteca de pesquisa está vazia.
                        Vamos começar o seu primeiro estudo acadêmico?
                    </p>
                    <button
                        onClick={() => setModal('novo-projeto')}
                        className="bg-amber-400 hover:bg-amber-500 text-white font-medium px-8 py-3 rounded-xl transition-colors shadow-sm"
                    >
                        Criar primeiro projeto
                    </button>
                </div>
            );
        }

        return (
            <>
                {filtroAtivo && (
                    <div className="flex items-center gap-3 mb-8">
                        <div className="flex items-center gap-1.5 px-3 py-1 bg-gray-200 rounded-full text-sm font-medium text-gray-700">
                            {filtroAtivo}
                            <button
                                onClick={() => { setFiltroAtivo(null); setEstado('populado'); }}
                                className="flex items-center justify-center hover:bg-gray-300 rounded-full p-0.5 transition-colors"
                            >
                                <span className="material-symbols-outlined text-[14px]">close</span>
                            </button>
                        </div>
                        <button
                            onClick={() => { setFiltroAtivo(null); setEstado('populado'); }}
                            className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
                        >
                            Limpar filtros
                        </button>
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-12 items-start">
                    <button
                        onClick={() => setModal('novo-projeto')}
                        className="group flex flex-col items-center justify-center h-64 bg-surface-container-low border-2 border-dashed border-outline-variant/50 rounded-xl hover:bg-surface-container hover:border-primary-fixed-dim transition-all duration-300"
                    >
                        <div className="w-16 h-16 rounded-full bg-surface-container-lowest flex items-center justify-center mb-4 text-on-surface-variant group-hover:text-primary-fixed-dim group-hover:scale-110 transition-all duration-300 shadow-[0_8px_16px_rgba(25,28,30,0.04)]">
                            <span className="material-symbols-outlined text-3xl">add</span>
                        </div>
                        <span className="font-medium text-on-surface">Novo Projeto</span>
                    </button>

                    {projetosFiltrados.map(projeto => (
                        <ProjectCard key={projeto.id} projeto={projeto} />
                    ))}

                    {estado === 'skeleton' && [1, 2, 3, 4].map(i => (
                        <div key={i} className="bg-white rounded-xl p-5 shadow-sm min-h-[200px] flex flex-col animate-pulse">
                            <div className="w-24 h-6 bg-gray-200 rounded-full mb-4"></div>
                            <div className="w-full h-5 bg-gray-200 rounded-md mb-2"></div>
                            <div className="w-2/3 h-5 bg-gray-200 rounded-md"></div>
                            <div className="mt-auto w-20 h-4 bg-gray-200 rounded-md"></div>
                        </div>
                    ))}
                </div>
            </>
        );
    };

    return (
        <div className="flex min-h-screen bg-surface text-on-surface font-body antialiased selection:bg-primary-fixed-dim selection:text-on-primary-fixed academic-gradient">
            <AppSidebar activeRoute="projetos" />

            <div className="flex-1 md:ml-64 relative overflow-hidden bg-gray-50/30 backdrop-blur-3xl">
                <header className="md:hidden flex justify-between items-center w-full px-6 h-20 bg-surface/90 backdrop-blur-xl sticky top-0 z-50">
                    <span className="font-display font-bold text-xl text-primary-fixed-dim tracking-tight">Oráculo</span>
                    <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-on-surface-variant">notifications</span>
                        <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-primary-fixed-dim font-bold">A</div>
                    </div>
                </header>

                <div className="hidden md:flex justify-between items-center w-full px-12 pt-12 pb-6">
                    <div></div>
                    <div className="flex items-center gap-6">
                        <button className="w-10 h-10 flex items-center justify-center rounded-xl text-on-surface-variant hover:bg-surface-container transition-colors relative">
                            <span className="material-symbols-outlined">notifications</span>
                            <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-secondary rounded-full border-2 border-surface"></span>
                        </button>
                        <div className="flex items-center gap-3 bg-surface-container-low py-2 px-3 rounded-full cursor-pointer hover:bg-surface-container transition-colors">
                            <div className="text-right">
                                <p className="text-sm font-medium text-on-surface">Ana</p>
                                <p className="text-xs text-on-surface-variant">Pesquisadora Sênior</p>
                            </div>
                            <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-primary-fixed-dim font-bold">
                                A
                            </div>
                        </div>
                    </div>
                </div>

                <main className="px-6 md:px-12 py-8 max-w-7xl mx-auto">
                    {renderBoasVindas()}
                    {renderConteudo()}
                </main>

                <div className="fixed bottom-4 right-4 flex gap-2 z-40 opacity-20 hover:opacity-100 transition-opacity">
                    {(['populado', 'vazio', 'filtrado', 'erro', 'skeleton'] as const).map(e => (
                        <button key={e} onClick={() => setEstado(e)} className={`px-2 py-1 text-[10px] rounded border ${estado === e ? 'bg-black text-white' : 'bg-white text-black'}`}>
                            {e}
                        </button>
                    ))}
                </div>
            </div>

            {modal === 'novo-projeto' && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/40 backdrop-blur-sm">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 overflow-hidden">
                        <div className="p-6 border-b border-gray-100">
                            <h2 className="font-display text-2xl font-bold text-gray-900 mb-1">
                                Iniciar Novo Projeto
                            </h2>
                            <p className="text-sm text-gray-500 font-body">
                                Dê um nome ao seu projeto de pesquisa para começar.
                            </p>
                        </div>
                        <div className="p-6">
                            <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="projectName">
                                Nome do Projeto
                            </label>
                            <input
                                autoFocus
                                id="projectName"
                                type="text"
                                value={nomeProjeto}
                                onChange={e => setNomeProjeto(e.target.value)}
                                placeholder="Ex: Impacto da IA na Educação Superior"
                                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-fixed-dim focus:border-primary-fixed-dim outline-none transition-all font-body text-gray-900"
                            />
                        </div>
                        <div className="p-6 bg-gray-50 flex justify-end gap-3 rounded-b-2xl border-t border-gray-100">
                            <button
                                onClick={() => { setModal(null); setNomeProjeto(''); }}
                                className="px-5 py-2.5 rounded-xl text-gray-700 font-medium hover:bg-gray-200 transition-colors bg-white border border-gray-200 shadow-sm"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={() => {
                                    if (!nomeProjeto) {
                                        setModal('erro-modal');
                                    } else {
                                        setModal('sucesso');
                                    }
                                }}
                                className="px-5 py-2.5 rounded-xl text-primary font-medium bg-primary-fixed-dim hover:bg-inverse-primary transition-colors shadow-sm"
                            >
                                Criar e Iniciar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {modal === 'sucesso' && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/40 backdrop-blur-sm">
                    <div className="bg-white rounded-3xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden flex flex-col items-center text-center p-10">
                        <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mb-6 text-green-500">
                            <span className="material-symbols-outlined text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>check</span>
                        </div>
                        <h2 className="font-display text-2xl font-bold text-gray-900 mb-2">
                            Projeto criado com sucesso!
                        </h2>
                        <p className="text-base text-gray-500 font-body mb-8">
                            Preparando o seu assistente metodológico...
                        </p>
                        <svg className="animate-spin text-amber-400 w-6 h-6" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" fill="currentColor" />
                        </svg>
                    </div>
                </div>
            )}

            {modal === 'erro-modal' && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/40 backdrop-blur-sm">
                    <div className="bg-white rounded-3xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden flex flex-col items-center text-center p-10">
                        <div className="w-20 h-20 rounded-full bg-red-100 flex items-center justify-center mb-6 text-red-500">
                            <span className="material-symbols-outlined text-4xl">error</span>
                        </div>
                        <h2 className="font-display text-2xl font-bold text-gray-900 mb-2">
                            Erro ao criar projeto
                        </h2>
                        <p className="text-base text-gray-500 font-body mb-8">
                            Não foi possível processar sua solicitação no momento.
                            Por favor, verifique sua conexão e tente novamente.
                        </p>
                        <div className="flex flex-col w-full">
                            <button
                                onClick={() => setModal('novo-projeto')}
                                className="bg-amber-400 text-white font-semibold rounded-xl px-6 py-2.5 hover:bg-amber-500 transition-colors"
                            >
                                Tentar novamente
                            </button>
                            <button
                                onClick={() => setModal(null)}
                                className="text-gray-500 hover:bg-gray-100 px-5 py-2.5 rounded-xl font-medium mt-2"
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DashboardPage;
