# Spec: Dashboard — Controles Interativos e View de Tabela

## Objetivo
Implementar os dropdowns reais de filtro e ordenação, o menu do usuário (admin e comum)
e a view de listagem em tabela, completando o dashboard conforme os protótipos do Stitch.

## Critérios de Aceitação
- [ ] Hook useClickOutside criado em hooks/
- [ ] Novos tipos OrdemOpcao e ViewMode adicionados a types/index.ts
- [ ] StatusFilterPanel como componente em components/ui/
- [ ] SortDropdown como componente em components/ui/
- [ ] UserMenuDropdown como componente em components/ui/ (variante admin e comum)
- [ ] ProjectTableRow como componente em components/ui/
- [ ] CSS skeleton-shimmer adicionado ao index.css
- [ ] DashboardPage atualizado: viewMode, ordenacao, dropdowns, userMenu, view tabela
- [ ] Toggle grid/lista funciona alternando as duas views
- [ ] Filtro e ordenação aplicam-se a ambas as views
- [ ] npm run build e npm run lint passando com 0 erros

## Fora do Escopo
- Integração com API real (dados continuam mockados)
- Autenticação real (isAdmin mockado como true)
- Paginação real (lazy loading permanece simulado)
