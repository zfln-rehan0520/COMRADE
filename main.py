import sys
import argparse
import os
import platform
import secrets  # Added for secure wiping
from colorama import Fore, init
from cli.interface import display_banner, show_vault, get_password
from core.file_manager import save_file, extract_file, delete_vault_file, list_secured_files
from core.config import VAULT_DIR

init(autoreset=True)

# Global lock to prevent deletion by keeping a file handle open
VAULT_HANDLE = None

def secure_wipe(file_path):
    """Overwrites file with random data before deleting to prevent recovery."""
    if os.path.exists(file_path):
        try:
            size = os.path.getsize(file_path)
            with open(file_path, "ba+", buffering=0) as f:
                f.write(secrets.token_bytes(size))
            os.remove(file_path)
        except:
            os.remove(file_path)  # Fallback to standard delete if wipe fails

def apply_operational_lock():
    global VAULT_HANDLE
    manifest_path = os.path.join(VAULT_DIR, ".vault_manifest")
    if os.path.exists(manifest_path):
        try:
            VAULT_HANDLE = open(manifest_path, "a")
            if platform.system() != "Windows":
                import fcntl
                fcntl.flock(VAULT_HANDLE, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (ImportError, IOError):
            pass

def release_lock():
    global VAULT_HANDLE
    if VAULT_HANDLE:
        if platform.system() != "Windows":
            try:
                import fcntl
                fcntl.flock(VAULT_HANDLE, fcntl.LOCK_UN)
            except:
                pass
        VAULT_HANDLE.close()
        VAULT_HANDLE = None

def main():
    apply_operational_lock()
    parser = argparse.ArgumentParser(description="COMRADE: Secure Local Vault")
    parser.add_argument("--secure", type=str, help="Path to file")
    parser.add_argument("--list", action="store_true", help="List vault")
    parser.add_argument("--extract", type=str, help="Vault ID")
    parser.add_argument("--remove", type=str, help="Vault ID to delete")
    args = parser.parse_args()

    if args.secure:
        display_banner()
        password = get_password("CREATE MASTER KEY: ")
        try:
            original_path = args.secure
            name = save_file(original_path, password)
            
            # --- THE FIX: Wipe original after securing ---
            secure_wipe(original_path)
            
            apply_operational_lock() 
            print(f"✅ Secured as: {name} (Original Wiped)")
        except Exception as e:
            print(f"❌ Error: {e}")

    elif args.list:
        display_banner()
        files = list_secured_files()
        if not files:
            print(f"{Fore.YELLOW}[!] Vault is empty.")
        else:
            show_vault(files)

    elif args.extract:
        display_banner()
        password = get_password("ENTER MASTER KEY: ")
        try:
            # 1. Restore the file to the user
            path = extract_file(args.extract, password)
            
            # --- THE FIX: Wipe vault copy after extraction ---
            print(f"{Fore.CYAN}🧹 Finalizing extraction: Shredding vault residue...")
            release_lock()  # Release lock to allow vault modification
            delete_vault_file(args.extract, password)
            apply_operational_lock() # Re-engage lock
            # ------------------------------------------------
            
            print(f"✅ Restored to: {path}")
            print(f"{Fore.GREEN}🛡️ Vault entry cleared. No encrypted trace remains.")
        except Exception as e:
            print(f"❌ Denied: Invalid Key.")

    elif args.remove:
        display_banner()
        print(f"{Fore.RED}⚠️  AUTHORIZATION REQUIRED")
        password = get_password("ENTER MASTER KEY TO WIPE: ")
        if password:
            try:
                release_lock()
                delete_vault_file(args.remove, password)
                apply_operational_lock()
                print(f"🗑️  Asset {args.remove} erased.")
            except Exception as e:
                apply_operational_lock()
                print(f"❌ Denied: {e}")

    else:
        try:
            from ui.app import ComradeApp
            app = ComradeApp()
            app.mainloop()
        except Exception as e:
            print(f"GUI Error: {e}")

if __name__ == "__main__":
    main()
