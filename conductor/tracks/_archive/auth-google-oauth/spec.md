# Spec: Autenticação OAuth Google com JWT em httpOnly Cookie

## Objetivo
Implementar o fluxo completo de login com Google OAuth 2.0, armazenando a sessão
em httpOnly cookie (proteção XSS) e conectando ao model Usuario do banco de dados.

## Fluxo Completo
1. Frontend: usuário clica "Entrar com Google"
2. Frontend: chama GET /api/v2/auth/google/url → recebe a URL do Google
3. Frontend: redireciona o browser para a URL do Google (window.location.href)
4. Google: autentica o usuário → redireciona para o callback do backend
5. Backend: GET /api/v2/auth/google/callback?code=...
 → troca code por access_token via Google API
 → busca perfil do usuário no Google (nome, email, foto)
 → cria ou atualiza Usuario no banco
 → gera JWT com user_id
 → seta httpOnly cookie "access_token"
 → redireciona para http://localhost:5173/dashboard
6. Frontend: carrega /dashboard com cookie já setado
7. Frontend: chama GET /api/v2/auth/me → recebe dados do usuário logado
8. Zustand auth store: armazena o usuário → dashboard renderiza

## Critérios de Aceitação
- [ ] core/config.py com Settings carregando o .env
- [ ] core/security.py com criar_token() e verificar_token()
- [ ] database/repositories/usuario_repository.py com get_by_email() e upsert()
- [ ] api/v2/routers/auth.py com 4 endpoints: /google/url, /google/callback, /me, /logout
- [ ] api/v2/dependencies.py com get_current_user() lendo o cookie
- [ ] main_api.py atualizado: CORS com credentials + router V2 registrado
- [ ] frontend/src/lib/apiClient.ts com axios withCredentials: true
- [ ] frontend/src/store/useAuthStore.ts com Zustand
- [ ] frontend/src/components/ui/ProtectedRoute.tsx
- [ ] frontend/src/router.tsx atualizado com rotas protegidas
- [ ] frontend/src/pages/auth/LoginPage.tsx conectada ao backend real
- [ ] Fluxo completo funciona: login → dashboard → /me retorna usuário
