import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Загружаем переменные окружения
load_dotenv()

# Берём URL базы данных из .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаём синхронный движок
engine = create_engine(DATABASE_URL, echo=True)

# Создаём фабрику сессий
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Определяем базовый класс для моделей
Base = declarative_base()
# Функция для получения сессии (с использованием `yield`)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
