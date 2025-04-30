from services.whatsapp_service import WhatsAppService
from services.session_manager import SessionManager
from globals import constants
from core.logger import get_logger
import time
import asyncio

logger = get_logger()

class MessageHandler:
    def __init__(self, whatsapp_service: WhatsAppService, session_manager: SessionManager):
        self.whatsapp_service = whatsapp_service
        self.session_manager = session_manager

    async def handle_text_message(self, from_number: str, text: str, username: str):
        
        if text.strip().lower() == "test":
            await self.whatsapp_service.send_message(from_number, "hello world!")
        else:
            await self.whatsapp_service.send_main_menu(from_number, username)

        # Active session, update TTL
        await self.session_manager.update_last_timestamp(from_number)
        await self.session_manager.start_ttl_watcher(interval_seconds=60)


    async def handle_interactive_message(self, from_number: str, interactive_data: dict):
        ttl = await self.session_manager.get_ttl(from_number)

        if ttl == -2 or ttl == -1:
            logger.info(f"[MessageHandler] Session expired or not found for {from_number}. Sending goodbye.")
            await self.whatsapp_service.send_message(from_number, "Terimakasih telah menghubungi layanan Alfamidi. Sampai jumpa lain waktu!")
            await self.session_manager.delete_session(from_number)
            await self.session_manager.stop_auto_refresh(from_number)
            return

        # Active session, update TTL
        await self.session_manager.update_last_timestamp(from_number)

        reply_id = interactive_data.get("list_reply", {}).get("id")

        if reply_id == constants.MENU_1:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu 1")
        elif reply_id == constants.MENU_2:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu 2")
        else:
            await self.whatsapp_service.send_message(from_number, "Menu tidak dikenali.")
