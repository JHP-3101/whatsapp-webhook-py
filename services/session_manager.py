import aioredis
from core.logger import get_logger
import time

logger = get_logger()

class SessionManager:
    def __init__(self, redis_url: str = "redis://localhost", session_ttl: int = 60):
        self.redis = None
        self.redis_url = redis_url
        self.session_ttl = session_ttl
        self.key_prefix = "last_timestamp"

    async def connect(self):
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url)
            logger.info("[SessionManager] Connected to Redis")

    def _session_key(self, wa_id: str) -> str:
        return f"{self.key_prefix}:{wa_id}"

    async def get_ttl(self, wa_id: str) -> int:
        await self.connect()
        key = self._session_key(wa_id)
        ttl = await self.redis.ttl(key)
        logger.info(f"[SessionManager] TTL for {wa_id} is {ttl} seconds")
        return ttl

    async def has_session(self, wa_id: str) -> bool:
        await self.connect()
        key = self._session_key(wa_id)
        exists = await self.redis.exists(key)
        logger.info(f"[SessionManager] Session exists for {wa_id}: {bool(exists)}")
        return exists == 1

    async def get_last_timestamp(self, wa_id: str):
        await self.connect()
        key = self._session_key(wa_id)
        value = await self.redis.get(key)
        ttl = await self.redis.ttl(key)

        if value:
            timestamp = int(value)
            logger.info(f"[SessionManager] Found session for {wa_id}: timestamp={timestamp}, TTL={ttl}")
            return timestamp
        else:
            logger.info(f"[SessionManager] No session for {wa_id}, TTL={ttl}")
            return None

    async def update_last_timestamp(self, wa_id: str):
        await self.connect()
        key = self._session_key(wa_id)
        current_time = int(time.time())
        await self.redis.set(key, current_time, ex=self.session_ttl)
        logger.info(f"[SessionManager] Updated session for {wa_id} with timestamp={current_time}, TTL reset to {self.session_ttl} seconds")

    async def get_all_sessions(self):
        await self.connect()
        pattern = f"{self.key_prefix}:*"
        keys = await self.redis.keys(pattern)
        logger.info(f"[SessionManager] Retrieved {len(keys)} session keys")
        return keys

    async def delete_session(self, wa_id: str):
        await self.connect()
        key = self._session_key(wa_id)
        await self.redis.delete(key)
        logger.info(f"[SessionManager] Deleted session for {wa_id}")
