from services.whatsapp_service import WhatsAppService
from core.logger import get_logger

logger = get_logger()

class ContactHandler:
    def __init__(self, whatsapp_service: WhatsAppService):
        self.whatsapp_service = whatsapp_service

    async def get_profile_name(self, contact: dict) -> str:
        """Extract profile name from contact object"""
        try:
            profile_name = contact.get("profile", {}).get("name")
            logger.info(f"Profile Name: {profile_name}")
            return profile_name
        except Exception as e:
            logger.error(f"Error extracting profile name: {e}")
            return "Unknown"
        
    async def get_phone_number(self, contact: dict) -> str:
        """Extract phone number from contact object"""
        try:
            phone_number = contact.get("wa_id")
            logger.info(f"Phone Number: {phone_number}")
            return phone_number
        except Exception as e:
            logger.error(f"Error extracting phone number: {e}")
            return "Unknown"