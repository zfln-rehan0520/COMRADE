import sys
import argparse
from cli.interface import display_banner, show_vault, get_password
from core.file_manager import save_file, extract_file

def main():
    parser = argparse.ArgumentParser(description="COMRADE: Secure Local Vault")
    parser.add_argument("--secure", type=str, help="Path to the file you want to encrypt")
    parser.add_argument("--list", action="store_true", help="List all files in the vault")
    parser.add_argument("--extract", type=str, help="Vault ID to decrypt")
    
    args = parser.parse_args()

    if args.secure:
        display_banner()
        password = get_password()
        try:
            vault_name = save_file(args.secure, password)
            print(f"✅ File secured successfully as {vault_name}")
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

    else:
        try:
            from ui.app import ComradeApp
            app = ComradeApp()
            app.mainloop()
        except Exception:
            display_banner()
            print("\n[!] Use --list, --secure <file>, or --extract <id>")

if __name__ == "__main__":
    main()
