from services import redis as redisService
from db import redis
from repositories.books import BookRepository
from services.books import BookService
from dependency_injector import containers, providers

from dependency_injector import containers, providers


"""
Файл внедрения зависимостей
"""

# repository - работа с БД

book_repository = BookRepository()

# service - слой UseCase

book_service = BookService(book_repository)


def get_book_service() -> BookService:
    return book_service


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    redis_pool = providers.Resource(
        redis.init_redis_pool,
        host=config.redis_host,
        password=config.redis_password,
    )

    service = providers.Factory(
        redisService.RedisService,
        redis=redis_pool,
    )
