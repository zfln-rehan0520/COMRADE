import sys
import argparse
from colorama import Fore, init
from cli.interface import display_banner, show_vault, get_password
from core.file_manager import save_file, extract_file, delete_vault_file, list_secured_files

init(autoreset=True)

def main():
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
            print(f"✅ Secured as: {name}")
        except Exception as e:
            print(f"❌ Error: {e}")

    elif args.list:
        display_banner()
        files = list_secured_files() # No password needed for listing
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
                delete_vault_file(args.remove, password)
                print(f"🗑️  Asset {args.remove} erased.")
            except Exception as e:
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
