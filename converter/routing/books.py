from typing import List

from fastapi import APIRouter, Depends

from services.redis import RedisService
from depends import get_book_service
from depends import Container
from schemas.books import Book
from services.books import BookService
from fastapi import FastAPI, Depends
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject


router = APIRouter(prefix="/books", tags=["books"])


@router.get(
    "",
    responses={400: {"description": "Bad request"}},
    response_model=List[Book],
    description="Получение листинга всех книг",
)
async def get_all_books(
    book_service: BookService = Depends(get_book_service),
) -> List[Book]:
    books = book_service.get_books()
    return books


@router.post(
    "",
    responses={400: {"description": "Bad request"}},
    response_model=Book,
    description="Создание книги",
)
async def get_all_books(
    book_service: BookService = Depends(get_book_service),
) -> Book:
    book = book_service.create_book()
    return book


@router.post(
    "/redis",
    responses={400: {"description": "Bad request"}},
    description="Redis",
)
@inject
async def getRedis(service: RedisService = Depends(Provide[Container.service])):
    value = await service.process()
    return {"result": value}


container = Container()
container.config.redis_host.from_env("REDIS_HOST", "redis")
container.config.redis_password.from_env("REDIS_PASSWORD", "password")
container.wire(modules=[__name__])
