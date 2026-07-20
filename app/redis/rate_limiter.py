import random
import os
from time import time

from fastapi import Request, HTTPException, Depends

from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

redis_client = Redis.from_url(url=REDIS_URL)


def get_redis_client() -> Redis | None:
    return redis_client

def rate_limiter(
    max_requests: int,
    window_seconds: int,
    key_prefix: str = "rate_limiter",
):
    async def dependency(
        request: Request, redis: Redis | None = Depends(get_redis_client)
    ):
        if redis is None:
            return

        if request.client is None:
            raise RuntimeError("Client not found")

        user_ip_address = request.client.host

        key = f"{key_prefix}:{user_ip_address}"

        now = time()
        window_start = now - window_seconds

        current_requests = f"{now}-{random.randint(0, 100_000)}"

        async with redis.pipeline() as pipe:
            await pipe.zremrangebyscore(key, 0, window_start)

            await pipe.zcard(key)

            await pipe.zadd(key, {current_requests: now})

            await pipe.expire(key, window_seconds)

            result = await pipe.execute()

        requests_count = result[1]

        if requests_count >= max_requests:
            raise HTTPException(status_code=429, detail="Too many requests")

    return dependency
