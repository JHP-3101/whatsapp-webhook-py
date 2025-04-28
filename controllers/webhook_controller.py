# app/controllers/webhook_handler.py
import os
from fastapi import APIRouter, Request
from starlette.responses import Response
from handlers.message_handler import MessageHandler
from handlers.contact_handler import ContactHandler
from core.loggerlogger import logger
from globals.constants import PHONE_NUMBER_ID

router = APIRouter()

@router.post("/webhook")
async def webhook_handler(request: Request):
    try:
        body = await request.json()
        logger.info(f"Received webhook body: {body}")

        if not body.get("object"):
            logger.warning("Invalid object in webhook body")
            return Response(content="Invalid object", status_code=200)

        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        incoming_phone_number_id = value.get("metadata", {}).get("phone_number_id")
        if incoming_phone_number_id != PHONE_NUMBER_ID:
            logger.warning(f"Phone number mismatch. Expected {PHONE_NUMBER_ID}, got {incoming_phone_number_id}")
            return Response(content="Phone number ID does not match", status_code=200)

        messages = value.get("messages", [])
        contacts = value.get("contacts", [])

        if contacts:
            for contact in contacts:
                await ContactHandler.process_contact(contact)

        if messages:
            for message in messages:
                await MessageHandler.process_message(message)

        return Response(content="Webhook processed successfully", status_code=200)

    except Exception as e:
        logger.error(f"Webhook handler error: {str(e)}", exc_info=True)
        return Response(content="Internal server error", status_code=200)

@router.get("/webhook")
async def webhook_verification(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    challenge = params.get("hub.challenge")
    verify_token = params.get("hub.verify_token")

    if mode == "subscribe" and verify_token == os.getenv("TOKEN_VERIFIER_WEBHOOK"):
        return Response(content=challenge, status_code=200)
    else:
        return Response(content="Verification failed", status_code=403)
