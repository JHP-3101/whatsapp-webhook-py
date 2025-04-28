from fastapi import APIRouter, Request, Response
from services.whatsapp_service import WhatsAppService
from handlers.message_handler import MessageHandler
from handlers.contact_handler import ContactHandler
from core.logger import get_logger
import os

router = APIRouter()
logger = get_logger()

TOKEN_VERIFIER_WEBHOOK = os.getenv("TOKEN_VERIFIER_WEBHOOK")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

whatsapp_service = WhatsAppService()
message_handler = MessageHandler(whatsapp_service)
contact_handler = ContactHandler(whatsapp_service)

@router.get("/webhook")
async def verify_webhook(request: Request):
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
    logger.info(f"Verification attempt - Mode: {hub_mode}, Token: {hub_verify_token}")

    if not all([hub_mode, hub_challenge, hub_verify_token]):
        logger.error("Missing one or more verification parameters")
        raise HTTPException(status_code=400, detail="Bad Request: Missing parameters")

    if hub_mode == "subscribe" and hub_verify_token == TOKEN_VERIFIER_WEBHOOK:
        logger.info("Webhook verified successfully")
        return int(hub_challenge)

    logger.error(f"Verification failed - Expected token: {TOKEN_VERIFIER_WEBHOOK}, Received: {hub_verify_token}")
    raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/webhook")
async def webhook_handler(request: Request):
    try:
        body = await request.json()
        logger.info(f"Received webhook body: {body}")

        if not body.get("object"):
            return Response(content="Invalid object", status_code=200)

        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        # Validate phone number ID
        if value.get("metadata", {}).get("phone_number_id") != PHONE_NUMBER_ID:
            return Response(content="Phone number ID does not match", status_code=400)

        # Handle messages
        messages = value.get("messages", [])
        contacts = value.get("contacts", [])

        # Handle messages
        if messages:
            for message in messages:
                from_number = message.get("from")

                if message["type"] == "text":
                    await message_handler.handle_text_message(from_number, message["text"]["body"])
                elif message["type"] == "interactive":
                    await message_handler.handle_interactive_message(from_number, message["interactive"])

        # Handle contacts
        if contacts:
            for contact in contacts:
                profile_name = await contact_handler.get_profile_name(contact)
                logger.info(f"Incoming message from profile: {profile_name}")


        return Response(content="Event received", status_code=200)

    except Exception as e:
        logger.error(f"Error in webhook_handler: {str(e)}", exc_info=True)
        return Response(content="Internal server error", status_code=200)
