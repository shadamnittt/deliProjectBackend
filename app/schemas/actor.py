from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_class import Base

if TYPE_CHECKING:
    from .film import Film

# Связующая таблица для отношения многие-ко-многим между Film и Actor/Director
film_actor_association = Table(
    "film_actor_association",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("film.id"), primary_key=True),
    Column("actor_id", Integer, ForeignKey("actor.id"), primary_key=True)
)

# Модель актера/режиссера
class Actor(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    films = relationship("Film", secondary=film_actor_association, back_populates="actors")