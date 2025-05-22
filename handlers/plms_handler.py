from services.whatsapp_service import WhatsAppService
from services.plms_service import PLMSService
from core.logger import get_logger

logger = get_logger()

class PLMSHandler:
    def __init__(self, whatsapp_service: WhatsAppService, plms_service: PLMSService):
        self.plms_service = plms_service
        self.whatsapp_service = whatsapp_service
        
    async def member_activation_status(self, phone_number: str, register_data: dict):
        try :
            result = self.plms_service.member_activation(phone_number, register_data)
            code = result.get("response_code")
            
            if code == "00":
                await self.validate_tnc(phone_number)
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
                    "Syarat dan Ketentuan",
                    "Terms & Condition",
                    "Anda belum mensetujui syarat dan ketentuan member Alfamidi.\n\n"
                    "_Klik tombol di bawah ini untuk ke halaman syarat dan ketentuan._"
                    )  
                  
                await self.whatsapp_service.send_message(phone_number, 'Silahkan ketik kata "*konfirmasi*" '
                                                         'dan kirimkan jika anda sudah melakukan konfirmasi syarat dan ketentuan.')           
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