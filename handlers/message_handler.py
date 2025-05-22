import json
from services.whatsapp_service import WhatsAppService
from services.plms_service import PLMSService
from handlers.contact_handler import ContactHandler
from handlers.plms_handler import PLMSHandler
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
        self.plms_handler = PLMSHandler(whatsapp_service, plms_service)

    async def handle_text_message(self, phone_number: str, text: str, username: str):
        if text.lower() == "konfirmasi":
            await self.plms_handler.tnc_inquiry_commit(phone_number)   
        else:
            await self.whatsapp_service.send_greetings(phone_number, username)

    async def handle_list_reply(self, phone_number: str, interactive_data: dict):
        reply_id = interactive_data.get("id")
        
        if reply_id == Menu.MEMBER:
            await self.plms_handler.validate_member(phone_number)
            
        elif reply_id == Menu.MENU_2:
            await self.whatsapp_service.send_message(phone_number, "anda memilih menu 2")
            
        elif reply_id == Menu.MEMBER_STATUS_KARTU:
            await self.whatsapp_service.send_message(phone_number, "anda memilih menu VALIDASI")
            
        elif reply_id == Menu.MEMBER_AKTIVASI:
            await self.whatsapp_service.send_form_register(phone_number)
            
        elif reply_id == Menu.MEMBER_CEK_POIN:  
            # result = self.plms_service.inquiry(phone_number)
            # card_number = result.get("card_number", "")
            # total_points = result.get("redeemable_pool_units", 0)
            # expired_points = result.get("eeb_pool_units", [])
            # expired_points_date = result.get("eeb_date", [])
            
            # expired_sections = ""
            # for date, point in zip(expired_points_date, expired_points):
            #     expired_sections += f"Poin Expired {date} sebesar {point:,}\n"
                
            # message = (
            #     f"Poin Member Anda *{card_number}* sebesar {total_points:,}\n\n"
            #     f"{expired_sections}\n"
            #     "Gunakan terus kartu member Alfamidi setiap melakukan transaksi\n"
            #     "Download aplikasi MIDIKRIING untuk penukaran poin dan dapatkan promo2 Spesial Redeem lainnya."
            # )
            
            # await self.whatsapp_service.send_message(phone_number, message)
            
            await None
            
        else:
            await self.whatsapp_service.send_message(phone_number, "Menu tidak dikenali.")
    
    async def handle_nfm_reply(self, phone_number: str, interactive_data: dict):    
        try:
            flowData = interactive_data.get("response_json")
            logger.info(f"RESPONSE FROM FLOW {flowData}")
            responseJSON = json.loads(flowData)
            
            # Handle Member Activation Response
            validateTokenActivation = responseJSON.get("flow_token")
            if validateTokenActivation == self.flow_token_activation:
                await self.plms_handler.member_activation_status(phone_number, responseJSON)
                
            else :
                logger.error("Validation Error. Activation Token Not Found")
            
        except Exception as e:
            logger.error(f"Error in handle_nfm_reply: {str(e)}", exc_info=True)  
            
            
            
                
            
                
        
            
    
            
 

    