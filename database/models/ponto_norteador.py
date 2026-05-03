from typing import Optional, Any
from sqlalchemy import String, Integer, Text, Boolean, JSON, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from database.models.enums import TipoInput

class PontoNorteador(Base):
    """Modelo que representa um ponto norteador de um bloco lógico."""
    __tablename__ = "pontos_norteadores"

    ponto_id: Mapped[int] = mapped_column(primary_key=True)
    bloco_id: Mapped[int] = mapped_column(ForeignKey("blocos_logicos.bloco_id", ondelete="RESTRICT"), nullable=False)
    nome_ponto: Mapped[str] = mapped_column(String(255), nullable=False)
    pergunta_agente: Mapped[str] = mapped_column(Text, nullable=False)
    proposito_ponto: Mapped[str] = mapped_column(Text, nullable=False)
    instrucao_agente: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exemplo_resposta: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tipo_input: Mapped[TipoInput] = mapped_column(Enum(TipoInput), default=TipoInput.TEXTO_LIVRE, nullable=False)
    opcoes_selecao: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    e_obrigatorio: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    ordem_exibicao: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("bloco_id", "ordem_exibicao", name="uq_ponto_bloco_ordem"),
    )

    bloco: Mapped["BlocoLogico"] = relationship("BlocoLogico", back_populates="pontos")

    def __repr__(self) -> str:
        return f"<PontoNorteador(ponto_id={self.ponto_id}, nome_ponto='{self.nome_ponto}')>"
