# Plano: Models SQLAlchemy 2.0 — Modelo Relacional Completo

## Status: [x] Complete

---

## Fase 1 — Enums Compartilhados
- [x] Task 1.1: Criar database/models/enums.py

Conteúdo:
from enum import Enum

class TipoInput(str, Enum):
    """Tipos de input suportados para pontos norteadores."""
    TEXTO_LIVRE = "TEXTO_LIVRE"
    LISTA_NUMERADA = "LISTA_NUMERADA"
    SELECAO_UNICA = "SELECAO_UNICA"
    SELECAO_MULTIPLA = "SELECAO_MULTIPLA"
    BOOLEANO = "BOOLEANO"

class StatusContexto(str, Enum):
    """Estados do ciclo de vida de um contexto de projeto."""
    PENDENTE = "PENDENTE"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    RASCUNHO = "RASCUNHO"
    RESPONDIDO = "RESPONDIDO"
    REVISADO = "REVISADO"
    IGNORADO = "IGNORADO"

Verificação da Fase 1:
- python -c "from database.models.enums import TipoInput, StatusContexto; print('OK')"

---

## Fase 2 — Models Independentes
- [x] Task 2.1: Criar database/models/usuario.py

Campos: usuario_id (PK), auth_provider (VARCHAR 50, not null),
auth_provider_id (VARCHAR 255, not null, unique), nome (VARCHAR 255, not null),
email (VARCHAR 255, not null, unique), foto_perfil (TEXT, nullable),
is_admin (BOOLEAN, default False), data_criacao (TIMESTAMP, default now()),
ultimo_login (TIMESTAMP, nullable)
Relacionamento: projetos → list[Projeto] com back_populates="usuario", lazy="selectin"

- [x] Task 2.2: Criar database/models/bloco_logico.py

Campos: bloco_id (PK), nome_bloco (VARCHAR 255, not null),
descricao_bloco (TEXT, nullable), ordem_exibicao (INT, not null, unique)
Relacionamento: pontos → list[PontoNorteador] com back_populates="bloco",
lazy="selectin", order_by=PontoNorteador.ordem_exibicao

Verificação da Fase 2:
- python -c "from database.models.usuario import Usuario; from database.models.bloco_logico import BlocoLogico; print('OK')"

---

## Fase 3 — Models de Primeira Dependência
- [x] Task 3.1: Criar database/models/projeto.py

Campos: projeto_id (PK), usuario_id (FK → usuarios.usuario_id, ondelete="CASCADE"),
titulo_projeto (VARCHAR 500, not null), data_criacao (TIMESTAMP, default now()),
data_ultima_modificacao (TIMESTAMP, nullable, onupdate=datetime.utcnow)
Relacionamentos: usuario → Usuario (back_populates="projetos"),
contextos → list[ContextoProjeto] (back_populates="projeto", lazy="selectin")

- [x] Task 3.2: Criar database/models/ponto_norteador.py

Campos: ponto_id (PK), bloco_id (FK → blocos_logicos.bloco_id, ondelete="RESTRICT"),
nome_ponto (VARCHAR 255, not null), pergunta_agente (TEXT, not null),
proposito_ponto (TEXT, not null), instrucao_agente (TEXT, nullable),
exemplo_resposta (TEXT, nullable), tipo_input (Enum TipoInput, default TEXTO_LIVRE),
opcoes_selecao (JSON, nullable), e_obrigatorio (BOOLEAN, not null, default True),
ordem_exibicao (INT, not null)
UniqueConstraint: (bloco_id, ordem_exibicao)
Relacionamento: bloco → BlocoLogico (back_populates="pontos")

Verificação da Fase 3:
- python -c "from database.models.projeto import Projeto; from database.models.ponto_norteador import PontoNorteador; print('OK')"

---

## Fase 4 — Models de Segunda Dependência
- [x] Task 4.1: Criar database/models/contexto_projeto.py

Campos: contexto_id (PK), projeto_id (FK → projetos.projeto_id, ondelete="CASCADE"),
ponto_id (FK → pontos_norteadores.ponto_id, ondelete="RESTRICT"),
conteudo (TEXT, nullable), status (Enum StatusContexto, default PENDENTE),
versao (INT, not null, default 1), data_resposta (TIMESTAMP, nullable),
data_modificacao (TIMESTAMP, nullable)
UniqueConstraint: (projeto_id, ponto_id)
Relacionamentos: projeto → Projeto (back_populates="contextos"),
ponto → PontoNorteador, historico → list[HistoricoContexto]
(back_populates="contexto", lazy="selectin")

- [x] Task 4.2: Criar database/models/historico_contexto.py

Campos: historico_id (PK), contexto_id (FK → contexto_projeto.contexto_id, ondelete="CASCADE"),
conteudo_anterior (TEXT, not null), status_anterior (Enum StatusContexto, not null),
versao_anterior (INT, not null), data_substituicao (TIMESTAMP, not null, default now())
Relacionamento: contexto → ContextoProjeto (back_populates="historico")
Observação: tabela append-only — nunca deve receber UPDATE, apenas INSERT

Verificação da Fase 4:
- python -c "from database.models.contexto_projeto import ContextoProjeto; from database.models.historico_contexto import HistoricoContexto; print('OK')"

---

## Fase 5 — Integração e Validação Final
- [x] Task 5.1: Atualizar database/models/__init__.py exportando todos os symbols:
from database.models.enums import TipoInput, StatusContexto
from database.models.usuario import Usuario
from database.models.bloco_logico import BlocoLogico
from database.models.projeto import Projeto
from database.models.ponto_norteador import PontoNorteador
from database.models.contexto_projeto import ContextoProjeto
from database.models.historico_contexto import HistoricoContexto
__all__ com todos os nomes acima

- [x] Task 5.2: Validar importação completa e ausência de circular imports
Comando: python -c "from database.models import *; print('Todos os models importados com sucesso')"

Verificação da Fase 5:
- Comando acima executa sem erros ou warnings
- Todos os __tablename__ são únicos e em snake_case
- Todos os relacionamentos têm back_populates correspondente
