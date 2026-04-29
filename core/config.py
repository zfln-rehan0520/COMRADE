import os

# This moves the vault to C:\Users\YourName\AppData\Local\ComradeVault
VAULT_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'ComradeVault')

# Rename the extension to look like a generic Windows data file
VAULT_EXTENSION = ".dat"
