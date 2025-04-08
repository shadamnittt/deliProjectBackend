from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base_class import Base

# Таблицы-связки Many-to-Many
film_genre = Table(
    "film_genre", Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True)
)

film_actor = Table(
    "film_actor", Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("actor_id", Integer, ForeignKey("actors.id"), primary_key=True)
)

film_director = Table(
    "film_director", Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("director_id", Integer, ForeignKey("directors.id"), primary_key=True)
)

film_keyword = Table(
    "film_keyword", Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keywords.id"), primary_key=True)
)

class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    poster = Column(String, nullable=True)

    genres = relationship("Genre", secondary=film_genre, back_populates="films")
    actors = relationship("Actor", secondary=film_actor, back_populates="films")
    directors = relationship("Director", secondary=film_director, back_populates="films")
    keywords = relationship("Keyword", secondary=film_keyword, back_populates="films")
