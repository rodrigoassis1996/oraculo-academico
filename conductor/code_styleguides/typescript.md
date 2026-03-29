# Guia de Estilo: TypeScript (React 19)

Este documento estabelece as convenções de codificação para o frontend do **Oráculo Acadêmico**.

## Regras de React 19

-   **Componentes Funcionais**: Use funções (`const App = () => ...`).
-   **Hooks**: Prefira hooks personalizados para lógica de estado complexa ou efeitos colaterais.
-   **Prop Types**: Use `interface` ou `type` para definir as props de cada componente.

## TypeScript e Tipagem

-   **`any` Proibido**: Evite o uso de `any`; defina tipos explícitos para garantir segurança.
-   **Interfaces**: Nomeie interfaces com PascalCase (ex: `UserProps`).
-   **Enums**: Use `enum` para estados finitos e fixos.

## Padrões de Interface (UI)

-   **Ant Design (v6)**: Use componentes AntD para estrutura básica e formulários.
-   **TailwindCSS (v4)**: Use classes utilitárias para layout, espaçamento e estilização fina.
-   **Arquitetura**: Separe componentes em `components/ui/` (genéricos) e `components/features/` (lógica de negócio).

## Gerenciamento de Estado

-   **Zustand**: Para estado global da aplicação (ex: dados da sessão, tema).
-   **React Query**: Para cache e orquestração de dados de API.

## Testes de Frontend

-   **Vitest**: Use `describe` e `it/test` para estruturar os testes.
-   **Testing Library**: Teste o comportamento do usuário final, não a implementação interna.

---

> [!TIP]
> **Acessibilidade (a11y)**: Certifique-se de que todos os componentes interativos possuam `aria-label` apropriados.
