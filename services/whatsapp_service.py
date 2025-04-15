import os
import logging
import httpx
from globals import constants
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

async def get_whatsapp_profile(phone_number: str):
    """Get WhatsApp user's profile information (including name)"""
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "contacts"
    }
    headers = {
        "Authorization": f"Bearer {TOKEN_META}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(f"Profile lookup error: {response.text}")
                return None
            
            data = response.json()
            if data.get("contacts"):
                contact = data["contacts"][0]
                return contact.get("profile", {}).get("name")
    except Exception as e:
        logger.error(f"Error fetching WhatsApp profile: {str(e)}")
        return None

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
    username = await get_whatsapp_profile(no_hp) or "Pelanggan"
    
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages?access_token={TOKEN_META}"
    payload = {
        "messaging_product": "whatsapp",
        "to": no_hp,
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
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"Send menu error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to send menu")