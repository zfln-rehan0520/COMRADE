import os
import platform
import logging

logger = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX   = platform.system() == "Linux"
IS_MAC     = platform.system() == "Darwin"

if IS_WINDOWS:
    base_dir = os.getenv('LOCALAPPDATA', os.getcwd())
    VAULT_DIR = os.path.join(base_dir, 'ComradeVault')
else:
    base_dir = os.path.expanduser('~')
    VAULT_DIR = os.path.join(base_dir, '.comrade_vault')

VAULT_EXTENSION = ".dat"
MANIFEST_PATH   = os.path.join(VAULT_DIR, "sys_cache.idx")

# Salt size must match what auth.py generates (32 bytes)
SALT_SIZE = 32
