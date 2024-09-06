from typing import AsyncIterator

import redis.asyncio as redis


async def init_redis_pool(host: str, password: str) -> AsyncIterator[redis]:
    pool = redis.ConnectionPool.from_url(
        f"redis://{host}", password=password, encoding="utf-8", decode_responses=True
    )
    session = redis.Redis.from_pool(pool)
    yield session
    session.close()
    await session.wait_closed()
