from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from database.repositories import usuario_repository
from core.security import verificar_token
from database.models.usuario import Usuario

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    """Dependency que extrai o usuário logado do cookie JWT."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    user_id = verificar_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    usuario = await usuario_repository.get_by_id(db, user_id)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return usuario
