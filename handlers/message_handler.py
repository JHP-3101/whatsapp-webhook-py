import json
from services.whatsapp_service import WhatsAppService
from services.plms_service import PLMSService
from handlers.contact_handler import ContactHandler
from globals.constants import Menu
from globals.constants import WAFlow
from core.logger import get_logger

logger = get_logger()

class MessageHandler:
    def __init__(self, whatsapp_service: WhatsAppService, plms_service: PLMSService):
        self.flow_token_activation = WAFlow.WAFLOW_TOKEN_ACTIVATE
        self.whatsapp_service = whatsapp_service
        self.contact_handler = ContactHandler(whatsapp_service)
        self.plms_service = plms_service

    async def handle_text_message(self, from_number: str, text: str, username: str):
        if text.lower() == "test":
            await self.whatsapp_service.send_message(from_number, "hello world!")
        else:
            await self.whatsapp_service.send_greetings(from_number, username)

    async def handle_list_reply(self, from_number: str, interactive_data: dict):
        reply_id = interactive_data.get("id")
        
        if reply_id == Menu.MEMBER:
            contact = {"wa_id": from_number}
            await self.validate_member(from_number, contact)
            
        elif reply_id == Menu.MENU_2:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu 2")
            
        elif reply_id == Menu.MEMBER_STATUS_KARTU:
            await self.whatsapp_service.send_message(from_number, "anda memilih menu VALIDASI")
            
        elif reply_id == Menu.MAIN_MENU:
            await self.whatsapp_service.send_main_menu(from_number)
            
        elif reply_id == Menu.MEMBER_AKTIVASI:
            await self.whatsapp_service.send_form_register(from_number)
            
        elif reply_id == Menu.MEMBER_CEK_POIN:
            phone_number = from_number
            logger.info(f"Matched Phone Number {phone_number} = {from_number}")
            
            result = self.plms_service.inquiry(phone_number)
            card_number = result.get("card_number", "")
            total_points = result.get("redeemable_pool_units", 0)
            expired_points = result.get("eeb_pool_units", [])
            expired_points_date = result.get("eeb_date", [])
            
            expired_sections = ""
            for date, point in zip(expired_points_date, expired_points):
                expired_sections += f"Poin Expired {date} sebesar {point:,}\n"
                
            message = (
                f"Poin Member Anda *{card_number}* sebesar {total_points:,}\n\n"
                f"{expired_sections}\n"
                "Gunakan terus kartu member Alfamidi setiap melakukan transaksi\n"
                "Download aplikasi MIDIKRIING untuk penukaran poin dan dapatkan promo2 Spesial Redeem lainnya."
            )
            
            await self.whatsapp_service.send_message(from_number, message)
            
        else:
            await self.whatsapp_service.send_message(from_number, "Menu tidak dikenali.")
    
    async def handle_nfm_reply(self, from_number: str, interactive_data: dict):    
        try:
            flowData = interactive_data.get("response_json")
            logger.info(f"RESPONSE FROM FLOW {flowData}")
            responseJSON = json.loads(flowData)
            
            # Handle Member Activation Response
            validateTokenActivation = responseJSON.get("flow_token")
            if validateTokenActivation == self.flow_token_activation:
                contact = {"wa_id": from_number}
                await self.member_activation_status(from_number, contact, responseJSON)
                
            else :
                logger.error("Validation Error. Activation Token Not Found")
            
        except Exception as e:
            logger.error(f"Error in handle_nfm_reply: {str(e)}", exc_info=True)  
            
    async def member_activation_status(self, from_number: str, contact: dict, register_data: dict):
        phone_number = await self.contact_handler.get_phone_number(contact)
        if not phone_number or phone_number == "Unknown" :
            logger.info(f"Failed to get phone number")
            return
        
        try :
            result = self.plms_service.member_activation(phone_number, register_data)
            code = result.get("response_code")
            member_id = result.get("member_id")
            card_number = result.get("card_number")
            
            if code == "00":
                await self.whatsapp_service.send_message(from_number, f"Pendaftaran berhasil! Selamat datang sebagai member Alfamidi.",
                                                         f"\n\n- Nomor member: {member_id},",
                                                         f"\n\n- Nomor kartu: {card_number}")
            elif code == "E050":
                await self.whatsapp_service.send_message(from_number, f"Pendaftaran gagal.\n\nNomor anda {from_number} telah terdaftar sebagai member.")
            else : 
                await self.whatsapp_service.send_message(from_number, "Terjadi gangguan. Mohon tunggu")
        
        except Exception as e:
            logger.error(f"Error during member activation: {e}", exc_info=True)
            
    async def validate_member(self, from_number: str, contact:dict):
        phone_number = await self.contact_handler.get_phone_number(contact)
        if not phone_number or phone_number == "Unknown" :
            logger.info(f"Failed to get phone number")
            return

        try :
            result = self.plms_service.validate_member(phone_number)
            code = result.get("response_code")
            card_number = result.get("card_number", "")
                
            if code == "00":
                # Valid member: show member services menu
                await self.whatsapp_service.send_message(from_number, f"Nomor Anda telah terdaftar ke dalam member Alfamidi.\n\nNomor kartu Anda: *{card_number}*.")
                await self.whatsapp_service.send_member_services_menu(from_number)
            elif code == "E073":
                # Not a member: show registration option
                await self.whatsapp_service.send_activation_menu(from_number)
            else:
                await self.whatsapp_service.send_message(from_number, "Terjadi gangguan. Mohon tunggu")
                
        except Exception as e:
            logger.error(f"Error during auto member validation: {e}", exc_info=True)
            
                
                
            
                
        
            
    
            
 

    