from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.service.hashing import Hasher  # Мы используем твой хешировщик паролей
from app.schemas.user import UserCreate

def get_user_by_username(db: Session, username: str):
    """
    Получение пользователя по username.
    """
    query = select(User).filter(User.username == username)
    return db.execute(query).scalar_one_or_none()  # Лучше scalar_one_or_none()

def create_user(user: UserCreate, db: Session):
    new_user = User(
        username=user.username,
        password_hash=user.password,  # password = уже хеш, это норм
        role=user.role                # ❗️ты забыл передать роль!
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def show_users(db: Session):
    """
    Получение списка всех пользователей.
    """
    query = select(User)
    return db.execute(query).scalars().all()
