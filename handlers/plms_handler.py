from services.whatsapp_service import WhatsAppService
from services.plms_service import PLMSService
from globals.constants import API
from core.logger import get_logger
from datetime import datetime, time, timedelta

logger = get_logger()

class PLMSHandler:
    def __init__(self, whatsapp_service: WhatsAppService, plms_service: PLMSService):
        self.plms_service = plms_service
        self.whatsapp_service = whatsapp_service
        self.api_redirect_midikrring = API.API_REDIRECT_MOBILE_MIDIKRIING
        
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
                    "Terms & Condition",
                    "Syarat & Ketentuan",
                    "Anda belum mensetujui syarat dan ketentuan member Alfamidi.\n\n"
                    "_Klik tombol di bawah ini untuk ke halaman syarat dan ketentuan._"
                    )  
                  
                await self.whatsapp_service.send_message(phone_number, 'Silahkan ketik kata "*KONFIRMASI*" '
                                                         'dan kirimkan jika anda sudah melakukan konfirmasi syarat dan ketentuan.')           
            else:
                await self.whatsapp_service.send_member_services_menu(phone_number, f"Anda berada di dalam layanan member.\n\n"
                                                                        f"- Nomor kartu Anda: *{card_number}*\n\n"
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
                                    await self.whatsapp_service.send_member_services_menu(phone_number, f"Yeay 🎉! Selamat anda telah terdaftar ke dalam member.\n\n"
                                                                    f"- Nomor kartu Anda: *{card_number}*\n\n"
                                                                    "_Silahkan pilih layanan member yang tersedia._")       
                else :
                    logger.error("Invalid Token")
                    await self.whatsapp_service.send_message_with_button(phone_number, "Gagal memproses.\n\nIngin kembali ke halaman utama atau mengulangi T&C?",
                                                                    [
                                                                        {"id": "go-back-main-menu", "title": "Kembali"},
                                                                        {"id": "validate-tnc", "title": "Terms & Condition"}
                                                                    ])
                    
            elif response_inquiry == "E110":
                await self.whatsapp_service.send_message_with_button(phone_number, "Anda belum mensetujui syarat dan ketentuan.\n\nIngin kembali ke halaman utama atau mengulangi T&C?",
                                                                [
                                                                    {"id": "go-back-main-menu", "title": "Kembali"},
                                                                    {"id": "go-validate-tnc", "title": "Terms & Condition"}
                                                                ])
                
            elif response_inquiry == "E073":
                await self.whatsapp_service.send_message_with_button(phone_number, "Anda telah mensetujui TNC, namun belum terdaftar sebagai member.\n\nIngin kembali ke halaman utama atau mendaftar member?",
                                                                [
                                                                    {"id": "go-back-main-menu", "title": "Kembali"},
                                                                    {"id": "go-member-activation", "title": "Aktivasi"}
                                                                ])
                
            else: 
                logger.error("Invalid Session Error")
                
            
        except Exception as e:   
            logger.error(f"Error during TNC Inquiry and Commit: {e}", exc_info=True)  
    
    
    async def check_point_member(self, phone_number: str):
        try:
            result = self.plms_service.inquiry(phone_number)
            card_number = result.get("card_number", "")
            total_points = result.get("redeemable_pool_units", 0)
            
            expired_points = result.get("eeb_pool_units", [])
            expired_points_date = result.get("eeb_date", [])
            
            # Normalize to list if not already
            if not isinstance(expired_points, list):
                expired_points = [expired_points]

            if not isinstance(expired_points_date, list):
                expired_points_date = [expired_points_date]
            
            expired_sections = ""
            for date, point in zip(expired_points_date, expired_points):
                try:
                    formatted_date = datetime.strptime(date, "%Y%m%d").strftime("%d/%m/%Y")
                except Exception:
                    formatted_date = date  # fallback if parsing fails
                expired_sections += f"Poin Expired {formatted_date} sebesar {point:,}\n"
                
            message = (
                f"Poin Member Anda *{card_number}* sebesar {total_points:,}\n\n"
                f"{expired_sections}\n"
                "Gunakan terus kartu member *Alfamidi* setiap melakukan transaksi\n"
                "_Download aplikasi_ *_MIDIKRIING_* _untuk penukaran poin dan dapatkan promo2 Spesial Redeem lainnya._"
            )
            
            await self.whatsapp_service.send_message_with_button(phone_number, message,
                                                            [
                                                                {"id": "go-back-member-menu", "title": "Kembali"}
                                                            ])
            
        except Exception as e:
            logger.error(f"Error during Cek Poin Member: {e}", exc_info=True)
            

    async def transaction_history_summary(self, phone_number: str):
        try:
            # Calculate date range
            start_date = datetime.now()
            end_date = start_date + timedelta(days=14)
            start_date_str = start_date.strftime("%Y%m%d")
            end_date_str = end_date.strftime("%Y%m%d")
            
            logger.info(f"Start Date : {start_date_str} | End Date : {end_date_str}")

            # Call PLMS transaction history service
            result = self.plms_service.transaction_history(
                phone_number=phone_number,
                startDate=start_date_str,
                endDate=end_date_str
            )

            history = result.get("history", [])
            if not history:
                await self.whatsapp_service.send_message(
                    phone_number, 
                    "Belum ada transaksi poin dalam 2 minggu terakhir."
                )
                return

            # Format the message
            message = "Riwayat transaksi poin.\n\n"
            for trx in history:
                trx_date_raw = trx.get("transaction_date", "").split(" ")[0]
                formatted_date = datetime.strptime(trx_date_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
                place = trx.get("transaction_place", "Toko")
                point = trx.get("point", 0)
                status = trx.get("status", "").lower()

                if status == "award":
                    message += f"Tgl {formatted_date} di {place} mendapatkan {point} poin\n"
                elif status == "redeem":
                    message += f"Tgl {formatted_date} di {place} transaksi dengan {abs(point)} poin\n"
                else:
                    # fallback for unknown status
                    message += f"Tgl {formatted_date} di {place} dengan status {status} sejumlah {point} poin\n"

            message += (
                "\nGunakan terus kartu member *Alfamidi* setiap melakukan transaksi\n"
                "_Download aplikasi_ *_MIDIKRIING_* _untuk penukaran poin dan dapatkan promo2 Spesial Redeem lainnya._"
            )

            await self.whatsapp_service.send_message_with_button(phone_number, message,
                                                            [
                                                                {"id": "go-back-member-menu", "title": "Kembali"}
                                                            ])

        except Exception as e:
            logger.error(f"Error during transaction history summary: {e}", exc_info=True)
    
    async def check_pin(self, phone_number: str):
        try:
            result = self.plms_service.inquiry(phone_number)
            card_number = result.get("card_number", "")
            
            pin_check = self.plms_service.pin_check(phone_number, card_number)
            response_code = pin_check.get("response_code")
            logger.info(f"Response Code From Pin Check : {response_code}")
            
            if response_code == "00":
                logger.info(f"{phone_number} Has Set Pin")
                await self.whatsapp_service.send_form_reset_pin(phone_number)
                
            elif response_code == "E102":
                logger.info(f"{phone_number} Never Set Pin")
                await self.whatsapp_service.send_cta_url_message(
                    phone_number,
                    self.api_redirect_midikrring,
                    "Pin Service",
                    "Layanan Pin",
                    "Anda belum mengatur Pin Member.\n\n"
                    "_Klik tombol di bawah ini untuk mengatur Pin Member melalui aplikasi MidiKriing._"
                    )
                
            else: 
                logger.error(f"{response_code} | Invalid Session Error")
            
        except Exception as e:
            logger.error(f"Error during Pin Checker: {e}", exc_info=True)
            
    async def resets_pin(self, phone_number: str, pin: str):
        try: 
            result = self.plms_service.pin_reset(phone_number, pin)
            response_code = result.get("response_code")
            logger.info(f"Response Code From Pin Reset: {response_code}")
            
            if response_code == "00":
                logger.info(f"{phone_number} has reset pin ")
                await self.whatsapp_service.send_message_with_button(phone_number, "Anda telah berhasil melakukan Reset Pin\n\nSilahkan pilih layanan member lainnya.",
                                                            [
                                                                {"id": "go-back-member-menu", "title": "Kembali"}
                                                            ])
                
            else :
                logger.error(f"{response_code} | Gagal melakukan proses reset pin")
                
            
        except Exception as e:
            logger.error(f"Error during Pin Resets: {e}", exc_info=True)
        
        
            
            