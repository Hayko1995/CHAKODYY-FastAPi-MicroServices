import json

from fastapi import HTTPException

from apps.converter.repository import ConvertRepository, RedisRepository
import asyncio_redis
import sqlalchemy.orm as _orm

from typing import List

from apps.auth.service import get_user_by_id
from apps.converter.repository import ConvertRepository, RedisRepository
from apps.converter.schema import BuyCoin, Market
from db import models


class ConvertService:
    def __init__(self, repository: ConvertRepository) -> None:
        self.repository = repository

    def limit_buy(self, req_body: Market, payload, db: _orm.Session):
        from_coin = req_body.from_coin.upper()
        to_coin = req_body.to_coin.upper()

        try:
            from_coin = self.repository.get_coin(payload["id"], from_coin, db=db)
            if from_coin == None:
                return {"status": " not found from coin "}

            to_coin = self.repository.get_coin(payload["id"], to_coin, db=db)

            if to_coin == None:
                return {"status": "not found to  coin "}

            if float(to_coin.count) <= float(req_body.count) * float(req_body.price):
                return {"status": "not  enugth coins"}

            contest_id = (
                db.query(models.ContestParticipant)
                .filter(models.ContestParticipant.participant == payload["id"])
                .first()
                .contest_id
            )

            order = models.OrderPending(
                order_type="limit",
                order_direction="buy",
                from_coin=req_body.from_coin,
                to_coin=req_body.to_coin,
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

    def limit_sell(self, req_body: Market, payload, db: _orm.Session):
        from_coin = req_body.from_coin.upper()
        to_coin = req_body.to_coin.upper()

        try:

            from_coin = self.repository.get_coin(payload["id"], from_coin, db=db)
            if from_coin == None:
                return {"status": "not found  from coin "}

            to_coin = self.repository.get_coin(payload["id"], to_coin, db=db)

            if to_coin == None:
                return {"status": "not  found to coin "}

            if float(to_coin.count) <= float(req_body.count) * float(req_body.price):
                return {"status": "not enugth coins "}

            to_coin.count = float(
                float(to_coin.count) + float(req_body.count) * float(req_body.price)
            )
            from_coin.count = from_coin.count - req_body.count
            contest_id = (
                db.query(models.ContestParticipant)
                .filter(models.ContestParticipant.participant == payload["id"])
                .first()
                .contest_id
            )

            order = models.OrderPending(
                order_type="limit",
                order_direction="cell",
                from_coin=req_body.from_coin,
                to_coin=req_body.to_coin,
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

    def market_buy(self, req_body: Market, id, db: _orm.Session):
        print("................................buy.....")
        from_coin = req_body.from_coin.upper()
        to_coin = req_body.to_coin.upper()

        try:

            from_coin = self.repository.get_coin(id, from_coin, db=db)

            if from_coin == None:
                return {"status": "not found from coin "}

            to_coin = self.repository.get_coin(id, to_coin, db=db)

            if to_coin == None:
                return {"status": "not found to coin "}

            if float(to_coin.count) <= float(req_body.count) * float(req_body.price):
                return {"status": "not enugth coins"}

            to_coin.count = float(
                float(to_coin.count) + float(req_body.count) * float(req_body.price)
            )
            from_coin.count = float(from_coin.count) - float(req_body.count)
            contest = (
                db.query(models.ContestParticipant)
                .filter(models.ContestParticipant.participant == id)
                .first()
            )
            if contest:
                contest_id = contest.contest_id

                order = models.OrderArchived(
                    order_type="market",
                    order_direction="buy",
                    from_coin=req_body.from_coin,
                    to_coin=req_body.to_coin,
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

    def market_sell(self, req_body: Market, id, db):
        from_coin = req_body.from_coin.upper()
        to_coin = req_body.to_coin.upper()

        try:
            from_coin = self.repository.get_coin(id, from_coin, db=db)
            if from_coin == None:
                return {"status": "not found from coin "}

            to_coin = self.repository.get_coin(id, to_coin, db=db)

            if to_coin == None:
                return {"status": "not found to coin "}

            if float(to_coin.count) <= float(req_body.count) * 1 / float(
                req_body.price
            ):
                return {"status": "not enugth coins"}

            to_coin.count = float(to_coin.count) + float(req_body.count) *  float(
                req_body.price
            )
            from_coin.count = float(from_coin.count) - float(req_body.count)

            contest_id = (
                db.query(models.ContestParticipant)
                .filter(models.ContestParticipant.participant == id)
                .first()
                .contest_id
            )

            order = models.OrderArchived(
                order_type="market",
                order_direction="sell",
                from_coin=req_body.from_coin,
                to_coin=req_body.to_coin,
                order_quantity=req_body.count,
                price=req_body.price,
                order_status=True,
                user_id=id,
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

    async def buy_coin(self, coin_uuid, coin_name, coin_count) -> BuyCoin:
        result = await self.repository.buy_coin(coin_uuid, coin_name, coin_count)
        return result


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

    def set_value(self, request: Market, buy: str, payload: dict) -> None:
        connection = self.connection
        coin_set = request.from_coin + request.to_coin
        limit = {}
        limit["user_id"] = payload["id"]
        limit["coin_set"] = request.from_coin + request.to_coin
        limit["price"] = float(request.price)
        limit["count"] = request.count
        limit["order_direction"] = buy

        item = {
            "price": float(request.price),
            "user_id": payload["id"],
            "order_direction": buy,
            "coin_set": request.from_coin + request.to_coin,
            "from_coin": request.from_coin,
            "to_coin": request.to_coin,
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
