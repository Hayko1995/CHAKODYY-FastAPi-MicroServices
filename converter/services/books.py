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
