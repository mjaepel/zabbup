import base64
import hashlib
import os

from cryptography.fernet import Fernet


def convert_key(key: str) -> bytes:
    input_bytes = key.encode()
    sha3_256_hash = hashlib.sha3_256(input_bytes).digest()
    return base64.urlsafe_b64encode(sha3_256_hash)


class FernetDeterministic(Fernet):
    def __init__(self, key: bytes | str, *, deterministic: bool = False) -> None:
        self.iv_deterministic = False
        if deterministic:
            self.iv_deterministic = hashlib.sha3_256(key).digest()[:16]
        super().__init__(key)

    def encrypt_at_time(self, data: bytes, current_time: int) -> bytes:
        iv = os.urandom(16)

        if self.iv_deterministic:
            iv = self.iv_deterministic
            current_time = 0

        return self._encrypt_from_parts(data, current_time, iv)


def encrypt(content: str, key: str, *, deterministic: bool = False) -> bytes:
    f = FernetDeterministic(key=convert_key(key), deterministic=deterministic)
    return f.encrypt(content.encode())


def decrypt(content: bytes, key: str, *, deterministic: bool = False) -> str:
    f = FernetDeterministic(key=convert_key(key), deterministic=deterministic)
    return f.decrypt(content).decode()
