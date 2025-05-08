import requests
from globals.constants import PLMSUser, PLMSSecretKey, PLMSEndpoint
from handlers.contact_handler import ContactHandler
from core.logger import get_logger
import hashlib

logger = get_logger()

class PLMSService:
    def __init__(self):
        self.endpoint = PLMSEndpoint.ENDPOINT.value
        self.token = None
        self.mode = "mobile"
        
    def login(self):
        text = PLMSUser.USERNAME.value + PLMSUser.PASSWORD.value + PLMSSecretKey.SECRET_KEY.value
        checksum = hashlib.sha256(text.encode()).hexdigest()
        logger.info(f"CHECKSUM FOR LOGIN {checksum}")
    
        payload = {
            "username": PLMSUser.USERNAME.value,
            "password": PLMSUser.PASSWORD.value,
            "checksum": checksum
        }
        
        try:
            response = requests.post(f"{self.endpoint}/login", json=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("token")
            
            if not self.token:
                raise ValueError("Token not found in login response")
            
            logger.info("PLMS login successful, token acquired.")
            return self.token
        
        except Exception as e:
            logger.error(f"PLMS login failed: {e}")
            raise
        
    def validate_member(self, phone_number: str):
        if not self.token:
            self.login()
            logger.info(f"VALIDATE MEMBER | Token: {self.token}")
        
        phone_number = str(phone_number)
        
        # if phone_number.startswith("62"):
        #     phone_number = "0" + phone_number[2:]
            
        logger.info(f"Validating member with phone number: {phone_number}")
            
        text = "mobile" + "085394202728" + self.token + PLMSSecretKey.SECRET_KEY.value
        checksum = str(hashlib.sha256(text.encode()).hexdigest())
        logger.info(f"VALIDATE MEMBER : {checksum}")
        
        payload = {
            "mode": "mobile",
            "id": "085394202728",
            "token": self.token,
            "checksum": checksum
        }
        
        logger.info(payload)
        
        try:
            response = requests.post(f"{self.endpoint}/validatemember", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Validate member response: {data}")
            return data
        except Exception as e:
            logger.error(f"Validate member failed: {e}")
            raise
            
        
        
        
