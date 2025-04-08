from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_class import Base

if TYPE_CHECKING:
    from .film import Film

film_director_association = Table(
    "film_director_association",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("film.id"), primary_key=True),
    Column("director_id", Integer, ForeignKey("director.id"), primary_key=True)
)

# Модель режиссера
class Director(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    films = relationship("Film", secondary=film_director_association, back_populates="directors")