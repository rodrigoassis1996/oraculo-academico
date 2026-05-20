from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.usuario import Usuario

async def get_by_id(db: AsyncSession, usuario_id: int) -> Usuario | None:
    """Busca usuário por ID primário."""
    result = await db.execute(select(Usuario).where(
        Usuario.usuario_id == usuario_id))
    return result.scalar_one_or_none()

async def get_by_email(db: AsyncSession, email: str) -> Usuario | None:
    """Busca usuário por email."""
    result = await db.execute(select(Usuario).where(Usuario.email == email))
    return result.scalar_one_or_none()

async def upsert_google_user(
    db: AsyncSession,
    google_id: str,
    nome: str,
    email: str,
    foto_perfil: str | None
) -> Usuario:
    """Cria ou atualiza usuário autenticado via Google."""
    result = await db.execute(select(Usuario).where(
        Usuario.auth_provider_id == google_id))
    usuario = result.scalar_one_or_none()

    if usuario:
        usuario.nome = nome
        usuario.email = email
        usuario.foto_perfil = foto_perfil
    else:
        usuario = Usuario(
            auth_provider="google",
            auth_provider_id=google_id,
            nome=nome,
            email=email,
            foto_perfil=foto_perfil,
        )
        db.add(usuario)

    await db.commit()
    await db.refresh(usuario)
    return usuario
