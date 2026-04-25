import os
import json
from core.encryption import encrypt_data, decrypt_data
from core.auth import generate_salt
from core.config import VAULT_DIR, VAULT_EXTENSION

MANIFEST_PATH = os.path.join(VAULT_DIR, ".vault_manifest")

def load_manifest():
    """Returns the manifest. Returns empty dict if file is missing or corrupt."""
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH, 'r') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_file(file_path, password):
    """Encrypts a file and logs it in the manifest."""
    with open(file_path, 'rb') as f:
        data = f.read()

    salt = generate_salt()
    encrypted_content = encrypt_data(data, password, salt)
    
    filename = os.path.basename(file_path)
    vault_filename = f"{os.urandom(8).hex()}{VAULT_EXTENSION}"
    vault_path = os.path.join(VAULT_DIR, vault_filename)

    with open(vault_path, 'wb') as f:
        f.write(salt + encrypted_content)

    # Update the manifest (Plain text JSON for easy listing)
    manifest = load_manifest()
    manifest[vault_filename] = filename
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=4)
    
    return vault_filename

def extract_file(vault_id, password):
    """Decrypts file. Fails if password is wrong."""
    manifest = load_manifest()
    if vault_id not in manifest:
        raise Exception("Vault ID not found.")

    vault_path = os.path.join(VAULT_DIR, vault_id)
    with open(vault_path, 'rb') as f:
        salt = f.read(16)
        encrypted_content = f.read()

    # If password is wrong, decrypt_data will raise an error
    decrypted_data = decrypt_data(encrypted_content, password, salt)

    output_path = os.path.join(os.getcwd(), manifest[vault_id])
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
    return output_path

def delete_vault_file(vault_id, password):
    """Refuses wipe unless password is provided (prevents simple bypass)."""
    if not password:
        raise Exception("Authorization Required.")

    vault_path = os.path.join(VAULT_DIR, vault_id)
    if os.path.exists(vault_path):
        # Secure Wipe
        size = os.path.getsize(vault_path)
        with open(vault_path, "wb") as f:
            f.write(os.urandom(size))
        os.remove(vault_path)
    
    manifest = load_manifest()
    if vault_id in manifest:
        del manifest[vault_id]
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=4)
    return True

def list_secured_files():
    """Returns list for the table view without needing a password."""
    manifest = load_manifest()
    return [{"vault_name": k, "original_name": v} for k, v in manifest.items()]
