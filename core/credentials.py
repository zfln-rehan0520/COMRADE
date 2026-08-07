import json
import os
import base64
from cryptography.exceptions import InvalidTag
from core.encryption import encrypt_text, decrypt_text

CRED_FILE = ".comrade_credentials.json"

def load_credentials():
    if not os.path.exists(CRED_FILE):
        return {}
    try:
        with open(CRED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_credentials(credentials_dict):
    try:
        with open(CRED_FILE, "w", encoding="utf-8") as f:
            json.dump(credentials_dict, f, indent=4)
        return True
    except Exception:
        return False

def encrypt_individual_pass(plain_password, item_key):
    try:
        cipher_output = encrypt_text(plain_password, item_key)
        
        # Explicitly tag bytes so we don't accidentally scramble strings later
        if isinstance(cipher_output, bytes):
            return "B64:" + base64.b64encode(cipher_output).decode('utf-8')
            
        return str(cipher_output)
    except Exception as e:
        print(f"[Crypto Error - Encrypt]: {e}")
        return None

def decrypt_individual_pass(cipher_text, item_key):
    """
    Decrypts individual stored passwords using item_key.
    Relies purely on cryptographic tag verification instead of substring heuristics (Fixes M1).
    """
    try:
        # Decode base64 payload if tagged
        if isinstance(cipher_text, str) and cipher_text.startswith("B64:"):
            cipher_data = base64.b64decode(cipher_text[4:].encode('utf-8'))
        else:
            cipher_data = cipher_text

        plain_output = decrypt_text(cipher_data, item_key)
        
        if plain_output is None:
            return None
            
        if isinstance(plain_output, bytes):
            plain_output = plain_output.decode('utf-8')

        # REMOVED (Fixes M1): The string heuristic check looking for "error", "fail", "invalid", etc.
        # Decryption correctness is handled via the AEAD tag check inside decrypt_text/AES-GCM.

        return plain_output
    except InvalidTag:
        # Native AEAD tag mismatch signal for invalid key or tampered ciphertext
        print("[Crypto Error - Decrypt]: Invalid key or corrupted tag.")
        return None
    except Exception as e:
        print(f"[Crypto Error - Decrypt]: {e}")
        return None