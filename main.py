import sys
import argparse
from colorama import Fore, init  # Added this for the red color to work
from cli.interface import display_banner, show_vault, get_password
from core.file_manager import save_file, extract_file, delete_vault_file

# Initialize colorama for Windows terminals
init(autoreset=True)

def main():
    parser = argparse.ArgumentParser(description="COMRADE: Secure Local Vault")
    
    # CLI Arguments
    parser.add_argument("--secure", type=str, help="Path to the file you want to encrypt")
    parser.add_argument("--list", action="store_true", help="List all files in the vault")
    parser.add_argument("--extract", type=str, help="Vault ID to decrypt")
    parser.add_argument("--remove", type=str, help="Delete a file from the vault using its ID")
    
    args = parser.parse_args()

    if args.secure:
        display_banner()
        password = get_password()
        try:
            vault_name = save_file(args.secure, password)
            print(f"✅ File secured successfully as: {vault_name}")
        except Exception as e:
            print(f"❌ Error: {e}")

    elif args.list:
        display_banner()
        # Since we implemented Encrypted Manifest (Option 1), 
        # let's ask for the key before showing the list
        password = get_password("ENTER MASTER KEY TO VIEW VAULT: ")
        from core.file_manager import load_manifest
        files_dict = load_manifest(password)
        files_list = [{"vault_name": k, "original_name": v} for k, v in files_dict.items()]
        
        if not files_list:
            print(f"{Fore.RED}[!] Access Denied or Vault Empty.")
        else:
            show_vault(files_list)

    elif args.extract:
        display_banner()
        password = get_password()
        try:
            path = extract_file(args.extract, password)
            print(f"✅ File restored successfully to: {path}")
        except Exception as e:
            print(f"❌ Decryption Failed: {e}")

    elif args.remove: # Fixed the spacing here (Exactly 4 spaces)
        display_banner()
        
        print(f"{Fore.RED}⚠️  SECURITY AUTHORIZATION REQUIRED")
        auth_key = get_password("ENTER MASTER KEY TO AUTHORIZE WIPE: ")
        
        if auth_key:
            confirm = input(f"Are you sure you want to delete {args.remove}? (y/n): ")
            if confirm.lower() == 'y':
                try:
                    delete_vault_file(args.remove)
                    print(f"🗑️  Asset {args.remove} has been permanently erased.")
                except Exception as e:
                    print(f"❌ Deletion Failed: {e}")
        else:
            print(f"{Fore.YELLOW}❌ Deletion cancelled: No key provided.")

    else:
        try:
            from ui.app import ComradeApp
            app = ComradeApp()
            app.mainloop()
        except Exception as e:
            display_banner()
            print(f"\n[!] GUI could not start: {e}")
            print("[!] Usage: --list, --secure <file>, --extract <id>, or --remove <id>")

if __name__ == "__main__":
    main()
