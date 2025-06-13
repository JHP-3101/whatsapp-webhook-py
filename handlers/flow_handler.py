from core.logger import get_logger
from services.whatsapp_service import WhatsAppService
from services.plms_service import PLMSService
from handlers.message_handler import MessageHandler
from globals.constants import WAFlow
from core.logger import get_logger
from time import datetime

logger = get_logger()

class FlowHandler:
    def __init__(self, whatsapp_service: WhatsAppService, plms_service: PLMSService):
        self.flow_token_activate = WAFlow.WAFLOW_TOKEN_ACTIVATE
        self.flow_token_reset_pin = WAFlow.WAFLOW_TOKEN_RESET_PIN
        self.whatsapp_service = whatsapp_service
        self.plms_service = plms_service
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
            
        # Flow Token Handling
        if flow_token == self.flow_token_activate:
            if screen == "REGISTER":
                return await self.validate_activation(version, data)
            
        elif flow_token == self.flow_token_reset_pin:
            if screen == "VALIDATION":
                return await self.validate_birth_date(version, data)
            elif screen == "RESET_PIN":
                return await self.validate_pin(version, data)
        
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
    
    
    async def validate_birth_date(self, version: str, data: dict):
        phone_number = data.get("phone_number", "")
        submitted_birth_date = data.get("birth_date", "")
        
        # Get From PLMS
        member_info = await self.plms_service.inquiry(phone_number)
        correct_birth_date = member_info.get("birth_date", "")
        
        try: 
            parsed_birth_date = datetime.strptime(submitted_birth_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            if parsed_birth_date != correct_birth_date:
                return {
                    "version": version,
                    "screen": "VALIDATION",
                    "action": "update",
                    "data": {
                        "birth_date_error": "Tanggal lahir tidak sesuai dengan data kami."
                    }
                }
                
        except Exception:
            return {
                "version": version,
                "screen": "VALIDATION",
                "action": "update",
                "data": {
                    "birth_date_error": "Format tanggal tidak valid."
                }
            }
            
        # Pass validation → move to RESET_PIN screen
        return {
            "version": version,
            "screen": "RESET_PIN",
            "action": "update",
            "data": {
                "phone_number": phone_number
            }
        }
        
    
    async def validate_pin(self, version: str, data: dict):
        pin = data.get("pin", "")
        confirm_pin = data.get("confirm_pin", "")
        phone_number = data.get("phone_number", "")

        if pin != confirm_pin:
            return {
                "version": version,
                "screen": "RESET_PIN",
                "action": "update",
                "data": {
                    "pin_error": "PIN dan konfirmasi PIN tidak sama."
                }
            }

        # Final success response
        return {
            "version": version,
            "screen": "RESET_PIN",
            "action": "complete",
            "data": {
                "message": f"PIN berhasil direset untuk nomor {phone_number}."
            }
        }      
    

