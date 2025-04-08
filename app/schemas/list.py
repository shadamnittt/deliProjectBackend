from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_class import Base

if TYPE_CHECKING:
    from .film import Film

# Модель списка фильмов (полученные с парсинга)
class List(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    films = relationship("Film", secondary="film_list_association", back_populates="lists")