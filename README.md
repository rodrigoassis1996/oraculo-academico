# 👨🏾‍🎓 Oráculo Acadêmico: Ecossistema de IA Full Stack

O **Oráculo Acadêmico** evoluiu de uma ferramenta experimental para um ecossistema robusto de assistência científica. Ele integra inteligência artificial de ponta (**RAG - Retrieval-Augmented Generation**) com a produtividade do **Google Docs**, garantindo que mestrandos e pesquisadores produzam textos de alta qualidade técnica seguindo rigorosamente as normas **ABNT**.

---

## ✨ Diferenciais Tecnológicos

- **Arquitetura Full Stack Moderna**: Backend resiliente em FastAPI e Frontend reativo em React 19.
- **Cérebro Multiagente (Maestro)**: Um orquestrador inteligente que tria solicitações entre especialistas em **Redação/Estruturação** e **Análise/QA**.
- **Integração Nativa Google Docs**:
    - Persistência automática via placeholders inteligentes (`{{*KEY*}}`).
    - Fatiamento de seções baseado em cabeçalhos acadêmicos (`###`).
    - Formatação ABNT nativa automatizada (margens, fontes, espaçamentos).
- **Garantia de Qualidade (QA)**: Suíte abrangente com **42 testes automatizados** (Backend + Frontend).
- **Resiliência Industrial**: Protocolos de auto-recuperação para o banco vetorial e rate limiting exponencial para APIs externas.

---

## 🤖 Fluxo de IA e Roteamento

O sistema utiliza um fluxo de trabalho orquestrado para garantir precisão e contexto em cada etapa da pesquisa acadêmica.

```mermaid
graph TD
    A[Usuário] -->|Input| B(Orquestrador / Maestro)
    B -->|Triagem Inteligente| C{Intenção?}
    
    C -->|Produzir / Editar| D[Agente Estruturador]
    C -->|Dúvida / Análise| E[Agente QA / Consulta]
    
    D -->|Proposta de Estrutura| F{Aprovação?}
    F -->|Sim| G[Sistema Google Docs ABNT]
    F -->|Ajustar| D
    
    G -->|Escrita de Seção| H[Persistência via {{*KEY*}}]
    H -->|Refinamento Contextual| D
    
    E -->|Resposta Baseada em Dados| A
    
    subgraph "Camada de Conhecimento"
        R[RAG Global & Local]
    end
    
    D --> R
    E --> R
```

---

## 🏗️ Estrutura do Projeto

O Oráculo Acadêmico é organizado em camadas para facilitar a manutenção e escalabilidade:

### 🐍 Backend (Python 3.11 + FastAPI)
- `agents/`: Definições de personas, prompts e o motor do Orquestrador.
- `services/`: 
    - `google_docs/`: Gerenciador de documentos, formatador ABNT e cliente resiliente.
    - `rag/`: Motor vetorial (ChromaDB) com suporte a auto-recuperação.
- `main_api.py`: API RESTful com suporte a Streaming de IA e gestão de sessões.

### ⚛️ Frontend (React 19 + TypeScript)
- Localizado em `frontend/`.
- UI moderna e reativa utilizando **TailwindCSS** e **Ant Design**.
- Gestão de estado global com **Zustand** e query handling com **TanStack Query**.

### 🧪 QA & Testes (Pytest + Vitest)
- `tests/`: 36 testes de backend (unitários e integração).
- `frontend/src/__tests__/`: 6 testes de frontend (fluxo de chat e store).

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+ e Node.js 18+
- Chave de API OpenAI (em `.env`)
- Google Cloud: Arquivo `credentials.json` na raiz do projeto.

### Instalação Simplificada

1.  **Backend**:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    python -m uvicorn main_api:app --reload
    ```

2.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

---

## 🧪 Suíte de Validação

Para garantir que cada alteração seja segura, execute os testes:

```bash
# Rodar todos os testes de backend
pytest tests/

# Rodar testes de frontend
cd frontend
npm test
```

**Atualmente: 42/42 testes passando com 100% de sucesso.**

---

**Oráculo Acadêmico**: Transformando a complexidade da pesquisa científica em um processo de co-criação fluído, estável e padronizado. 🎓👨🏾‍🎓✨
