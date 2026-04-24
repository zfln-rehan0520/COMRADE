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

    update_manifest(vault_filename, filename)
    return vault_filename

def extract_file(vault_id, password):
    """Decrypts a file from the vault and restores it to the current directory."""
    manifest = load_manifest()
    
    if vault_id not in manifest:
        raise Exception(f"Vault ID '{vault_id}' not found in the manifest.")

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

def delete_vault_file(vault_id):
    """Permanently deletes a file from the vault and updates the manifest."""
    # 1. Physical Wipe from the vault folder
    vault_path = os.path.join(VAULT_DIR, vault_id)
    if os.path.exists(vault_path):
        os.remove(vault_path)
    
    # 2. Manifest Cleanup
    manifest = load_manifest()
    if vault_id in manifest:
        del manifest[vault_id]
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=4)
    return True

def update_manifest(vault_filename, original_name):
    """Logs the relationship between the vault file and the original name."""
    manifest = load_manifest()
    manifest[vault_filename] = original_name
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=4)

def load_manifest():
    """Loads the file index."""
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def list_secured_files():
    """Returns a list of all files currently in the vault."""
    manifest = load_manifest()
    return [{"vault_name": k, "original_name": v} for k, v in manifest.items()]
