from core.logger import get_logger
from services.whatsapp_service import WhatsAppService

class FlowHandler :
    def __init__(self, whatsapp_service: WhatsAppService):
        self.whatsapp_service = whatsapp_service
    
    async def handle_flow(self, screen: str, version: str, data: dict, flow_token: str):
        screen_data = {
            "version": version,
            "screen": "REGISTER",
            "action": "ping",
            "data": {
                "status": "active",
            },
        }

        if flow_token == "WAFLOW_ACTIVATE":  # Replace with real value or ENV if needed
            if screen == "REGISTER":
                screen_data = self.validate_register(version, data)

        return screen_data
    
    def validate_register(self, version: str, data: dict):
        name = data.get("name", "")
        birth_date = data.get("birth_date", "")
        phone_number = data.get("phone_number", "")

        name_error = "" if name else "Nama wajib diisi"
        birth_date_error = "" if birth_date else "Tanggal lahir wajib diisi"

        if name_error or birth_date_error:
            return {
                "version": version,
                "screen": "REGISTER",
                "action": "update",
                "data": {
                    "name_error": name_error,
                    "birth_date_error": birth_date_error,
                    "phone_number": phone_number,
                }
            }

        return {
            "version": version,
            "screen": "CONFIRM",
            "action": "update",
            "data": {
                "name": name,
                "birth_date": birth_date,
                "phone_number": phone_number,
            }
        }