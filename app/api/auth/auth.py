from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from sqlalchemy import or_
from app.database import get_db
from app.models import Actor, User, Film, Genre, Director
from app.models.user import UserRole
from app.service.auth import verify_password, create_access_token, get_password_hash
from app.schemas.user import UserLogin, UserCreate, UserUpdate
from app.orm.user import create_user
from app.service.hashing import Hasher
from app.tasks import parse_films_task  
from app.service.dependencies import is_admin

router = APIRouter()

def create_admin_if_not_exists(db: Session):
    # Проверяем, существует ли админ
    existing_admin = db.query(User).filter(User.username == "queen").first()
    if not existing_admin:
        # Если администратора нет, создаем его
        admin_user = User(
            username="queen",  # Можно изменить на желаемое имя
            password_hash=get_password_hash("secret"),  # Установите безопасный пароль
            role=UserRole.admin  # Назначаем роль администратора
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print("Admin user created.")

def init_admin():
    db_generator = get_db()
    db = next(db_generator)
    try:
        create_admin_if_not_exists(db)
    finally:
        db_generator.close()

init_admin()

@router.get("/admin/users_lists")
def admin_dashboard(db: Session = Depends(get_db), current_user: User = Depends(is_admin)):
    # Получаем список всех пользователей
    users = db.query(User).all()
    return {"users": users}

@router.post("/admin/parse_films")
def parse_films(db: Session = Depends(get_db), current_user: User = Depends(is_admin)):
    # Запускаем парсинг фильмов через Celery
    parse_films_task.delay()  # Запуск задачи парсинга в фоне
    return {"message": "Парсинг фильмов запущен"}

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    if user_data.username == "queen" and user_data.password == "secret":
        access_token = create_access_token(
            data={"sub": "queen"},
            expires_delta=timedelta(days=30)  # Токен для админа действует 30 дней
        )
        return {"access_token": access_token, "token_type": "bearer"}

    # Получаем пользователя из базы по имени пользователя
    user = db.query(User).filter(User.username == user_data.username).first()
    print(user, user_data.password, user.password_hash, verify_password(user_data.password, user.password_hash))
    
    # Проверяем, существует ли пользователь и совпадает ли пароль
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Создаём токен доступа с данными пользователя
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=120)  # Время жизни токена
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверка на существование пользователя с таким же username
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Если это админ (с username и паролем)
    if user_data.username == "queen" and user_data.password == "secret":
        user_data.role = UserRole.admin  # Назначаем роль админа
    else:
        user_data.role = UserRole.user

    # Хешируем пароль перед сохранением
    user_data.password = get_password_hash(user_data.password)
    
    # Создаём нового пользователя
    new_user = create_user(user_data, db)
    
    return {"username": new_user.username}

@router.delete("/delete/{username}")
def delete_account(username: str, db: Session = Depends(get_db)):
    # Получаем пользователя по имени
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Удаляем пользователя из базы
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.put("update/{username}")
def update_account(username: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    # Получаем пользователя по имени
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Обновляем данные пользователя
    if user_update.new_username:
        user.username = user_update.new_username
    if user_update.new_password:
        user.password_hash = get_password_hash(user_update.new_password)

    db.commit()
    return {"message": "User updated successfully"}

@router.get("/search")
def search_movies(query: str, db: Session = Depends(get_db)):
    words = query.split()
    filters = []
    for word in words:
        ilike = f"%{word}%"
        filters += [
            Film.title.ilike(ilike),
            Film.description.ilike(ilike),
            Genre.name.ilike(ilike),
            Director.name.ilike(ilike),
        ]

    movies = db.query(Film)\
        .join(Film.genres)\
        .join(Film.directors)\
        .join(Film.actors)\
        .filter(or_(*filters))\
        .distinct()\
        .all()

    return movies