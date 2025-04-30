from fastapi import FastAPI
from contextlib import asynccontextmanager
from services.session_manager import SessionManager
from services.whatsapp_service import WhatsAppService
from handlers.message_handler import MessageHandler

whatsapp_service = WhatsAppService()
session_manager = SessionManager()
message_handler = MessageHandler(whatsapp_service, session_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await session_manager.connect()

    # This callback stays in the handler
    await session_manager.start_ttl_watcher(
        on_expire_callback=message_handler.on_session_expired,
        interval_seconds=60
    )

    yield
