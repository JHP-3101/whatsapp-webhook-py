from services.whatsapp_service import WhatsAppService
from services.session_manager import SessionManager
from globals import constants
from core.logger import get_logger
import time

logger = get_logger()

class MessageHandler:
    def __init__(self, whatsapp_service: WhatsAppService, session_manager: SessionManager):
        self.whatsapp_service = whatsapp_service
        self.session_manager = session_manager

    async def handle_text_message(self, from_number: str, text: str, username: str):
        ttl = await self.session_manager.get_ttl(from_number)
        ttl = None

        if ttl == -2:
            # Session has expired (key doesn't exist anymore)
            logger.info(f"Session expired for {from_number}")
            await self.whatsapp_service.send_message(from_number, "Terimakasih telah menghubungi layanan Alfamidi. Sampai jumpa lain waktu!")
            return

        if ttl == -1:
            # Key exists but no expiry (should not happen)
            logger.warning(f"Session for {from_number} exists but has no TTL.")
            await self.session_manager.update_last_timestamp(from_number)

        elif ttl >= 0:
            # Session is still active
            await self.session_manager.update_last_timestamp(from_number)
        
        if text.lower() == "test":
            await self.whatsapp_service.send_message(from_number, "hello world!")
        else:
            await self.whatsapp_service.send_main_menu(from_number, username)

    async def handle_interactive_message(self, from_number: str, interactive_data: dict):
        ttl = await self.session_manager.get_ttl(from_number)

        if ttl == -2:
            # Session has expired (key doesn't exist anymore)
            logger.info(f"Session expired for {from_number}")
            await self.whatsapp_service.send_message(from_number, "Terimakasih telah menghubungi layanan Alfamidi. Sampai jumpa lain waktu!")
            return

        if ttl == -1:
            # Key exists but no expiry (should not happen)
            logger.warning(f"Session for {from_number} exists but has no TTL.")
            await self.session_manager.update_last_timestamp(from_number)

        elif ttl >= 0:
            # Session is still active
            await self.session_manager.update_last_timestamp(from_number)
        
        reply_id = interactive_data.get("list_reply", {}).get("id")
        if reply_id == constants.MENU_1:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu 1")
        elif reply_id == constants.MENU_2:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu 2")
        else:
            await self.whatsapp_service.send_message(from_number, "Menu tidak dikenali.")
