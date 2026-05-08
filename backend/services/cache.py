"""Redis 缓存服务"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

import redis

from config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None


def _get_redis() -> Optional[redis.Redis]:
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        _redis_client.ping()
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis 连接失败，降级到无缓存模式: {e}")
        _redis_client = None
        return None


def cache_get(key: str) -> Optional[Any]:
    r = _get_redis()
    if r is None:
        return None
    try:
        value = r.get(key)
        if value is None:
            return None
        return json.loads(value)
    except Exception as e:
        logger.warning(f"Redis GET 失败: {e}")
        return None


def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    r = _get_redis()
    if r is None:
        return False
    try:
        r.setex(key, ttl, json.dumps(value, ensure_ascii=False, default=str))
        return True
    except Exception as e:
        logger.warning(f"Redis SET 失败: {e}")
        return False


def cache_delete(key: str) -> bool:
    r = _get_redis()
    if r is None:
        return False
    try:
        r.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Redis DELETE 失败: {e}")
        return False


def cache_exists(key: str) -> bool:
    r = _get_redis()
    if r is None:
        return False
    try:
        return bool(r.exists(key))
    except Exception as e:
        logger.warning(f"Redis EXISTS 失败: {e}")
        return False
