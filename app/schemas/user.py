from pydantic import BaseModel, EmailStr
from typing import Optional


class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str   

class UserUpdate(BaseModel):
    new_email: Optional[EmailStr] = None
    new_password: Optional[str] = None
