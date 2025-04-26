from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.service.dependencies import get_current_user
from app.orm.profile import upload_avatar
from app.schemas.user import UserOut
from app.models.user import User
from sqlalchemy.orm import Session
from app.database import get_db

api_router = APIRouter()

@api_router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    # Возвращаем текущего пользователя
    return current_user

@api_router.post("/upload_avatar")
def new_avatar(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Загрузка аватара
    return upload_avatar(file=file, db=db, user=user)