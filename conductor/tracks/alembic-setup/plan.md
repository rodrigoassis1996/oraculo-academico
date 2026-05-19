# Plano: Alembic — Configuração e Migration Inicial

## Status: [~] Em Progresso

---

## Fase 1 — Inicialização do Alembic
- [x] Task 1.1: Executar na raiz do projeto:
alembic init alembic
Isso cria: alembic.ini + alembic/ com env.py, script.py.mako e versions/

- [x] Task 1.2: Configurar alembic.ini
Localizar a linha: sqlalchemy.url = driver://user:pass@localhost/dbname
Substituir por: sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/oraculo_academico
Adicionar comentário: # Sobrescrito por DATABASE_URL em env.py

Verificação da Fase 1:
- Diretório alembic/ existe com env.py, script.py.mako e versions/
- alembic.ini existe na raiz

---

## Fase 2 — Configuração do env.py para Async
- [x] Task 2.1: Substituir completamente o conteúdo de alembic/env.py pelo seguinte:

import os
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Importar Base e todos os models para detecção automática
from database.database import Base
from database.models import (  # noqa: F401
  Usuario,
  Projeto,
  BlocoLogico,
  PontoNorteador,
  ContextoProjeto,
  HistoricoContexto,
  TipoInput,
  StatusContexto,
)

# Configuração de logging do Alembic
config = context.config
if config.config_file_name is not None:
  fileConfig(config.config_file_name)

# Sobrescrever a URL com a variável de ambiente se disponível
DATABASE_URL = os.getenv(
  "DATABASE_URL",
  "postgresql+asyncpg://postgres:postgres@localhost:5432/oraculo_academico"
)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Metadata de todos os models para autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
  """Modo offline: gera SQL sem conectar ao banco."""
  url = config.get_main_option("sqlalchemy.url")
  context.configure(
      url=url,
      target_metadata=target_metadata,
      literal_binds=True,
      dialect_opts={"paramstyle": "named"},
      compare_type=True,
  )
  with context.begin_transaction():
      context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
  """Executa as migrations em uma conexão síncrona (chamado pelo async wrapper)."""
  context.configure(
      connection=connection,
      target_metadata=target_metadata,
      compare_type=True,
  )
  with context.begin_transaction():
      context.run_migrations()

async def run_async_migrations() -> None:
  """Cria engine assíncrono e executa migrations via run_sync."""
  connectable = async_engine_from_config(
      config.get_section(config.config_ini_section, {}),
      prefix="sqlalchemy.",
      poolclass=pool.NullPool,
  )
  async with connectable.connect() as connection:
      await connection.run_sync(do_run_migrations)
  await connectable.dispose()

def run_migrations_online() -> None:
  """Modo online: conecta ao banco e executa migrations."""
  asyncio.run(run_async_migrations())

if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()

- [x] Task 2.2: Verificar que o env.py importa corretamente executando:
python -c "from alembic.config import Config; from alembic import command; c = Config('alembic.ini'); print('env.py OK')"

Verificação da Fase 2:
- Comando acima executa sem erros de importação

---

## Fase 3 — Migration Inicial e Aplicação
- [ ] Task 3.1: Gerar a migration inicial com autogenerate:
alembic revision --autogenerate -m "create_all_tables"
O arquivo gerado em alembic/versions/ deve conter op.create_table()
para todas as 6 tabelas: usuarios, projetos, blocos_logicos,
pontos_norteadores, contexto_projeto, historico_contexto

- [ ] Task 3.2: Aplicar a migration ao banco PostgreSQL:
alembic upgrade head
Saída esperada: "Running upgrade -> <hash>, create_all_tables"

- [ ] Task 3.3: Verificar tabelas criadas:
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

async def check():
    url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/oraculo_academico')
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        result = await conn.execute(text(\"SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename\"))
        tabelas = [row[0] for row in result]
        print('Tabelas criadas:', tabelas)
    await engine.dispose()

asyncio.run(check())
"
Tabelas esperadas: alembic_version, blocos_logicos, contexto_projeto,
historico_contexto, pontos_norteadores, projetos, usuarios

Verificação da Fase 3:
- Migration aplicada sem erros
- 7 tabelas presentes (6 do sistema + alembic_version)
