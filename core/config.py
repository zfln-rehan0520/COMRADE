import os
import platform

# Detect the Operating System
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    # Windows: Use the Local AppData folder
    # Fallback to current directory if LOCALAPPDATA isn't found for some reason
    base_dir = os.getenv('LOCALAPPDATA', os.getcwd())
    VAULT_DIR = os.path.join(base_dir, 'ComradeVault')
else:
    # Linux/Mac: Use a hidden folder in the User's Home directory
    # ~/.comrade_vault is the standard Linux way to hide app data
    base_dir = os.path.expanduser('~')
    VAULT_DIR = os.path.join(base_dir, '.comrade_vault')

VAULT_EXTENSION = ".dat"

# Manifest path logic
MANIFEST_PATH = os.path.join(VAULT_DIR, "sys_cache.idx")
