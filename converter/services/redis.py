"""Services module."""

import redis.asyncio as redis


class RedisService:
    def __init__(self, redis: redis) -> None:
        self._redis = redis

    async def process(self) -> str:

        await self._redis.set("my-key", "11111")
        return await self._redis.get("my-key")
