import os
import httpx
from core.logger import get_logger
from fastapi import HTTPException
from dotenv import load_dotenv
from globals.constants import Menu, WAFlow

logger = get_logger()

load_dotenv()

class WhatsAppService:

    def __init__(self):
        self.token = os.getenv("TOKEN_META")
        self.phone_number_id = os.getenv("PHONE_NUMBER_ID")
        self.base_url = "https://graph.facebook.com/v20.0"
        
        self.flow_mode = WAFlow.WAFLOW_MODE_ACTIVATE
        self.flow_id = WAFlow.WAFLOW_ID_ACTIVATE
        self.flow_token = WAFlow.WAFLOW_TOKEN_ACTIVATE
        self.flow_version = "3"
        
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

    async def send_greetings(self, to: str, username: str = "Pelanggan"):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": f"Halo *_{username}_*! 👋🏻 🤗. Selamat datang di layanan Member *Alfamidi*. Silahkan pilih layanan yang anda butuhkan."},
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
        
    async def send_main_menu(self, to: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": f"Silahkan pilih layanan yang anda butuhkan."},
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
        
    async def send_member_services_menu(self, to: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": "Silakan pilih layanan member yang tersedia:"},
                "action": {
                    "sections": [{
                        "title": "Layanan Member",
                        "rows": [
                            {"id": Menu.MEMBER_CEK_POIN, "title": "Cek Poin"},
                            {"id": Menu.MEMBER_STATUS_KARTU, "title": "Cek Status Member"},
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
    
    async def send_activation_menu(self, to: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": "Nomor Anda belum terdaftar sebagai member.\n\nSilakan daftar di bawah ini:"},
                "action": {
                    "sections": [{
                        "title": "Registrasi Member",
                        "rows": [
                            {"id": Menu.MEMBER_AKTIVASI, "title": "Aktivasi"},
                            {"id": Menu.MAIN_MENU, "title": "Kembali ke Menu Utama"}
                        ]
                    }],
                    "button": "Lanjutkan"
                }
            }
        }
        await self._post("messages", payload)
        
    async def send_form_register(self, to: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "flow",
                "body": {
                    "text": "📝 Registrasi Member"
                },
                "action": {
                    "name": "flow",
                    "parameters": {
                        "flow_message_version": self.flow_version,
                        "mode": self.flow_mode,
                        "flow_token": self.flow_token,
                        "flow_id": self.flow_id,
                        "flow_cta": "Daftar Sekarang",
                        "flow_action": "navigate",
                        "flow_action_payload": {
                            "screen": "REGISTER",
                            "data": {
                                "phone_number": to, 
                            },
                        }
                    }
                }
            }
        }
        await self._post("messages", payload)
    