import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

class PinEncryptor:
    def encrypt_pin(self, pin: str) -> str:
        key = pin.encode()  # 🔑 using the PIN as key
        if len(key) != 32:
            raise ValueError("Encryption key (PIN) must be 32 bytes long for AES-256.")

        iv = os.urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_text = pad(pin.encode(), AES.block_size)  # also encrypting the PIN itself
        cipher_text = cipher.encrypt(padded_text)
        return base64.b64encode(iv + cipher_text).decode()