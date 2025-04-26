from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.models.base_class import Base
import enum

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user)  # Здесь Enum импортирован правильно

