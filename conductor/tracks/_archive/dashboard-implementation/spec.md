# Spec: Dashboard de Projetos — Login, Sidebar e Páginas V2.0

## Objetivo
Implementar as páginas de Login e Dashboard com fidelidade total ao Design System
"The Illuminated Archive", usando o código exportado do Google Stitch como referência.

## Contexto do Design System
Paleta de cores definida no Stitch (tokens custom Tailwind):
primary-fixed-dim: #ffba3c (âmbar — acento principal)
secondary: #405f91 (azul — links e destaques)
surface: #f7f9fc (fundo global)
surface-container-lowest: #ffffff (cards)
surface-container-low: #f2f4f7 (fundos de seção)
on-surface: #191c1e (texto principal — nunca usar #000000)
on-surface-variant: #43474f (texto secundário)
outline-variant: #c4c6d0 (bordas sutis)

Tipografia:
Space Grotesk → headlines, títulos, display
Inter → body, labels, parágrafos

Status dos projetos (badge colors baseados no Stitch):
Rascunho           → bg-gray-100 text-gray-600 dot-gray-400
Etapa 1: Contexto  → bg-blue-50 text-blue-700 dot-blue-500
Etapa 2: Revisão   → bg-purple-50 text-purple-700 dot-purple-500
Etapa 3: Metodologia → bg-amber-50 text-amber-700 dot-amber-500
Etapa 4: Escrita   → bg-emerald-50 text-emerald-700 dot-emerald-500
Revisão            → bg-blue-50 text-blue-700 dot-blue-500

## Critérios de Aceitação
- [ ] Tailwind config atualizado com tokens do Design System e fontes
- [ ] Google Fonts (Space Grotesk + Inter) e Material Symbols carregados no index.html
- [ ] AppSidebar.tsx criado como componente reutilizável
- [ ] ProjectCard.tsx criado com StatusBadge interno
- [ ] LoginPage.tsx fiel ao código Stitch
- [ ] DashboardPage.tsx com os 5 estados (populado, vazio, filtrado, erro, skeleton)
- [ ] 3 modais implementados: NovoProjetoModal, SucessoModal, ErroModal
- [ ] main.tsx atualizado com BrowserRouter
- [ ] router.tsx criado com rotas /login e /dashboard
- [ ] npm run build e npm run lint passando sem erros
