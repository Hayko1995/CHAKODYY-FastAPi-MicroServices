from urllib import response
import uuid

import db.database as _database
import db.models as _models
import sqlalchemy.orm as _orm

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from depends import get_book_service, get_redis_service, get_convert_service
from pydantic import BaseModel
from schemas.schema import (
    Book,
    BuyRequest,
    ConvertRequest,
    ConvertImmediately,
    LimitRequest,
    ReqBody,
    ReqCoins,
)
from services.convert import BookService, RedisService, ConvertService
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from typing import List


router = APIRouter(prefix="/api", tags=["coins"])


# Defining a basic pydantic class that will be used by fastAPI to validate request body and generate swagger


@router.post("/get_buy_history", status_code=200)
async def buy_coin(req_body: ReqCoins, db: _orm.Session = Depends(_database.get_db)):
    try:
        buys = list(
            db.query(_models.BuyHistory).filter(
                _models.BuyHistory.user_id == req_body.id
            )
        )
        results = []
        for buy in buys:
            results.append({buy.name: buy.count})
        res = {"status": "success", "buys": results}
        return res
    except:
        raise HTTPException(status_code=response.status_code, detail=response.json())


@router.post("/buy", status_code=200)
async def buy_coin(req_body: ReqBody, db: _orm.Session = Depends(_database.get_db)):
    try:
        row = (
            db.query(_models.CoinAccount)
            .filter(
                _models.CoinAccount.user_id == req_body.id,
                _models.CoinAccount.name == req_body.coin_name,
            )
            .first()
        )
        if row is None:
            # Add coin in the db.
            coin_uuid = uuid.uuid4()
            data = _models.CoinAccount(
                uuid=coin_uuid,
                name=req_body.coin_name,
                count=req_body.coin_count,
                user_id=int(req_body.id),
            )

            db.add(data)
            db.commit()
        else:
            row.count = row.count + req_body.coin_count
            db.commit()

        coin_history = _models.BuyHistory(
            name=req_body.coin_name, count=req_body.coin_count, user_id=int(req_body.id)
        )
        db.add(coin_history)
        db.commit()

        res = {
            "status": "success",
        }
        return res
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="some problem in code ")


@router.post("/convert_Immediately", status_code=200)
def convert_Immediately(
    req_body: ConvertImmediately,
    db: _orm.Session = Depends(_database.get_db),
    service: ConvertService = Depends(get_convert_service),
):
    try:
        return service.convert_imidiatly(req_body, db=db)
    except:
        # raise HTTPException(status_code=response.status_code, detail=response.json())
        return {
            "status": "unsuccess",
        }


@router.post("/get_coins", status_code=200)
async def buy_coin(req_body: ReqCoins, db: _orm.Session = Depends(_database.get_db)):

    # _models.CoinAccount
    try:
        res = list(
            db.query(_models.CoinAccount)
            .filter(_models.CoinAccount.user_id == req_body.id)
            .all(),
        )
        coins = []
        for coin in res:
            coins.append({coin.name: coin.count})

    except:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    res = {"status": "success", "coins": coins}
    return res


@router.post(
    "/limit",
    responses={400: {"description": "Bad request"}},
)
def limit(
    request: LimitRequest,
    service: RedisService = Depends(get_redis_service),
):
    service.set_value(request.price_coin, request.convert)
    return {"status": "sucess"}


@router.post(
    "/redis",
    responses={400: {"description": "Bad request"}},
    description="Redis",
)
async def getRedis(service: RedisService = Depends(get_redis_service)):
    value = service.get_value("my_key")
    return {"result": value}
