from ast import literal_eval
import json
from typing import List
from urllib import response

from fastapi import HTTPException

from repositories.books import BookRepository, ConvertRepository, RedisRepository
from schemas.schema import Book, BuyCoin
import asyncio_redis
import sqlalchemy.orm as _orm


class BookService:

    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def get_books(self) -> List[Book]:
        result = self.repository.get_books()
        return result

    def create_book(self) -> Book:
        result = self.repository.create_book()
        return result


class ConvertService:
    def __init__(self, repository: ConvertRepository) -> None:
        self.repository = repository

    def convert_imidiatly(self, req_body, db) -> List[Book]:
        try:
            from_coin = self.repository.get_coin(req_body.id, req_body.from_coin, db=db)
            to_coin = self.repository.get_coin(req_body.id, req_body.to_coin, db=db)

            if from_coin.count < req_body.count:
                raise HTTPException(
                    status_code=response.status_code, detail=response.json()
                )
            from_coin.count = from_coin.count - req_body.count

            to_coin.count = float(
                float(to_coin.count) + float(req_body.count) * float(req_body.price)
            )
            db.flush()
            db.commit()
            return req_body
        except:
            # raise HTTPException(status_code=response.status_code, detail=response.json())
            return {
                "status": "unsuccess",
            }
        return result

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
