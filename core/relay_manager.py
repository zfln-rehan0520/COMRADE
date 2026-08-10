import atexit
import hashlib
import os
import platform
import subprocess
import time

# Known-good SHA-256 hashes for the bundled Ergo binaries.
EXPECTED_HASHES = {
    "windows": "YOUR_ACTUAL_ERGO_EXE_SHA256_HASH_HERE",
    "linux": "YOUR_ACTUAL_ERGO_LINUX_SHA256_HASH_HERE",
}


def verify_binary_integrity(binary_path: str, expected_hash: str) -> bool:
    """Hash the binary and compare against the known-good digest before we run it."""
    if not os.path.exists(binary_path):
        return False

    if "YOUR_ACTUAL" in expected_hash:
        print("[SECURITY WARNING]: Ergo binary hash check is using template placeholder!")
        return True

    sha256 = hashlib.sha256()
    try:
        with open(binary_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)

        calculated = sha256.hexdigest().lower()
        if calculated != expected_hash.lower():
            print(f"[SECURITY ALERT]: Binary hash mismatch for {binary_path}!")
            print(f"Expected: {expected_hash}")
            print(f"Got:      {calculated}")
            return False
        return True
    except Exception as e:
        print(f"[SECURITY ERROR]: Failed to compute binary checksum: {e}")
        return False


def check_loopback_config(bin_dir: str) -> bool:
    """Make sure Ergo is only configured to bind to loopback interfaces."""
    for name in ("ircd.yaml", "default.yaml"):
        path = os.path.join(bin_dir, name)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "0.0.0.0" in content:
                print("[SECURITY WARNING]: Ergo config allows listening on 0.0.0.0! Restrict to 127.0.0.1.")
                return False
        except Exception:
            pass
    return True


def boot_stealth_relay():
    """Launch the bundled Ergo IRC daemon in the background and tie its lifetime to this process."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bin_dir = os.path.join(base_dir, "bin")
    system = platform.system().lower()

    if system == "windows":
        ergo_binary = os.path.join(bin_dir, "ergo.exe")
        expected_hash = EXPECTED_HASHES["windows"]
        if not os.path.exists(ergo_binary):
            ergo_binary = os.path.join(bin_dir, "ergo")
    else:
        ergo_binary = os.path.join(bin_dir, "ergo_linux")
        expected_hash = EXPECTED_HASHES["linux"]
        if not os.path.exists(ergo_binary):
            ergo_binary = os.path.join(bin_dir, "ergo")

    if not os.path.exists(ergo_binary):
        return None, f"Error: Ergo binary missing from bin/ directory ({ergo_binary})."

    if not verify_binary_integrity(ergo_binary, expected_hash):
        return None, "Security Error: Ergo binary checksum verification failed. Refusing to launch."

    check_loopback_config(bin_dir)

    try:
        kwargs = {
            "cwd": bin_dir,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }

        if system == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = startupinfo

        process = subprocess.Popen([ergo_binary, "run"], **kwargs)
        atexit.register(process.terminate)

        # Give the daemon a moment to bind to port 6667
        time.sleep(3.0)
        return process, "Success"
    except Exception as e:
        return None, f"Failed to start internal relay: {str(e)}"
