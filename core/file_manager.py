def extract_file(vault_id, password):
    """Decrypts a file from the vault and restores it to the current directory."""
    manifest = load_manifest()
    
    if vault_id not in manifest:
        raise Exception(f"Vault ID '{vault_id}' not found in the manifest.")

    original_name = manifest[vault_id]
    vault_path = os.path.join(VAULT_DIR, vault_id)

    if not os.path.exists(vault_path):
        raise Exception(f"The encrypted file {vault_id} is missing from the vault folder.")

    # 1. Read the raw vault file
    with open(vault_path, 'rb') as f:
        # We know the first 16 bytes are the SALT (based on your save_file logic)
        salt = f.read(16)
        encrypted_content = f.read()

    # 2. Use your existing decrypt_data tool
    decrypted_data = decrypt_data(encrypted_content, password, salt)

    # 3. Save the restored file to your current working directory
    output_path = os.path.join(os.getcwd(), original_name)
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)

    return output_path
