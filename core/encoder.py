import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

class PinEncryptor:
    def __init__(self, key: str):
        self.key = key.encode()  # convert to bytes
        if len(self.key) != 32:
            raise ValueError("Key must be 32 bytes long for AES-256.")

    def encrypt_pin(self, plain_text: str) -> str:
        iv = os.urandom(16)  # Generate 16-byte IV
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_text = pad(plain_text.encode(), AES.block_size)  # pad to 16 bytes
        cipher_text = cipher.encrypt(padded_text)
        result = base64.b64encode(iv + cipher_text).decode()  # IV + ciphertext, base64
        return result