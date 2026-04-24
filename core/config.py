import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Where the encrypted files live
VAULT_DIR = os.path.join(BASE_DIR, "vault")

# Ensure the vault directory exists
if not os.path.exists(VAULT_DIR):
    os.makedirs(VAULT_DIR)

# File extension for COMRADE encrypted files
VAULT_EXTENSION = ".vault"
