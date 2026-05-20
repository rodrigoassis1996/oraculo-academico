import httpx
from urllib.parse import urlencode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from database.repositories import usuario_repository
from core.config import settings
from core.security import criar_access_token
from api.v2.dependencies import get_current_user
from database.models.usuario import Usuario

router = APIRouter(prefix="/api/v2/auth", tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

@router.get("/google/url")
async def google_auth_url():
    """Retorna a URL de autenticação do Google."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return {"url": url}

@router.get("/google/callback")
async def google_auth_callback(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """Recebe o código do Google, cria/atualiza usuário e seta o cookie JWT."""
    async with httpx.AsyncClient() as client:
        # 1. Trocar code por access_token
        token_response = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        if token_response.status_code != 200:
            raise HTTPException(status_code=400,
                                detail="Falha ao trocar código pelo token Google")
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        # 2. Buscar dados do usuário no Google
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=400,
                                detail="Falha ao buscar dados do usuário no Google")
        userinfo = userinfo_response.json()

    # 3. Criar ou atualizar usuário no banco
    usuario = await usuario_repository.upsert_google_user(
        db=db,
        google_id=userinfo["id"],
        nome=userinfo.get("name", ""),
        email=userinfo.get("email", ""),
        foto_perfil=userinfo.get("picture"),
    )

    # 4. Gerar JWT e setar cookie httpOnly
    jwt_token = criar_access_token(usuario.usuario_id)
    redirect_url = f"{settings.FRONTEND_URL}/dashboard"
    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        samesite="lax",
        secure=False,  # True em produção com HTTPS
        max_age=settings.JWT_EXPIRE_MINUTES * 60,
    )
    return response

@router.get("/me")
async def get_me(usuario: Usuario = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado."""
    return {
        "id": usuario.usuario_id,
        "nome": usuario.nome,
        "email": usuario.email,
        "fotoPerfil": usuario.foto_perfil,
        "role": "admin" if usuario.is_admin else "pesquisador",
    }

@router.post("/logout")
async def logout():
    """Remove o cookie de sessão."""
    response = JSONResponse(content={"message": "Logout realizado com sucesso"})
    response.delete_cookie(key="access_token")
    return response
