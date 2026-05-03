# Spec: Models SQLAlchemy 2.0 — Modelo Relacional Completo

## Objetivo
Criar os models SQLAlchemy 2.0 para as 6 tabelas do sistema, usando a sintaxe moderna
(Mapped, mapped_column, DeclarativeBase) e respeitando todos os relacionamentos,
constraints e enums definidos na arquitetura.

## Dependências
- database/database.py deve existir com a classe Base exportada
- Pasta database/models/ deve existir com __init__.py vazio

## Modelo Relacional
USUARIOS (1) → (N) PROJETOS
PROJETOS (1) → (N) CONTEXTO_PROJETO
BLOCOS_LOGICOS (1) → (N) PONTOS_NORTEADORES
PONTOS_NORTEADORES (1) → (N) CONTEXTO_PROJETO
CONTEXTO_PROJETO (1) → (N) HISTORICO_CONTEXTO

## Critérios de Aceitação
- [ ] database/models/enums.py com TipoInput e StatusContexto como str+Enum
- [ ] database/models/usuario.py com model Usuario completo
- [ ] database/models/bloco_logico.py com model BlocoLogico completo
- [ ] database/models/projeto.py com model Projeto completo
- [ ] database/models/ponto_norteador.py com model PontoNorteador completo
- [ ] database/models/contexto_projeto.py com model ContextoProjeto completo
- [ ] database/models/historico_contexto.py com model HistoricoContexto completo
- [ ] database/models/__init__.py exporta todos os models e enums
- [ ] python -c "from database.models import *" executa sem erros
- [ ] Nenhum circular import

## Padrões Obrigatórios
- Sintaxe SQLAlchemy 2.0: Mapped[T] e mapped_column() em todos os campos
- Base importada de database.database (não redefinir)
- Enums Python do tipo class X(str, Enum) para serialização JSON correta
- __tablename__ em snake_case em cada model
- __repr__ em cada model
- Docstrings em português no topo de cada classe
- Sem lógica de negócio nos models
