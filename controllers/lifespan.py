from fastapi import FastAPI
from contextlib import asynccontextmanager
from services.session_manager import SessionManager
from services.whatsapp_service import WhatsAppService
from handlers.message_handler import MessageHandler
from core.logger import get_logger

logger = get_logger()

whatsapp_service = WhatsAppService()
session_manager = SessionManager()
message_handler = MessageHandler(whatsapp_service, session_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[LIFESPAN] Application startup begins")

    await session_manager.connect()
    logger.info("[LIFESPAN] Connected to Redis")

    await session_manager.start_ttl_watcher(
        on_expire_callback=message_handler.on_session_expired,
        interval_seconds=60
    )
    logger.info("[LIFESPAN] TTL watcher started")

    yield

    logger.info("[LIFESPAN] Application shutdown")
