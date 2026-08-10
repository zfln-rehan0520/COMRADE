import base64
import json
import os

from cryptography.exceptions import InvalidTag

from core.encryption import decrypt_text, encrypt_text

CRED_FILE = ".comrade_credentials.json"


def load_credentials():
    if not os.path.exists(CRED_FILE):
        return {}
    try:
        with open(CRED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_credentials(credentials):
    try:
        with open(CRED_FILE, "w", encoding="utf-8") as f:
            json.dump(credentials, f, indent=4)
        return True
    except Exception:
        return False


def encrypt_individual_pass(plain_password, item_key):
    try:
        cipher = encrypt_text(plain_password, item_key)
        if isinstance(cipher, bytes):
            return "B64:" + base64.b64encode(cipher).decode("utf-8")
        return str(cipher)
    except Exception as e:
        print(f"[Crypto Error - Encrypt]: {e}")
        return None


def decrypt_individual_pass(cipher_text, item_key):
    """Decrypt a stored password. Relies on the AEAD tag check rather than string heuristics."""
    try:
        if isinstance(cipher_text, str) and cipher_text.startswith("B64:"):
            cipher_data = base64.b64decode(cipher_text[4:].encode("utf-8"))
        else:
            cipher_data = cipher_text

        plain = decrypt_text(cipher_data, item_key)
        if plain is None:
            return None
        if isinstance(plain, bytes):
            plain = plain.decode("utf-8")
        return plain
    except InvalidTag:
        print("[Crypto Error - Decrypt]: Invalid key or corrupted tag.")
        return None
    except Exception as e:
        print(f"[Crypto Error - Decrypt]: {e}")
        return None
