import os
import json
import platform
import secrets
import ctypes # We will wrap this in a try/except for Linux/Mac safety

# --- ADD THESE IMPORTS ---
from core.encryption import encrypt_data, decrypt_data
from core.auth import generate_salt
from core.config import VAULT_DIR, VAULT_EXTENSION

# Static Manifest Path
MANIFEST_PATH = os.path.join(VAULT_DIR, ".vault_manifest")

def hide_vault_folder(path):
    """
    STEALTH MODULE:
    Windows: Uses System+Hidden attributes.
    Linux/Mac: Relies on the '.' prefix and restricted permissions.
    """
    if not os.path.exists(path):
        return

    if platform.system() == "Windows":
        try:
            abs_path = os.path.abspath(path)
            # 0x02: Hidden, 0x04: System
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x02 | 0x04)
        except:
            pass # Fallback if Windows call fails
    else:
        # On Unix, we ensure the owner has full access, others have none (700)
        try:
            os.chmod(path, 0o700)
        except:
            pass

def unlock_for_writing(path):
    """Sets attributes to allow modification."""
    if not os.path.exists(path):
        return

    if platform.system() == "Windows":
        try:
            abs_path = os.path.abspath(path)
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x80) # Normal
        except:
            pass
    else:
        try:
            os.chmod(path, 0o700)
        except:
            pass

def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return {}
    try:
        with open(MANIFEST_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_file(file_path, password):
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR)
    
    hide_vault_folder(VAULT_DIR)

    with open(file_path, 'rb') as f:
        data = f.read()

    salt = generate_salt()
    encrypted_content = encrypt_data(data, password, salt)
    
    filename = os.path.basename(file_path)
    vault_filename = f"{os.urandom(8).hex()}{VAULT_EXTENSION}"
    vault_path = os.path.join(VAULT_DIR, vault_filename)

    with open(vault_path, 'wb') as f:
        f.write(salt + encrypted_content)

    hide_vault_folder(vault_path)

    manifest = load_manifest()
    manifest[vault_filename] = filename
    
    unlock_for_writing(MANIFEST_PATH)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=4)
    hide_vault_folder(MANIFEST_PATH)
    
    return vault_filename

def extract_file(vault_id, password):
    manifest = load_manifest()
    if vault_id not in manifest:
        raise Exception("Vault ID not found.")

    vault_path = os.path.join(VAULT_DIR, vault_id)
    with open(vault_path, 'rb') as f:
        salt = f.read(16)
        encrypted_content = f.read()

    decrypted_data = decrypt_data(encrypted_content, password, salt)
    output_path = os.path.join(os.getcwd(), manifest[vault_id])
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
    return output_path

def delete_vault_file(vault_id, password):
    if not password:
        raise Exception("Authorization required.")

    manifest = load_manifest()
    if vault_id not in manifest:
        raise Exception("Target asset not found.")
        
    vault_path = os.path.join(VAULT_DIR, vault_id)
    
    # Auth Validation
    with open(vault_path, 'rb') as f:
        salt = f.read(16)
        encrypted_content = f.read()
    decrypt_data(encrypted_content, password, salt)

    # UNLOCK and WIPE
    if os.path.exists(vault_path):
        unlock_for_writing(vault_path)
        file_size = os.path.getsize(vault_path)
        with open(vault_path, "wb") as f:
            f.write(os.urandom(file_size)) 
        os.remove(vault_path)
    
    # Manifest Cleanup
    del manifest[vault_id]
    unlock_for_writing(MANIFEST_PATH)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=4)
    hide_vault_folder(MANIFEST_PATH)
    return True

def list_secured_files():
    manifest = load_manifest()
    return [{"vault_name": k, "original_name": v} for k, v in manifest.items()]
