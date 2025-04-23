import os
import logging
import json
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv 
from fastapi import Depends, HTTPException
from globals import constants
from services.whatsapp_service import WhatsappService
from handlers.message_handler import MessageHandler  # Import MessageHandler

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

TOKEN_VERIFIER_WEBHOOK = os.getenv("TOKEN_VERIFIER_WEBHOOK")

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

# Dependency Injection for WhatsAppService
def get_whatsapp_service():
    return WhatsappService()

# Dependency Injection for WebhookProcessor
class WebhookProcessor:
    def __init__(self, whatsapp_service: WhatsappService):
        self.whatsapp_service = whatsapp_service
        self.message_handler = MessageHandler(whatsapp_service) # Initialize MessageHandler
        self.user_sessions = {} # Format: {phone: {"last_active": datetime, "active": bool}}
        self._initialized = False  # Prevent multiple inits
        
    async def initialize(self):
        if not self._initialized:
            self.lock = asyncio.Lock()
            asyncio.create_task(self.cleanup_sessions())
            self._initialized = True
        
    async def cleanup_sessions(self):
        while True:
            now = datetime.utcnow()
            
            async with self.lock:
                for user, session in list(self.user_sessions.items()):  
                    if session.get("active") and not session.get("ended"):
                        if now - session["last_active"] > timedelta(minutes=1):
                            await self.whatsapp_service.send_message(
                                user,
                                "Terimakasih telah menghubungi layanan member Alfamidi. Sampai jumpa lain waktu."
                            )
                            session["active"] = False
                            session["ended"] = True
                            logger.info(f"[Session] Ended session for {user} at {now.isoformat()}")
                            
            await asyncio.sleep(10)
        
    async def process_webhook_entry(self, entry: dict):
        await self.initialize()  # <-- Make sure everything is ready

        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        contacts = value.get("contacts", [])
        messages = value.get("messages", [])
        if not messages:
            return

        message = messages[0]
        from_no = message["from"]
        message_type = message.get("type")
        username = contacts[0].get("profile", {}).get("name", "Pelanggan") if contacts else "Pelanggan"

        now = datetime.utcnow()
        async with self.lock:
            session = self.user_sessions.get(from_no)

            # Do not greet again
            if not session or session.get("ended", False):
                logger.info(f"[Session] Starting new session for {from_no}.")

            self.user_sessions[from_no] = {
                "last_active": now,
                "active": True,
                "ended": False  # Reset session end flag when user sends a message
            }
            logger.info(f"[Session] Updated session for {from_no} at {now.isoformat()}")

        if message_type == constants.TEXT_MESSAGE:
            await self.message_handler.handle_text_message(message, from_no, username)
        elif message_type == constants.INTERACTIVE_MESSAGE:
            await self.message_handler.handle_interactive_message(message.get("interactive", {}), from_no, username)


def get_webhook_processor(whatsapp_service: WhatsappService = Depends(get_whatsapp_service)):
    return WebhookProcessor(whatsapp_service)

async def webhook_handler(payload: dict, webhook_processor: WebhookProcessor = Depends(get_webhook_processor)):
    try:
        logger.info(f"📩 Webhook payload masuk:\n{json.dumps(payload, indent=2)}")

        if not payload.get("object"):
            logger.warning("Received payload with invalid object")
            return {"message": "Invalid object"}

        entry = payload.get("entry", [{}])[0]
        await webhook_processor.process_webhook_entry(entry)

        return {"status": "success"}

    except HTTPException as http_exc:
        raise http_exc # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error in webhook handler: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")