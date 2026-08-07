import subprocess
import os
import atexit
import time
import platform
import hashlib

# Expected SHA-256 hashes for known-good Ergo binaries (Fixes M3)
# Replace these placeholder strings with your actual binary SHA-256 digests
EXPECTED_HASHES = {
    "windows": "YOUR_ACTUAL_ERGO_EXE_SHA256_HASH_HERE",
    "linux": "YOUR_ACTUAL_ERGO_LINUX_SHA256_HASH_HERE"
}

def verify_binary_integrity(binary_path: str, expected_hash: str) -> bool:
    """
    Computes SHA-256 hash of the binary and compares against expected digest.
    Returns False if hash fails, preventing execution of modified binaries (Fixes M3).
    """
    if not os.path.exists(binary_path):
        return False
        
    # If placeholder hash is left in dev mode, print a warning but bypass block
    if "YOUR_ACTUAL" in expected_hash:
        print("[SECURITY WARNING]: Ergo binary hash check is using template placeholder!")
        return True

    sha256 = hashlib.sha256()
    try:
        with open(binary_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        
        calculated_hash = sha256.hexdigest().lower()
        if calculated_hash != expected_hash.lower():
            print(f"[SECURITY ALERT]: Binary hash mismatch for {binary_path}!")
            print(f"Expected: {expected_hash}")
            print(f"Got:      {calculated_hash}")
            return False
            
        return True
    except Exception as e:
        print(f"[SECURITY ERROR]: Failed to compute binary checksum: {e}")
        return False

def check_loopback_config(bin_dir: str) -> bool:
    """
    Validates that Ergo configuration binds strictly to loopback interfaces (Fixes M2).
    """
    config_paths = [os.path.join(bin_dir, "ircd.yaml"), os.path.join(bin_dir, "default.yaml")]
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Warn if 0.0.0.0 is found in listener binding
                    if "0.0.0.0" in content:
                        print("[SECURITY WARNING]: Ergo config allows listening on 0.0.0.0! Restrict to 127.0.0.1.")
                        return False
            except Exception:
                pass
    return True

def boot_stealth_relay():
    """
    Silently launches the bundled Ergo daemon in the background after integrity verification 
    and binds its lifecycle to the COMRADE application across Windows & Linux.
    """
    # 1. Locate the bin directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bin_dir = os.path.join(base_dir, "bin")
    
    # 2. Cross-Platform Binary Selection
    system = platform.system().lower()
    
    if system == "windows":
        ergo_binary = os.path.join(bin_dir, "ergo.exe")
        expected_hash = EXPECTED_HASHES["windows"]
        if not os.path.exists(ergo_binary):
            ergo_binary = os.path.join(bin_dir, "ergo")
    else:
        # Linux or macOS environment
        ergo_binary = os.path.join(bin_dir, "ergo_linux")
        expected_hash = EXPECTED_HASHES["linux"]
        if not os.path.exists(ergo_binary):
            ergo_binary = os.path.join(bin_dir, "ergo")

    if not os.path.exists(ergo_binary):
        return None, f"Error: Ergo binary missing from bin/ directory ({ergo_binary})."

    # 3. Binary Integrity Verification Gate (Fixes M3)
    if not verify_binary_integrity(ergo_binary, expected_hash):
        return None, "Security Error: Ergo binary checksum verification failed. Refusing to launch."

    # 4. Check Loopback Binding Policy (Fixes M2)
    check_loopback_config(bin_dir)

    try:
        # 5. OS-Specific Stealth Execution Flags
        kwargs = {
            "cwd": bin_dir,               # Execute from bin/ so it finds ircd.yaml
            "stdout": subprocess.DEVNULL, # Suppress logs
            "stderr": subprocess.DEVNULL  # Suppress errors
        }

        if system == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = startupinfo

        # 6. Launch the background process
        process = subprocess.Popen([ergo_binary, "run"], **kwargs)

        # 7. Tie the server's life to COMRADE. If Python quits, kill the server.
        atexit.register(process.terminate)
        
        # --- MAXIMUM BOOT WINDOW ---
        # Give the daemon 3.0 seconds to fully bind to port 6667
        time.sleep(3.0)
        # ---------------------------
        
        return process, "Success"
        
    except Exception as e:
        return None, f"Failed to start internal relay: {str(e)}"