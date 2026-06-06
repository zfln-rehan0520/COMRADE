from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt_data(data: bytes, password: str, salt: bytes) -> bytes:
    """
    Encrypts raw bytes using AES-GCM.
    Returns: nonce + ciphertext
    """
    from core.auth import derive_key
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12) 
    
    ciphertext = aesgcm.encrypt(nonce, data, None)
   
    return nonce + ciphertext

def decrypt_data(encrypted_data: bytes, password: str, salt: bytes) -> bytes:
    """
    Decrypts AES-GCM data. 
    Expects nonce to be the first 12 bytes.
    """
    from core.auth import derive_key
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    
    return aesgcm.decrypt(nonce, ciphertext, None)
