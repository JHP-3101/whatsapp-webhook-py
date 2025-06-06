from core.logger import get_logger
from services.whatsapp_service import WhatsAppService
from handlers.message_handler import MessageHandler
from globals.constants import WAFlow
from core.logger import get_logger

logger = get_logger()

class FlowHandler:
    def __init__(self, whatsapp_service: WhatsAppService):
        self.flow_token_activate = WAFlow.WAFLOW_TOKEN_ACTIVATE
        self.whatsapp_service = whatsapp_service
        self.version = "3"
    
    async def handle_flow(self, screen: str, version: str, data: dict, flow_token: str, action: str = None):
        # Handle health check
        if action == "ping":
            return {
                "version": self.version,
                "screen": screen,
                "action": "ping",
                "data": {"status": "active"},
            }
            
        # ACTIVATE MEMBER
        if flow_token == self.flow_token_activate:
            if screen == "REGISTER":
                return await self.validate_activation(version, data)
        elif flow_token != self.flow_token_activate:
            return {
                "version": self.version,
                "screen": screen or "UNKNOWN",
                "action": "error",
                "data": {"message": "Invalid flow token"},
            }

        # Default response
        return {
            "version": self.version,
            "screen": screen or "UNKNOWN",
            "action": "error",
            "data": {"message": "Unhandled flow"},
        }

    async def validate_activation(self, version: str, data: dict):
        
        name = data.get("name", "")
        birth_date = data.get("birth_date", "")
        phone_number = data.get("phone_number", "")
        card_number = data.get("card_number", "")
        email = data.get("email", "")
        gender = data.get("gender", "")
        marital = data.get("marital", "")
        address = data.get("address", "")
            
        response = {
                "version": version,
                "screen": "CONFIRM",
                "action": "update",
                "data": {
                    "phone_number": phone_number,
                    "card_number": card_number,
                    "name": name,
                    "birth_date": birth_date,
                    "email": email,
                    "gender": gender,
                    "marital": marital,
                    "address": address
                }
            }
        
        logger.info(f"CONFIRMATION DATA FROM FLOW | {response}")
        return response
