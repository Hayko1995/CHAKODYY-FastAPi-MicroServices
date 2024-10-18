import json

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from apps.converter.repository import ConvertRepository, RedisRepository
import asyncio_redis
import sqlalchemy.orm as _orm

from typing import List
from apps.converter.repository import ConvertRepository, RedisRepository
from apps.converter.schema import BuyCoin, CoinSet, DeletePanding, Market, UpdateCoinSet
from db import models
from fastapi import status


class ConvertService:
    def __init__(self, repository: ConvertRepository) -> None:
        self.repository = repository

    def limit(self, req_body: Market, payload, db: _orm.Session):
        from_coin = req_body.coin1.upper()
        to_coin = req_body.coin2.upper()

        if req_body.buy:

            if (
                not db.query(models.CoinSet)
                .filter(models.CoinSet.buy_pair == coin1 + coin2)
                .first()
            ):
                coin1, coin2 = coin2, coin1
                if (
                    not db.query(models.CoinSet)
                    .filter(models.CoinSet.sell_pair == coin1 + coin2)
                    .first()
                ):
                    return {"status": "you don't have coinSet"}

        else:
            if (
                not db.query(models.CoinSet)
                .filter(models.CoinSet.sell_pair == coin1 + coin2)
                .first()
            ):
                coin1, coin2 = coin2, coin1
                if (
                    not db.query(models.CoinSet)
                    .filter(models.CoinSet.buy_pair == coin1 + coin2)
                    .first()
                ):
                    return {"status": "you don't have coinSet"}

        try:
            from_coin = self.repository.get_coin(payload["id"], from_coin, db=db)
            if from_coin == None:
                return {"status": " not found from coin "}

            to_coin = self.repository.get_coin(payload["id"], to_coin, db=db)

            if to_coin == None:
                return {"status": "not found to  coin "}

            if float(to_coin.count) < float(req_body.count):
                return {"status": "not  enugth coins"}

            contest_id = (
                db.query(models.ContestParticipant)
                .filter(models.ContestParticipant.participant == payload["id"])
                .first()
                .contest_id
            )
            if req_body.buy:
                order_direction = "buy"
            else:
                order_direction = "sell"

            order = models.OrderPending(
                order_type="limit",
                order_direction=order_direction,
                from_coin=req_body.coin1,
                to_coin=req_body.coin2,
                order_quantity=req_body.count,
                price=req_body.price,
                order_status=True,
                user_id=payload["id"],
                contest_id=contest_id,
            )
            db.add(order)
            db.commit()
            return req_body
        except Exception as e:
            print(e)
            return {
                "status": "unsuccess",
            }

    def get_coin(self, id, coin, db) -> models.Balance:
        try:
            coin_row = (
                db.query(models.Balance)
                .filter(
                    models.Balance.user_id == id,
                    models.Balance.name == coin,
                )
                .first()
            )
            if not coin_row:
                if coin == "USDT":
                    coin_row = models.Balance(
                        name="USDT",
                        count=0,
                        user_id=id,
                    )
                    db.add(coin_row)
                    db.commit()
                    db.refresh(coin_row)

            return coin_row
        except Exception as e:
            print(e)
            return {"status": "server error"}

    def market(self, req_body: Market, id, db: _orm.Session):
        try:
            coin1 = req_body.coin1.upper()
            coin2 = req_body.coin2.upper()

            if req_body.buy:
                if (
                    not db.query(models.CoinSet)
                    .filter(models.CoinSet.buy_pair == coin1 + coin2)
                    .first()
                ):
                    coin1, coin2 = coin2, coin1
                    if (
                        not db.query(models.CoinSet)
                        .filter(models.CoinSet.buy_pair == coin1 + coin2)
                        .first()
                    ):
                        return {"status": "you do not have coinSet"}

            else:
                if (
                    not db.query(models.CoinSet)
                    .filter(models.CoinSet.sell_pair == coin1 + coin2)
                    .first()
                ):
                    coin1, coin2 = coin2, coin1
                    if (
                        not db.query(models.CoinSet)
                        .filter(models.CoinSet.sell_pair == coin1 + coin2)
                        .first()
                    ):
                        return {"status": "you do not have coinSet"}

            coin1 = self.repository.get_coin(id, coin1, db=db)

            if coin1 == None:
                return {"status": "not found from coin "}

            coin2 = self.repository.get_coin(id, coin2, db=db)

            if coin2 == None:
                return {"status": "not found to coin "}

            if float(coin1.count) < float(req_body.count):
                return {"status": "not enough coins"}

            coin2.count = float(
                float(coin2.count) + float(req_body.count) * float(req_body.price)
            )
            coin2.count = round(coin2.count, 5)
            coin1.count = float(coin1.count) - float(req_body.count)
            contest = (
                db.query(models.ContestParticipant)
                .filter(models.ContestParticipant.participant == id)
                .first()
            )
            if contest:
                contest_id = contest.contest_id
                if req_body.buy:
                    order_direction = "buy"
                else:
                    order_direction = "sell"

                order = models.OrderArchived(
                    order_type="market",
                    order_direction=order_direction,
                    from_coin=req_body.coin1,
                    to_coin=req_body.coin2,
                    order_quantity=req_body.count,
                    price=req_body.price,
                    order_status=True,
                    user_id=id,
                    contest_id=contest_id,
                )
                db.add(order)
                db.commit()
            else:
                return {"status": "contest id not found"}
            return req_body

        except Exception as e:
            print(e)
            return {
                "status": "unsuccess",
            }

    async def buy_coin(self, coin_uuid, coin_name, coin_count) -> BuyCoin:
        result = await self.repository.buy_coin(coin_uuid, coin_name, coin_count)
        return result


async def get_coinSet(db: _orm.Session):
    try:
        return db.query(models.CoinSet).all()
    except Exception as e:
        print(e)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="Server Error"
    )


async def add_coinSet(req_body: CoinSet, db: _orm.Session):
    try:
        req_body.coin1 = req_body.coin1.upper()
        req_body.coin2 = req_body.coin2.upper()
        if (
            db.query(models.CoinSet)
            .filter(models.CoinSet.buy_pair == req_body.coin1 + req_body.coin2)
            .first()
        ):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT, content="already exist "
            )
        coin = models.CoinSet(
            buy_pair=req_body.coin1 + req_body.coin2,
            sell_pair=req_body.coin2 + req_body.coin1,
        )
        db.add(coin)
        db.commit()
        db.refresh(coin)
        return coin
    except Exception as e:
        print(e)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="Server Error"
    )


async def update_coinSet(req_body: UpdateCoinSet, db: _orm.Session):
    try:
        req_body.coin1 = req_body.coin1.upper()
        req_body.coin2 = req_body.coin2.upper()
        coin = db.query(models.CoinSet).filter(models.CoinSet.id == req_body.id).first()
        coin.buy_pair = req_body.coin1 + req_body.coin2
        coin.sell_pair = req_body.coin2 + req_body.coin1
        db.commit()
        db.refresh(coin)
        return coin
    except Exception as e:
        print(e)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="Server Error"
    )


async def delete_coinSet(id: int, db: _orm.Session):
    try:
        db.query(models.CoinSet).filter(models.CoinSet.id == id).delete()

        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content="done")
    except Exception as e:
        print(e)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="Server Error"
    )


async def get_balance(id, db: _orm.Session):
    try:
        return db.query(models.Balance).filter(models.Balance.user_id == id).all()
    except Exception as e:
        print(e)
        return False


class RedisService:
    def __init__(self, repository: RedisRepository, connection) -> None:
        self.repository = repository
        self.connection = connection

    def get_value(self, key) -> List[dict]:
        connection = self.connection
        return connection.get(key)

    def get_keys(self) -> List[dict]:
        connection = self.connection
        connection.keys()
        return connection.keys()

    def get_all(self, id) -> List[dict]:

        connection = self.connection
        connection.keys()
        keys = connection.keys()
        res = {}

        for i in keys:

            res[i] = connection.get(i)
        return res

    def get_user_all(self, id) -> List[dict]:

        connection = self.connection
        connection.keys()
        keys = connection.keys()
        res = {}
        user_1_orders = []
        for i in keys:
            res[i] = json.loads(connection.get(i))
            user_1_orders.append([order for order in res[i] if order["user_id"] == id])
            res[i] = user_1_orders
        return res

    def delete_panding_limit(self, request: DeletePanding, id, service) -> List[dict]:
        try:
            status = service.delete_value(request.coin_set, request.row)
            return {"status": status}
        except Exception as e:
            print(e)
            return {"status": "fail"}

    def set_value(self, request: Market, buy: str, payload: dict) -> None:
        connection = self.connection
        coin_set = request.coin1 + request.coin2
        limit = {}
        limit["user_id"] = payload["id"]
        limit["coin_set"] = request.coin1 + request.coin2
        limit["price"] = float(request.price)
        limit["count"] = request.count
        limit["order_direction"] = buy

        item = {
            "price": float(request.price),
            "user_id": payload["id"],
            "order_direction": buy,
            "coin_set": request.coin1 + request.coin2,
            "from_coin": request.coin1,
            "to_coin": request.coin2,
            "order_quantity": request.count,
        }
        redis_value = connection.get(coin_set)
        if redis_value == None:
            return connection.set(coin_set, json.dumps([item]))
        redis_value = json.loads(redis_value)
        if item not in redis_value:
            redis_value.append(item)

        return connection.set(coin_set, json.dumps(redis_value))

    def set_full_key(self, key, value):
        connection = self.connection
        connection.set(str(key), json.dumps(value))

    def delete_value(self, key, row) -> None:
        try:
            connection = self.connection
            values = connection.get(key)
            values = json.loads(values)

            # values.index(row)

            del values[values.index(row)]
            self.set_full_key(key, values)
            return True
        except Exception as e:
            print(e)
        return False
