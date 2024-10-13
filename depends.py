import asyncio_redis
import redis

from apps.converter.repository import ConvertRepository, RedisRepository
from apps.converter.service import ConvertService, RedisService

redis_repository = RedisRepository()
convert_repository = ConvertRepository()


def connect_to_redis():
    connection = redis.Redis(host="redis", password="password", port=6379)
    return connection


redis_service = RedisService(redis_repository, connect_to_redis())




def get_redis_service() -> RedisService:
    return redis_service


def get_convert_service() -> ConvertService:
    convert_service = ConvertService(convert_repository)
    return convert_service
