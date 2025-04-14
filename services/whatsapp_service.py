import os
import logging
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv  # <-- add this

# Load environment variables from .env
load_dotenv()

# Konfigurasi logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Optional: show logs in console

# Environment Variables
TOKEN_META = os.getenv("TOKEN_META")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

print("TOKEN_META:", TOKEN_META)  # Debug print, remove in production

# Menu Constants
MENU_1 = "menu-1"
MENU_2 = "menu-2"

async def send_message(no_hp: str, message: str):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages?access_token={TOKEN_META}"
    payload = {
        "messaging_product": "whatsapp",
        "to": no_hp,
        "type": "text",
        "text": {"body": message},
    }
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            logger.error(f"Send Message Error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to send message")

async def send_menu(no_hp: str):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages?access_token={TOKEN_META}"
    payload = {
        "messaging_product": "whatsapp",
        "to": no_hp,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "menu utama. Silakan pilih layanan"},
            "action": {
                "sections": [{
                    "title": "menu",
                    "rows": [
                        {"id": MENU_1, "title": "MENU 1"},
                        {"id": MENU_2, "title": "MENU 2"}
                    ]
                }],
                "button": "Pilih Menu"
            }
        }
    }
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            logger.error(f"Send main menu error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to send menu")
