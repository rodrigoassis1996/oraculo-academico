from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

class Projeto(Base):
    """Modelo que representa um projeto no sistema."""
    __tablename__ = "projetos"

    projeto_id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False)
    titulo_projeto: Mapped[str] = mapped_column(String(500), nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now(), nullable=False)
    data_ultima_modificacao: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=True)

    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="projetos")
    contextos: Mapped[list["ContextoProjeto"]] = relationship("ContextoProjeto", back_populates="projeto", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Projeto(projeto_id={self.projeto_id}, titulo_projeto='{self.titulo_projeto}')>"
