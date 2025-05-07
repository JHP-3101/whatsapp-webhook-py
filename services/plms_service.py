import requests
from globals.constants import PLMSUser, PLMSSecretKey, PLMSEndpoint
from core.logger import get_logger
import hashlib

logger = get_logger()

class PLMSService:
    def __init__(self):
        self.endpoint = PLMSEndpoint.ENDPOINT.value
        self.token = None

    def generate_checksum(self):
        text = PLMSUser.USERNAME.value + PLMSUser.PASSWORD.value + PLMSSecretKey.SECRET_KEY.value
        return hashlib.sha256(text.encode()).hexdigest()

    def login(self):
        payload = {
            "username": PLMSUser.USERNAME.value,
            "password": PLMSUser.PASSWORD.value,
            "checksum": self.generate_checksum()
        }
        try:
            response = requests.post(f"{self.endpoint}/login", json=payload)
            response.raise_for_status()
            data = response.json()
            self.data = data.get("data", {})
            logger.info("PLMS login successful, token acquired.")
        except Exception as e:
            logger.error(f"PLMS login failed: {e}")
            raise
