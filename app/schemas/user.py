from pydantic import BaseModel
from typing import Optional
from app.models.user import UserRole

# Схема для логина пользователя
class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True

# Схема для создания нового пользователя
class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.user

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    new_username: Optional[str] = None
    new_password: Optional[str] = None

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    username: str
    avatar_url: str

    class Config:
        orm_mode = True
