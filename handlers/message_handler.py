import logging
from services.whatsapp_service import WhatsappService
from globals import constants

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, whatsapp_service: WhatsappService):
        self.whatsapp_service = whatsapp_service

    async def handle_text_message(self, message: dict, from_no: str, username: str):
        msg_body = message.get("text", {}).get("body", "").lower()
        if msg_body == "test":
            logger.info(f"Handling 'test' message from {from_no}")
            await self.whatsapp_service.send_message(from_no, "hello world!")
        elif msg_body == "menu":
            logger.info(f"Sending main menu to {from_no}")
            await self.whatsapp_service.send_menu(from_no, username)
        else:
            logger.info(f"Received unknown text message '{msg_body}' from {from_no}. Sending main menu.")
            await self.whatsapp_service.send_menu(from_no, username) # Default response

    async def handle_interactive_message(self, interactive: dict, from_no: str):
        interactive_type = interactive.get("type")
        if interactive_type == constants.LIST_REPLY:
            list_reply_id = interactive.get(constants.LIST_REPLY, {}).get("id")
            
            if list_reply_id == constants.MEMBER:
                response_text = "Anda memilih menu Member."
                logger.info(f"Handling list reply for Member: {list_reply_id} from {from_no}")
                await self.whatsapp_service.send_message(from_no, response_text)
                
                # Future: Trigger member-related logic here
            elif list_reply_id == constants.ON_DEV_1:
                response_text = "Menu ini sedang dalam pengembangan."
                logger.info(f"Handling list reply for On Development: {list_reply_id} from {from_no}")
                await self.whatsapp_service.send_message(from_no, response_text)
                
                # Future: Indicate that this is under development
            else:
                response_text = f"Anda memilih: {list_reply_id}"
                logger.warning(f"Unhandled list reply ID: {list_reply_id} from {from_no}")
                await self.whatsapp_service.send_message(from_no, response_text)
        # Add handling for other interactive types (e.g., buttons) if needed