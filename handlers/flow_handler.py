from core.logger import get_logger
from services.whatsapp_service import WhatsAppService
from services.plms_service import PLMSService
from globals.constants import WAFlow
from core.logger import get_logger
from datetime import datetime

logger = get_logger()

class FlowHandler:
    def __init__(self, whatsapp_service: WhatsAppService, plms_service: PLMSService):
        
        self.version = "3"
        
        self.flow_token_activate = WAFlow.WAFLOW_TOKEN_ACTIVATE
        self.flow_token_reset_pin = WAFlow.WAFLOW_TOKEN_RESET_PIN

        self.whatsapp_service = whatsapp_service
        self.plms_service = plms_service
    
    async def handle_flow(self, screen: str, version: str, data: dict, flow_token: str, action: str = None):
        # Handle health check
        if action == "ping":
            return {
                "version": self.version,
                "screen": screen,
                "action": "ping",
                "data": {"status": "active"},
            }
            
        logger.info(f"[Flow Handler] Token Incoming : {flow_token}")
        logger.info(f"[FlowHandler] screen: {screen}, action: {action}, data: {data}")
            
        # ACTIVATE MEMBER
        if flow_token == self.flow_token_activate:
            if screen == "REGISTER":
                logger.info("[FlowHandler] entering validate_activation() flow path") 
                return await self.validate_activation(version, data)
            
        # RESET PIN 
        elif flow_token == self.flow_token_reset_pin:
            if screen == "VALIDATION":
                # phone_raw = data.get("phone_number")
                # logger.info(f"Phone Raw Data From Flow Reset PIN : {phone_raw}")
                # phone_number = phone_raw.get("value") if isinstance(phone_raw, dict) else phone_raw
                # logger.info(f"Phone Number Data From Flow Reset PIN : {phone_raw}")
                # if not phone_number:
                #     logger.error("Missing or malformed phone_number in VALIDATION flow")       
                logger.info("[FlowHandler] entering validate_birth_date() flow path")  
                return await self.validate_birth_date(version, data)
            
            elif screen == "RESET_PIN":
                # phone_raw = data.get("phone_number")
                # logger.info(f"Phone Raw Data From Flow Reset PIN : {phone_raw}")
                # phone_number = phone_raw.get("value") if isinstance(phone_raw, dict) else phone_raw
                # logger.info(f"Phone Number Data From Flow Reset PIN : {phone_raw}")
                # if not phone_number:
                #     logger.error("Missing or malformed phone_number in RESET_PIN flow")
                logger.info("[FlowHandler] entering validate_pin() flow path")    
                return await self.validate_pin(version, data)
            
            elif screen == "CONFIRMATION":
                logger.info("[FlowHandler] entering commit_pin() flow path") 
                return await self.commit_pin(version, data)
                
        else:
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
        birth_date_input = data.get("birth_date", "")
        phone_number = data.get("phone_number", "")
        
        logger.info(f"Reset PIN | Birth Date Input : {birth_date_input}")

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
            member = self.plms_service.inquiry(phone_number)
            if not member or not member.get("birth_date", ""):
                raise Exception("Data member tidak ditemukan atau tidak memiliki tanggal lahir.")

            # Format checking
            try:
                input_dt = datetime.strptime(birth_date_input, "%Y-%m-%d").strftime("%Y%m%d")
                member_dt = member.get("birth_date", "")
            except Exception as e:
                return {
                    "version": version,
                    "screen": "VALIDATION",
                    "action": "update",
                    "data": {
                        "birth_date_error": "Format tanggal tidak valid", 
                    }
                }

            if input_dt == member_dt:
                return {
                    "version": version,
                    "screen": "RESET_PIN",
                    "action": "update",
                    "data": {
                        "phone_number": phone_number,
                        "birth_date": birth_date_input
                    }
                }
            else:
                return {
                    "version": version,
                    "screen": "VALIDATION",
                    "action": "update",
                    "data": {
                        "birth_date_error": "⚠️ Tanggal lahir tidak sesuai dengan data yang terdaftar dengan member Alfamidi!"
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
        phone_number = data.get("phone_number", "")
                
        birth_date_input = data.get("birth_date", "")
        ddmmyy = yymmdd = None
        if birth_date_input:
            try:
                birth_dt = datetime.strptime(birth_date_input, "%Y-%m-%d")
                ddmmyy = birth_dt.strftime("%d%m%y")
                yymmdd = birth_dt.strftime("%y%m%d")
            except Exception as e:
                logger.warning(f"[FlowHandler] Invalid birth_date format: {birth_date_input}")
        
        try: 
            if not pin or not confirm_pin:
                return {
                    "version": version,
                    "screen": "RESET_PIN",
                    "action": "update",
                    "data": {
                        "pin_error": "⚠️ PIN dan konfirmasi wajib diisi"
                    }
                }

            elif pin != confirm_pin:
                return {
                    "version": version,
                    "screen": "RESET_PIN",
                    "action": "update",
                    "data": {
                        "pin_error": "⚠️ PIN dan konfirmasi PIN tidak sama"
                    }
                }

            # Rule 1: Cannot be same repeated digit
            elif len(set(pin)) == 1:
                return {
                    "version": version,
                    "screen": "RESET_PIN",
                    "action": "update",
                    "data": {
                        "pin_error": "⚠️ PIN tidak boleh berupa pengulangan angka"
                    }
                }

            # Rule 2: Cannot be sequential
            elif pin in ["123456", "234567", "345678", "456789", "012345", "654321", "543210", "432109"]:
                return {
                    "version": version,
                    "screen": "RESET_PIN",
                    "action": "update",
                    "data": {
                        "pin_error": "⚠️ PIN tidak boleh berupa angka berurutan"
                    }
                }

            # Rule 3: Cannot match birth date (ddmmyy / yymmdd)
            elif (ddmmyy and pin == ddmmyy) or (yymmdd and pin == yymmdd):
                return {
                    "version": version,
                    "screen": "RESET_PIN",
                    "action": "update",
                    "data": {
                        "pin_error": "⚠️ PIN tidak boleh sama dengan tanggal lahir Anda"
                    }
                }

            return {
                "version": version,
                "screen": "CONFIRMATION",
                "action": "update",
                "data": {
                        "pin": pin,
                        "confirm_pin": confirm_pin,
                        "birth_date": birth_date_input,
                        "phone_number": phone_number
                    }
                }
        
        except Exception as e:
            logger.error(f"Exception during checking pin reset: {e}", exc_info=True)


    async def commit_pin(self, version: str, data: dict):
        try:
            response = {
                "version": version,
                "screen": "CONFIRMATION",
                "action": "update",
                "data": {
                    key: data.get(key, "") for key in [
                        "phone_number", "pin", "confirm_pin"
                    ]
                }
            }
            
            logger.info(f"Commit PIN Response | {response}")
            return response

        except Exception as e:
            logger.error(f"Exception during commit pin reset: {e}", exc_info=True)

