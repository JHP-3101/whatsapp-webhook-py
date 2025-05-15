from core.logger import get_logger
from services.whatsapp_service import WhatsAppService
from globals.constants import WAFlow
from datetime import datetime
import re
from core.logger import get_logger

logger = get_logger()

class FlowHandler:
    def __init__(self, whatsapp_service: WhatsAppService):
        self.flow_token = WAFlow.WAFLOW_TOKEN_REGISTER
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
            
        if flow_token != self.flow_token:
            return {
                "version": self.version,
                "screen": screen or "UNKNOWN",
                "action": "error",
                "data": {"message": "Invalid flow token"},
            }

        if flow_token == self.flow_token:
            if screen == "REGISTER":
                return self.validate_register(version, data)

        # Default response
        return {
            "version": self.version,
            "screen": screen or "UNKNOWN",
            "action": "error",
            "data": {"message": "Unhandled flow"},
        }

    def validate_register(self, version: str, data: dict):
        
        name = data.get("name", "")
        birth_date = data.get("birth_date", "")
        phone_number = data.get("phone_number", "")
        card_number = data.get("card_number", "")
        email = data.get("email", "")
        gender = data.get("gender", "")
        marital = data.get("marital", "")
        address = data.get("address", "")
        
        formatted_birth_date = ""
        try:
            if birth_date:
                formatted_birth_date = datetime.strptime(birth_date, "%Y-%m-%d").strftime("%d%m%Y")
        except ValueError:
            logger.warning(f"Invalid birth_date format: {birth_date}")
            formatted_birth_date = birth_date

        return {
                "version": version,
                "screen": "CONFIRM",
                "action": "update",
                "data": {
                    "phone_number": phone_number,
                    "card_number": card_number,
                    "name": name,
                    "birth_date": formatted_birth_date,
                    "email": email,
                    "gender": gender,
                    "marital": marital,
                    "address": address
                }
            }
