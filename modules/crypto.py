from cryptography.fernet import Fernet
import hashlib
import base64


def convert_key(key: str) -> bytes:
    input_bytes = key.encode()
    sha256_hash = hashlib.sha256(input_bytes).digest()
    fernet_key = base64.urlsafe_b64encode(sha256_hash)
    return fernet_key


def encrypt(content: str, key: str) -> bytes:
    f = Fernet(convert_key(key))
    return f.encrypt(content.encode())


def decrypt(content: bytes, key: str) -> str:
    f = Fernet(convert_key(key))
    return f.decrypt(content).decode()
