import requests
import re
from globals.constants import PLMSUser, PLMSSecretKey, PLMSEndpoint
from core.encoder import PinEncryptor
from core.logger import get_logger
from datetime import datetime
import hashlib

logger = get_logger()

class PLMSService:
    def __init__(self):
        self.endpoint = PLMSEndpoint.ENDPOINT.value
        self.token = None
        self.q = None
        self.mode = "mobile"
        self.with_balance = 1
        self.encryptor = PinEncryptor()
        
        
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

        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]
            
        # Remove All Special Characters From Address
        address = data.get("address", "")
        address = re.sub(r"[^a-zA-Z0-9\s-]", "", address)
        
        # Change Birth Date Format
        birth_date = data.get("birth_date", "")
        try:
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d").strftime("%d%m%Y")
        except Exception:
            birth_date = birth_date  # fallback kalau parsing gagal
        
        name = data.get("name", "")
        email = data.get("email", "")
        card_number = data.get("card_number", "")
        gender = data.get("gender", "")
        marital = data.get("marital", "")
        
        # Checksum sesuai urutan: name + birth_date + phone_number + email + card_number + gender + marital + address + token + secretKey
        text = name + birth_date + phone_number + email + card_number + gender + marital + address + self.token + PLMSSecretKey.SECRET_KEY.value
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
            logger.info(f"MEMBER ACTIVATION RESPONSE {data}")
            return data

        except Exception as e:
            logger.error(f"Member activation failed: {e}")
            raise
        
    def inquiry(self, phone_number: str):
        if not self.token:
            self.login()
            
        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]
            
        text = self.mode + phone_number + str(self.with_balance) + self.token + PLMSSecretKey.SECRET_KEY.value
        logger.info(f"Inquiry Checksum: {text}")
        checksum = str(hashlib.sha256(text.encode()).hexdigest())
        
        payload = {
            "mode": self.mode,
            "id": phone_number,
            "with_balance": self.with_balance,
            "token": self.token,
            "checksum": checksum 
        }
        
        logger.info(f"PAYLOAD INQUIRY: {payload}")
        
        try :
            response = requests.post(f"{self.endpoint}/inquiry", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Inquiry response : {data}")
            return data

        except Exception as e:
            logger.error(f"Failed to inquiring member: {e}")
            raise
        
    def transaction_history(
        self,
        phone_number: str,
        startDate: str,
        endDate: str
        ):
        
        if not self.token:
            self.login()
            
        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]
            
        logger.info(f"StartDate: {startDate}, EndDate: {endDate}")
            
        text = self.mode + phone_number + startDate + endDate + "1" + "20" + self.token + PLMSSecretKey.SECRET_KEY.value
        logger.info(f"Text from transaction history: {text}")
        checksum = str(hashlib.sha256(text.encode()).hexdigest())
        logger.info(f"Checksum from transaction history: {checksum}")
        
        
        payload = {
            "mode": self.mode,
            "id": phone_number,
            "start_date": startDate,
            "end_date": endDate,
            "page": 1,
            "list_item": 20,
            "token": self.token,
            "checksum": checksum   
        }
        
        logger.info(f"Payload Transaction History: {payload}")
        
        try :
            response = requests.post(f"{self.endpoint}/transactionhistory", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Transactio History response : {data}")
            return data

        except Exception as e:
            logger.error(f"Failed to see transaction history member: {e}")
            raise
        
    def tnc_info(self, phone_number: str):
        self.action = "all"
        if not self.token:
            self.login()
            
        logger.info(f"Token TNC : {self.token}")
            
        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]

        text = self.mode + phone_number + self.action + self.token + PLMSSecretKey.SECRET_KEY.value
        logger.info(f"TNC Info Checksum {text}")
        checksum = str(hashlib.sha256(text.encode()).hexdigest())
        
        payload = {
            "mode": self.mode,
            "id": phone_number,
            "action": self.action,
            "token": self.token,
            "checksum": checksum
        }
        
        logger.info(f"TNC Payload : {payload}")
        try :
            response = requests.post(f"{self.endpoint}/tnc/info", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"TNC Info Response : {data}")
            return data                  
                                     
        except Exception as e:
            logger.error(f"Failed to load TNC Info Member: {e}")
            raise
    
    def tnc_inquiry(self, phone_number: str):
        self.action = "all"
        if not self.token:
            self.login()
            
        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]
        
        tnc_info = self.tnc_info(phone_number)
        self.q = tnc_info.get("q")
        logger.info(f"Session from TNC info (q): {self.q}")

        text = self.q + self.token + PLMSSecretKey.SECRET_KEY.value
        logger.info(f"TNC Inquiry Checksum {text}")
        checksum = str(hashlib.sha256(text.encode()).hexdigest())
        
        payload = {
            "q": self.q,
            "token": self.token,
            "checksum": checksum
        }
        
        try :
            response = requests.post(f"{self.endpoint}/tnc/inquiry", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"TNC Inquiry Response : {data}")
            return data                  
                                     
        except Exception as e:
            logger.error(f"Failed to load TNC Inquiry Member: {e}")
            raise
        
        
    def tnc_commit(self, phone_number: str):
        if not self.token:
            self.login()
            
        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]
            
        tnc_info = self.tnc_info(phone_number)
        self.q = tnc_info.get("q")
        logger.info(f"Session from TNC info (q): {self.q}")
        
        tnc_inquiry = self.tnc_inquiry(phone_number)
        member_id = tnc_inquiry.get("member_id")
        logger.info(f"Member ID: {member_id}")
        
        text = self.q + str(member_id) + self.token + PLMSSecretKey.SECRET_KEY.value
        logger.info(f"TNC Commit Checksum {text}")
        checksum = str(hashlib.sha256(text.encode()).hexdigest())
        
        payload = {
            "q": self.q,
            "member_id": member_id,
            "token": self.token,
            "checksum": checksum
        }
        
        logger.info(f"Commit Payload : {payload}")
        
        try :
            response = requests.post(f"{self.endpoint}/tnc/commit", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"TNC Commit Response : {data}")
            return data                  
                                     
        except Exception as e:
            logger.error(f"Failed to load TNC Inquiry Member: {e}")
            raise
        
    def pin_check(self, phone_number: str, card_number: str):
        if not self.token:
            self.login()
            
        logger.info(f"Token : {self.token}")
            
        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]
            
        text = card_number + self.token + PLMSSecretKey.SECRET_KEY.value
        logger.info(f"Text from Pin Check: {text}")
        checksum = str(hashlib.sha256(text.encode()).hexdigest())
        logger.info(f"Checksum from Pin Check: {checksum}")
        
        payload = {
            "card_number": card_number,
            "token": self.token,
            "checksum": checksum
        }
        
        try :
            response = requests.post(f"{self.endpoint}/pin/check", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Pin Check Response: {data}")
            return data

        except Exception as e:
            logger.error(f"Failed to do pin check: {e}")
            raise
        
        
    def pin_reset(self, phone_number: str, pin: str):
        if not self.token:
            self.login()
            
        if phone_number.startswith("62"):
            phone_number = "0" + phone_number[2:]
            
        inquiry = self.inquiry(phone_number)
        card_number = inquiry.get("card_number")
        
        # Encrypt PIN
        encrypted_pin = self.encryptor.encrypt_pin(pin)
        logger.info(f"Encrypted PIN: {encrypted_pin}")
            
        text = card_number + encrypted_pin + self.token + PLMSSecretKey.SECRET_KEY.value
        logger.info(f"Text from Pin Reset: {text}")
        checksum = str(hashlib.sha256(text.encode()).hexdigest())
        logger.info(f"Checksum from Pin Reset: {checksum}")
        
        payload = {
            "card_number": card_number,
            "pin": encrypted_pin,
            "token": self.token,
            "checksum": checksum
        }
        
        logger.info(f"Payload Pin Reset: {payload}")
        
        try :
            response = requests.post(f"{self.endpoint}/pin/reset", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Pin Reset Response: {data}")
            return data

        except Exception as e:
            logger.error(f"Failed to do pin reset: {e}")
            raise
