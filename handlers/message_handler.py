from services.whatsapp_service import WhatsAppService
from globals import constants
from core.logger import get_logger

logger = get_logger()

class MessageHandler:
    def __init__(self, whatsapp_service: WhatsAppService):
        self.whatsapp_service = whatsapp_service

    async def handle_text_message(self, from_number: str, text: str, username: str):
        if text.lower() == "test":
            await self.whatsapp_service.send_message(from_number, "hello world!")
        else:
            await self.whatsapp_service.send_menu(f"Halo {username}! 👋🏻 🤗. Selamat datang di layanan Member Alfamidi. Silahkan pilih layanan yang anda butuhkan.", from_number, username)

    async def handle_interactive_message(self, from_number: str, interactive_data: dict):
        reply_id = interactive_data.get("list_reply", {}).get("id")
        if reply_id == constants.MENU_1:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu 1")
        elif reply_id == constants.MENU_2:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu 2")
        else:
            await self.whatsapp_service.send_message(from_number, "Menu tidak dikenali.")
