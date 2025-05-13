import requests
from globals.constants import PLMSUser, PLMSSecretKey, PLMSEndpoint
from core.logger import get_logger
import hashlib

logger = get_logger()

class PLMSService:
    def __init__(self):
        self.endpoint = PLMSEndpoint.ENDPOINT.value
        self.token = None
        self.mode = "mobile"
        self.with_balance = 1
        
    def login(self):
        text = PLMSUser.USERNAME.value + PLMSUser.PASSWORD.value + PLMSSecretKey.SECRET_KEY.value
        checksum = hashlib.sha256(text.encode()).hexdigest()
    
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
        
        phone_number = str(phone_number)
        
        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]
            
        text = self.mode + phone_number + self.token + PLMSSecretKey.SECRET_KEY.value
        checksum = str(hashlib.sha256(text.encode()).hexdigest())
        
        payload = {
            "mode": self.mode,
            "id": phone_number,
            "token": self.token,
            "checksum": checksum
        }
        
        try:
            response = requests.post(f"{self.endpoint}/validatemember", json=payload)
            data = response.json()
            logger.info(f"VALIDATE MEMBER | Response: {data}")
            response_code = data.get("response_code")
            
            if response_code == "E004":
                logger.error("ERROR | token already expired")
                
            return data
        
        except Exception as e:
            logger.error(f"Validate member failed: {e}")
            raise
        
    def inquiry(self, phone_number: str):
        if not self.token:
            self.login()
        
        phone_number = str(phone_number)
        
        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]
            
        text = self.mode + phone_number + self.with_balance + self.token + PLMSSecretKey.SECRET_KEY.value
        checksum = str(hashlib.sha256(text.encode()).hexdigest())
        
        payload = {
            "mode" : self.mode,
            "id" : phone_number,
            "with_balance" : self.with_balance,
            "token" : self.token,
            "checksum" : checksum  
        }
        
        try:
            response = requests.post(f"{self.endpoint}/inquiry", json=payload)
            data = response.json()
            logger.info(f"INQUIRY MEMBER| Response: {data}")
            return data
            # card_number = data.get("card_number")
            # email = data.get("email")
            # total_points = data.get("redeemable_pool_units") # "redeemable_pool_units": 1663926
            # expired_point = data.get("eeb_pool_units") # "eeb_pool_units": 993601
            # expired_point_date = data.get("eeb_date") # "eeb_date": "20250531"
            
        except Exception as e:
            logger.error(f"Failed inquiry with status: {e}")
            raise
            
            
        
            
        
        
        
