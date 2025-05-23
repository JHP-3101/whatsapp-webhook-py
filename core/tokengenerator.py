import os
import time
import hmac
import hashlib
from base64 import b64encode
from globals.constants import WAFlow

class FlowTokenGenerator:
    def __init__(self, secret_key : str = "m1d1w3bh00kfl0w"):
        self.secret_key = secret_key.encode("utf-8")
        self.phone_number_id = os.getenv("PHONE_NUMBER_ID")
        self.flow_id = WAFlow.WAFLOW_ID_REGISTER

        if not self.phone_number_id or not self.flow_id:
            raise ValueError("Required environment variables are missing")

    def generate_token(self) -> str:
        '''
        METADATA = <PHONE_NUMBER_ID>|<WAFLOW_ID>|<TIMESTAMP>
        SIGNATURE = "m1d1w3bh00kfl0w" ; Static Secret Key
        '''
        timestamp = str(int(time.time()))
        metadata = f"{self.phone_number_id}|{self.flow_id}|{timestamp}"
        data = metadata.encode("utf-8")
        
        hmac_digest = hmac.new(self.secret_key, data, hashlib.sha256).digest()
        token = b64encode(hmac_digest).decode("utf-8")
        return token