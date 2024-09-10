from typing import List

from repositories.books import BookRepository, ConvertRepository, RedisRepository
from schemas.schema import Book, BuyCoin
import asyncio_redis


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

    def convert_coin(self) -> List[Book]:
        result = self.repository.convert_coin()
        return result

    async def buy_coin(self, coin_uuid, coin_name, coin_count) -> BuyCoin:
        result =  await self.repository.buy_coin(coin_uuid, coin_name, coin_count)
        return result


class RedisService:
    def __init__(self, repository: RedisRepository, connection) -> None:
        self.repository = repository
        self.connection = connection

    async def get_value(self, key) -> List[dict]:
        connection = await self.connection
        return await connection.get(key)

    def get_keys(self, key) -> List[dict]:
        raise NotImplemented

    def set_value(self) -> None:
        raise NotImplemented
