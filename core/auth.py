import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# OWASP's current minimum for PBKDF2-HMAC-SHA256
KDF_ITERATIONS = 600_000


def derive_key(password: str, salt: bytes) -> bytes:
    """Turn a password into a 32-byte key, expensive enough to resist GPU cracking."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
        backend=default_backend(),
    )
    return kdf.derive(password.encode())


def generate_salt() -> bytes:
    return os.urandom(16)
