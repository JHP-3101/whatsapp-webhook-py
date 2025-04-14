import os
import logging
from fastapi import HTTPException
from dotenv import load_dotenv  # ⬅️ Add this line to load .env
from services.whatsapp_service import send_message, send_menu

# Load environment variables from .env file
load_dotenv()

# Konfigurasi logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Environment Variables
TOKEN_VERIFIER_WEBHOOK = os.getenv("TOKEN_VERIFIER_WEBHOOK")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

async def webhook_verifier_handler(hub_mode: str, hub_challenge: str, hub_verify_token: str):
    if hub_mode and hub_verify_token:
        if hub_mode == "subscribe" and hub_verify_token == TOKEN_VERIFIER_WEBHOOK:
            return int(hub_challenge)
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
    raise HTTPException(status_code=400, detail="Bad Request")

async def webhook_handler(payload: dict):
    try:
        if not payload.get("object"):
            return {"message": "Invalid object"}

        entry = payload.get("entry", [])[0] if payload.get("entry") else None
        changes = entry.get("changes", [])[0] if entry and "changes" in entry else None
        messages = changes["value"].get("messages") if changes and "value" in changes else None

        if changes["value"]["metadata"]["phone_number_id"] != PHONE_NUMBER_ID:
            raise HTTPException(status_code=400, detail="Phone number ID does not match")

        if not messages:
            return {"message": "No messages to process"}

        from_no = messages[0]["from"]
        message = messages[0]
        
        if message["type"] == "text":
            msg_body = message["text"].get("body")
            if msg_body == "test":
                await send_message(from_no, "hello world!")
            else:
                await send_menu(from_no)

        elif message["type"] == "interactive" and message["interactive"]["type"] == "list_reply":
            list_reply_id = message["interactive"]["list_reply"]["id"]
            response_text = "anda memilih menu 1" if list_reply_id == "menu-1" else "anda memilih menu 2"
            await send_message(from_no, response_text)

    except Exception as e:
        logger.error(f"handleWebhook: get error {e}")
        return {"message": "Internal server error"}
