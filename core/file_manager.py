import os
import json
import platform
import secrets

# Import Windows-only libraries only if we are on Windows
if platform.system() == "Windows":
    import ctypes
else:
    import stat # For Linux/Mac permissions

def hide_vault_folder(path):
    """
    STEALTH MODULE:
    Windows: Uses System+Hidden attributes.
    Linux/Mac: Relies on the '.' prefix (set in config.py).
    """
    if not os.path.exists(path):
        return

    if platform.system() == "Windows":
        abs_path = os.path.abspath(path)
        # 0x02: Hidden, 0x04: System
        ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x02 | 0x04)
    else:
        # On Unix, we don't need a kernel call to hide (the dot does it),
        # but we can restrict permissions so only the owner can read/write.
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

def unlock_for_writing(path):
    """
    Sets attributes to allow modification.
    """
    if not os.path.exists(path):
        return

    if platform.system() == "Windows":
        abs_path = os.path.abspath(path)
        ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x80) # Normal
    else:
        # Ensure owner has write permissions on Unix
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        
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
