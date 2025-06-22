import redis.asyncio as redis

from equigest.settings import Settings

class AsyncRedisClient:
    def __init__(self, url: str):
        self._client = redis.from_url(url)

    async def hincryby_fields(self, key: str, **fields: int):
        try:
            for field, value in fields.items():
                self._client.hincrby(key, field, value)
        except redis.RedisError as e:
            raise e

    async def hget_all(self, key: str):
        try:
            result = self._client.hgetall(key)

            return {k.decode(): int(v) for k, v in result.items()}
        except redis.RedisError as e:
            raise e
        
    async def hset_initial(self, key: str, mapping: dict):
        try:
            await self._client.hset(key, mapping)
        except redis.RedisError as e:
            raise e

settings = Settings()
redis_url = settings.DEFINITIVE_REDIS_URL

async_redis_client = AsyncRedisClient(redis_url)