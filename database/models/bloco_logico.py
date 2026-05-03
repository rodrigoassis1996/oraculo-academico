from typing import Optional
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

class BlocoLogico(Base):
    """Modelo que representa um bloco lógico organizador de pontos norteadores."""
    __tablename__ = "blocos_logicos"

    bloco_id: Mapped[int] = mapped_column(primary_key=True)
    nome_bloco: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao_bloco: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ordem_exibicao: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    pontos: Mapped[list["PontoNorteador"]] = relationship(
        "PontoNorteador",
        back_populates="bloco",
        lazy="selectin",
        order_by="PontoNorteador.ordem_exibicao"
    )

    def __repr__(self) -> str:
        return f"<BlocoLogico(bloco_id={self.bloco_id}, nome_bloco='{self.nome_bloco}')>"
