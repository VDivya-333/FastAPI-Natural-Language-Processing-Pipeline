import redis
import json
import hashlib
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)


class CacheService:

    @staticmethod
    def is_healthy() -> bool:
        """Checks if the Redis connection is alive."""
        try:
            return redis_client.ping()
        except Exception as e:
            logger.error(f"Redis Health Check Failed: {e}")
            return False


    @staticmethod
    def generate_key(task: str, text: str) -> str:

        text_hash = hashlib.md5(text.encode()).hexdigest()

        return f"{task}:{text_hash}"

    @staticmethod
    def get_cached_result(key: str):
        try:
            cached_data = redis_client.get(key)
            if cached_data:
                logger.debug(f"CACHE HIT: {key}")
                return json.loads(cached_data)
            logger.debug(f"CACHE MISS: {key}")
        except Exception as e:
            logger.error(f"Cache lookup error for key {key}: {e}")
        return None

    @staticmethod
    def set_cached_result(
        key: str,
        result: dict,
        expire_time: int = 3600
    ):
        try:
            redis_client.set(
                key,
                json.dumps(result),
                ex=expire_time
            )
        except Exception as e:
            logger.error(f"Cache storage error for key {key}: {e}")