from typing import List

from repositories.books import BookRepository, RedisRepository
from schemas.books import Book
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


class RedisService:
    def __init__(self, repository: RedisRepository) -> None:
        self.repository = repository

    async def connect_to_redis(self):
        connection = await asyncio_redis.Connection.create(
            host="redis", password="password", port=6379
        )
        return connection

    async def get_value(self, key) -> List[dict]:
        connection = await self.connect_to_redis()
        return await connection.get(key)
        return "aaaa"

    def get_keys(self, key) -> List[dict]:
        raise NotImplemented

    def set_value(self) -> None:
        raise NotImplemented
