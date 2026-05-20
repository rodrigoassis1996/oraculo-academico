# Plano: Autenticação OAuth Google com JWT em httpOnly Cookie

## Status: [~] Em Progresso

---

## Fase 1 — Backend Core
- [x] Task 1.1: Criar core/__init__.py (vazio)

- [x] Task 1.2: Criar core/config.py

Conteúdo:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/api/v2/auth/google/callback"
    )
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/oraculo_academico"
    )

settings = Settings()
```

- [x] Task 1.3: Criar core/security.py

Conteúdo:
```python
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
```

- [x] Task 1.4: Criar database/repositories/usuario_repository.py

Conteúdo:
```python
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
```

Verificação da Fase 1:
- python -c "from core.config import settings; from core.security import criar_access_token; print('OK')"
- python -c "from database.repositories.usuario_repository import get_by_email; print('OK')"

---

## Fase 2 — Backend Auth Routes
- [x] Task 2.1: Criar api/v2/dependencies.py

Conteúdo:
```python
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
```

- [x] Task 2.2: Criar api/v2/routers/auth.py

Conteúdo:
```python
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
```

- [x] Task 2.3: Atualizar main_api.py

Adicionar no topo (após os imports existentes):
```python
from dotenv import load_dotenv
load_dotenv()
from api.v2.routers.auth import router as auth_router_v2
```

Substituir o CORSMiddleware existente:
DE: `allow_origins=["*"]`
PARA:
```python
from core.config import settings
allow_origins=[settings.FRONTEND_URL]
allow_credentials=True  (ADICIONAR esta linha)
```

Adicionar após a criação do app:
```python
app.include_router(auth_router_v2)
```

Verificação da Fase 2:
- uvicorn main_api:app --reload
- GET http://localhost:8000/api/v2/auth/google/url deve retornar {"url": "https://..."}
- GET http://localhost:8000/docs deve mostrar os endpoints /api/v2/auth/*

---

## Fase 3 — Frontend Auth
- [x] Task 3.1: Criar frontend/src/lib/apiClient.ts

Conteúdo:
```typescript
import axios from 'axios'

/** Cliente Axios configurado para enviar cookies em todas as requisições */
export const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,  // envia httpOnly cookies automaticamente
  headers: { 'Content-Type': 'application/json' },
})

/** Busca dados do usuário autenticado */
export async function fetchUsuarioAtual() {
  const response = await apiClient.get('/api/v2/auth/me')
  return response.data
}

/** Busca a URL de autenticação do Google */
export async function fetchGoogleAuthUrl(): Promise<string> {
  const response = await apiClient.get('/api/v2/auth/google/url')
  return response.data.url
}

/** Realiza logout */
export async function logout() {
  await apiClient.post('/api/v2/auth/logout')
}
```

- [x] Task 3.2: Criar frontend/src/store/useAuthStore.ts

Conteúdo:
```typescript
import { create } from 'zustand'
import type { Usuario } from '../types'
import { fetchUsuarioAtual, fetchGoogleAuthUrl, logout as logoutApi } from '../lib/apiClient'

interface AuthState {
  usuario: Usuario | null
  isLoading: boolean
  isAuthenticated: boolean
  carregarUsuario: () => Promise<void>
  iniciarLoginGoogle: () => Promise<void>
  logout: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  usuario: null,
  isLoading: true,
  isAuthenticated: false,

  carregarUsuario: async () => {
    set({ isLoading: true })
    try {
      const usuario = await fetchUsuarioAtual()
      set({ usuario, isAuthenticated: true, isLoading: false })
    } catch {
      set({ usuario: null, isAuthenticated: false, isLoading: false })
    }
  },

  iniciarLoginGoogle: async () => {
    try {
      const url = await fetchGoogleAuthUrl()
      window.location.href = url
    } catch {
      console.error('Erro ao obter URL de autenticação Google')
    }
  },

  logout: async () => {
    try {
      await logoutApi()
    } finally {
      set({ usuario: null, isAuthenticated: false })
      window.location.href = '/login'
    }
  },
}))
```

- [x] Task 3.3: Criar frontend/src/components/ui/ProtectedRoute.tsx

Conteúdo:
```tsx
import React, { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../../store/useAuthStore'

interface ProtectedRouteProps {
  children: React.ReactNode
}

/** Redireciona para /login se o usuário não estiver autenticado */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { usuario, isLoading, carregarUsuario } = useAuthStore()

  useEffect(() => {
    carregarUsuario()
  }, [carregarUsuario])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface">
        <div className="w-8 h-8 border-4 border-primary-fixed-dim border-t-transparent
                        rounded-full animate-spin" />
      </div>
    )
  }

  if (!usuario) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
```

- [x] Task 3.4: Atualizar frontend/src/lib/router.tsx

Importar ProtectedRoute e envolver a rota /dashboard:

DE:
```tsx
  { path: '/dashboard', element: <DashboardPage /> }
```

PARA:
```tsx
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    )
  }
```

A rota /login deve permanecer sem proteção.

- [ ] Task 3.5: Atualizar frontend/src/pages/auth/LoginPage.tsx

Substituir o handler do botão "Entrar com Google":

DE:
```tsx
  <LoginPage onGoogleLogin={() => console.log('login google')} />
  (ou como estiver atualmente)
```

PARA — no componente LoginPage, conectar ao authStore:
  Adicionar import: `import { useAuthStore } from '../../store/useAuthStore'`
  Dentro do componente:
    `const { iniciarLoginGoogle } = useAuthStore()`
  No botão "Entrar com Google":
    `onClick={iniciarLoginGoogle}`

Verificação da Fase 3:
- npm run build sem erros
- npm run lint sem erros

---

## Fase 4 — Validação End-to-End
- [ ] Task 4.1: Iniciar backend: uvicorn main_api:app --reload
- [ ] Task 4.2: Iniciar frontend: cd frontend && npm run dev
- [ ] Task 4.3: Acessar http://localhost:5173/login
Clicar em "Entrar com Google"
Autenticar com uma conta Google
Verificar redirecionamento para /dashboard
- [ ] Task 4.4: Verificar GET http://localhost:8000/api/v2/auth/me retorna dados do usuário
- [ ] Task 4.5: Verificar que /dashboard sem login redireciona para /login

Verificação da Fase 4:
- Login completo funciona end-to-end
- Cookie "access_token" aparece nas DevTools (httpOnly, não acessível via JS)
- /dashboard sem cookie → redireciona para /login
