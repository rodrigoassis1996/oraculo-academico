# Plano: Dashboard de Projetos — Login, Sidebar e Páginas V2.0

## Status: [~] Em Progresso

---

## Fase 1 — Design System Foundation
- [x] Task 1.1: Atualizar tailwind.config.js (ou .ts) com os tokens completos do Design System
- [x] Task 1.2: Atualizar frontend/index.html adicionando no <head>:
Google Fonts: Space Grotesk (300,400,500,600,700) + Inter (300,400,500,600,700)
Material Symbols Outlined (wght,FILL@100..700,0..1)
CSS para .material-symbols-outlined com font-variation-settings padrão

Verificação da Fase 1:
- npm run build sem erros
- Classes como text-primary-fixed-dim e bg-surface-container-low resolvem corretamente

---

## Fase 2 — Componentes Compartilhados
- [x] Task 2.1: Criar frontend/src/components/layout/AppSidebar.tsx

Sidebar fixa (w-64, hidden md:flex, fixed left-0 top-0, h-screen)
Logo "Oráculo Acadêmico" em primary-fixed-dim, Space Grotesk bold
4 itens de navegação: Projetos (ativo), Pesquisas, Biblioteca, Configurações
Item ativo: bg-amber-50/50 + border-l-4 border-primary-fixed-dim + rounded-r-xl
Item inativo: hover:bg-gray-50 + rounded-xl
Ícones: Material Symbols Outlined (dashboard, science, local_library, settings)
Rodapé: link Suporte com ícone help_outline
Props: activeRoute: string

- [x] Task 2.2: Criar frontend/src/components/ui/ProjectCard.tsx

Props: projeto: Projeto, onClick?: () => void
Card: bg-white rounded-xl p-6, h-64, shadow sutil, border border-gray-100
Hover: shadow maior + -translate-y-1
StatusBadge: pill com dot colorido + texto do status (mapeamento do Design System)
Título: font-display text-xl font-bold, line-clamp-3
Rodapé: ícone schedule + data formatada (pt-BR relativa ou absoluta)
Exportar também o componente interno StatusBadge separadamente

Verificação da Fase 2:
- npm run build sem erros
- Nenhum import de antd nos novos componentes

---

## Fase 3 — LoginPage
- [x] Task 3.1: Criar frontend/src/pages/auth/LoginPage.tsx

Referência: usar fielmente o HTML do Stitch da tela de Login como base.

Estrutura:
- Background: academic-gradient + hero-pattern radial + blur circles decorativos
- Layout: grid 2 colunas (lg) — coluna esquerda branding, coluna direita card
- Coluna esquerda: logo icon + "Oráculo Acadêmico" + headline h1 com "excelência"
  em itálico text-secondary + parágrafo descritivo + 3 feature pills
- Coluna direita: card bg-white rounded-[2rem] + shadow sutil
  Dentro do card: título "Bem-vindo ao Futuro da Pesquisa" + subtítulo +
  placeholder de imagem (div bg-surface-container-low h-48 rounded-2xl) +
  botão "Entrar com Google" (SVG Google + texto) +
  divisor "Exclusivo para Pesquisadores" + texto de termos
- Footer: logo + links Privacidade/Termos/Suporte + badge "Sistemas Operacionais"
- Handler: onGoogleLogin prop (onClick do botão → chamar prop)
- Mobile: apenas a coluna do card (coluna esquerda hidden abaixo de lg)

- [x] Task 3.2: Atualizar frontend/src/pages/auth/index.ts
Exportar: export { default as LoginPage } from './LoginPage'

Verificação da Fase 3:
- npm run build sem erros
- Nenhum import de antd

---

## Fase 4 — DashboardPage + Modais
- [x] Task 4.1: Criar frontend/src/pages/dashboard/DashboardPage.tsx

Referência: usar fielmente o HTML do Stitch do Dashboard como base.

Layout:
- AppSidebar à esquerda (fixo)
- Área principal: ml-64 bg-gray-50
- Header desktop: notificações + user chip (nome + cargo + avatar)
- Seção welcome: "Bem-vinda, Ana." → substituir por nome do usuário (prop ou mock)
- Controles: search input + botão Status (filtro) + botão ordenação + toggle grid/lista

5 Estados controlados por variável de estado interna (para mock):

Estado 1 — Populado (padrão):
  Grid 4 colunas (xl): card "Novo Projeto" (dashed) + ProjectCards com dados mockados
  Dados mock: 8 projetos com títulos, status e datas variados (cobrir todos os StatusEtapa)
  Card "Novo Projeto": borda dashed border-outline-variant/50, hover border-primary-fixed-dim,
  ícone "add" centralizado, texto "Novo Projeto" — ao clicar: abrir NovoProjetoModal

Estado 2 — Vazio (nenhum projeto):
  Ícone de documento centralizado (material symbol: description ou similar)
  Título "Nenhum projeto encontrado"
  Subtítulo "Sua biblioteca de pesquisa está vazia. Vamos começar o seu primeiro estudo acadêmico?"
  Botão primário "Criar primeiro projeto" (bg-primary-fixed-dim) → abre NovoProjetoModal

Estado 3 — Filtro ativo:
  Badge "Status: Revisão ×" + link "Limpar filtros" abaixo dos controles
  Grid mostrando apenas projetos com status "Revisão" (filtrar do mock)
  Botão Status com estilo ativo (bg-primary-fixed-dim text-on-primary-fixed)

Estado 4 — Erro de sistema:
  Ícone de triângulo warning (bg-amber-500)
  Título "Ops, algo não saiu como planejado"
  Subtítulo "Tivemos uma pequena falha técnica ao buscar seus projetos. Não se preocupe, seus dados estão seguros."
  Botão "Tentar novamente" (bg-primary-fixed-dim) + link "Contatar suporte"
  Sidebar permanece visível

Estado 5 — Skeleton (lazy loading):
  Grid com 8 cards skeleton: divs bg-gray-200 animate-pulse rounded-xl h-64
  Cada skeleton tem linhas de conteúdo simuladas (div menores dentro)

- [ ] Task 4.2: Criar os 3 modais como componentes internos do arquivo DashboardPage.tsx

Modal 1 — NovoProjetoModal:
  Backdrop: bg-black/30 fixed inset-0 flex items-center justify-center z-50
  Card modal: bg-white rounded-2xl p-8 w-full max-w-md shadow-xl
  Título "Iniciar Novo Projeto"
  Subtítulo "Dê um nome ao seu projeto de pesquisa para começar."
  Label "Nome do Projeto" + input text (placeholder: "Ex: Impacto da IA na Educação Superior",
  border-2 border-primary-fixed-dim quando focado)
  Botões: "Cancelar" (ghost) + "Criar e Iniciar" (bg-primary-fixed-dim)
  Comportamento: ao clicar "Criar e Iniciar" → fechar modal e abrir SucessoModal

Modal 2 — SucessoModal:
  Card modal similar ao anterior
  Ícone: quadrado bg-green-100 rounded-2xl com checkmark verde
  Título "Projeto criado com sucesso!"
  Subtítulo "Preparando o seu assistente metodológico..."
  Spinner de loading (border-4 border-primary-fixed-dim border-t-transparent animate-spin)
  Sem botões — fecha automaticamente após 2.5 segundos (setTimeout)

Modal 3 — ErroModal:
  Card modal similar
  Ícone: quadrado bg-red-100 rounded-2xl com exclamação vermelha
  Título "Erro ao criar projeto"
  Subtítulo "Não foi possível processar sua solicitação no momento. Por favor, verifique sua conexão e tente novamente."
  Botões: "Tentar novamente" (bg-primary-fixed-dim) + "Cancelar" (link ghost)

- [x] Task 4.3: Atualizar frontend/src/pages/dashboard/index.ts
Exportar: export { default as DashboardPage } from './DashboardPage'

Verificação da Fase 4:
- npm run build sem erros
- Todos os 5 estados renderizam sem erros de TypeScript
- Nenhum import de antd

---

## Fase 5 — Roteamento e Validação Final
- [x] Task 5.1: Configurar frontend/src/lib/router.tsx
- [x] Task 5.2: Atualizar frontend/src/App.tsx
- [x] Task 5.3: Executar npm run build e npm run lint

Verificação da Fase 5:
- build e lint passam com 0 erros e 0 warnings
- Navegação entre rotas funcionando via RouterProvider
