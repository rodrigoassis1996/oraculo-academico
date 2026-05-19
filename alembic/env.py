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
