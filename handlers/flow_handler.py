from core.logger import get_logger
from services.whatsapp_service import WhatsAppService
from globals.constants import WAFlow

class FlowHandler:
    def __init__(self, whatsapp_service: WhatsAppService):
        self.flow_token = WAFlow.WAFLOW_TOKEN_ACTIVATE
        self.whatsapp_service = whatsapp_service
        self.version = "3"
    
    async def handle_flow(self, screen: str, version: str, data: dict, flow_token: str, action: str = None):
        # Handle health check
        if action == "ping":
            return {
                "version": self.version,
                "screen": screen or "REGISTER",
                "action": "ping",
                "data": {"status": "active"},
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

        name_error = "" if name else "Nama wajib diisi"
        birth_date_error = "" if birth_date else "Tanggal lahir wajib diisi"

        if name_error or birth_date_error:
            return {
                "version": self.version,
                "screen": "REGISTER",
                "action": "update",
                "data": {
                    "name_error": name_error,
                    "birth_date_error": birth_date_error,
                    "phone_number": phone_number,
                }
            }

        return {
            "version": self.version,
            "screen": "CONFIRM",
            "action": "update",
            "data": {
                "name": name,
                "birth_date": birth_date,
                "phone_number": phone_number,
            }
        }
