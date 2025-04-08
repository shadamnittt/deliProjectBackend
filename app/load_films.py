import json
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.film import Film
from app.models.genre import Genre
from app.models.actor import Actor
from app.models.director import Director

# Загружаем переменные окружения
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаём асинхронный движок и сессию
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Загружаем JSON один раз
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "films.json")
with open(file_path, "r", encoding="utf-8") as file:
    films_data = json.load(file)

async def load_films():
    async with AsyncSessionLocal() as session:
        try:
            for film in films_data:
                print(f"Добавление фильма: {film['title']}")  # Для проверки

                # Проверяем, есть ли такой режиссёр
                director = await session.execute(
                    Director.__table__.select().where(Director.name == film["director"])
                )
                director = director.scalar()
                if not director:
                    director = Director(name=film["director"])
                    session.add(director)
                    await session.flush()  # Сохранение в БД, чтобы получить ID

                # Создаём объект фильма
                new_film = Film(
                    title=film["title"],
                    year=int(film["year"]),
                    description=film["description"],
                    director_id=director.id
                )

                # Добавляем жанры
                genres = []
                for genre_name in film["genres"].split(", "):
                    genre = await session.execute(
                        Genre.__table__.select().where(Genre.name == genre_name)
                    )
                    genre = genre.scalar()
                    if not genre:
                        genre = Genre(name=genre_name)
                        session.add(genre)
                        await session.flush()
                    genres.append(genre)
                new_film.genres = genres

                # Добавляем актёров
                actors = []
                for actor_name in film["actors"].split(", "):
                    actor = await session.execute(
                        Actor.__table__.select().where(Actor.name == actor_name)
                    )
                    actor = actor.scalar()
                    if not actor:
                        actor = Actor(name=actor_name)
                        session.add(actor)
                        await session.flush()
                    actors.append(actor)
                new_film.actors = actors

                session.add(new_film)

            await session.commit()
            print("Фильмы успешно добавлены в базу данных!")

        except Exception as e:
            await session.rollback()
            print("Ошибка:", e)

# Запуск загрузки
if __name__ == "__main__":
    asyncio.run(load_films())
