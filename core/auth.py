import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend

# Scrypt parameters — tuned for memory-hardness
# N=2^17 (131072): Work factor (CPU/memory cost). Higher = slower brute-force.
# r=8: Block size parameter, affects memory bandwidth usage.
# p=1: Parallelization factor.
# These parameters require ~128MB of RAM per derivation, making GPU/ASIC attacks unviable.
SCRYPT_N = 2**17
SCRYPT_R = 8
SCRYPT_P = 1
KEY_LENGTH = 32  # 256-bit key for AES-256

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a 256-bit cryptographic key from a plaintext password using Scrypt KDF.
    Memory-hard: resistant to GPU and ASIC brute-force attacks.
    """
    kdf = Scrypt(
        salt=salt,
        length=KEY_LENGTH,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))

def generate_salt() -> bytes:
    """Generates a cryptographically secure random 32-byte salt."""
    return os.urandom(32)
