from datetime import datetime, timedelta
from jose import jwt, JWTError
from core.config import settings

def criar_access_token(user_id: int) -> str:
    """Gera JWT com user_id como subject."""
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY,
                      algorithm=settings.JWT_ALGORITHM)

def verificar_token(token: str) -> int | None:
    """Decodifica o JWT e retorna o user_id. Retorna None se inválido."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY,
                             algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except JWTError:
        return None
