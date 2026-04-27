import sys
import argparse
import os
import platform  # Added for OS detection
from colorama import Fore, init
from cli.interface import display_banner, show_vault, get_password
from core.file_manager import save_file, extract_file, delete_vault_file, list_secured_files
from core.config import VAULT_DIR

init(autoreset=True)

# Global lock to prevent deletion by keeping a file handle open
VAULT_HANDLE = None

def apply_operational_lock():
    """
    Prevents deletion while the app is running.
    Windows: Persistent handle in append mode.
    Linux/Mac: fcntl advisory lock.
    """
    global VAULT_HANDLE
    manifest_path = os.path.join(VAULT_DIR, ".vault_manifest")
    
    if os.path.exists(manifest_path):
        try:
            # Step 1: Open the handle (Cross-platform)
            VAULT_HANDLE = open(manifest_path, "a")
            
            # Step 2: Apply Unix-specific lock
            if platform.system() != "Windows":
                import fcntl
                # LOCK_EX: Exclusive lock
                # LOCK_NB: Non-blocking (don't wait if someone else has it)
                fcntl.flock(VAULT_HANDLE, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (ImportError, IOError):
            # If locking isn't supported or fails, we still allow the app to run
            pass

def release_lock():
    """Completely releases the file handle so the OS allows modifications."""
    global VAULT_HANDLE
    if VAULT_HANDLE:
        # Step 1: Explicitly unlock for Unix before closing
        if platform.system() != "Windows":
            try:
                import fcntl
                fcntl.flock(VAULT_HANDLE, fcntl.LOCK_UN)
            except:
                pass
        
        # Step 2: Close and clear handle (Windows & Unix)
        VAULT_HANDLE.close()
        VAULT_HANDLE = None

def main():
    # 1. Engage the lock immediately
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
            name = save_file(args.secure, password)
            # Re-lock in case directory/manifest was just created
            apply_operational_lock() 
            print(f"✅ Secured as: {name}")
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
            path = extract_file(args.extract, password)
            print(f"✅ Restored to: {path}")
        except Exception as e:
            print(f"❌ Denied: Invalid Key.")

    elif args.remove:
        display_banner()
        print(f"{Fore.RED}⚠️  AUTHORIZATION REQUIRED")
        password = get_password("ENTER MASTER KEY TO WIPE: ")
        if password:
            try:
                # RELEASE LOCK BEFORE WIPE (Crucial for all OS)
                release_lock()
                
                delete_vault_file(args.remove, password)
                
                # RE-ENGAGE LOCK after deletion is complete
                apply_operational_lock()
                print(f"🗑️  Asset {args.remove} erased.")
            except Exception as e:
                apply_operational_lock()
                print(f"❌ Denied: {e}")

    else:
        # Launch GUI
        try:
            from ui.app import ComradeApp
            app = ComradeApp()
            app.mainloop()
        except Exception as e:
            print(f"GUI Error: {e}")

if __name__ == "__main__":
    main()
