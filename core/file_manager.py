import os
import json
import ctypes
import platform

def hide_vault_folder(path):
    """Sets folder to System (0x04) + Hidden (0x02)"""
    if platform.system() == "Windows":
        # This tells Windows: "Treat this file as a hidden system component"
        ctypes.windll.kernel32.SetFileAttributesW(path, 0x02 | 0x04)
import secrets
from core.encryption import encrypt_data, decrypt_data
from core.auth import generate_salt
from core.config import VAULT_DIR, VAULT_EXTENSION

# Static Manifest Path
MANIFEST_PATH = os.path.join(VAULT_DIR, ".vault_manifest")

def hide_vault_folder(path):
    """
    STEALTH MODULE: Sets folder/file to System + Hidden.
    Prevents discovery by standard users even with 'Show Hidden Files' enabled.
    """
    if platform.system() == "Windows" and os.path.exists(path):
        # 0x02: Hidden, 0x04: System
        ctypes.windll.kernel32.SetFileAttributesW(path, 0x02 | 0x04)

def unlock_for_writing(path):
    """Temporarily removes System/Hidden attributes to allow file modifications."""
    if platform.system() == "Windows" and os.path.exists(path):
        # 0x80: Normal
        ctypes.windll.kernel32.SetFileAttributesW(path, 0x80)

def load_manifest():
    """Retrieves the vault mapping. Returns empty dict if inaccessible."""
    if not os.path.exists(MANIFEST_PATH):
        return {}
    try:
        with open(MANIFEST_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_file(file_path, password):
    """Encrypts a file, logs it in the manifest, and hides the vault folder/files."""
    
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR)
    
    # Hide the main directory
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

    # --- NEW: Hide the individual encrypted .vault file ---
    hide_vault_folder(vault_path)

    # Update the manifest
    manifest = load_manifest()
    manifest[vault_filename] = filename
    
    unlock_for_writing(MANIFEST_PATH)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=4)
    
    hide_vault_folder(MANIFEST_PATH)
    
    return vault_filename

def extract_file(vault_id, password):
    """DECRYPTION ENGINE: Restores asset to CWD. Validates key via AES check."""
    manifest = load_manifest()
    if vault_id not in manifest:
        raise Exception("Vault ID not found in local manifest.")

    vault_path = os.path.join(VAULT_DIR, vault_id)
    with open(vault_path, 'rb') as f:
        salt = f.read(16)
        encrypted_content = f.read()

    # Validation happens inside decrypt_data (HMAC/Tag check)
    decrypted_data = decrypt_data(encrypted_content, password, salt)

    output_path = os.path.join(os.getcwd(), manifest[vault_id])
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
    return output_path

def delete_vault_file(vault_id, password):
    """
    WIPE ENGINE: Validates Master Key, then performs a Single-Pass Secure Erase.
    """
    if not password:
        raise Exception("Authorization required.")

    # 1. AUTHENTICATION VALIDATION
    try:
        manifest = load_manifest()
        if vault_id not in manifest:
            raise Exception("Target asset not found.")
            
        vault_path = os.path.join(VAULT_DIR, vault_id)
        with open(vault_path, 'rb') as f:
            salt = f.read(16)
            encrypted_content = f.read()
        
        # Test Decryption: If password is wrong, this raises Exception
        decrypt_data(encrypted_content, password, salt)
        
    except Exception:
        raise Exception("CRITICAL: Invalid Master Key. Action Aborted.")

    # 2. SECURE WIPE (Overwrites with random bits before OS removal)
    if os.path.exists(vault_path):
        file_size = os.path.getsize(vault_path)
        with open(vault_path, "wb") as f:
            f.write(os.urandom(file_size)) 
        os.remove(vault_path)
    
    # 3. MANIFEST CLEANUP with Stealth Toggle
    if vault_id in manifest:
        del manifest[vault_id]
        unlock_for_writing(MANIFEST_PATH)
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=4)
        hide_vault_folder(MANIFEST_PATH)
            
    return True

def list_secured_files():
    """METADATA ENGINE: Returns asset list for UI rendering."""
    manifest = load_manifest()
    return [{"vault_name": k, "original_name": v} for k, v in manifest.items()]
