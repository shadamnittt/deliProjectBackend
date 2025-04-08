from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base_class import Base
from app.models.film import film_actor

class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    films = relationship("Film", secondary=film_actor, back_populates="actors")
