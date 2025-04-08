from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from orm.film import create_film, get_films
from schemas.film import FilmCreate, FilmResponse

api_router = APIRouter(prefix="/api/films", tags=["films"])

@api_router.post("/", response_model=FilmResponse, status_code=status.HTTP_201_CREATED)
async def add_film(film: FilmCreate, db: AsyncSession = Depends(get_async_session)):
    """
    Добавление нового фильма.
    """
    new_film = await create_film(db=db, film=film)
    return new_film

@api_router.get("/", response_model=List[FilmResponse], status_code=status.HTTP_200_OK)
async def get_all_films(db: AsyncSession = Depends(get_async_session)):
    """
    Получение списка всех фильмов.
    """
    films = await get_films(db=db)
    return films
