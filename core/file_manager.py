import os
import json
import platform
import secrets
import ctypes
import subprocess

from core.encryption import encrypt_data, decrypt_data
from core.auth import generate_salt
from core.config import VAULT_DIR, VAULT_EXTENSION, MANIFEST_PATH

def secure_wipe(path):
    """
    ANTI-FORENSIC SHREDDER:
    Physically overwrites the file with random bits before deletion.
    """
    if os.path.exists(path):
        try:
            # Normalize attributes to allow overwriting
            unlock_for_writing(path)
            size = os.path.getsize(path)
            with open(path, "wb", buffering=0) as f:
                f.write(secrets.token_bytes(size))
            os.remove(path)
        except Exception as e:
            # Fallback to standard delete if shredding is blocked
            os.remove(path)

def hide_vault_folder(path):
    """
    STEALTH MODULE (Ghost Mode):
    Windows: Sets Hidden (0x02) + System (0x04) attributes.
    Linux/Mac: Sets permissions to 700 (Owner-only).
    """
    if not os.path.exists(path):
        return

    abs_path = os.path.abspath(path)

    if platform.system() == "Windows":
        try:
            # Direct Kernel Call
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x02 | 0x04)
            # Recursive Shell Fallback
            subprocess.run(['attrib', '+s', '+h', abs_path, '/s', '/d'], 
                           check=False, capture_output=True)
        except:
            pass
    else:
        # Linux Security: Restricted access permissions
        try:
            os.chmod(abs_path, 0o700)
        except:
            pass

def unlock_for_writing(path):
    """Removes 'System' and 'Hidden' protections to allow modification."""
    if not os.path.exists(path):
        return

    abs_path = os.path.abspath(path)

    if platform.system() == "Windows":
        try:
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x80) # Normal
            subprocess.run(['attrib', '-s', '-h', abs_path, '/s', '/d'], 
                           check=False, capture_output=True)
        except:
            pass
    else:
        try:
            os.chmod(abs_path, 0o700)
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
    """
    COMMIT TO VAULT:
    Encrypts, moves to AppData/Hidden folder, and wipes the original.
    """
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR, mode=0o700, exist_ok=True)
    
    hide_vault_folder(VAULT_DIR)

    # Capture original home location for restoration
    abs_original_path = os.path.abspath(file_path)

    with open(file_path, 'rb') as f:
        data = f.read()

    salt = generate_salt()
    encrypted_content = encrypt_data(data, password, salt)
    
    # Camouflage the filename as a system cache index
    vault_filename = f"idx_{os.urandom(4).hex()}{VAULT_EXTENSION}"
    vault_path = os.path.join(VAULT_DIR, vault_filename)

    with open(vault_path, 'wb') as f:
        f.write(salt + encrypted_content)

    hide_vault_folder(vault_path)

    # Update Manifest
    manifest = load_manifest()
    manifest[vault_filename] = abs_original_path 
    
    unlock_for_writing(MANIFEST_PATH)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=4)
    hide_vault_folder(MANIFEST_PATH)
    
    # Final Security Step: Shred the unencrypted original
    secure_wipe(file_path)
    
    return vault_filename

def extract_file(vault_id, password):
    """
    RESTORE HOME:
    Decrypts and 'teleports' the file back to its original directory.
    """
    manifest = load_manifest()
    if vault_id not in manifest:
        raise Exception("Asset signature not found in manifest.")

    vault_path = os.path.join(VAULT_DIR, vault_id)
    with open(vault_path, 'rb') as f:
        salt = f.read(16)
        encrypted_content = f.read()

    decrypted_data = decrypt_data(encrypted_content, password, salt)
    
    # Get original path from manifest
    target_path = manifest[vault_id]
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    with open(target_path, 'wb') as f:
        f.write(decrypted_data)
    
    # Post-Extraction Cleanup: Wipe the vault residue
    secure_wipe(vault_path)
    
    # Update Manifest
    del manifest[vault_id]
    unlock_for_writing(MANIFEST_PATH)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=4)
    hide_vault_folder(MANIFEST_PATH)

    return target_path

def list_secured_files():
    manifest = load_manifest()
    return [{"vault_name": k, "original_name": v} for k, v in manifest.items()]
