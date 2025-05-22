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

    async def handle_text_message(self, phone_number: str, text: str, username: str):
        if text.lower() == "konfirmasi":
            await self.tnc_inquiry_commit(phone_number)   
        else:
            await self.whatsapp_service.send_greetings(phone_number, username)

    async def handle_list_reply(self, phone_number: str, interactive_data: dict):
        reply_id = interactive_data.get("id")
        
        if reply_id == Menu.MEMBER:
            await self.validate_member(phone_number)
            
        elif reply_id == Menu.MENU_2:
            await self.whatsapp_service.send_message(phone_number, "anda memilih menu 2")
            
        elif reply_id == Menu.MEMBER_STATUS_KARTU:
            await self.whatsapp_service.send_message(phone_number, "anda memilih menu VALIDASI")
            
        elif reply_id == Menu.MEMBER_AKTIVASI:
            await self.whatsapp_service.send_form_register(phone_number)
            
        elif reply_id == Menu.MEMBER_CEK_POIN:  
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
            
            await self.whatsapp_service.send_message(phone_number, message)
            
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
                await self.member_activation_status(phone_number, responseJSON)
                
            else :
                logger.error("Validation Error. Activation Token Not Found")
            
        except Exception as e:
            logger.error(f"Error in handle_nfm_reply: {str(e)}", exc_info=True)  
            
    async def member_activation_status(self, phone_number: str, register_data: dict):
        
        try :
            result = self.plms_service.member_activation(phone_number, register_data)
            code = result.get("response_code")
            tnc_flag = self.plms_service.tnc_info(phone_number)
            tnc_url = self.plms_service.tnc_info(phone_number)
            member_id = result.get("member_id")
            card_number = result.get("card_number")
            
            if code == "00":
                if tnc_flag == "F":
                    await self.whatsapp_service.send_cta_url_message(
                        phone_number, 
                        tnc_url,
                        "Terms & Condition",
                        "Terms & Condition",
                        "Silahkan lanjutkan persetujuan syarat dan ketentuan"
                        "_Klik tombol di bawah ini untuk ke halaman syarat dan ketentuan._"
                        )
                    await self.whatsapp_service.send_message(phone_number, 'Silahkan ketik _*"konfirmasi"*_ dan kirimkan jika anda sudah melakukan konfirmasi syarat dan ketentuan.')
                    
                else :
                    await self.whatsapp_service.send_member_services_menu(phone_number, f"Pendaftaran berhasil! Selamat datang sebagai member Alfamidi.",
                                                         f"\n\n- Nomor member: {member_id},",
                                                         f"\n\n- Nomor kartu: {card_number}")
                
            elif code == "E050":
                await self.whatsapp_service.send_message(phone_number, f"Pendaftaran gagal.\n\nNomor anda {phone_number} telah terdaftar sebagai member.")
            else : 
                await self.whatsapp_service.send_message(phone_number, "Terjadi gangguan. Mohon tunggu")
            
            
        
        except Exception as e:
            logger.error(f"Error during member activation: {e}", exc_info=True)
            
    async def validate_member(self, phone_number: str):

        try :
            result = self.plms_service.validate_member(phone_number)
            code = result.get("response_code")
                
            if code == "00":
                await self.validate_tnc(phone_number)   
            elif code == "E073":
                # Not a member: show registration option
                await self.whatsapp_service.send_activation_menu(phone_number)
            else:
                await self.whatsapp_service.send_message(phone_number, "Terjadi gangguan. Mohon tunggu")
                
        except Exception as e:
            logger.error(f"Error during auto member validation: {e}", exc_info=True)
            
    async def validate_tnc(self, phone_number: str):
        try:
            result = self.plms_service.validate_member(phone_number)
            card_number = result.get("card_number", "")
            
            tnc_info = self.plms_service.tnc_info(phone_number)
            tnc_flag = tnc_info.get("flag")
            tnc_url = tnc_info.get("link")
            
            if tnc_flag == "F":
                await self.whatsapp_service.send_cta_url_message(
                    phone_number, 
                    tnc_url,
                    "Terms & Condition",
                    "Terms & Condition",
                    "Anda belum mensetujui syarat dan ketentuan member Alfamidi.\n\n"
                    "_Klik tombol di bawah ini untuk ke halaman syarat dan ketentuan._"
                    )               
            else:
                await self.whatsapp_service.send_member_services_menu(phone_number, f"Nomor Anda telah terdaftar ke dalam member Alfamidi.\n\n"
                                                                        f"-Nomor kartu Anda: *{card_number}*\n\n"
                                                                        "Silahkan pilih layanan member yang tersedia.")            
                
        except Exception as e:
            logger.error(f"Error during TNC validation: {e}", exc_info=True)
            
    async def tnc_inquiry_commit(self, phone_number: str):
        try:
            result = self.plms_service.validate_member(phone_number)
            card_number = result.get("card_number", "")
            tnc_inquiry = self.plms_service.tnc_inquiry(phone_number)
            response_inquiry = tnc_inquiry.get("response_code")
            
            if response_inquiry == "00":
                tnc_commit = self.plms_service.tnc_commit(phone_number)
                response_commit = tnc_commit.get("response_code")

                if response_commit == "00":
                                    await self.whatsapp_service.send_member_services_menu(phone_number, f"Nomor Anda telah terdaftar ke dalam member Alfamidi.\n\n"
                                                                    f"-Nomor kartu Anda: *{card_number}*\n\n"
                                                                    "Silahkan pilih layanan member yang tersedia.")       
                else :
                    logger.error("Invalid Token")
                    
            elif response_inquiry == "E110":
                await self.whatsapp_service.send_main_menu(phone_number, "Anda belum mensetujui syarat dan ketentuan.")
                
            elif response_inquiry == "E073":
                await self.whatsapp_service.send_main_menu(phone_number, "Anda telah mensetujui TNC, namun belum terdaftar sebagai member.")
                
            else: 
                logger.error("Invalid Session Error")
                
            
        except Exception as e:   
            logger.error(f"Error during TNC Inquiry and Commit: {e}", exc_info=True)  
            
            
                
            
                
        
            
    
            
 

    