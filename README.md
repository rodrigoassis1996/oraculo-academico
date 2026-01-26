# 👨🏾‍🎓 Oráculo Acadêmico

O **Oráculo Acadêmico** é um assistente de pesquisa avançado baseado em IA, projetado para realizar análise documental profunda utilizando RAG (*Retrieval Augmented Generation*). Ele permite que pesquisadores, estudantes e profissionais interajam com múltiplos documentos de forma inteligente, obtendo respostas estruturadas e fundamentadas.

---

## ✨ Principais Funcionalidades

- **Multi-Formato**: Suporte nativo para PDF, DOCX, TXT, CSV e extração de conteúdo diretamente de URLs (Sites).
- **Cérebro RAG (Persistente)**: Utiliza ChromaDB para manter um índice vetorial persistente. Seus documentos sobrevivem ao reinício da aplicação.
- **Indexação Incremental**: Graças à deduplicação por Hash (MD5), o sistema identifica arquivos já processados e pula etapas desnecessárias de embedding, economizando tempo e processamento.
- **Persona Acadêmica Sênior**: Prompt refinado para atuar como um pesquisador experiente, focando em síntese multi-documento e rigor factual.
- **Gestão de Dados**: Controle total sobre o armazenamento local através de botões de limpeza de sessão e purga física de dados.
- **Interface Fluida**: UI construída em Streamlit otimizada para longas conversas e validação de contexto (Debug Tab).

---

## 🏗️ Arquitetura do Projeto

O projeto segue uma arquitetura de 3 camadas para garantir escalabilidade e manutenção:

1.  **Execution Layer (`execution/`)**: Scripts independentes para ingestão e extração de texto bruto (OCR/Leitura).
2.  **Service Layer (`services/`)**: Gerenciadores de lógica de negócio (`UploadManager`, `RAGManager`, `ModelManager`) que orquestram a comunicação entre a interface e o processamento pesado.
3.  **UI Layer (`components/` & `01_home.py`)**: Componentes visuais e fluxo do usuário em Streamlit.

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10 ou superior
- Uma chave de API da OpenAI (ou outro provedor configurado)

### Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/rodrigoassis1996/oraculo-academico.git
    cd oraculo-academico
    ```

2.  Crie e ative um ambiente virtual:
    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure as variáveis de ambiente:
    Crie um arquivo `.env` na raiz do projeto:
    ```env
    OPENAI_API_KEY=sua_chave_aqui
    ```

### Rodando o App
```bash
streamlit run 01_home.py
```

---

## ⚙️ Configurações Centralizadas

Toda a calibração do sistema pode ser feita no arquivo `config/settings.py`, onde você encontrará:
- Parâmetros do RAG (`top_k`, `chunk_size`, `overlap`)
- Configuração de Modelos (GPT-4o, etc.)
- Prompts de Sistema (Customização da Persona)
- Limites de Upload e Extensões Permitidas

---

## 🧪 Notas de Desenvolvimento

- **Sincronização de Sessão**: O sistema sincroniza automaticamente o banco vetorial local com os arquivos visíveis na tela.
- **Lifecycle Management**: Arquivos temporários com mais de 48h são removidos automaticamente para evitar acúmulo de lixo eletrônico.

Desenvolvido para auxiliar no rigor e na produtividade da pesquisa acadêmica moderna. 🎓✨
