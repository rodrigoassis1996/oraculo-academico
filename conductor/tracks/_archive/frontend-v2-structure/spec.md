# Spec: Estrutura e Fundação do Frontend V2.0

## Objetivo
Preparar o frontend para receber os novos componentes e páginas da V2.0, adicionando
roteamento, criando a estrutura de pastas e definindo os tipos TypeScript compartilhados,
sem quebrar nada existente da V1.0.

## Contexto
O frontend atual é uma SPA sem roteamento entre páginas (tudo em App.tsx).
A V2.0 introduz páginas distintas (login, dashboard, workspace) com navegação
via React Router. O Design System "The Illuminated Archive" usa Tailwind puro.
O antd permanece instalado para os componentes legados da V1.0.

## Critérios de Aceitação
- [ ] react-router-dom v7 instalado e presente no package.json
- [ ] Pastas pages/auth/, pages/dashboard/, pages/workspace/ criadas com index.ts
- [ ] Pastas components/ui/, hooks/, lib/, types/ criadas com index.ts
- [ ] Arquivo frontend/src/types/index.ts com interfaces Usuario, Projeto e type StatusEtapa
- [ ] App.tsx, store/, api/ e components/features/ inalterados
- [ ] antd não removido do package.json
- [ ] Projeto compila sem erros (npm run build)

## Fora do Escopo
- Implementação das páginas (LoginPage, DashboardPage)
- Configuração do roteamento em main.tsx
- Criação de componentes UI
- Remoção do antd
