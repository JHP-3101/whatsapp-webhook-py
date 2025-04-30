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
        self.ttl_watcher_task = None

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

    async def start_ttl_watcher(self, on_expire_callback, interval_seconds: int = 60):
        if self.ttl_watcher_task and not self.ttl_watcher_task.done():
            logger.info("[TTLWatcher] Already running")
            return

        async def watch_loop():
            logger.info("[TTLWatcher] Started")
            while True:
                await asyncio.sleep(interval_seconds)
                keys = await self.get_all_sessions()
                
                if not keys:
                    logger.info("[TTLWatcher] No active sessions found")
                    continue

                for key in keys:
                    wa_id = key.decode().split(":")[-1]
                    ttl = await self.get_ttl(wa_id)
                    
                    logger.info(f"[TTLWatcher] TTL for {wa_id} is {ttl} seconds")

                    if ttl == -2 or ttl == -1:
                        logger.info(f"[TTLWatcher] Session expired for {wa_id}")
                        await self.delete_session(wa_id)
                        await on_expire_callback(wa_id)

        self.ttl_watcher_task = asyncio.create_task(watch_loop())
