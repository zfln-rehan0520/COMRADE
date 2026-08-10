import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core.auth import derive_key


def encrypt_data(data: bytes, password: str, salt: bytes) -> bytes:
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext


def decrypt_data(encrypted_data: bytes, password: str, salt: bytes) -> bytes:
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)


def encrypt_text(plaintext: str, room_key: str) -> str:
    """String-friendly wrapper around encrypt_data, used by the IRC chat client."""
    salt = os.urandom(16)
    raw = plaintext.encode("utf-8")
    encrypted = encrypt_data(raw, room_key, salt)
    return base64.b64encode(salt + encrypted).decode("utf-8")


def decrypt_text(b64_payload: str, room_key: str) -> str:
    try:
        raw = base64.b64decode(b64_payload)
        salt, encrypted = raw[:16], raw[16:]
        return decrypt_data(encrypted, room_key, salt).decode("utf-8")
    except Exception:
        return "<Decryption Failed: Invalid Key or Corrupt Data>"
