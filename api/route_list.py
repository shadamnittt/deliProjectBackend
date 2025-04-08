from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from orm.list import create_list, get_lists, get_list_by_name
from schemas.list import ListCreate, ListResponse

api_router = APIRouter(prefix="/api/lists", tags=["lists"])

@api_router.post("/", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
async def add_list(list_data: ListCreate, db: AsyncSession = Depends(get_async_session)):
    """
    Добавление нового списка. Проверяется уникальность названия.
    """
    existing_list = await get_list_by_name(db, list_data.name)
    if existing_list:
        raise HTTPException(status_code=400, detail="Список с таким названием уже существует")
    
    new_list = await create_list(db=db, list_data=list_data)
    return new_list

@api_router.get("/", response_model=List[ListResponse], status_code=status.HTTP_200_OK)
async def get_all_lists(db: AsyncSession = Depends(get_async_session)):
    """
    Получение списка всех списков.
    """
    lists = await get_lists(db=db)
    return lists
