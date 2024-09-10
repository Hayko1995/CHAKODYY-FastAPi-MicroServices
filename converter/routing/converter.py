from typing import List

from fastapi import APIRouter, Depends


from depends import get_book_service, get_redis_service, get_convert_service
from schemas.schema import Book, BuyRequest, ConvertRequest
from services.convert import BookService, RedisService, ConvertService
from fastapi import FastAPI, Depends
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
import sqlalchemy.orm as _orm
import db.database as _database

router = APIRouter(prefix="/api", tags=["coins"])


@router.get(
    "/buy",
    responses={400: {"description": "Bad request"}},
)
async def buy_coin(
    coin: BuyRequest,
    converter_service: ConvertService = Depends(get_convert_service),
    db: _orm.Session = Depends(_database.get_db),
) -> bool:
    result = await converter_service.buy_coin(coin.coin_name, coin.coin_count, db)
    return result


@router.post(
    "/convert",
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
async def getRedis(service: RedisService = Depends(get_redis_service)):
    value = await service.get_value("my_key")
    return {"result": value}
