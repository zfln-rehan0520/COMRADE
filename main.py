import sys
import argparse
from cli.interface import display_banner, show_vault, get_password
from core.file_manager import save_file, extract_file # Added extract_file here

def main():
    # Setup Argument Parser
    parser = argparse.ArgumentParser(description="COMRADE: Secure Local Vault")
    parser.add_argument("--secure", type=str, help="Path to the file you want to encrypt")
    parser.add_argument("--list", action="store_true", help="List all files in the vault")
    parser.add_argument("--extract", type=str, help="Vault ID to decrypt (e.g., 9168bcc...)")
    
    args = parser.parse_args()

    # Case 1: Secure/Encrypt
    if args.secure:
        display_banner()
        password = get_password()
        try:
            vault_name = save_file(args.secure, password)
            print(f"✅ File secured successfully as {vault_name}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Case 2: List Vault Content
    elif args.list:
        display_banner()
        show_vault()

    # Case 3: Extract/Decrypt
    elif args.extract:
        display_banner()
        password = get_password()
        try:
            path = extract_file(args.extract, password)
            print(f"✅ File restored successfully to: {path}")
        except Exception as e:
            print(f"❌ Decryption Failed: {e}")

    # Case 4: Launch GUI
    else:
        try:
            from ui.app import ComradeApp
            app = ComradeApp()
            app.mainloop()
        except Exception as e:
            display_banner()
            print(f"\n[!] GUI failed to launch: {e}")
            print("[!] Usage: python main.py --list | --secure <file> | --extract <id>")

if __name__ == "__main__":
    main()
