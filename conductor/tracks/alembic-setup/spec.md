# Spec: Alembic — Configuração e Migration Inicial

## Objetivo
Configurar o Alembic para gerenciar migrations do banco PostgreSQL, integrado com
o SQLAlchemy 2.0 assíncrono do projeto, e criar a migration inicial que gera todas
as tabelas definidas nos models.

## Contexto Técnico
- SQLAlchemy 2.0 com AsyncEngine (asyncpg driver)
- Alembic precisa de configuração especial para rodar com async
- O env.py padrão do Alembic é síncrono — precisa ser sobrescrito
- Enums Python (TipoInput, StatusContexto) serão criados como tipos nativos no PostgreSQL

## Critérios de Aceitação
- [ ] Diretório alembic/ criado na raiz do projeto com estrutura padrão
- [ ] alembic.ini configurado com sqlalchemy.url lendo da variável de ambiente
- [ ] alembic/env.py configurado para SQLAlchemy 2.0 async (asyncio + async_engine_from_config)
- [ ] Todos os models importados no env.py para detecção automática
- [ ] Migration inicial gerada com --autogenerate detectando todas as tabelas
- [ ] Migration aplicada com sucesso: alembic upgrade head
- [ ] Tabelas criadas no PostgreSQL e verificadas

## Fora do Escopo
- Seed de dados iniciais
- Migrations futuras (serão criadas conforme o projeto evolui)
