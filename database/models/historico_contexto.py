from datetime import datetime
from sqlalchemy import Integer, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from database.models.enums import StatusContexto

class HistoricoContexto(Base):
    """Modelo que armazena as versões anteriores do contexto do projeto."""
    __tablename__ = "historico_contexto"

    historico_id: Mapped[int] = mapped_column(primary_key=True)
    contexto_id: Mapped[int] = mapped_column(ForeignKey("contexto_projeto.contexto_id", ondelete="CASCADE"), nullable=False)
    conteudo_anterior: Mapped[str] = mapped_column(Text, nullable=False)
    status_anterior: Mapped[StatusContexto] = mapped_column(Enum(StatusContexto), nullable=False)
    versao_anterior: Mapped[int] = mapped_column(Integer, nullable=False)
    data_substituicao: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now(), nullable=False)

    contexto: Mapped["ContextoProjeto"] = relationship("ContextoProjeto", back_populates="historico")

    def __repr__(self) -> str:
        return f"<HistoricoContexto(historico_id={self.historico_id}, contexto_id={self.contexto_id}, versao_anterior={self.versao_anterior})>"
