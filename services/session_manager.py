import aioredis
from core.logger import get_logger
import time
import asyncio

logger = get_logger()

class SessionManager:
    def __init__(self, redis_url: str = "redis://localhost", session_ttl: int = 60):
        self.redis = None
        self.redis_url = redis_url
        self.session_ttl = session_ttl
        self.key_prefix = "last_timestamp"
        self.refresh_tasks = {}

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
        return self.session_ttl

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
        
    async def _start_auto_refresh(self, wa_id: str, interval_seconds: int = 60):
        logger.info(f"[AutoRefresh] Starting auto-refresh for {wa_id}")
        try:
            while await self.has_session(wa_id):
                await asyncio.sleep(interval_seconds)
                await self.update_last_timestamp(wa_id)
                logger.info(f"[AutoRefresh] Refreshed session for {wa_id}")
        except asyncio.CancelledError:
            logger.info(f"[AutoRefresh] Auto-refresh cancelled for {wa_id}")

    async def start_auto_refresh(self, wa_id: str, interval_seconds: int = 60):
        if wa_id not in self.refresh_tasks:
            task = asyncio.create_task(self._start_auto_refresh(wa_id, interval_seconds))
            self.refresh_tasks[wa_id] = task
            logger.info(f"[AutoRefresh] Scheduled auto-refresh for {wa_id}")
        else:
            logger.info(f"[AutoRefresh] Refresh task already running for {wa_id}")

    async def stop_auto_refresh(self, wa_id: str):
        task = self.refresh_tasks.pop(wa_id, None)
        if task:
            task.cancel()
            logger.info(f"[AutoRefresh] Stopped auto-refresh for {wa_id}")
