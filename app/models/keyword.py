from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base_class import Base
from app.models.film import film_keyword

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    films = relationship("Film", secondary=film_keyword, back_populates="keywords")
