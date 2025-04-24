import asyncio
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self, on_session_end_callback):
        self.sessions = {} #{phone_number: session_info}
        self.on_session_end_callback = on_session_end_callback
        self.lock = asyncio.Lock()
        
    async def update_session(self, phone_number):
        now = datetime.utcnow()
        async with self.lock:
            session = self.sessions.get(phone_number)
            if not session or session.get("ended"):
                self.sessions[phone_number] = {
                    "last_active": now,
                    "active": True,
                    "ended": False
                }
            else :
                self.sessions[phone_number]["last_active"] = now
                self.sessions[phone_number]["active"] = True
                self.sessions[phone_number]["ended"] = False
                
            asyncio.create_task(self._schedule_end_session(phone_number))
        
    async def _schedule_end_session(self, phone_number):
        await asyncio.sleep(60)
        async with self.lock:
            session = self.sessions.get(phone_number)
            if session and not session["ended"]:
                last_active = session["last_active"]
                if datetime.utcnow() - last_active >= timedelta(minutes=1):
                    session["active"] = False
                    session["ended"] = True
                    await self.on_session_end_callback(phone_number)