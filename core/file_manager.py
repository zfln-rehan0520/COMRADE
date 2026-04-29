import os
import json
import platform
import secrets
import ctypes
import subprocess # Added for robust stealth fallback

from core.encryption import encrypt_data, decrypt_data
from core.auth import generate_salt
from core.config import VAULT_DIR, VAULT_EXTENSION

# Static Manifest Path
MANIFEST_PATH = os.path.join(VAULT_DIR, ".vault_manifest")

def secure_wipe(path):
    """Physically overwrites file with random data before deletion."""
    if os.path.exists(path):
        unlock_for_writing(path) 
        size = os.path.getsize(path)
        with open(path, "wb", buffering=0) as f:
            f.write(secrets.token_bytes(size))
        os.remove(path)

def hide_vault_folder(path):
    """
    STEALTH MODULE (Ghost Mode):
    Windows: 0x02 (Hidden) + 0x04 (System)
    Applies recursively to ensure all contents are invisible.
    """
    if not os.path.exists(path):
        return

    if platform.system() == "Windows":
        try:
            abs_path = os.path.abspath(path)
            # 1. Apply to the target path
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x02 | 0x04)
            
            # 2. Recursive application for directories
            if os.path.isdir(abs_path):
                for root, dirs, files in os.walk(abs_path):
                    for item in dirs + files:
                        item_path = os.path.join(root, item)
                        ctypes.windll.kernel32.SetFileAttributesW(item_path, 0x02 | 0x04)
            
            # 3. Secondary Shell Fallback (Ensures persistence)
            subprocess.run(['attrib', '+s', '+h', abs_path, '/s', '/d'], check=False, capture_output=True)
        except:
            pass 
    else:
        try:
            os.chmod(path, 0o700)
        except:
            pass

def unlock_for_writing(path):
    """Normalizes attributes (0x80) to allow modification/deletion."""
    if not os.path.exists(path):
        return

    if platform.system() == "Windows":
        try:
            abs_path = os.path.abspath(path)
            # 0x80 is 'FILE_ATTRIBUTE_NORMAL'
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x80)
            # Strip S/H via Shell to be sure
            subprocess.run(['attrib', '-s', '-h', abs_path, '/s', '/d'], check=False, capture_output=True)
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
    
    # Capture the HOME location of the file
    abs_original_path = os.path.abspath(file_path)

    with open(file_path, 'rb') as f:
        data = f.read()

    salt = generate_salt()
    encrypted_content = encrypt_data(data, password, salt)
    
    # Camouflage the filename: Looks like a system cache entry
    vault_filename = f"idx_{os.urandom(4).hex()}{VAULT_EXTENSION}"
    vault_path = os.path.join(VAULT_DIR, vault_filename)

    with open(vault_path, 'wb') as f:
        f.write(salt + encrypted_content)

    # Hide the vault in AppData
    hide_vault_folder(VAULT_DIR)

    manifest = load_manifest()
    # Save the exact original path for the 'Restore' feature
    manifest[vault_filename] = abs_original_path 
    
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
    
    # THE RESTORE FIX: Get the original home path from manifest
    target_output_path = manifest[vault_id] 
    
    # Auto-create the directory if the user deleted it in the meantime
    os.makedirs(os.path.dirname(target_output_path), exist_ok=True)

    with open(target_output_path, 'wb') as f:
        f.write(decrypted_data)
    
    return target_output_path

def delete_vault_file(vault_id, password):
    if not password:
        raise Exception("Authorization required.")

    manifest = load_manifest()
    if vault_id not in manifest:
        raise Exception("Target asset not found.")
        
    vault_path = os.path.join(VAULT_DIR, vault_id)
    
    with open(vault_path, 'rb') as f:
        salt = f.read(16)
        encrypted_content = f.read()
    decrypt_data(encrypted_content, password, salt)

    if os.path.exists(vault_path):
        secure_wipe(vault_path)
    
    del manifest[vault_id]
    unlock_for_writing(MANIFEST_PATH)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=4)
    hide_vault_folder(MANIFEST_PATH)
    return True

def list_secured_files():
    manifest = load_manifest()
    return [{"vault_name": k, "original_name": v} for k, v in manifest.items()]
