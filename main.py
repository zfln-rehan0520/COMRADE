import sys
import argparse
from cli.interface import display_banner, show_vault, get_password
from core.file_manager import save_file, extract_file, delete_vault_file

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
        show_vault() 

    
    elif args.extract:
        display_banner()
        password = get_password()
        try:
            path = extract_file(args.extract, password)
            print(f"✅ File restored successfully to: {path}")
        except Exception as e:
            print(f"❌ Decryption Failed: {e}")

    
   elif args.remove:
        display_banner()
        
        # 🛡️ ADD THIS: MASTER KEY AUTHORIZATION
        print(f"{Fore.RED}⚠️  SECURITY AUTHORIZATION REQUIRED")
        auth_key = get_password("ENTER MASTER KEY TO AUTHORIZE WIPE: ")
        
        # Only proceed if they actually typed a key
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
