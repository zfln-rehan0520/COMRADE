import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# OWASP recommended minimum for PBKDF2-HMAC-SHA256 (Fixes H1)
KDF_ITERATIONS = 600_000

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Turns a plain-text password into a 32-byte cryptographic key.
    Uses 600,000 PBKDF2 iterations to resist modern GPU cracking attempts.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def generate_salt() -> bytes:
    """Generates a random 16-byte salt."""
    return os.urandom(16)