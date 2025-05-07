import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from globals.constants import ChecksumPin
from core.logger import get_logger

logger = get_logger()

class EncryptionService:
    def __init__(self):
        self.key = ChecksumPin.PIN.value.encode("utf-8")  # Convert to bytes
        if len(self.key) != 32:
            logger.error("Encryption key must be 32 bytes for AES-256")
            raise ValueError("Invalid encryption key length")

    def encrypt_pin(self, text: str) -> str:
        try:
            iv = os.urandom(16)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            padded_text = pad(text.encode(), AES.block_size)
            ciphertext = cipher.encrypt(padded_text)
            iv_ciphertext = iv + ciphertext
            logger.info(f"base64.b64encode(iv_ciphertext).decode()")
            return base64.b64encode(iv_ciphertext).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise