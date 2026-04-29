import sys
import argparse
import os
import platform
import logging
import secrets
from colorama import Fore, init
from cli.interface import display_banner, show_vault, get_password, confirm_password
from core.file_manager import save_file, extract_file, delete_vault_file, list_secured_files
from core.config import VAULT_DIR

init(autoreset=True)
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

# Global lock to prevent vault deletion while app is active
VAULT_HANDLE = None


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
            except (ImportError, IOError):
                pass
        VAULT_HANDLE.close()
        VAULT_HANDLE = None


def main():
    apply_operational_lock()
    parser = argparse.ArgumentParser(description="COMRADE: Secure Local Vault")
    parser.add_argument("--secure",  type=str,          help="Path to file to encrypt")
    parser.add_argument("--list",    action="store_true", help="List vault contents")
    parser.add_argument("--extract", type=str,           help="Vault ID to extract")
    parser.add_argument("--remove",  type=str,           help="Vault ID to permanently wipe")
    args = parser.parse_args()

    if args.secure:
        display_banner()
        password = get_password("CREATE MASTER KEY: ")
        confirmed = confirm_password("CONFIRM MASTER KEY: ")
        if password != confirmed:
            print(f"{Fore.RED}❌ Keys do not match. Operation aborted.")
            sys.exit(1)
        try:
            name = save_file(args.secure, password)
            apply_operational_lock()
            print(f"{Fore.GREEN}✅ Secured as: {name} (Original wiped)")
        except FileNotFoundError as e:
            print(f"{Fore.RED}❌ File not found: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}")
            sys.exit(1)

    elif args.list:
        display_banner()
        password = get_password("ENTER MASTER KEY: ")
        try:
            files = list_secured_files(password)
            if not files:
                print(f"{Fore.YELLOW}[!] Vault is empty.")
            else:
                show_vault(files)
        except RuntimeError:
            print(f"{Fore.RED}❌ Denied: Invalid key or corrupted manifest.")
            sys.exit(1)

    elif args.extract:
        display_banner()
        password = get_password("ENTER MASTER KEY: ")
        try:
            path = extract_file(args.extract, password)
            release_lock()
            apply_operational_lock()
            print(f"{Fore.GREEN}✅ Restored to: {path}")
            print(f"{Fore.GREEN}🛡️  Vault entry cleared. No encrypted trace remains.")
        except (KeyError, FileNotFoundError) as e:
            print(f"{Fore.RED}❌ Asset not found: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}❌ Denied: Invalid key.")
            sys.exit(1)

    elif args.remove:
        display_banner()
        print(f"{Fore.RED}⚠️  AUTHORIZATION REQUIRED")
        password = get_password("ENTER MASTER KEY TO WIPE: ")
        if password:
            try:
                release_lock()
                delete_vault_file(args.remove, password)
                apply_operational_lock()
                print(f"{Fore.GREEN}🗑️  Asset {args.remove} permanently erased.")
            except (KeyError, ValueError) as e:
                apply_operational_lock()
                print(f"{Fore.RED}❌ Denied: {e}")
                sys.exit(1)
            except Exception as e:
                apply_operational_lock()
                print(f"{Fore.RED}❌ Error: {e}")
                sys.exit(1)

    else:
        try:
            from ui.app import ComradeApp
            app = ComradeApp()
            app.mainloop()
        except ImportError as e:
            print(f"{Fore.RED}GUI Error: missing dependency — {e}")
            print(f"{Fore.YELLOW}Try: sudo apt install python3-tk")
        except Exception as e:
            print(f"{Fore.RED}GUI Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
