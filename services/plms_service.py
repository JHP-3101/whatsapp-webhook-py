import requests
from globals.constants import PLMSUser, PLMSSecretKey, PLMSEndpoint
from core.logger import get_logger
from datetime import datetime
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
        
    def member_activation(self, phone_number: str, register_data: dict):
        if not self.token:
            self.login()
            
        data = register_data
        
        logger.info(f"DATA MEMBER ACTIVATION: {data}")

        phone_number = data.get("phone_number", "")
        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]
        
        name = data.get("name", "")
        birth_date = data.get("birth_date", "")
        email = data.get("email", "")
        card_number = data.get("card_number", "")
        gender = data.get("gender", "")
        marital = data.get("marital", "")
        address = data.get("address", "")
        
        try:
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d").strftime("%d%m%Y")
        except Exception:
            birth_date = birth_date  # fallback kalau parsing gagal
            
        logger.info(f"BIRTH DATE MEMBER : {birth_date}")
        
        # Checksum sesuai urutan: name + birth_date + phone_number + email + card_number + gender + marital + address + token + secretKey
        text = name + birth_date + phone_number + email + card_number + gender + marital + address + self.token + PLMSSecretKey.SECRET_KEY.value
        logger.info(f"CHECKSUM MEMBER ACTIVATION: {text}")
        checksum = str(hashlib.sha256(text.encode()).hexdigest())

        payload = {
            "name": name,
            "birth_date": birth_date,
            "phone_number": phone_number,
            "email": email,
            "card_number": card_number,
            "gender": gender,
            "marital": marital,
            "address": address,      
            "token": self.token,
            "checksum": checksum
        }

        logger.info(f"PAYLOAD MEMBER ACTIVATION: {payload}")
        
        try:
            response = requests.post(f"{self.endpoint}/memberactivation", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"MEMBER ACTIVATION | Response: {data}")
            return data

        except Exception as e:
            logger.error(f"Member activation failed: {e}")
            raise

        