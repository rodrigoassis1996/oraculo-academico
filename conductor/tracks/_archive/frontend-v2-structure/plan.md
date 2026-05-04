# Plano: Estrutura e Fundação do Frontend V2.0

## Status: [x] Complete

---

## Fase 1 — Dependências
- [x] Task 1.1: Instalar react-router-dom@^7.6.0 via npm (dentro de frontend/)

Verificação da Fase 1:
- package.json contém react-router-dom na seção dependencies
- node_modules/react-router-dom existe
- npm run build não apresenta erros relacionados ao router

---

## Fase 2 — Estrutura de Pastas
- [x] Task 2.1: Criar frontend/src/pages/auth/index.ts (vazio)
- [x] Task 2.2: Criar frontend/src/pages/dashboard/index.ts (vazio)
- [x] Task 2.3: Criar frontend/src/pages/workspace/index.ts (vazio)
- [x] Task 2.4: Criar frontend/src/components/ui/index.ts (vazio)
- [x] Task 2.5: Criar frontend/src/hooks/index.ts (vazio)
- [x] Task 2.6: Criar frontend/src/lib/index.ts (vazio)

Verificação da Fase 2:
- Todas as pastas existem com index.ts
- Nenhum arquivo preexistente foi alterado
- npm run build continua sem erros

---

## Fase 3 — Tipos Compartilhados
- [x] Task 3.1: Criar frontend/src/types/index.ts com as interfaces TypeScript do projeto

Conteúdo esperado do arquivo:

/** Perfil do usuário autenticado via OAuth Google */
export interface Usuario {
id: number
nome: string
email: string
fotoPerfil: string | null
role: 'pesquisador' | 'admin'
}

/** Projeto de pesquisa pertencente a um usuário */
export interface Projeto {
id: number
titulo: string
etapaAtual: 1 | 2 | 3 | 4 | 5
status: StatusEtapa
dataCriacao: string
dataUltimaModificacao: string | null
}

/** Rótulos de status exibidos nos cards do dashboard */
export type StatusEtapa =
| 'Rascunho'
| 'Etapa 1: Contexto'
| 'Etapa 2: Revisão'
| 'Etapa 3: Metodologia'
| 'Etapa 4: Escrita'
| 'Revisão'

Verificação da Fase 3:
- frontend/src/types/index.ts existe e exporta as três definições
- npm run build sem erros de TypeScript
- npm run lint sem erros

---
