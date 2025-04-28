import os
import httpx
from core.logger import get_logger
from globals import constants

logger = get_logger()

TOKEN_META = os.getenv("TOKEN_META")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

class WhatsAppService:
    def __init__(self):
        self.token = os.getenv("TOKEN_META")
        self.phone_number_id = os.getenv("PHONE_NUMBER_ID")
        self.base_url = "https://graph.facebook.com/v20.0"

    async def _post(self, endpoint: str, payload: dict) :
        url = f"{self.base_url}/{self.phone_number_id}/{endpoint}?access_token={self.token}"
        headers = {"Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=10) # Add timeout
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"WhatsApp API Error ({e.response.status_code if e.response else 'N/A'}): {e} - Endpoint: {endpoint}, Payload: {payload}")
                raise HTTPException(status_code=500, detail=f"Failed to interact with WhatsApp API: {e}")
            except httpx.TimeoutException as e:
                logger.error(f"WhatsApp API Timeout Error: {e} - Endpoint: {endpoint}, Payload: {payload}")
                raise HTTPException(status_code=504, detail="WhatsApp API request timed out")
            except Exception as e:
                logger.error(f"An unexpected error occurred during WhatsApp API call: {e} - Endpoint: {endpoint}, Payload: {payload}")
                raise HTTPException(status_code=500, detail="Internal server error during WhatsApp API call")

    async def send_message(self, to: str, message: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
        await self._post("messages", payload)

    async def send_menu(self, to: str, username: str = "Pelanggan"):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": f"Halo {username}! 👋🏻 🤗. Selamat datang di layanan Member Alfamidi. Silahkan pilih layanan yang anda butuhkan."},
                "action": {
                    "sections": [{
                        "title": "Pilih Menu",
                        "rows": [
                            {"id": constants.MENU_1, "title": "Member"},
                            {"id": constants.MENU_2, "title": "Menu On Development"}
                        ]
                    }],
                    "button": "Pilih Menu"
                }
            }
        }
        await self._post("messages", payload)