import sys
import os
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.models import actor, director, film, genre, user  # Импортируем все модели

# Импортируем метаданные
from app.models.actor import Actor
from app.models.director import Director
from app.models.film import Film
from app.models.genre import Genre
from app.models.user import User

# Загружаем переменные окружения из файла .env
load_dotenv()

# Строка подключения из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Если строка подключения не была найдена в переменных окружения, можно добавить fallback:
if not DATABASE_URL:
    DATABASE_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Если все модели используют одну Base, можно указать любую модель, все метаданные будут доступны
target_metadata = Actor.metadata  # или комбинировать метаданные всех моделей

# Прочие настройки Alembic (не изменяй их)
from alembic import context

# Ранее настроенный объект Base
Base = declarative_base()

# Функции подключения и миграции
def run_migrations_online():
    # Создаём соединение с базой данных с использованием DATABASE_URL
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,  # Указываем target_metadata
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
