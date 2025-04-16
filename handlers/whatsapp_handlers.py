import logging
from services.whatsapp_service import WhatsappService
from globals import constants

logger = logging.getLogger(__name__)

wa_service = WhatsappService()

class ContactHandler:
    def __init__(self, value: dict):
        self.value = value
        
    def extract_username(self, value: dict) -> str:
        contacts = value.get("contacts", [])
        if contacts:
            profile = contacts[0].get("profile", {})
            username = profile.get("name", "Pelanggan")
            logger.info(f"👤 Nama pengguna: {username}")
            return username
        return "Pelanggan"

class MessageHandler:
    async def handle_text(self, from_no: str, body: str, username: str):
        body = body.lower()
        if body == "test":
            logger.info("📤 Kirim test message")
            await wa_service.send_message(from_no, "hello world!")
        else:
            logger.info("📤 Kirim main menu")
            await wa_service.send_menu(from_no, username)

    async def handle_interactive(self, from_no: str, interactive: dict):
        if interactive["type"] == "list_reply":
            list_id = interactive["list_reply"]["id"]
            logger.info(f"📥 List menu terpilih: {list_id}")

            # Deteksi berdasarkan ID
            if list_id == constants.MEMBER:
                await wa_service.send_message(from_no, "👤 Anda memilih Member")
            elif list_id == constants.ON_DEV_1:
                await wa_service.send_message(from_no, "🚧 Menu sedang dikembangkan")
            else:
                await wa_service.send_message(from_no, "❌ Menu tidak dikenali")
