import redis
from apps.converter.repository import ConvertRepository, RedisRepository
from apps.converter.service import ConvertService
from dependency_injector import containers, providers
import asyncio_redis


"""
dependenci injection file 
"""

# repository


redis_repository = RedisRepository()
convert_repository = ConvertRepository()


def connect_to_redis():
    connection = redis.Redis(host="redis", password="password", port=6379)
    return connection


convert_service = ConvertService(convert_repository)


def get_convert_service() -> ConvertService:
    return convert_service
