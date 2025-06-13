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
        from handlers.plms_handler import PLMSHandler
        
        self.flow_token_activation = WAFlow.WAFLOW_TOKEN_ACTIVATE
        self.whatsapp_service = whatsapp_service
        self.contact_handler = ContactHandler(whatsapp_service)
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
        
        elif reply_id == Menu.MAIN_MENU:
            await self.whatsapp_service.send_main_menu(phone_number, "Anda berada di Menu Utama.\nSilahkan pilih layanan yang anda butuhkan.")
            
        elif reply_id == Menu.MEMBER_STATUS_KARTU:
            await self.whatsapp_service.send_message(phone_number, "anda memilih menu VALIDASI")
            
        elif reply_id == Menu.MEMBER_AKTIVASI:
            await self.whatsapp_service.send_form_register(phone_number)
            
        elif reply_id == Menu.MEMBER_CEK_POIN:  
            await self.plms_handler.check_point_member(phone_number)
            
        elif reply_id == Menu.MEMBER_RIWAYAT_TRANSAKSI_POIN:
            await self.plms_handler.transaction_history_summary(phone_number)
        
        elif reply_id == Menu.MEMBER_STATUS_KARTU:
            await None
        
        elif reply_id == Menu.MEMBER_RESET_PIN:
            await self.whatsapp_service.send_form_reset_pin(phone_number)
        
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
            
    
    async def handle_button_reply(self, phone_number: str, interactive_data: dict):
        button_id =  interactive_data.get("id")
        
        if button_id == "go-back-main-menu" :
            await self.whatsapp_service.send_main_menu(phone_number, "Silahkan pilih layanan yang tersedia.")
            
        elif button_id == "go-back-member-menu":
            await self.whatsapp_service.send_member_services_menu(phone_number, "Silahkan pilih layanan member yang tersedia.")
            
        elif button_id == "go-validate-tnc":
            await self.whatsapp_service.send_activation_menu(phone_number)
            
        elif button_id == "go-member-activation":
            await self.whatsapp_service.send_activation_menu(phone_number)
        else :
            await self.whatsapp_service.send_message(phone_number, "Menu tidak dikenali.")