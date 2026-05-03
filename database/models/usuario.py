from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

class Usuario(Base):
    """Modelo que representa um usuário do sistema."""
    __tablename__ = "usuarios"

    usuario_id: Mapped[int] = mapped_column(primary_key=True)
    auth_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    auth_provider_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    foto_perfil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now(), nullable=False)
    ultimo_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    projetos: Mapped[list["Projeto"]] = relationship("Projeto", back_populates="usuario", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Usuario(usuario_id={self.usuario_id}, nome='{self.nome}', email='{self.email}')>"
