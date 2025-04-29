import aioredis

class SessionManager:
    def __init__(self):
        self.redis = None

    async def connect(self):
        if not self.redis:
            self.redis = await aioredis.from_url("redis://localhost")
            
    async def get_ttl(self, wa_id: str) -> int:
        await self.connect()
        return await self.redis.ttl(f"last_timestamp:{wa_id}")

    async def get_last_timestamp(self, wa_id: str):
        await self.connect()
        result = await self.redis.get(f"last_timestamp:{wa_id}")
        return int(result) if result else None

    async def update_last_timestamp(self, wa_id: str, timestamp: int):
        await self.connect()
        await self.redis.set(f"last_timestamp:{wa_id}", timestamp, ex=60)

    async def get_all_sessions(self):
        await self.connect()
        keys = await self.redis.keys("last_timestamp:*")
        return keys

    async def delete_session(self, wa_id: str):
        await self.connect()
        await self.redis.delete(f"last_timestamp:{wa_id}")