import json

from fastapi import HTTPException

from apps.converter.repository import ConvertRepository, RedisRepository
from apps.converter.schema import Book, BuyCoin, Market
import asyncio_redis
import sqlalchemy.orm as _orm

from typing import List

from apps.auth.service import get_user_by_id
from apps.converter.repository import ConvertRepository, RedisRepository
from apps.converter.schema import BuyCoin, Market, SetCoin
from db import models


class ConvertService:
    def __init__(self, repository: ConvertRepository) -> None:
        self.repository = repository

    def limit_buy(self, req_body: Market, payload, db: _orm.Session):
        req_body.coin_set = req_body.coin_set.upper()
        from_coin = req_body.coin_set[: req_body.coin_set.index("/")].upper()
        to_coin = req_body.coin_set[req_body.coin_set.index("/") + 1 :].upper()

        try:
            from_coin = self.repository.get_coin(payload["id"], from_coin, db=db)
            if from_coin == None:
                return {"status": " not found from coin "}

            to_coin = self.repository.get_coin(payload["id"], to_coin, db=db)

            if to_coin == None:
                return {"status": "not found to  coin "}

            if float(to_coin.count) <= float(req_body.count) * float(
                req_body.price
            ):
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
                order_coin=req_body.coin_set,
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
        req_body.coin_set = req_body.coin_set.upper()
        from_coin = req_body.coin_set[: req_body.coin_set.index("/")].upper()
        to_coin = req_body.coin_set[req_body.coin_set.index("/") + 1 :].upper()

        try:

            from_coin = self.repository.get_coin(payload["id"], from_coin, db=db)
            if from_coin == None:
                return {"status": "not found  from coin "}

            to_coin = self.repository.get_coin(payload["id"], to_coin, db=db)

            if to_coin == None:
                return {"status": "not  found to coin "}

            if float(to_coin.count) <= float(req_body.count) * float(
                req_body.price
            ):
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
                order_coin=req_body.coin_set,
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

    def market_buy(self, req_body: Market, payload, db: _orm.Session):
        req_body.coin_set = req_body.coin_set.upper()
        from_coin = req_body.coin_set[: req_body.coin_set.index("/")].upper()
        to_coin = req_body.coin_set[req_body.coin_set.index("/") + 1 :].upper()

        try:

                from_coin = self.repository.get_coin(payload["id"], from_coin, db=db)
                if from_coin == None:
                    return {"status": "not found from coin "}

                to_coin = self.repository.get_coin(payload["id"], to_coin, db=db)

                if to_coin == None:
                    return {"status": "not found to coin "}

                if float(to_coin.count) <= float(req_body.count) * float(
                    req_body.price
                ):
                    return {"status": "not enugth coins"}

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

                order = models.OrderArchived(
                    order_type="market",
                    order_direction="buy",
                    order_coin=req_body.coin_set,
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

    def market_sell(self, req_body: Market, payload, db):
        req_body.coin_set = req_body.coin_set.upper()
        from_coin = req_body.coin_set[: req_body.coin_set.index("/")].upper()
        to_coin = req_body.coin_set[req_body.coin_set.index("/") + 1 :].upper()

        try:
            from_coin = self.repository.get_coin(payload["id"], from_coin, db=db)
            if from_coin == None:
                return {"status": "not found from coin "}

            to_coin = self.repository.get_coin(payload["id"], to_coin, db=db)

            if to_coin == None:
                return {"status": "not found to coin "}

            if float(to_coin.count) <= float(req_body.count) * 1 / float(
                req_body.price
            ):
                return {"status": "not enugth coins"}

            to_coin.count = float(
                float(to_coin.count) - float(req_body.count) * 1 / float(req_body.price)
            )
            from_coin.count = from_coin.count + req_body.count

            contest_id = (
                db.query(models.ContestParticipant)
                .filter(models.ContestParticipant.participant == payload["id"])
                .first()
                .contest_id
            )

            order = models.OrderArchived(
                order_type="market",
                order_direction="sell",
                order_coin=req_body.coin_set,
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

    def set_value(self, key, value) -> None:
        connection = self.connection
        redis_value = connection.get(key)
        if redis_value == None:
            return connection.set(str(key), json.dumps([value]))
        redis_value = json.loads(redis_value)

        redis_value.append(value)

        return connection.set(str(key), json.dumps(redis_value))

    def delete_value(self, key) -> None:
        connection = self.connection
        return connection.delete(str(key))