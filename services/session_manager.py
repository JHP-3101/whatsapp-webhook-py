import asyncio
import threading
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, whatsapp_service):
        self.whatsapp_service = whatsapp_service
        self.user_sessions = {}  # {user_id: {"last_active": datetime, "active": True, "ended": False}}
        self.initialized = False

    def initialize(self):
        if not self.initialized:
            logger.info("🟢 Initializing SessionManager...")
            thread = threading.Thread(target=self._cleanup_sessions, daemon=True)
            thread.start()
            self.initialized = True

    def _cleanup_sessions(self):
        while True:
            now = datetime.utcnow()
            for user, session in list(self.user_sessions.items()):
                if session.get("active") and not session.get("ended") and now - session["last_active"] > timedelta(minutes=1):
                    asyncio.run(self.whatsapp_service.send_message(
                        user,
                        "Terimakasih telah menghubungi layanan member Alfamidi. Sampai jumpa lain waktu."
                    ))
                    session["active"] = False
                    session["ended"] = True
                    logger.info(f"🔴 Session ended for {user}")
            time.sleep(10)  # or 10

    def update_session(self, user_id):
        now = datetime.utcnow()
        session = self.user_sessions.get(user_id)

        if session:
            if not session.get("ended", False):
                session["last_active"] = now
                session["active"] = True
                logger.info(f"🔄 Session refreshed for {user_id}")
            else:
                logger.info(f"⚠️ Session for {user_id} already ended. Skipping update.")
        else:
            self.user_sessions[user_id] = {
                "last_active": now,
                "active": True,
                "ended": False
            }
            logger.info(f"🆕 New session created for {user_id}")

    def is_session_active(self, user_id):
        return self.user_sessions.get(user_id, {}).get("active", False)
