import uuid

import db.database as _database
import db.models as _models
import sqlalchemy.orm as _orm

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import Response
from depends import get_book_service, get_redis_service, get_convert_service
from pydantic import BaseModel
from schemas.schema import Book, BuyRequest, ConvertRequest
from services.convert import BookService, RedisService, ConvertService
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from typing import List


router = APIRouter(prefix="/api", tags=["coins"])

# Defining a basic pydantic class that will be used by fastAPI to validate request body and generate swagger
class ReqBody(BaseModel):
    coin_name: str
    coin_count: float

    class Config:
        schema_extra = {
            "examples": {
                "coin_name": "SHIB",
                "coin_count": 0.9765677
            }
        }


@router.post("/buy", status_code=201)
# async def buy_coin(
#     coin: BuyRequest,
#     converter_service: ConvertService = Depends(get_convert_service),
#     db: _orm.Session = Depends(_database.get_db),
# ) -> dict:
    
#     req_json = 
#     # Generate a unique UUID.
#     coin_uuid = uuid.uuid4()
    
    
#     result = await converter_service.buy_coin(coin_uuid, coin.coin_name, coin.coin_count)
#     return result

async def buy_coin(req_body: ReqBody, db: _orm.Session = Depends(_database.get_db)):
    # Generate a unique UUID.
    coin_uuid = uuid.uuid4()
    
    # Add coin in the db.
    data = _models.CoinAccount(
        uuid = coin_uuid,
        name = req_body.coin_name,
        count = req_body.coin_count
    )

    db.add(data)   
    db.commit()
    
    res = {
        "status": "success",
        "body": {
            "coin_uuid": coin_uuid,
            "coin_name": req_body.coin_name,
            "coin_count": req_body.coin_count
        }
    }
    return res


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
