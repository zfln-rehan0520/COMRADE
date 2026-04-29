import os
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

logger = logging.getLogger(__name__)

NONCE_SIZE = 12  # 96-bit nonce — optimal for AES-GCM

def encrypt_data(data: bytes, password: str, salt: bytes) -> bytes:
    """
    Encrypts raw bytes using AES-256-GCM (Authenticated Encryption).

    Returns: nonce (12 bytes) + ciphertext+tag
    The GCM authentication tag is appended automatically by the library.
    """
    from core.auth import derive_key
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext

def decrypt_data(encrypted_data: bytes, password: str, salt: bytes) -> bytes:
    """
    Decrypts AES-256-GCM data.

    Expects: nonce (first 12 bytes) + ciphertext+tag
    Raises InvalidTag if the password is wrong or data has been tampered with.
    """
    from core.auth import derive_key
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    if len(encrypted_data) < NONCE_SIZE:
        raise ValueError("Encrypted data is too short to contain a valid nonce.")

    nonce = encrypted_data[:NONCE_SIZE]
    ciphertext = encrypted_data[NONCE_SIZE:]

    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except InvalidTag:
        # Re-raise with a cleaner message — do not leak internal details
        raise InvalidTag("Decryption failed: invalid key or data has been tampered with.")
