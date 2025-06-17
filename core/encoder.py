import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from globals.constants import SaltPin

class PinEncryptor:
    def encrypt_pin(text: str) -> str:
        key = SaltPin.PIN.encode()
        if len(key) != 32:
            raise ValueError("Key must be exactly 32 bytes long for AES-256-CBC.")

        iv = os.urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_text = pad(text.encode(), AES.block_size)
        cipher_text = cipher.encrypt(padded_text)

        iv_cipher = iv + cipher_text
        return base64.b64encode(iv_cipher).decode()
