from repositories.books import BookRepository, RedisRepository
from services.books import BookService, RedisService
from dependency_injector import containers, providers
import asyncio_redis


"""
Файл внедрения зависимостей
"""

# repository - работа с БД

book_repository = BookRepository()
redis_repository = RedisRepository()


async def connect_to_redis():
        connection = await asyncio_redis.Connection.create(
            host="redis", password="password", port=6379
        )
        return connection



book_service = BookService(book_repository)
redis_service = RedisService(redis_repository, connect_to_redis())


def get_book_service() -> BookService:
    return book_service


def get_redis_service() -> RedisService:
    return redis_service
