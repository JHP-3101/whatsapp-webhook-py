import os
import logging
from fastapi import HTTPException
from dotenv import load_dotenv
from services.whatsapp_service import send_message, send_menu
from handlers.whatsapp_handlers import MessageHandler, ContactHandler

# Load .env
load_dotenv()

# Konfigurasi logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Env vars
TOKEN_VERIFIER_WEBHOOK = os.getenv("TOKEN_VERIFIER_WEBHOOK")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


class WebhookController:
    def __init__(self):
        self.token_verifier = TOKEN_VERIFIER_WEBHOOK
        self.phone_number_id = PHONE_NUMBER_ID

    async def verify(self, hub_mode: str, hub_challenge: str, hub_verify_token: str):
        logger.info(f"🔐 Verification request: mode={hub_mode}, token={hub_verify_token}")
        
        if not all([hub_mode, hub_challenge, hub_verify_token]):
            logger.error("❌ Missing verification parameters")
            raise HTTPException(status_code=400, detail="Bad Request: Missing parameters")

        if hub_mode == "subscribe" and hub_verify_token == self.token_verifier:
            logger.info("✅ Webhook verified successfully")
            return int(hub_challenge)

        logger.error(f"❌ Token mismatch: expected={self.token_verifier}")
        raise HTTPException(status_code=403, detail="Forbidden")

    async def handle_webhook(self, payload: dict):
        import json
        logger.info(f"📩 Payload masuk:\n{json.dumps(payload, indent=2)}")

        if not payload.get("object"):
            logger.warning("⚠️ Invalid payload object")
            return {"message": "Invalid object"}

        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        if value.get("metadata", {}).get("phone_number_id") != self.phone_number_id:
            logger.error("📞 Phone number ID mismatch")
            raise HTTPException(status_code=400, detail="Phone number ID does not match")

        contact_handler = ContactHandler(value)
        username, from_no = contact_handler.extract_user_info()

        message_handler = MessageHandler(value, from_no, username)
        return await message_handler.process()
