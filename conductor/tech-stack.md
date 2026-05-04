# Pilha Tecnológica: Oráculo Acadêmico

Este documento detalha as escolhas de tecnologia, dependências e infraestrutura do projeto.

## Backend (Python 3.11+)

-   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Web server assíncrono)
-   **Orquestração de LLM**: [LangChain](https://python.langchain.com/) (v0.3.0)
-   **Banco Vetorial**: [ChromaDB](https://www.trychroma.com/) (v1.3.7) - Armazenamento resiliente de embeddings.
-   **Processamento de Documentos**:
    -   `pypdf`, `docx2txt`, `beautifulsoup4`, `unstructured`.
-   **IA/Embeddings**:
    -   `langchain-openai`, `langchain-groq`, `sentence-transformers`.
-   **Integração Google**:
    -   `google-api-python-client`, `google-auth-oauthlib`.

## Frontend (React 19)

-   **Framework**: [React](https://react.dev/) (v19.2.0)
-   **Linguagem**: TypeScript (v5.9.3)
-   **Build Tool**: [Vite](https://vitejs.dev/) (v7.3.1)
-   **Estilização**:
    -   [TailwindCSS](https://tailwindcss.com/) (v4.1.18)
    -   [Ant Design](https://ant.design/) (v6.3.0)
-   **Gerenciamento de Estado**: [Zustand](https://docs.pmnd.rs/zustand/) (v5.0.11)
-   **Data Fetching**: [TanStack Query](https://tanstack.com/query/latest) (v5.90.21)

## Infraestrutura e Ferramentas

-   **Testes**:
    -   Backend: `pytest` (v9.0.2) + `pytest-mock`.
    -   Frontend: `vitest` (v4.0.18) + `@testing-library/react`.
-   **Ambiente**: `python-dotenv` para gerenciamento de variáveis de ambiente.
-   **Linting**: `eslint`, `typescript-eslint`.

## V2.0 — Decisões Arquiteturais

### Banco de Dados
- **PostgreSQL**: Substituição de sessões em memória por um banco relacional para garantir persistência robusta.
- **asyncpg**: Adoção de driver assíncrono para máxima performance junto ao FastAPI.
- **SQLAlchemy 2.0**: Utilização do ORM em modo assíncrono (`Mapped`/`mapped_column`) para tipagem forte e código moderno.
- **Alembic**: Padronização para versionamento e controle das migrações do banco de dados.

### Autenticação
- **OAuth 2.0 via Google**: Integração do provedor existente com o novo modelo persistido de usuários no banco de dados.
- **JWT para sessões**: Adoção da biblioteca `python-jose[cryptography]` para emissão e validação segura de tokens.

### Frontend
- **react-router-dom v7**: Inclusão para gerenciamento de roteamento entre páginas na arquitetura SPA.
- **Design System próprio**: Migração gradual do Ant Design para componentes padronizados baseados apenas em Tailwind puro.
- **Componentes novos**: Construção exclusiva com Tailwind, evitando dependência de bibliotecas de UI pesadas.
- **Componentes legados (V1.0)**: Manutenção temporária com Ant Design para preservar o funcionamento atual durante a transição.

### Nova Estrutura de Pastas
- **Backend**: Criação das pastas `database/`, `database/models/`, `database/repositories/`, `api/v2/` e `api/v2/routers/` para isolar a camada de dados e endpoints V2.
- **Frontend**: Criação de `pages/`, `pages/auth/`, `pages/dashboard/`, `pages/workspace/`, `components/ui/`, `hooks/`, `lib/` e `types/` para separar conceitos e escalar o frontend.

### Design System ("The Illuminated Archive")
- **Base**: Utilização estrita de TailwindCSS puro.
- **Cores**: Fundo global definido como `#f7f9fc` com cor de acento em `amber-500`.
- **Tipografia**: Combinação da fonte `Space Grotesk` para títulos (headlines) e `Inter` para os blocos de texto (body).
- **Estilo Geral**: Regra explícita de evitar bordas de 1px visíveis para criar um visual mais leve e sofisticado.

---

> [!NOTE]
> O projeto utiliza uma suíte de testes segregada entre unitários/integração (rápidos) e End-to-End (E2E), exigindo credenciais reais para os testes E2E.
