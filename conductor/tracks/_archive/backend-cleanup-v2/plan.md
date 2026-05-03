# Plano: Limpeza e Reestruturação do Backend V2.0

## Status: [x] Complete

---

## Fase 1 — Limpeza de Dependências
- [x] Task 1.1: Remover youtube_transcript_api e fake_useragent do requirements.txt
- [x] Task 1.2: Adicionar bloco "# V2.0 — Database & Auth" ao requirements.txt com: sqlalchemy==2.0.36, alembic==1.14.0, asyncpg==0.30.0, psycopg2-binary==2.9.10, python-jose[cryptography]==3.3.0, authlib==1.3.2, httpx==0.27.2

Verificação da Fase 1:
- requirements.txt não contém youtube_transcript_api nem fake_useragent
- Todas as dependências V2.0 estão presentes com versões fixas

---

## Fase 2 — Estrutura de Pastas
- [x] Task 2.1: Criar database/__init__.py (vazio)
- [x] Task 2.2: Criar database/models/__init__.py (vazio)
- [x] Task 2.3: Criar database/repositories/__init__.py (vazio)
- [x] Task 2.4: Criar api/__init__.py, api/v2/__init__.py, api/v2/routers/__init__.py (todos vazios)

Verificação da Fase 2:
- Todas as pastas existem com __init__.py
- Nenhum arquivo preexistente foi alterado

---

## Fase 3 — Configuração do Banco de Dados
- [x] Task 3.1: Criar database/database.py com configuração assíncrona do SQLAlchemy
- [x] Task 3.2: Verificar importações e sintaxe do database.py

Verificação da Fase 3:
- database/database.py importa sem erros (python -c "from database.database import get_db")
- DATABASE_URL lê da variável de ambiente com fallback correto
- Funções get_db() e create_all_tables() estão presentes e tipadas
