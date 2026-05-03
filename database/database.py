import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import DeclarativeBase

# Configuração de logging estruturado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fallback URL conforme especificado
DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/oraculo_academico"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

def _mask_url(url: str) -> str:
    """
    Masca a senha na URL do banco de dados para logging seguro.
    
    Args:
        url (str): A URL original do banco de dados.
        
    Returns:
        str: URL com a senha mascarada (ex: postgres:***@localhost).
    """
    try:
        if "@" in url and "://" in url:
            prefix, rest = url.split("://", 1)
            if "@" in rest:
                credentials, address = rest.split("@", 1)
                if ":" in credentials:
                    username = credentials.split(":")[0]
                    return f"{prefix}://{username}:***@{address}"
    except Exception:
        pass
    return "***masked_url***"

# Log da URL mascarada sem expor a senha
logger.info(f"Inicializando conexão com o banco de dados em: {_mask_url(DATABASE_URL)}")

# Criação do motor assíncrono
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False
)

# Criador de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Base declarativa para os modelos (será usada pelos models)
class Base(DeclarativeBase):
    """Classe base declarativa para todos os models SQLAlchemy 2.0 do projeto."""
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injetável para rotas do FastAPI.
    Garante a criação e fechamento seguro da sessão do banco de dados por requisição.
    
    Yields:
        AsyncSession: Uma sessão de banco de dados assíncrona.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_all_tables() -> None:
    """
    Cria todas as tabelas no banco de dados baseado nos metadados declarativos.
    Usado tipicamente durante a inicialização da aplicação (startup event).
    """
    try:
        logger.info("Criando as tabelas no banco de dados...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tabelas criadas com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise
