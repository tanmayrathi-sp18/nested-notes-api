import json
import logging
from typing import Any

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=1,
                socket_connect_timeout=1
            )
            # Test connection
            self.client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}. Falling back to DB.")
            self.client = None

    def get(self, key: str) -> Any | None:
        if not self.client:
            return None
        try:
            data = self.client.get(key)
            if data is None:
                return None
            return json.loads(str(data))
        except Exception as e:
            logger.warning(f"Redis GET error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        if not self.client:
            return
        try:
            self.client.set(key, json.dumps(value), ex=ttl)
        except Exception as e:
            logger.warning(f"Redis SET error for key {key}: {e}")

    def delete(self, *keys: str):
        if not self.client:
            return
        try:
            self.client.delete(*keys)
        except Exception as e:
            logger.warning(f"Redis DELETE error for keys {keys}: {e}")

redis_client = RedisClient()
