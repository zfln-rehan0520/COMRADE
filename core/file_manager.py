import ctypes
import json
import os
import platform
import secrets
import subprocess

from core.auth import generate_salt
from core.config import MANIFEST_PATH, VAULT_DIR, VAULT_EXTENSION
from core.encryption import decrypt_data, encrypt_data


def secure_wipe(path):
    """Overwrite a file with random bytes in place before deleting it."""
    if not os.path.exists(path):
        return
    try:
        unlock_for_writing(path)
        size = os.path.getsize(path)
        with open(path, "r+b", buffering=0) as f:
            f.write(secrets.token_bytes(size))
        os.remove(path)
    except Exception:
        try:
            os.remove(path)
        except Exception:
            pass


def hide_vault_folder(path):
    """Windows: sets Hidden + System attributes. Linux/Mac: restricts to owner-only."""
    if not os.path.exists(path):
        return

    abs_path = os.path.abspath(path)

    if platform.system() == "Windows":
        try:
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x02 | 0x04)
            subprocess.run(["attrib", "+s", "+h", abs_path, "/s", "/d"], check=False, capture_output=True)
        except Exception:
            pass
    else:
        try:
            os.chmod(abs_path, 0o700)
        except Exception:
            pass


def unlock_for_writing(path):
    """Clears the System/Hidden attributes so the file can be modified."""
    if not os.path.exists(path):
        return

    abs_path = os.path.abspath(path)

    if platform.system() == "Windows":
        try:
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x80)
            subprocess.run(["attrib", "-s", "-h", abs_path, "/s", "/d"], check=False, capture_output=True)
        except Exception:
            pass
    else:
        try:
            os.chmod(abs_path, 0o700)
        except Exception:
            pass


def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return {}
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, IOError):
        return {}


def save_manifest(manifest):
    try:
        unlock_for_writing(MANIFEST_PATH)
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4)
        hide_vault_folder(MANIFEST_PATH)
        return True
    except Exception as e:
        print(f"[CORE ERROR] Manifest save failed: {e}")
        return False


def save_file(file_path, password):
    """Encrypts a file into the vault, then shreds the original."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")

    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR, mode=0o700, exist_ok=True)

    hide_vault_folder(VAULT_DIR)
    abs_original_path = os.path.abspath(file_path)

    with open(file_path, "rb") as f:
        data = f.read()

    salt = generate_salt()
    encrypted = encrypt_data(data, password, salt)

    vault_filename = f"idx_{os.urandom(4).hex()}{VAULT_EXTENSION}"
    vault_path = os.path.join(VAULT_DIR, vault_filename)

    with open(vault_path, "wb") as f:
        f.write(salt + encrypted)

    hide_vault_folder(vault_path)

    manifest = load_manifest()
    manifest[vault_filename] = abs_original_path
    save_manifest(manifest)

    secure_wipe(file_path)
    return vault_filename


def extract_file(vault_id, password):
    """Decrypts a vault entry and restores it to its original path."""
    manifest = load_manifest()

    key = vault_id
    if key not in manifest and not key.endswith(VAULT_EXTENSION):
        key = f"{vault_id}{VAULT_EXTENSION}"

    if key not in manifest:
        raise Exception("Asset signature not found in manifest.")

    vault_path = os.path.join(VAULT_DIR, key)
    if not os.path.exists(vault_path):
        raise FileNotFoundError("Vault entry missing from disk.")

    with open(vault_path, "rb") as f:
        salt = f.read(16)
        encrypted = f.read()

    decrypted = decrypt_data(encrypted, password, salt)

    dest = manifest[key]
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    with open(dest, "wb") as f:
        f.write(decrypted)

    secure_wipe(vault_path)

    del manifest[key]
    save_manifest(manifest)

    return dest


def delete_vault_file(vault_id, password):
    """Requires the password to succeed, so a stolen manifest alone can't shred assets."""
    if not password:
        raise Exception("Authorization required.")

    manifest = load_manifest()

    key = vault_id
    if key not in manifest and not key.endswith(VAULT_EXTENSION):
        key = f"{vault_id}{VAULT_EXTENSION}"

    if key not in manifest:
        raise Exception("Target not found in manifest.")

    vault_path = os.path.join(VAULT_DIR, key)

    if os.path.exists(vault_path):
        with open(vault_path, "rb") as f:
            salt = f.read(16)
            encrypted = f.read()
        decrypt_data(encrypted, password, salt)  # raises if the password is wrong
        secure_wipe(vault_path)

    del manifest[key]
    save_manifest(manifest)
    return True


def list_secured_files():
    try:
        manifest = load_manifest()
        entries = []

        for vault_file, orig_path in manifest.items():
            v_path = os.path.join(VAULT_DIR, vault_file)
            if os.path.exists(v_path):
                entries.append({
                    "vault_name": str(vault_file),
                    "original_name": str(os.path.basename(orig_path)),
                })

        return entries
    except Exception as e:
        print(f"[CORE ERROR] Vault list parsing failed: {e}")
        return []
