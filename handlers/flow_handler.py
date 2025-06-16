from core.logger import get_logger
from services.whatsapp_service import WhatsAppService
from services.plms_service import PLMSService
from globals.constants import WAFlow
from core.logger import get_logger
from datetime import datetime

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
            
        logger.info(f"Flow Handler | Token Incoming : {flow_token}")
            
        # ACTIVATE MEMBER
        if flow_token == self.flow_token_activate:
            if screen == "REGISTER":
                return await self.validate_activation(version, data)
            
        # RESET PIN 
        elif flow_token == self.flow_token_reset_pin:
            if screen == "VALIDATION":
                return await self.validate_birth_date(version, data)
                
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
        response = {
            "version": version,
            "screen": "CONFIRM",
            "action": "update",
            "data": {
                key: data.get(key, "") for key in [
                    "phone_number", "card_number", "name", "birth_date",
                    "email", "gender", "marital", "address"
                ]
            }
        }
        logger.info(f"CONFIRMATION DATA FROM FLOW | {response}")
        return response

    async def validate_birth_date(self, version: str, data: dict):
        phone_number = data.get("phone_number", "")
        birth_date_input = data.get("birth_date", "")

        if not birth_date_input:
            return {
                "version": version,
                "screen": "VALIDATION",
                "action": "update",
                "data": {
                    "birth_date_error": "Tanggal lahir wajib diisi"
                }
            }

        try:
            member = await self.plms_service.tnc_inquiry(str(phone_number))
            if not member or not member.get("birth_date", ""):
                raise Exception("Data member tidak ditemukan atau tidak memiliki tanggal lahir.")

            # Format checking
            try:
                input_dt = datetime.strptime(birth_date_input, "%Y-%m-%d").date()
                member_dt = datetime.strptime(member["birth_date"], "%Y-%m-%d").date()
            except Exception as e:
                return {
                    "version": version,
                    "screen": "VALIDATION",
                    "action": "update",
                    "data": {
                        "birth_date_error": "Format tanggal tidak valid"
                    }
                }

            if input_dt == member_dt:
                return {
                    "version": version,
                    "screen": "RESET_PIN",
                    "action": "update",
                    "data": {}
                }
            else:
                return {
                    "version": version,
                    "screen": "VALIDATION",
                    "action": "update",
                    "data": {
                        "birth_date_error": "Tanggal lahir tidak sesuai dengan data kami"
                    }
                }
                
        except Exception as e:
            logger.error(f"Birth date validation error: {str(e)}")
            return {
                "version": version,
                "screen": "VALIDATION",
                "action": "update",
                "data": {
                    "birth_date_error": "Terjadi kesalahan saat validasi. Silakan coba lagi."
                }
            }
        
    
    async def validate_pin(self, version: str, data: dict):
        pin = data.get("pin", "")
        confirm_pin = data.get("confirm_pin", "")

        if not pin or not confirm_pin:
            return {
                "version": version,
                "screen": "RESET_PIN",
                "action": "update",
                "data": {
                    "pin_error": "PIN dan konfirmasi wajib diisi"
                }
            }

        if pin != confirm_pin:
            return {
                "version": version,
                "screen": "RESET_PIN",
                "action": "update",
                "data": {
                    "pin_error": "PIN dan konfirmasi PIN tidak sama"
                }
            }

        return {
            "version": version,
            "screen": "RESET_PIN",
            "action": "complete",
            "data": {
                "pin": pin
            }
        }