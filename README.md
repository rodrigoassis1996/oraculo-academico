# 👨🏾‍🎓 Oráculo Acadêmico: Ecossistema Multiagentes

O **Oráculo Acadêmico** evoluiu de um simples chat RAG para um ecossistema de **Agentes Inteligentes** especializados em análise, planejamento e escrita acadêmica. Projetado para pesquisadores e estudantes, o sistema utiliza orquestração de agentes para construir documentos científicos com rigor conceitual e precisão factual.

---

## ✨ Diferenciais Tecnológicos

- **Orquestração Multiagentes**: Arquitetura baseada em papéis técnicos onde um **Agente Orquestrador** planeja a estrutura do documento antes da execução.
- **Rigor Científico Elevado**: Integrado com skills especialistas em *AI Engineering* e *Prompt Engineering Patterns* para garantir saídas de alta fidelidade.
- **Cérebro RAG Dinâmico**: Recuperação inteligente de contexto com citações automáticas no formato acadêmico.
- **Indexação Inteligente**: Deduplicação por Hash (MD5) que economiza processamento ao reconhecer arquivos já indexados.

---

## 🤖 Sistema de Agentes (Fase 1)

Atualmente, o sistema conta com a inteligência central ativa:

1.  **Agente Orquestrador**: Atua como um Coordenador de Pesquisa. Analisa o *corpus* documental subido, entende o objetivo do usuário e propõe um "Plano de Voo" (Outline) estruturado.

---

## 🏗️ Arquitetura do Projeto

Para suportar a inteligência multiagentes, o projeto está estruturado em:

1.  **Agent Layer (`agents/`)**: Contém a lógica de raciocínio, personas e prompts especializados de cada agente.
2.  **Service Layer (`services/`)**: Gerenciadores core (`RAGManager`, `ModelManager`) que provêem ferramentas de consulta e modelos para os agentes.
3.  **Skill Vault (`.agent/skills/`)**: Módulos de conhecimento avançado (AI Engineer, Prompt Specialist, Orchestrator) que expandem as capacidades nativas do sistema.
4.  **UI Layer (`01_home.py`)**: Interface Streamlit otimizada com indicadores de status de agentes ativos.

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10 ou superior
- Chave de API (OpenAI ou compatível)

### Instalação e Execução

1.  **Clone e Prepare o Ambiente**:
    ```bash
    git clone https://github.com/rodrigoassis1996/oraculo-academico.git
    cd oraculo-academico
    python -m venv .venv
    .\.venv\Scripts\activate  # Windows
    pip install -r requirements.txt
    ```

2.  **Configure o .env**:
    ```env
    OPENAI_API_KEY=sua_chave_aqui
    ```

3.  **Inicie o Oráculo**:
    ```bash
    streamlit run 01_home.py
    ```

---

## 🧪 Notas de Qualidade

- **Testes Unitários**: O sistema inclui suítes de teste para validar a inicialização do LLM e a lógica do Orquestrador (`tests/unit/`).
- **Intelligence Validation**: Prompts construídos com técnicas de *Chain-of-Thought* para evitar alucinações.

Desenvolvido para elevar a produtividade científica com inteligência artificial de ponta. 🎓✨

