import React from 'react';

export interface LoginPageProps {
    onGoogleLogin?: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onGoogleLogin }) => {
    return (
        <div className="min-h-screen flex flex-col academic-gradient selection:bg-primary-fixed-dim selection:text-on-primary-fixed">
            <main className="flex-grow flex items-center justify-center p-6 relative overflow-hidden">
                {/* Background Decoration */}
                <div className="absolute inset-0 hero-pattern pointer-events-none"></div>
                <div className="absolute top-[-10%] right-[-5%] w-96 h-96 bg-secondary-container/20 rounded-full blur-[120px] pointer-events-none"></div>
                <div className="absolute bottom-[-10%] left-[-5%] w-96 h-96 bg-primary-fixed/10 rounded-full blur-[120px] pointer-events-none"></div>
                <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-12 items-center z-10">
                    
                    {/* Left Column: Branding & Value Prop */}
                    <div className="hidden lg:block space-y-8 text-left lg:pr-12">
                        <div className="space-y-2">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-primary-container rounded-xl flex items-center justify-center">
                                    <span className="material-symbols-outlined text-primary-fixed-dim" style={{ fontVariationSettings: "'FILL' 1" }}>auto_stories</span>
                                </div>
                                <span className="font-headline text-2xl font-bold tracking-tighter text-on-surface">Oráculo Acadêmico</span>
                            </div>
                        </div>
                        <div className="space-y-6">
                            <h1 className="font-headline text-4xl lg:text-5xl font-bold text-on-surface leading-[1.1] tracking-tight">
                                Seu assistente de IA para escrita acadêmica de <span className="text-secondary italic">excelência</span>
                            </h1>
                            <p className="text-on-surface-variant text-lg leading-relaxed max-w-md">
                                Transforme sua pesquisa bruta em artigos científicos estruturados com rigor metodológico e clareza editorial.
                            </p>
                        </div>
                        {/* Feature Pills */}
                        <div className="flex flex-wrap gap-3">
                            <div className="flex items-center gap-2 px-4 py-2 bg-surface-container-lowest rounded-full shadow-sm text-sm font-medium text-on-surface-variant">
                                <span className="material-symbols-outlined text-secondary text-lg">verified</span>
                                Rigor Científico
                            </div>
                            <div className="flex items-center gap-2 px-4 py-2 bg-surface-container-lowest rounded-full shadow-sm text-sm font-medium text-on-surface-variant">
                                <span className="material-symbols-outlined text-secondary text-lg">science</span>
                                Análise de Dados
                            </div>
                            <div className="flex items-center gap-2 px-4 py-2 bg-surface-container-lowest rounded-full shadow-sm text-sm font-medium text-on-surface-variant">
                                <span className="material-symbols-outlined text-secondary text-lg">history_edu</span>
                                Revisão Crítica
                            </div>
                        </div>
                    </div>

                    {/* Right Column: Auth Card */}
                    <div className="relative group">
                        {/* Tonal Layering for Card */}
                        <div className="absolute inset-0 bg-on-surface/5 blur-3xl group-hover:bg-on-surface/10 transition-colors duration-500 rounded-3xl"></div>
                        <div className="relative bg-surface-container-lowest p-8 lg:p-12 rounded-[2rem] shadow-[0_24px_48px_-12px_rgba(0,0,0,0.05)] border border-outline-variant/10 flex flex-col items-center text-center">
                            <div className="mb-8">
                                <h2 className="font-headline text-2xl font-semibold text-on-surface mb-2">Bem-vindo ao Futuro da Pesquisa</h2>
                                <p className="text-on-surface-variant text-sm">Acesse sua biblioteca pessoal e continue seus projetos.</p>
                            </div>
                            {/* Illustration Placeholder */}
                            <div className="w-full h-48 mb-10 bg-surface-container-low rounded-2xl flex items-center justify-center overflow-hidden relative">
                                <img alt="Abstract desk with books and digital light" className="w-full h-full object-cover opacity-60 mix-blend-multiply filter grayscale" src="https://lh3.googleusercontent.com/aida-public/AB6AXuA8C6KpRTdChChs2uuJJ4Biquu3xhERezCuIdzrLv4Bkea-5jSwBcD-lvtS88OjiDfAxdWJvy9uqVye8XEx0HG-iNUAZVfHRQyRkEgPSh4Iz0z6_HsiDrLlGrnyYh55UtOMR4eXnJa7RctGYpUrgKKPrTj43V3sG4z8mC0oYLrSP1--ugUAxNfDN6B8bdN2vdXTYeVkvIz18_I5Mt1HHe9m7eBC2rLbpdqdII1mo9ggMHF_fxqFScrMmPonWqMQXhkcQvNp6PMSuvsH"/>
                                <div className="absolute inset-0 bg-gradient-to-t from-surface-container-lowest via-transparent to-transparent"></div>
                                <span className="absolute material-symbols-outlined text-4xl text-primary-fixed-dim opacity-80" style={{ fontVariationSettings: "'FILL' 1" }}>flare</span>
                            </div>
                            {/* Google Sign In */}
                            <button onClick={onGoogleLogin} className="w-full flex items-center justify-center gap-3 bg-white border border-outline-variant py-4 px-6 rounded-xl hover:bg-surface-container transition-all duration-300 active:scale-[0.98] group/btn">
                                <svg className="w-5 h-5" viewBox="0 0 24 24">
                                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
                                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
                                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"></path>
                                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
                                </svg>
                                <span className="font-label font-semibold text-on-surface tracking-tight">Entrar com Google</span>
                            </button>
                            <div className="mt-8 flex items-center w-full gap-4">
                                <div className="h-[1px] flex-grow bg-outline-variant/30"></div>
                                <span className="text-[10px] font-bold uppercase tracking-widest text-outline">Exclusivo para Pesquisadores</span>
                                <div className="h-[1px] flex-grow bg-outline-variant/30"></div>
                            </div>
                            <p className="mt-8 text-xs text-on-surface-variant leading-relaxed">
                                Ao continuar, você concorda com nossos termos de uso institucionais. <br/>
                                Ambiente protegido por criptografia de nível acadêmico.
                            </p>
                        </div>
                    </div>
                </div>
            </main>
            {/* Footer */}
            <footer className="py-10 px-8 flex flex-col md:flex-row items-center justify-between gap-6 border-t border-outline-variant/10">
                <div className="flex items-center gap-2 text-on-surface-variant/60">
                    <span className="font-headline text-sm font-bold tracking-tighter">ORÁCULO</span>
                    <span className="text-[10px] font-medium tracking-widest uppercase">© 2024 Research Intelligence</span>
                </div>
                <nav className="flex gap-8">
                    <a className="text-xs font-semibold uppercase tracking-widest text-on-surface-variant hover:text-secondary transition-colors duration-300" href="/privacidade">Privacidade</a>
                    <a className="text-xs font-semibold uppercase tracking-widest text-on-surface-variant hover:text-secondary transition-colors duration-300" href="/termos">Termos de Uso</a>
                    <a className="text-xs font-semibold uppercase tracking-widest text-on-surface-variant hover:text-secondary transition-colors duration-300" href="/suporte">Suporte</a>
                </nav>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1.5 px-3 py-1 bg-surface-container rounded-full text-[10px] font-bold text-on-surface-variant">
                        <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
                        SISTEMAS OPERACIONAIS
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LoginPage;
