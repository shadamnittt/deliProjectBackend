from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, func, Integer, String, Text, TIMESTAMP, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_class import Base

if TYPE_CHECKING:
    from .user import User

# Связующая таблица для отношения многие-ко-многим между Film и Genre
film_genre_association = Table(
    "film_genre_association",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("film.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genre.id"), primary_key=True)
)

class Film(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    director: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    author: Mapped["User"] = relationship("User", back_populates="films")
    genres = relationship("Genre", secondary=film_genre_association, back_populates="films")
