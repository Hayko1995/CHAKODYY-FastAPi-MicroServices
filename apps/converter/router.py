import uuid

import fastapi
import db.database as database
import db.models as _models
import sqlalchemy.orm as _orm

from fastapi import APIRouter, Depends, HTTPException
from urllib import response

from apps.auth.router import jwt_validation
from apps.converter import service
from apps.converter.schema import CoinSet, Market, ReqBody, UpdateCoinSet, DeletePanding
from apps.converter.service import ConvertService, RedisService
from depends import get_convert_service, get_redis_service


router = APIRouter(prefix="/api", tags=["converter"])


@router.post("/get_buy_history", status_code=200)
async def get_coins(
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

        db.query(_models.Balance).filter(
            _models.Balance.user_id == payload["id"]
        ).delete()
        db.commit()

    except Exception as e:
        print(e)
        raise HTTPException(status_code=response.status_code, detail=response.json())


@router.post("/buy", status_code=200)
async def get_coins(
    req_body: ReqBody,
    payload: dict = fastapi.Depends(jwt_validation),
    db: _orm.Session = Depends(database.get_db),
):
    req_body.coin_name = req_body.coin_name.upper()
    try:
        row = (
            db.query(_models.Balance)
            .filter(
                _models.Balance.user_id == payload["id"],
                _models.Balance.name == req_body.coin_name,
            )
            .first()
        )
        if row is None:
            # Add coin in the db.
            coin_uuid = uuid.uuid4()
            data = _models.Balance(
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


@router.post("/market", status_code=200)
def market_coin(
    req_body: Market,
    db: _orm.Session = Depends(database.get_db),
    service: ConvertService = Depends(get_convert_service),
    payload: dict = fastapi.Depends(jwt_validation),
):

    return service.market(req_body, payload["id"], db=db)


@router.post("/get_coins", status_code=200)
async def get_coins(
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    try:
        res = list(
            db.query(_models.Balance)
            .filter(_models.Balance.user_id == payload["id"])
            .all(),
        )
        coins = []
        for coin in res:
            coins.append({coin.name: coin.count})

    except Exception as e:
        print(e)
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"status": "success", "coins": coins}


@router.get("/balance", responses={400: {"description": "Bad request"}})
async def get_balance(
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return await service.get_balance(payload["id"], db)


@router.post(
    "/limit",
    responses={400: {"description": "Bad request"}},
)
def set_limit(
    request: Market,
    redis_service: RedisService = Depends(get_redis_service),
    service: ConvertService = Depends(get_convert_service),
    payload: dict = fastapi.Depends(jwt_validation),
    db: _orm.Session = Depends(database.get_db),
):
    if request.buy:
        transaction_type = "buy"
    else:
        transaction_type = "sell"
    return service.limit(
        req_body=request,
        payload=payload,
        db=db,
        redis_service=redis_service,
        transaction_type=transaction_type,
    )


@router.get(
    "/all-pending-limit",
    responses={400: {"description": "Bad request"}},
)
def get_panding(
    service: RedisService = Depends(get_redis_service),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return service.get_all(payload)


@router.get(
    "/pending-limit",
    responses={400: {"description": "Bad request"}},
)
def get_user_panding(
    service: RedisService = Depends(get_redis_service),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return service.get_user_all(payload["id"])


@router.delete(
    "/pending-limit",
    responses={400: {"description": "Bad request"}},
)
def delete_panding(
    request: DeletePanding,
    service: RedisService = Depends(get_redis_service),
    payload: dict = fastapi.Depends(jwt_validation),
    db: _orm.Session = Depends(database.get_db),
):
    return service.delete_panding_limit(request, payload["id"], service, db)


@router.get(
    "/get_panding_transactions_db",
    responses={400: {"description": "Bad request"}},
)
async def get_panding_transactions_db(
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return await service.get_panding_transactions_db(payload["id"], db)

@router.get(
    "/get_archived_transactions",
    responses={400: {"description": "Bad request"}},
)
async def get_archived_transactions(
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return await service.get_archived(payload["id"], db)


@router.get(
    "/coinset",
    responses={400: {"description": "Bad request"}},
)
async def get_coinset(
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return await service.get_coinSet(db)


@router.post(
    "/coinset",
    responses={400: {"description": "Bad request"}},
)
async def add_coinSet(
    req_body: CoinSet,
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return await service.add_coinSet(req_body, db)


@router.delete(
    "/coinset",
    responses={400: {"description": "Bad request"}},
)
async def delete_coinset(
    id: int,
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return await service.delete_coinSet(id, db)


@router.put(
    "/coinset",
    responses={400: {"description": "Bad request"}},
)
async def update_coinset(
    req_body: UpdateCoinSet,
    db: _orm.Session = Depends(database.get_db),
    payload: dict = fastapi.Depends(jwt_validation),
):
    return await service.update_coinSet(req_body, db)
