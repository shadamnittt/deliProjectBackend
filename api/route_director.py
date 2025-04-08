from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from orm.director import create_director, get_directors
from schemas.director import DirectorCreate, DirectorResponse

api_router = APIRouter(prefix="/api/directors", tags=["directors"])

@api_router.post("/", response_model=DirectorResponse, status_code=status.HTTP_201_CREATED)
async def add_director(director: DirectorCreate, db: AsyncSession = Depends(get_async_session)):
    """
    Добавление нового режиссера.
    """
    return await create_director(db=db, director=director)

@api_router.get("/", response_model=List[DirectorResponse], status_code=status.HTTP_200_OK)
async def get_all_directors(db: AsyncSession = Depends(get_async_session)):
    """
    Получение списка всех режиссеров.
    """
    return await get_directors(db=db)
