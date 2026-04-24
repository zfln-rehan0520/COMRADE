import os
import json
from core.encryption import encrypt_data, decrypt_data
from core.auth import generate_salt
from core.config import VAULT_DIR, VAULT_EXTENSION

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

    # The vault file structure: [SALT(16 bytes)] + [ENCRYPTED_DATA]
    with open(vault_path, 'wb') as f:
        f.write(salt + encrypted_content)

    # Update manifest so COMRADE knows what this random hex file is
    update_manifest(vault_filename, filename)
    
    # Optional: os.remove(file_path) # Uncomment to delete original after securing
    return vault_filename

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
        return json.load(f)

def list_secured_files():
    """Returns a list of all files currently in the vault."""
    manifest = load_manifest()
    return [{"vault_name": k, "original_name": v} for k, v in manifest.items()]
