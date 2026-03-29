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

---

> [!NOTE]
> O projeto utiliza uma suíte de testes segregada entre unitários/integração (rápidos) e End-to-End (E2E), exigindo credenciais reais para os testes E2E.
