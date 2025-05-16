import json
from services.whatsapp_service import WhatsAppService
from services.plms_service import PLMSService
from handlers.contact_handler import ContactHandler
from globals.constants import Menu
from globals.constants import WAFlow
from core.logger import get_logger

logger = get_logger()

class MessageHandler:
    def __init__(self, whatsapp_service: WhatsAppService):
        self.flow_token = WAFlow.WAFLOW_TOKEN_ACTIVATE
        self.whatsapp_service = whatsapp_service
        self.contact_handler = ContactHandler(whatsapp_service)
        self.plms_service = PLMSService()

    async def handle_text_message(self, from_number: str, text: str, username: str):
        if text.lower() == "test":
            await self.whatsapp_service.send_message(from_number, "hello world!")
        else:
            await self.whatsapp_service.send_greetings(from_number, username)

    async def handle_list_reply(self, from_number: str, interactive_data: dict):
        reply_id = interactive_data.get("list_reply", {}).get("id")
        
        if reply_id == Menu.MEMBER:
            contact = {"wa_id": from_number}
            await self.validate_member(from_number, contact)
            
        elif reply_id == Menu.MENU_2:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu 2")
            
        elif reply_id == Menu.MEMBER_STATUS_KARTU:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu VALIDASI")
            
        elif reply_id == Menu.MAIN_MENU:
            await self.whatsapp_service.send_main_menu(from_number)
            
        elif reply_id == Menu.MEMBER_REGISTRASI:
            await self.whatsapp_service.send_form_register(from_number)
            
        else:
            await self.whatsapp_service.send_message(from_number, "Menu tidak dikenali.")
    
    async def handle_nfm_reply(self, from_number: str, interactive_data: dict):
        flowData = interactive_data.get("nfm_reply", {}).get("response_json")

        try:
            responseJSON = json.loads(flowData)
            validateToken = responseJSON["flow_token"]
            
            result = self.plms_service.member_activation(from_number)
            code = result.get("response_code")
            member_id = result.get("member_id")
            card_number = result.get("card_number")
            logger.info(f"PLMS Activation Response: {result}")
            
            if code == "00" and validateToken == self.flow_token:
                await self.whatsapp_service.send_message(from_number, f"Pendaftaran berhasil! Selamat datang sebagai member Alfamidi. * Nomor member: {member_id}, * Nomor kartu: {card_number}")
            elif code == "E050" and validateToken == self.flow_token:
                await self.whatsapp_service.send_message(from_number, f"Pendaftaran gagal.\n\nNomor anda {from_number} telah terdafatar sebagai member.")
            else : 
                await self.whatsapp_service.send_message(from_number, "Terjadi gangguan. Mohon tunggu")
            
        except Exception as e:
            logger.error(f"Activation failed: {e}")   
            
    async def validate_member(self, from_number: str, contact:dict):
        phone_number = await self.contact_handler.get_phone_number(contact)
        if not phone_number or phone_number == "Unknown" :
            await self.whatsapp_service.send_message(from_number, "Failed to get phone number")
            return

        try :
            result = self.plms_service.validate_member(phone_number)
            code = result.get("response_code")
            card_number = result.get("card_number", "")
                
            if code == "00":
                # Valid member: show member services menu
                await self.whatsapp_service.send_message(from_number, f"Nomor Anda telah terdaftar ke dalam member Alfamidi.\n\nNomor member Anda: *{card_number}*.")
                await self.whatsapp_service.send_member_services_menu(from_number)
            elif code == "E073":
                # Not a member: show registration option
                await self.whatsapp_service.send_registration_menu(from_number)
            else:
                await self.whatsapp_service.send_message(from_number, "Terjadi gangguan. Mohon tunggu")
                
        except Exception as e:
            logger.error(f"Error during auto member validation: {e}", exc_info=True)
            
 

    
