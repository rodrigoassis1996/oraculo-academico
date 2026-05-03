# Spec: Limpeza e Reestruturação do Backend V2.0

## Objetivo
Preparar o backend para a arquitetura V2.0, removendo resquícios do protótipo V1.0,
adicionando dependências necessárias e criando a estrutura de pastas e a camada de
configuração do banco de dados.

## Contexto
O backend atual usa sessões em memória (Dict), sem banco de dados persistente e com
dependências desatualizadas. A V2.0 introduz PostgreSQL, SQLAlchemy assíncrono e uma
arquitetura orientada a serviços com API Gateway.

## Critérios de Aceitação
- [ ] requirements.txt sem youtube_transcript_api e fake_useragent
- [ ] Dependências V2.0 adicionadas (sqlalchemy, alembic, asyncpg, psycopg2-binary, python-jose, authlib, httpx)
- [ ] Pastas database/, database/models/, database/repositories/, api/, api/v2/, api/v2/routers/ criadas com __init__.py
- [ ] Arquivo database/database.py criado com AsyncEngine, AsyncSessionLocal, get_db() e create_all_tables()
- [ ] Nenhum arquivo existente fora do requirements.txt foi alterado ou deletado
- [ ] Todos os __init__.py existentes preservados

## Fora do Escopo
- Criação dos models SQLAlchemy (será feito no próximo track)
- Alteração do main_api.py
- Remoção de qualquer pasta ou módulo existente
