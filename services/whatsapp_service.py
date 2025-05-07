import os
import httpx
from core.logger import get_logger
from fastapi import HTTPException
from dotenv import load_dotenv
from globals.constants import Menu

logger = get_logger()

load_dotenv()

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

    async def send_main_menu(self, to: str, username: str = "Pelanggan"):
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
                            {"id": Menu.MEMBER, "title": "Member"},
                            {"id": Menu.MENU_2, "title": "MENU ON DEV 2"}
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
                "body": {"text": "Silakan pilih layanan member yang anda butuhkan"},
                "action": {
                    "sections": [{
                        "title": "Pilih Menu",
                        "rows": [
                            {"id": Menu.MEMBER_REGISTRASI, "title": "Validasi"},
                            {"id": Menu.MAIN_MENU, "title": "Menu Utama"}
                        ]
                    }],
                    "button": "Pilih Menu"
                }
            }
        }
        await self._post("messages", payload)
        
    async def send_member_services_menu(self, to: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": "Nomor Anda telah terdaftar ke dalam member Alfamidi.\nSilakan pilih layanan member yang tersedia:"},
                "action": {
                    "sections": [{
                        "title": "Layanan Member",
                        "rows": [
                            {"id": Menu.MEMBER_CEK_POIN, "title": "Cek Poin"},
                            {"id": Menu.MEMBER_STATUS_KARTU, "title": "Status Kartu"},
                            {"id": Menu.MEMBER_RIWAYAT_TRANSAKSI_POIN, "title": "Riwayat Transaksi Poin"},
                            {"id": Menu.MEMBER_RESET_PIN, "title": "Reset PIN"},
                            {"id": Menu.MAIN_MENU, "title": "Kembali ke Menu Utama"}
                        ]
                    }],
                    "button": "Pilih Layanan"
                }
            }
        }
        await self._post("messages", payload)
    
    async def send_registration_menu(self, to: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": "Nomor Anda belum terdaftar sebagai member. Silakan daftar di bawah ini:"},
                "action": {
                    "sections": [{
                        "title": "Registrasi Member",
                        "rows": [
                            {"id": Menu.MEMBER_REGISTRASI, "title": "Registrasi"},
                            {"id": Menu.MAIN_MENU, "title": "Kembali ke Menu Utama"}
                        ]
                    }],
                    "button": "Lanjutkan"
                }
            }
        }
        await self._post("messages", payload)