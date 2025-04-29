import aioredis
from core.logger import get_logger

class SessionManager:
    def __init__(self):
        self.redis = None

    async def connect(self):
        if not self.redis:
            self.redis = await aioredis.from_url("redis://localhost")

    async def get_last_timestamp(self, wa_id: str):
        await self.connect()
        key = f"last_timestamp:{wa_id}"
        result = await self.redis.get(key)
        ttl = await self.redis.ttl(key)

        if result:
            get_logger.info(f"[SessionManager] Found session for {wa_id}: timestamp={int(result)}, ttl={ttl} seconds left")
            return int(result)
        else:
            get_logger.info(f"[SessionManager] No session found for {wa_id}. TTL={ttl}")
            return None

    async def update_last_timestamp(self, wa_id: str, timestamp: int):
        await self.connect()
        key = f"last_timestamp:{wa_id}"
        await self.redis.set(key, timestamp, ex=60)  # 1 hour expiration
        ttl = await self.redis.ttl(key)
        get_logger.info(f"[SessionManager] Updated session for {wa_id}: timestamp={timestamp}, new ttl={ttl} seconds")

    async def get_all_sessions(self):
        await self.connect()
        keys = await self.redis.keys("last_timestamp:*")
        return keys

    async def delete_session(self, wa_id: str):
        await self.connect()
        key = f"last_timestamp:{wa_id}"
        await self.redis.delete(key)
        get_logger.info(f"[SessionManager] Deleted session for {wa_id}")