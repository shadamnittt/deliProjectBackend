from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from orm.genre import create_genre, get_genres, get_genre_by_name
from schemas.genre import GenreCreate, GenreResponse

api_router = APIRouter(prefix="/api/genres", tags=["genres"])

@api_router.post("/", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
async def add_genre(genre: GenreCreate, db: AsyncSession = Depends(get_async_session)):
    """
    Добавление нового жанра. Проверяется уникальность названия.
    """
    existing_genre = await get_genre_by_name(db, genre.name)
    if existing_genre:
        raise HTTPException(status_code=400, detail="Жанр с таким названием уже существует")
    
    new_genre = await create_genre(db=db, genre=genre)
    return new_genre

@api_router.get("/", response_model=List[GenreResponse], status_code=status.HTTP_200_OK)
async def get_all_genres(db: AsyncSession = Depends(get_async_session)):
    """
    Получение списка всех жанров.
    """
    genres = await get_genres(db=db)
    return genres
