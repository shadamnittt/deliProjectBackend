from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base_class import Base
from app.models.film import film_genre

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    films = relationship("Film", secondary=film_genre, back_populates="genres")
