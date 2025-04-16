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

async def webhook_verifier_handler(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    logger.info(f"Verification attempt - Mode: {hub_mode}, Token: {hub_verify_token}")
    
    if not all([hub_mode, hub_challenge, hub_verify_token]):
        logger.error("Missing one or more verification parameters")
        raise HTTPException(status_code=400, detail="Bad Request: Missing parameters")
    
    if hub_mode == "subscribe" and hub_verify_token == TOKEN_VERIFIER_WEBHOOK:
        logger.info("Webhook verified successfully")
        return int(hub_challenge)
    
    logger.error(f"Verification failed - Expected token: {TOKEN_VERIFIER_WEBHOOK}, Received: {hub_verify_token}")
    raise HTTPException(status_code=403, detail="Forbidden")

async def webhook_handler(payload: dict):
    try:
        if not payload.get("object"):
            logger.warning("Received payload with invalid object")
            return {"message": "Invalid object"}

        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        if value.get("metadata", {}).get("phone_number_id") != PHONE_NUMBER_ID:
            logger.error("Phone number ID mismatch")
            raise HTTPException(status_code=400, detail="Phone number ID does not match")

        messages = value.get("messages", [])
        if not messages:
            logger.info("No messages in payload")
            return {"message": "No messages to process"}

        message = messages[0]
        from_no = message["from"]
        username = message.get("profile", {}).get("name", "Pelanggan")
        
        if message["type"] == "text":
            msg_body = message["text"].get("body", "").lower()
            username = message.get("profile", {}).get("name", "Pelanggan")
            
            if msg_body == "test":
                logger.info("Sending test message")
                await send_message(from_no, "hello world!")
            else:
                logger.info("Sending main menu")
                await send_menu(from_no, username)

        elif message["type"] == "interactive":
            interactive = message["interactive"]
            if interactive["type"] == "list_reply":
                list_reply_id = interactive["list_reply"]["id"]
                response_text = "Anda memilih menu 1" if list_reply_id == "menu-1" else "Anda memilih menu 2"
                logger.info(f"Handling list reply: {list_reply_id}")
                await send_message(from_no, response_text)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error in webhook handler: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")