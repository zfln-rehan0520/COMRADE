import sys
import argparse
from cli.interface import display_banner, show_vault, get_password
from core.file_manager import save_file

def main():
    # Setup Argument Parser for CLI mode
    parser = argparse.ArgumentParser(description="COMRADE: Secure Local Vault")
    parser.add_argument("--secure", type=str, help="Path to the file you want to encrypt")
    parser.add_argument("--list", action="store_true", help="List all files in the vault")
    
    args = parser.parse_args()

    # Case 1: User wants to secure a file via CLI
    if args.secure:
        display_banner()
        password = get_password()
        try:
            vault_name = save_file(args.secure, password)
            print(f"✅ File secured successfully as {vault_name}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Case 2: User wants to see the vault list via CLI
    elif args.list:
        display_banner()
        show_vault()

    # Case 3: No arguments provided -> Launch GUI
    else:
        try:
            from ui.app import ComradeApp
            app = ComradeApp()
            app.mainloop()
        except ImportError:
            display_banner()
            print("\n[!] GUI modules not found or ui/app.py is empty.")
            print("[!] Usage: python main.py --list OR python main.py --secure <file>")

if __name__ == "__main__":
    main()
# Add this inside your main() function in main.py
parser.add_argument("--extract", type=str, help="Vault ID to decrypt")

# Then add this logic block:
if args.extract:
    from core.file_manager import extract_file
    password = get_password()
    try:
        path = extract_file(args.extract, password)
        print(f"✅ File restored to: {path}")
    except Exception as e:
        print(f"❌ Decryption Failed: {e}")
