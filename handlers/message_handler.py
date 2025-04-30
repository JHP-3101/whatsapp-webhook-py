from services.whatsapp_service import WhatsAppService
from services.session_manager import SessionManager
from globals import constants
from core.logger import get_logger
import time

logger = get_logger()

class MessageHandler:
    def __init__(self, whatsapp_service: WhatsAppService, session_manager: SessionManager, session_timeout: int = 60):
        self.whatsapp_service = whatsapp_service
        self.last_timestamps = {}
        self.session_manager = session_manager
        self.session_timeout = session_timeout
    
    async def handle_text_message(self, from_number: str, text: str, username: str):
        has_session = await self.session_manager.has_session(from_number)
        ttl = await self.session_manager.get_ttl(from_number)

        logger.info(f"TTL for {from_number} is {ttl} seconds")
        
        if not has_session or ttl == -2:
            if has_session:
                # Session expired (user was active before)
                logger.info(f"Session expired for {from_number}")
                await self.whatsapp_service.send_message(from_number, "Terimakasih telah menghubungi layanan Alfamidi. Sampai jumpa lain waktu!")

            # Start new session
            logger.info(f"Starting new session for {from_number}")
            await self.session_manager.update_last_timestamp(from_number)
            await self.whatsapp_service.send_main_menu(from_number, username)
            return

        # Session still active — refresh timestamp
        await self.session_manager.update_last_timestamp(from_number)
        
        if text.lower() == "test":
            await self.whatsapp_service.send_message(from_number, "hello world!")
        else:
            await self.whatsapp_service.send_main_menu(from_number, username)

    async def handle_interactive_message(self, from_number: str, interactive_data: dict):
        current_time = int(time.time())
        last_timestamp = await self.session_manager.get_last_timestamp(from_number)

        if last_timestamp and (current_time > last_timestamp + self.session_timeout):
            # Session expired
            logger.info(f"Session expired for {from_number}")
            await self.whatsapp_service.send_message(from_number, "Terimakasih telah menghubungi layanan Alfamidi. Sampai jumpa lain waktu!")
            await self.session_manager.delete_session(from_number)
            return

        if not last_timestamp:
            # No session, start fresh
            logger.info(f"Starting new session for {from_number}")
            await self.session_manager.update_last_timestamp(from_number, current_time)
            return

        # User still active session
        await self.session_manager.update_last_timestamp(from_number, current_time)
        
        reply_id = interactive_data.get("list_reply", {}).get("id")
        if reply_id == constants.MENU_1:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu 1")
        elif reply_id == constants.MENU_2:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu 2")
        else:
            await self.whatsapp_service.send_message(from_number, "Menu tidak dikenali.")