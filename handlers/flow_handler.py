from core.logger import get_logger
from services.whatsapp_service import WhatsAppService
from services.plms_service import PLMSService
from globals.constants import WAFlow
from datetime import datetime
import re
from core.logger import get_logger

logger = get_logger()

class FlowHandler:
    def __init__(self, whatsapp_service: WhatsAppService):
        self.flow_token = WAFlow.WAFLOW_TOKEN_REGISTER
        self.whatsapp_service = whatsapp_service
        self.plms_service = PLMSService()
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
                return await self.validate_register(version, data)
            if screen == "CONFIRM":
                return await self.confirm_register(version, data)

        # Default response
        return {
            "version": self.version,
            "screen": screen or "UNKNOWN",
            "action": "error",
            "data": {"message": "Unhandled flow"},
        }

    async def validate_register(self, version: str, data: dict):
        
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
        return response.get("data")
    
    async def confirm_register(self, version: str, data: dict):
        phone_number = data.get("phone_number")

        try:
            result = self.plms_service.member_activation(phone_number)
            code = result.get("response_code")
            member_id = result.get("member_id")
            card_number = result.get("card_number")
            logger.info(f"PLMS Activation Response: {result}")
            
            if code == "00" :
                await self.whatsapp_service.send_message(phone_number, f"Pendaftaran berhasil! Selamat datang sebagai member Alfamidi. * Nomor member: {member_id}, * Nomor kartu: {card_number}")
                return {
                    "version": version,
                    "screen": "DONE",
                    "action": "submit",
                    "data": {"status": "success"}
                }
            elif code == "E050":
                await self.whatsapp_service.send_message(phone_number, f"Pendaftaran gagal.\n\nNomor anda {phone_number} telah terdafatar sebagai member.")
                return {
                    "version": version,
                    "screen": "CONFIRM",
                    "action": "error",
                    "data": {"status": "failed", "message": str(e)}
                }
            else : 
                await self.whatsapp_service.send_message(phone_number, "Terjadi gangguan. Mohon tunggu")
            
            
        except Exception as e:
            logger.error(f"Activation failed: {e}")
            return {
                "version": version,
                "screen": "CONFIRM",
                "action": "error",
                "data": {"status": "failed", "message": str(e)}
            }
    
        
