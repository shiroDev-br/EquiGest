from json import dumps, loads

import redis.asyncio as redis

from equigest.settings import Settings

class AsyncRedisClient:
    def __init__(self, url: str):
        self._client = redis.from_url(url)

    async def set_from_dictionary(self, key: str, dictionary: dict, expire: float = 0):
        try:
            encoded_data = dumps(dictionary, indent=4)

            self._client.set(key, encoded_data, expire)

            return {
                "key_set": key,
                "data_set": dictionary,
                "expires_at": expire
            }
        except redis.RedisError as e:
            raise e

    async def get_dictionary(self, key: str):
        try:
            encoded_data = self._client.get(key)
            if not encoded_data:
                return {}

            return loads(encoded_data)
        except redis.RedisError as e:
            raise e

settings = Settings()
redis_url = settings.DEFINITIVE_REDIS_URL

async_redis_client = AsyncRedisClient(redis_url)