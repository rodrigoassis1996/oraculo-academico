# Oráculo Acadêmico

Sistema Multiagente de IA para assistência na produção de textos acadêmicos longos com qualidade científica. Projeto de dissertação do PPGIT/UFMG.

O **Oráculo Acadêmico** utiliza inteligência artificial generativa avançada e uma arquitetura multiagente para auxiliar pesquisadores na estruturação, fundamentação e redação de trabalhos científicos, garantindo rigor metodológico e conformidade com normas acadêmicas.

## Stack Tecnológica

### Backend:
- **Linguagem**: Python 3.11+
- **Framework Web**: FastAPI
- **Persistência**: SQLAlchemy 2.0 (async) + Alembic
- **Banco de Dados**: PostgreSQL + asyncpg
- **Orquestração Multiagente**: LangGraph / AutoGen
- **RAG (Retrieval-Augmented Generation)**: ChromaDB (base vetorial)
- **Integrações**: Google Docs API
- **LLMs**: GPT-4, Claude (via API com versionamento fixo)

### Frontend:
- **Framework**: React 19 + TypeScript + Vite
- **Estilização**: TailwindCSS (Design System "The Illuminated Archive")
- **Roteamento**: React Router v7
- **Gerenciamento de Estado**: Zustand
- **Data Fetching**: TanStack Query (React Query)

## Estrutura do Projeto

- `agents/` — Lógica dos agentes especializados e definições de personas.
- `services/` — Integrações externas (RAG, Google Docs, Gerenciamento de Memória).
- `database/` — Models SQLAlchemy, migrações Alembic e configuração do PostgreSQL.
- `api/v2/` — Endpoints FastAPI da versão 2.0, organizados por domínio.
- `conductor/` — Framework de gerenciamento de contexto, design system e tracks de desenvolvimento.
- `frontend/src/` — Aplicação React V2.0.
  - `pages/` — Páginas da aplicação organizadas por rota (Auth, Dashboard, Workspace).
  - `components/` — Componentes reutilizáveis divididos em `ui` (base) e `features` (complexos).
  - `types/` — Interfaces TypeScript compartilhadas entre frontend e definições de API.

## Arquitetura do Sistema

O sistema opera através de um pipeline multiagente dividido em 5 etapas fundamentais:

1.  **Agente Questionador**: Realiza a entrevista metodológica inicial para capturar o tema, problema e objetivos.
2.  **Revisão de Literatura**: Ingestão de corpus acadêmico via RAG/ChromaDB para fundamentação teórica.
3.  **Alinhamento e Cruzamento**: Análise de consistência entre o contexto do pesquisador e a literatura revisada.
4.  **Agente Estruturador**: Geração do esqueleto/sumário detalhado do documento acadêmico.
5.  **Escrita Assistida**: Redação iterativa das seções com suporte human-in-the-loop para refinamento.

## Como Executar

### Backend:
```bash
# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar servidor de desenvolvimento
uvicorn main_api:app --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Variáveis de Ambiente Necessárias:
Crie um arquivo `.env` na raiz (backend) e em `frontend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/oraculo_academico
# Google OAuth, OpenAI API Key, Claude API Key, etc.
```

## Status do Projeto

Em desenvolvimento ativo — dissertação PPGIT/UFMG 2025–2026.
Foco atual: Estabilização do Frontend V2.0 e unificação do sistema de tipos.

---
**Oráculo Acadêmico** — Transformando a complexidade da pesquisa científica em um processo de co-criação fluido e padronizado. 🎓✨
