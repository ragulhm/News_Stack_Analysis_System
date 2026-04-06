import redis.asyncio as redis
import os
import json
import logging
from typing import Any, Optional

class RedisCache:
    """Resilient Caching Node with In-Memory fallback."""
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis_url = f"redis://{host}:{port}/{db}"
        self.client: Optional[redis.Redis] = None
        self.is_offline = True
        self._local_buffer = {}

    async def connect(self):
        """Initialize connection to the Redis buffer."""
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            await self.client.ping()
            self.is_offline = False
            logging.info("REDIS_CACHE: Neural Link established to Redis node.")
        except Exception as e:
            logging.error(f"REDIS_CACHE_ERROR: Link failure: {str(e)}. Activating In-Memory Fallback.")
            self.is_offline = True

    async def get(self, key: str) -> Optional[Any]:
        if self.is_offline or not self.client:
            return self._local_buffer.get(key)
        try:
            data = await self.client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return self._local_buffer.get(key)

    async def set(self, key: str, value: Any, expire: int = 3600):
        if self.is_offline or not self.client:
            self._local_buffer[key] = value
            return

        try:
            await self.client.set(key, json.dumps(value), ex=expire)
        except Exception:
            self._local_buffer[key] = value

    async def delete(self, key: str):
        if self.is_offline or not self.client:
            self._local_buffer.pop(key, None)
            return
        try:
            await self.client.delete(key)
        except Exception:
            self._local_buffer.pop(key, None)

# Global Cache Instance
cache = RedisCache()
