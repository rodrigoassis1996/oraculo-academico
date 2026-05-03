from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Text, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from database.models.enums import StatusContexto

class ContextoProjeto(Base):
    """Modelo que representa o contexto respondido de um ponto norteador para um projeto."""
    __tablename__ = "contexto_projeto"

    contexto_id: Mapped[int] = mapped_column(primary_key=True)
    projeto_id: Mapped[int] = mapped_column(ForeignKey("projetos.projeto_id", ondelete="CASCADE"), nullable=False)
    ponto_id: Mapped[int] = mapped_column(ForeignKey("pontos_norteadores.ponto_id", ondelete="RESTRICT"), nullable=False)
    conteudo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[StatusContexto] = mapped_column(Enum(StatusContexto), default=StatusContexto.PENDENTE, nullable=False)
    versao: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    data_resposta: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    data_modificacao: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("projeto_id", "ponto_id", name="uq_contexto_projeto_ponto"),
    )

    projeto: Mapped["Projeto"] = relationship("Projeto", back_populates="contextos")
    ponto: Mapped["PontoNorteador"] = relationship("PontoNorteador")
    historico: Mapped[list["HistoricoContexto"]] = relationship("HistoricoContexto", back_populates="contexto", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ContextoProjeto(contexto_id={self.contexto_id}, projeto_id={self.projeto_id}, ponto_id={self.ponto_id})>"
