import os
import json
from core.encryption import encrypt_data, decrypt_data
from core.auth import generate_salt
from core.config import VAULT_DIR, VAULT_EXTENSION

# Standardized path for your manifest
MANIFEST_PATH = os.path.join(VAULT_DIR, ".vault_manifest")

def save_file(file_path, password):
    """Encrypts a file and moves it into the vault."""
    with open(file_path, 'rb') as f:
        data = f.read()

    salt = generate_salt()
    encrypted_content = encrypt_data(data, password, salt)
    
    filename = os.path.basename(file_path)
    vault_filename = f"{os.urandom(8).hex()}{VAULT_EXTENSION}"
    vault_path = os.path.join(VAULT_DIR, vault_filename)

    # Structure: [SALT(16 bytes)] + [ENCRYPTED_DATA]
    with open(vault_path, 'wb') as f:
        f.write(salt + encrypted_content)

    # FIX: Passing password to update_manifest
    update_manifest(vault_filename, filename, password)
    return vault_filename

def extract_file(vault_id, password):
    """Decrypts a file from the vault and restores it to the current directory."""
    # FIX: Passing password to load_manifest
    manifest = load_manifest(password)
    
    if vault_id not in manifest:
        raise Exception(f"Vault ID '{vault_id}' not found or incorrect Master Key.")

    original_name = manifest[vault_id]
    vault_path = os.path.join(VAULT_DIR, vault_id)

    if not os.path.exists(vault_path):
        raise Exception(f"Encrypted file {vault_id} missing from vault folder.")

    with open(vault_path, 'rb') as f:
        salt = f.read(16)
        encrypted_content = f.read()

    decrypted_data = decrypt_data(encrypted_content, password, salt)

    output_path = os.path.join(os.getcwd(), original_name)
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)

    return output_path

def delete_vault_file(vault_id, password=None):
    """Securely wipes and permanently deletes a file from the vault."""
    vault_path = os.path.join(VAULT_DIR, vault_id)
    
    if os.path.exists(vault_path):
        # SECURE WIPE: Overwrite with random data before deletion
        file_size = os.path.getsize(vault_path)
        with open(vault_path, "wb") as f:
            f.write(os.urandom(file_size))
        
        os.remove(vault_path)
    
    # 2. Manifest Cleanup (Requires password to rewrite the encrypted file)
    if password:
        manifest = load_manifest(password)
        if vault_id in manifest:
            del manifest[vault_id]
            # Re-save the manifest without the deleted entry
            save_encrypted_manifest(manifest, password)
    return True

def update_manifest(vault_filename, original_name, password):
    """Logs the relationship and saves it encrypted."""
    manifest = load_manifest(password)
    manifest[vault_filename] = original_name
    save_encrypted_manifest(manifest, password)

def save_encrypted_manifest(manifest, password):
    """Helper to encrypt the manifest file."""
    salt = generate_salt()
    json_data = json.dumps(manifest).encode('utf-8')
    encrypted_manifest = encrypt_data(json_data, password, salt)
    
    with open(MANIFEST_PATH, 'wb') as f:
        f.write(salt + encrypted_manifest)

def load_manifest(password=None):
    """FIXED: Now takes 1 positional argument (password)."""
    if not os.path.exists(MANIFEST_PATH) or not password:
        return {}
    
    with open(MANIFEST_PATH, 'rb') as f:
        try:
            salt = f.read(16)
            encrypted_content = f.read()
            decrypted_json = decrypt_data(encrypted_content, password, salt)
            return json.loads(decrypted_json.decode('utf-8'))
        except Exception:
            return {} # Returns empty if decryption fails

def list_secured_files(password):
    """Returns a list of all files currently in the vault (requires key)."""
    manifest = load_manifest(password)
    return [{"vault_name": k, "original_name": v} for k, v in manifest.items()]
