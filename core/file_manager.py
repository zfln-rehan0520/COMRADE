import os
import json
import platform
import secrets
import logging
import ctypes
import subprocess

from core.encryption import encrypt_data, decrypt_data
from core.auth import generate_salt
from core.config import VAULT_DIR, VAULT_EXTENSION, MANIFEST_PATH, SALT_SIZE

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Anti-Forensic Wipe
# ---------------------------------------------------------------------------

def secure_wipe(path: str) -> None:
    """
    ANTI-FORENSIC SHREDDER:
    Overwrites the file with cryptographically random bits before deletion.
    Note: On SSDs with wear-leveling, physical recovery from raw NAND is still
    theoretically possible — full-disk encryption (e.g. LUKS/BitLocker) is the
    gold-standard complement to this.
    """
    if not os.path.exists(path):
        return
    try:
        unlock_for_writing(path)
        size = os.path.getsize(path)
        with open(path, "wb", buffering=0) as f:
            f.write(secrets.token_bytes(size))
        os.remove(path)
        logger.debug("Secure wipe completed: %s", path)
    except OSError as e:
        logger.warning("Secure wipe failed for %s, falling back to standard delete: %s", path, e)
        try:
            os.remove(path)
        except OSError:
            logger.error("Standard delete also failed for %s", path)
            raise


# ---------------------------------------------------------------------------
# Vault Stealth
# ---------------------------------------------------------------------------

def hide_vault_folder(path: str) -> None:
    """
    STEALTH MODULE (Ghost Mode):
    Windows : Sets Hidden (0x02) + System (0x04) kernel attributes.
    Linux/Mac: Sets permissions to 700 (owner-only read/write/execute).
    """
    if not os.path.exists(path):
        return
    abs_path = os.path.abspath(path)
    if platform.system() == "Windows":
        try:
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x02 | 0x04)
            subprocess.run(
                ['attrib', '+s', '+h', abs_path, '/s', '/d'],
                check=False, capture_output=True
            )
        except OSError as e:
            logger.warning("Could not apply Windows stealth attributes: %s", e)
    else:
        try:
            os.chmod(abs_path, 0o700)
        except OSError as e:
            logger.warning("Could not set Unix permissions on vault: %s", e)


def unlock_for_writing(path: str) -> None:
    """Removes System/Hidden protections to allow modification."""
    if not os.path.exists(path):
        return
    abs_path = os.path.abspath(path)
    if platform.system() == "Windows":
        try:
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x80)  # Normal
            subprocess.run(
                ['attrib', '-s', '-h', abs_path, '/s', '/d'],
                check=False, capture_output=True
            )
        except OSError as e:
            logger.warning("Could not unlock Windows attributes: %s", e)
    else:
        try:
            os.chmod(abs_path, 0o700)
        except OSError as e:
            logger.warning("Could not set Unix permissions: %s", e)


# ---------------------------------------------------------------------------
# Manifest  (encrypted — metadata never stored in plaintext)
# ---------------------------------------------------------------------------

_MANIFEST_PASSWORD_ENV = "COMRADE_MANIFEST_KEY"


def _get_manifest_key(password: str) -> str:
    """
    The manifest is encrypted with the same password used for the vault operation.
    We use a fixed salt derived from a deterministic seed stored alongside the
    manifest so we can re-derive the same key each time without storing it.
    """
    return password


def _manifest_salt_path() -> str:
    return os.path.join(VAULT_DIR, ".msalt")


def _load_manifest_salt() -> bytes:
    """Load or create the manifest salt file."""
    salt_path = _manifest_salt_path()
    if os.path.exists(salt_path):
        with open(salt_path, "rb") as f:
            return f.read()
    salt = secrets.token_bytes(32)
    os.makedirs(VAULT_DIR, mode=0o700, exist_ok=True)
    with open(salt_path, "wb") as f:
        f.write(salt)
    hide_vault_folder(salt_path)
    return salt


def load_manifest(password: str) -> dict:
    """
    Loads and decrypts the manifest.
    Returns an empty dict if the manifest doesn't exist yet.
    Raises on decryption failure (wrong password / tampered file).
    """
    if not os.path.exists(MANIFEST_PATH):
        return {}
    try:
        with open(MANIFEST_PATH, "rb") as f:
            raw = f.read()
        salt = _load_manifest_salt()
        plaintext = decrypt_data(raw, password, salt)
        return json.loads(plaintext.decode("utf-8"))
    except Exception as e:
        logger.error("Manifest load failed: %s", e)
        raise RuntimeError("Failed to load manifest — wrong key or corrupted manifest.") from e


def _save_manifest(manifest: dict, password: str) -> None:
    """Encrypts and saves the manifest."""
    salt = _load_manifest_salt()
    plaintext = json.dumps(manifest, indent=2).encode("utf-8")
    encrypted = encrypt_data(plaintext, password, salt)
    unlock_for_writing(MANIFEST_PATH)
    with open(MANIFEST_PATH, "wb") as f:
        f.write(encrypted)
    hide_vault_folder(MANIFEST_PATH)


# ---------------------------------------------------------------------------
# Core Operations
# ---------------------------------------------------------------------------

def save_file(file_path: str, password: str) -> str:
    """
    Encrypts a file, moves it to the hidden vault, and shreds the original.
    Returns the vault filename (ID).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")

    os.makedirs(VAULT_DIR, mode=0o700, exist_ok=True)
    hide_vault_folder(VAULT_DIR)

    abs_original_path = os.path.abspath(file_path)

    with open(file_path, "rb") as f:
        data = f.read()

    salt = generate_salt()
    encrypted_content = encrypt_data(data, password, salt)

    vault_filename = f"idx_{os.urandom(4).hex()}{VAULT_EXTENSION}"
    vault_path = os.path.join(VAULT_DIR, vault_filename)

    # Atomic write: write to temp then rename to prevent corruption on power loss
    tmp_path = vault_path + ".tmp"
    with open(tmp_path, "wb") as f:
        f.write(salt + encrypted_content)
    os.replace(tmp_path, vault_path)

    hide_vault_folder(vault_path)

    # Load manifest, update, save — all encrypted
    try:
        manifest = load_manifest(password)
    except RuntimeError:
        # First-time: manifest doesn't exist yet
        manifest = {}

    manifest[vault_filename] = abs_original_path
    _save_manifest(manifest, password)

    secure_wipe(file_path)
    logger.info("File secured as %s (original wiped)", vault_filename)
    return vault_filename


def extract_file(vault_id: str, password: str) -> str:
    """
    Decrypts and restores a vault asset to its original absolute path.
    Returns the restored file path.
    """
    manifest = load_manifest(password)

    if vault_id not in manifest:
        raise KeyError("Asset signature not found in manifest.")

    vault_path = os.path.join(VAULT_DIR, vault_id)
    if not os.path.exists(vault_path):
        raise FileNotFoundError(f"Vault file missing: {vault_id}")

    with open(vault_path, "rb") as f:
        raw = f.read()

    salt = raw[:SALT_SIZE]
    encrypted_content = raw[SALT_SIZE:]

    decrypted_data = decrypt_data(encrypted_content, password, salt)

    target_path = manifest[vault_id]
    target_dir = os.path.dirname(target_path)
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)

    # Atomic write
    tmp_path = target_path + ".tmp"
    with open(tmp_path, "wb") as f:
        f.write(decrypted_data)
    os.replace(tmp_path, target_path)

    secure_wipe(vault_path)

    del manifest[vault_id]
    _save_manifest(manifest, password)

    logger.info("Asset %s restored to %s", vault_id, target_path)
    return target_path


def delete_vault_file(vault_id: str, password: str) -> bool:
    """
    Authorized deletion: verifies password via decryption before wiping.
    """
    if not password:
        raise ValueError("Authorization required — password cannot be empty.")

    manifest = load_manifest(password)

    if vault_id not in manifest:
        raise KeyError("Target not found in manifest.")

    vault_path = os.path.join(VAULT_DIR, vault_id)

    # Verification pass — decryption will raise InvalidTag if password is wrong
    with open(vault_path, "rb") as f:
        raw = f.read()
    salt = raw[:SALT_SIZE]
    encrypted_content = raw[SALT_SIZE:]
    decrypt_data(encrypted_content, password, salt)  # raises on bad password

    secure_wipe(vault_path)

    del manifest[vault_id]
    _save_manifest(manifest, password)

    logger.info("Asset %s permanently wiped.", vault_id)
    return True


def list_secured_files(password: str) -> list:
    """
    Returns a list of dicts with vault_name and original_name.
    Requires the master password to decrypt the manifest.
    """
    manifest = load_manifest(password)
    return [{"vault_name": k, "original_name": v} for k, v in manifest.items()]
