from sqlalchemy.orm import Session

from app.models import User
from app.service.auth import hash_password
from app.schemas.user import UserCreate

def create_user(db: Session, user_data: UserCreate, password: str):
    password_hash = hash_password(password)  # предполагаемая функция хеширования
    print("QWEQWEQWEEW", password_hash)
    db_user = User(username=user_data.username, email=user_data.email, password_hash=password_hash,)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
