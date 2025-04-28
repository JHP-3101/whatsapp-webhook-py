from fastapi import APIRouter, Request, Response
from services.whatsapp_service import WhatsAppService
from handlers.message_handler import MessageHandler
from handlers.contact_handler import ContactHandler
from core.logger import get_logger
from dotenv import load_dotenv
import os

router = APIRouter()
logger = get_logger()
load_dotenv()

TOKEN_VERIFIER_WEBHOOK = os.getenv("TOKEN_VERIFIER_WEBHOOK")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

whatsapp_service = WhatsAppService()
message_handler = MessageHandler(whatsapp_service)
contact_handler = ContactHandler(whatsapp_service)

@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    challenge = request.query_params.get("hub.challenge")
    verify_token = request.query_params.get("hub.verify_token")

    if mode and verify_token:
        if mode == "subscribe" and verify_token == TOKEN_VERIFIER_WEBHOOK:
            return Response(content=challenge, status_code=200)
        else:
            return Response(content="Forbidden", status_code=403)
    else:
        return Response(content="Bad Request", status_code=400)

def safe_validate_phone_number_id(value: dict) -> bool:
    received_phone_number_id = value.get("metadata", {}).get("phone_number_id")
    if received_phone_number_id != PHONE_NUMBER_ID:
        logger.warning(f"Phone number ID mismatch: received={received_phone_number_id}, expected={PHONE_NUMBER_ID}")
        return False
    return True

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
        safe_validate_phone_number_id(value)

        # Handle messages
        messages = value.get("messages", [])
        contacts = value.get("contacts", [])
        username = await contact_handler.get_profile_name(contact)

        # Handle messages
        if messages:
            message = messages[0]
            from_number = message.get("from")

            if message["type"] == "text":
                await message_handler.handle_text_message(from_number, message["text"]["body"], username)
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
