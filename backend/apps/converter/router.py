from urllib import response
import uuid

import fastapi

from apps.auth.router import jwt_validation
from apps.converter import service
import db.database as database
import db.models as _models
import sqlalchemy.orm as _orm

from fastapi import APIRouter, Depends, HTTPException
from depends import get_redis_service, get_convert_service
from apps.converter.schema import (
    Market,
    LimitRequest,
    ReqBody,
    SetCoin,
)
from apps.converter.service import RedisService, ConvertService


router = APIRouter(prefix="/api", tags=["converter"])
coin = APIRouter(prefix="/api", tags=["coinSet"])


@router.post("/get_buy_history", status_code=200)
async def buy_coin(
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    try:
        buys = list(
            db.query(_models.BuyHistory).filter(
                _models.BuyHistory.user_id == payload["id"]
            )
        )
        results = []
        for buy in buys:
            results.append({buy.name: buy.count})
        res = {"status": "success", "buys": results}
        return res

    except Exception as e:
        print(e)
        raise HTTPException(status_code=response.status_code, detail=response.json())


@router.post("/delete_history", status_code=200)
async def delete_history(
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    try:

        db.query(_models.BuyHistory).filter(
            _models.BuyHistory.user_id == payload["id"]
        ).delete()
        db.commit()

    except Exception as e:
        print(e)
        raise HTTPException(status_code=response.status_code, detail=response.json())


@router.post("/delete_buys", status_code=200)
async def delete_buys(
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    try:

        db.query(_models.CoinAccount).filter(
            _models.CoinAccount.user_id == payload["id"]
        ).delete()
        db.commit()

    except Exception as e:
        print(e)
        raise HTTPException(status_code=response.status_code, detail=response.json())


@router.post("/buy", status_code=200)
async def buy_coin(
    req_body: ReqBody,
    payload: dict = fastapi.Depends(jwt_validation),
    db: _orm.Session = Depends(database.get_db),
):
    req_body.coin_name = req_body.coin_name.upper()
    try:
        row = (
            db.query(_models.CoinAccount)
            .filter(
                _models.CoinAccount.user_id == payload["id"],
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
                user_id=int(payload["id"]),
            )

            db.add(data)
            db.commit()
        else:
            row.count = row.count + req_body.coin_count
            db.commit()

        coin_history = _models.BuyHistory(
            name=req_body.coin_name,
            count=req_body.coin_count,
            user_id=int(payload["id"]),
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


@router.post("/market_buy", status_code=200)
def market_buy_coin(
    req_body: Market,
    db: _orm.Session = Depends(database.get_db),
    service: ConvertService = Depends(get_convert_service),
    payload: dict = fastapi.Depends(jwt_validation),
):
    try:
        return service.market_buy(req_body, payload, db=db)

    except Exception as e:
        print(e)
        return {
            "status": "unsuccess",
        }


@router.post("/market_sell", status_code=200)
def market_sell_coin(
    req_body: Market,
    db: _orm.Session = Depends(database.get_db),
    service: ConvertService = Depends(get_convert_service),
    payload: dict = fastapi.Depends(jwt_validation),
):
    try:
        return service.market_sell(req_body, payload, db=db)

    except Exception as e:
        print(e)
        return {
            "status": "unsuccess",
        }


@router.post("/get_coins", status_code=200)
async def buy_coin(
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    try:
        res = list(
            db.query(_models.CoinAccount)
            .filter(_models.CoinAccount.user_id == payload["id"])
            .all(),
        )
        coins = []
        for coin in res:
            coins.append({coin.name: coin.count})

    except Exception as e:
        print(e)
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"status": "success", "coins": coins}


@router.post(
    "/limit_buy",
    responses={400: {"description": "Bad request"}},
)
def limit_buy(
    request: LimitRequest,
    service: RedisService = Depends(get_redis_service),
):

    service.set_value(request.price_coin, request.convert)
    return {"status": "sucess"}


@router.post(
    "/limit_cell",
    responses={400: {"description": "Bad request"}},
)
def limit_cell(
    request: LimitRequest,
    service: RedisService = Depends(get_redis_service),
    payload: dict = fastapi.Depends(jwt_validation),
):
    service.set_value(request.price_coin, request.convert)
    return {"status": "sucess"}


@coin.get("/coin_set", responses={400: {"description": "Bad request"}})
async def coins_get(
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return await service.get_coins(db)


@coin.post("/coin_set", responses={400: {"description": "Bad request"}})
async def coin_set(
    request: SetCoin,
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return await service.set_coins(payload["id"], request, db)


@coin.delete("/coin_set", responses={400: {"description": "Bad request"}})
async def coins_delete(
    request: int,
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return await service.delete_coins(request, db)
