from fastapi import APIRouter, Request, Response
from services.whatsapp_service import WhatsAppService
from services.plms_service import PLMSService
from handlers.message_handler import MessageHandler
from handlers.contact_handler import ContactHandler
from handlers.flow_handler import FlowHandler
from services.flow_service import FlowCryptoService
from core.logger import get_logger
from dotenv import load_dotenv
import os

router = APIRouter()
logger = get_logger()
load_dotenv()

TOKEN_VERIFIER_WEBHOOK = os.getenv("TOKEN_VERIFIER_WEBHOOK")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
PASSPHRASE_ENV = os.environ.get("PASSPHRASE_ENV")  # if needed

crypto_service = FlowCryptoService(PRIVATE_KEY, PASSPHRASE_ENV)

whatsapp_service = WhatsAppService()
plms_service = PLMSService()
flow_handler = FlowHandler(whatsapp_service)
message_handler = MessageHandler(whatsapp_service)
contact_handler = ContactHandler(whatsapp_service)


@router.get("/login")
async def plms_login():
    try:
        plms_service = PLMSService()
        plms_service.login()
        return{"message": "Login successful", "token": plms_service.token}
    except Exception as e:
        return Response(content=f"Login failed: {str(e)}", status_code=500)

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
        # Know The Body Of The Messages
        # logger.info(f"Received webhook body: {body}") 

        if not body.get("object"):
            return Response(content="Invalid object", status_code=200)

        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        # Validate phone number ID
        safe_validate_phone_number_id(value)

        # Get the value of messages and contacts
        messages = value.get("messages", [])
        contacts = value.get("contacts", [])
        
        # Handle contacts
        if contacts:
            for contact in contacts:
                username = await contact_handler.get_profile_name(contact)
                phone_number = await contact_handler.get_phone_number(contact)
                logger.info(f"Incoming message from profile: {username} | {phone_number}")

        # Handle messages
        if messages:
            message = messages[0]
            from_number = message.get("from")

            if message["type"] == "text":
                await message_handler.handle_text_message(from_number, message["text"]["body"], username)
                
            if message["type"] == "interactive":
                interactive_type = message["interactive"].get("type")
                
                if interactive_type == "list_reply":
                    await message_handler.handle_list_reply(from_number, message["interactive"]["list_reply"])
                elif interactive_type == "nfm_reply":
                    await message_handler.handle_nfm_reply(from_number, message["interactive"]["nfm_reply"])
                

        return Response(content="Event received", status_code=200)

    except Exception as e:
        logger.error(f"Error in webhook_handler: {str(e)}", exc_info=True)
        return Response(content="Internal server error", status_code=200)
    
@router.post("/waflow")
async def waflow_handler(request: Request):
    try:
        encrypted_body = await request.body()
        decrypted_body, aes_key, iv = crypto_service.decrypt_request(encrypted_body)

        screen = decrypted_body.get("screen")
        data = decrypted_body.get("data")
        version = decrypted_body.get("version")
        action = decrypted_body.get("action")
        flow_token = decrypted_body.get("flow_token")

        if not version or not action:
            return Response(content="Missing required fields", status_code=400)

        screen_data = await flow_handler.handle_flow(screen, version, data, flow_token, action)

        if screen_data and all(k in screen_data for k in ["version", "screen", "action", "data"]):
            encrypted_response = crypto_service.encrypt_response(screen_data, aes_key, iv)
            return Response(content=encrypted_response, media_type="text/plain")
        else:
            return Response(content="Invalid screenData", status_code=500)

    except Exception as e:
        logger.error(f"Error waflow handler: {str(e)}", exc_info=True)
        return Response(content="Internal Server Error", status_code=500)
