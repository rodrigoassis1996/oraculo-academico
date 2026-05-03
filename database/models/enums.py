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
