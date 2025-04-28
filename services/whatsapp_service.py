import os
import httpx
from core.logger import get_logger
from dotenv import load_dotenv
from globals import constants

logger = get_logger()

load_dotenv()
TOKEN_META = os.getenv("TOKEN_META")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


class WhatsAppService:
    BASE_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    async def send_message(self, phone_number: str, message: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message},
        }
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.BASE_URL}?access_token={TOKEN_META}",
                    json=payload,
                    headers=self.headers,
                )
        except Exception as e:
            logger.error(f"Send Message Error: {e}")
            raise

    async def send_menu(self, phone_number: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": "menu utama. Silakan pilih layanan",
                },
                "action": {
                    "sections": [
                        {
                            "title": "menu",
                            "rows": [
                                {"id": constants.MENU_1, "title": "MENU 1"},
                                {"id": constants.MENU_2, "title": "MENU 2"},
                            ],
                        }
                    ],
                    "button": "Pilih Menu",
                },
            },
        }
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.BASE_URL}?access_token={TOKEN_META}",
                    json=payload,
                    headers=self.headers,
                )
        except Exception as e:
            logger.error(f"Send Menu Error: {e}")
            raise
