import os

# Using a dot-prefix ensures it's hidden on Linux/Mac
# On Windows, we will still apply the Kernel 'System' attribute to this folder
VAULT_DIR = os.path.join(os.getcwd(), ".comrade_vault")
VAULT_EXTENSION = ".vault"
