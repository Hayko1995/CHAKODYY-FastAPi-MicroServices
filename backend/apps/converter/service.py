from ast import literal_eval
import json
from typing import List
from urllib import response

from fastapi import HTTPException

from apps.converter.repository import ConvertRepository, RedisRepository
from apps.converter.schema import Book, BuyCoin, Market, SetCoin
import asyncio_redis
import sqlalchemy.orm as _orm

from apps.auth.service import get_user_by_id
from db import models


class ConvertService:
    def __init__(self, repository: ConvertRepository) -> None:
        self.repository = repository

    def market_buy(self, req_body: Market, payload, db):

        from_coin = req_body.coin_set[: req_body.coin_set.index("/")].upper()
        to_coin = req_body.coin_set[req_body.coin_set.index("/") + 1 :].upper()

        try:
            from_coin = self.repository.get_coin(payload["id"], from_coin, db=db)
            if from_coin == None:
                return {"status": "not found from coin "}

            to_coin = self.repository.get_coin(payload["id"], to_coin, db=db)

            if to_coin == None:
                return {"status": "not found to coin "}

            if float(to_coin.count) <= float(req_body.count) * float(req_body.price):
                return {"status": "not enugth coins"}

            to_coin.count = float(
                float(to_coin.count) + float(req_body.count) * float(req_body.price)
            )
            from_coin.count = from_coin.count - req_body.count
            db.commit()
            return req_body
        except Exception as e:
            print(e)
            return {
                "status": "unsuccess",
            }

    def market_sell(self, req_body: Market, payload, db):

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


async def get_coins(db: _orm.Session):
    try:
        return db.query(models.CoinSet).all()

    except Exception as e:
        print(e)
        return False


async def set_coins(id: str, coins_set: SetCoin, db: _orm.Session):

    user = await get_user_by_id(id, db)
    if user.is_admin:

        try:
            if coins_set.id == -1:
                coin_set = models.CoinSet(coins=coins_set.coin_set)
                db.add(coin_set)
                db.commit()
            else:
                _ = (
                    db.query(models.CoinSet)
                    .filter(models.CoinSet.coins == coins_set.coin_set)
                    .first()
                )
                db.add(_)
                db.commit()
            return True
        except Exception as e:
            print(e)
            return False
    else:
        return False


async def delete_coins(id, db: _orm.Session):
    try:
        db.query(models.CoinSet).filter(models.CoinSet.id == id).delete()
        db.commit()
        return True

    except Exception as e:
        print(e)
        return False
