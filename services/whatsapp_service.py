import os
import logging
import httpx
from globals import constants
from fastapi import HTTPException
from dotenv import load_dotenv  

# Load environment variables from .env
load_dotenv()

# Konfigurasi logging
logger = logging.getLogger(__name__)

class WhatsappService:
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
                            {"id": constants.MEMBER, "title": "Member"},
                            {"id": constants.ON_DEV_1, "title": "Menu On Development"}
                        ]
                    }],
                    "button": "Pilih Menu"
                }
            }
        }
        await self._post("messages", payload)
        
    async def send_member_menu(self, to: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": f"Berikut adalah layanan Member yang tersedia:"},
                "action": {
                    "sections": [{
                        "title": "Menu Member",
                        "rows": [
                            {"id": constants.MEMBER_MENU_INFO, "title": "Informasi Member"},
                            {"id": constants.MEMBER_MENU_REGISTER, "title": "Daftar Member"},
                            {"id": constants.MEMBER_MENU_CHECK_POINTS, "title": "Cek Poin Member"},
                            {"id": constants.BACK_TO_MAIN_MENU, "title": "Main Menu"}
                        ]
                    }],
                    "button": "Pilih Layanan Member"
                }
            }
        }
        
        await self._post("messages", payload)

    # Example of sending a template message (Illustrative)
    async def send_template_message(self, to: str, template_name: str, language_code: str, components: list = None):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }
        if components:
            payload["template"]["components"] = components
        await self._post("messages", payload)