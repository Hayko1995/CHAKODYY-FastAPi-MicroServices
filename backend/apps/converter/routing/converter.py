from urllib import response
import uuid

import fastapi

from apps.auth.service import JWT_SECRET
import db.database as _database
import db.models as _models
import sqlalchemy.orm as _orm

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from depends import get_redis_service, get_convert_service
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from apps.converter.schemas.schema import (
    ConvertImmediately,
    LimitRequest,
    ReqBody,
    ReqCoins,
)
from apps.converter.services.convert import RedisService, ConvertService
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from typing import List
import jwt


router = APIRouter(prefix="/api", tags=["coins"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Defining a basic pydantic class that will be used by fastAPI to validate request body and generate swagger


async def jwt_validation(token: str = fastapi.Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except UnicodeError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")


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
async def buy_coin(
    req_body: ReqBody,
    payload: dict = fastapi.Depends(jwt_validation),
    db: _orm.Session = Depends(_database.get_db),
):
    print("🐍 File: routing/converter.py | Line: 67 | undefined ~ payload", payload)
    try:
        row = (
            db.query(_models.CoinAccount)
            .filter(
                _models.CoinAccount.user_id == payload.id,
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
    payload: dict = fastapi.Depends(jwt_validation),
):
    try:
        print(
            "🐍 File: routing/converter.py | Line: 110 | undefined ~ payload", payload
        )
        print(
            "🐍 File: routing/converter.py | Line: 110 | undefined ~ req_body", req_body
        )
        return service.convert_imidiatly(req_body, payload, db=db)

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
