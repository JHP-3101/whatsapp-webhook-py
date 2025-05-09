import json
from base64 import b64decode, b64encode
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.hazmat.backends import default_backend

class FlowCryptoService:
    def __init__(self, private_key_pem: str, passphrase: str):
        self.private_key = serialization.load_pem_private_key(
            private_key_pem.encode("utf-8"),
            password=passphrase.encode("utf-8") if passphrase else None,
            backend=default_backend()
        )

    def decrypt_request(self, encrypted_body: bytes):
        """
        Parse JSON body and decrypt using RSA + AES-GCM
        """
        body = json.loads(encrypted_body)

        encrypted_flow_data_b64 = body["encrypted_flow_data"]
        encrypted_aes_key_b64 = body["encrypted_aes_key"]
        initial_vector_b64 = body["initial_vector"]

        flow_data = b64decode(encrypted_flow_data_b64)
        iv = b64decode(initial_vector_b64)
        encrypted_aes_key = b64decode(encrypted_aes_key_b64)

        aes_key = self.private_key.decrypt(
            encrypted_aes_key,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Split tag (last 16 bytes) from cipher
        encrypted_flow_data_body = flow_data[:-16]
        encrypted_flow_data_tag = flow_data[-16:]

        decryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv, encrypted_flow_data_tag),
            backend=default_backend()
        ).decryptor()

        decrypted_data_bytes = decryptor.update(encrypted_flow_data_body) + decryptor.finalize()
        decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))

        return decrypted_data, aes_key, iv

    def encrypt_response(self, response_data: dict, aes_key: bytes, iv: bytes) -> str:
        """
        Encrypt JSON response using AES-GCM with flipped IV
        """
        flipped_iv = bytes([b ^ 0xFF for b in iv])

        encryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(flipped_iv),
            backend=default_backend()
        ).encryptor()

        encrypted_bytes = encryptor.update(json.dumps(response_data).encode("utf-8")) + encryptor.finalize()
        tag = encryptor.tag

        return b64encode(encrypted_bytes + tag).decode("utf-8")
