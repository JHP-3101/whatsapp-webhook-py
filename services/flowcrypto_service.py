import json
import os
from base64 import b64decode, b64encode
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes


class FlowCryptoService:
    def __init__(self, private_key_str: str, passphrase: str = None):
        self.private_key = load_pem_private_key(
            private_key_str.encode('utf-8'),
            password=passphrase.encode('utf-8') if passphrase else None
        )

    def decrypt_request(self, encrypted_flow_data_b64: str, encrypted_aes_key_b64: str, initial_vector_b64: str):
        encrypted_aes_key = b64decode(encrypted_aes_key_b64)
        aes_key = self.private_key.decrypt(
            encrypted_aes_key,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        flow_data = b64decode(encrypted_flow_data_b64)
        iv = b64decode(initial_vector_b64)

        encrypted_data = flow_data[:-16]
        tag = flow_data[-16:]

        decryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv, tag)
        ).decryptor()

        decrypted_bytes = decryptor.update(encrypted_data) + decryptor.finalize()
        decrypted_json = json.loads(decrypted_bytes.decode('utf-8'))

        return decrypted_json, aes_key, iv

    def encrypt_response(self, response_data: dict, aes_key: bytes, request_iv: bytes) -> str:
        flipped_iv = bytearray([b ^ 0xFF for b in request_iv])
        encryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(bytes(flipped_iv))
        ).encryptor()

        response_bytes = json.dumps(response_data).encode('utf-8')
        encrypted = encryptor.update(response_bytes) + encryptor.finalize()
        return b64encode(encrypted + encryptor.tag).decode('utf-8')
