import os
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def display_banner():
    """Restored classic boxed blue banner"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "╔" + "═" * 45 + "╗")
    print(f"{Fore.CYAN}{Style.BRIGHT}║ {Fore.WHITE}       🛡️  COMRADE: ZERO-TRUST VAULT 🛡️       {Fore.CYAN}║")
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "╚" + "═" * 45 + "╝")
    print(f"\n{Style.DIM}{Fore.WHITE}                Secured Files")

def show_vault(files):
    """Restored original classic table layout"""
    if not files:
        print(f"\n{Fore.RED}  [!] No files found in the vault.")
        return

    # Table Header
    print(f"{Fore.WHITE}┌" + "─" * 25 + "┬" + "─" * 35 + "┐")
    print(f"{Fore.WHITE}│ {Style.BRIGHT}Vault ID                {Fore.WHITE}│ {Style.BRIGHT}Original Filename                 {Fore.WHITE}│")
    print(f"{Fore.WHITE}├" + "─" * 25 + "┼" + "─" * 35 + "┤")

    # Data Rows
    for f in files:
        vault_id = f['vault_name']
        original = f['original_name']
        print(f"{Fore.WHITE}│ {Fore.WHITE}{vault_id:<23} {Fore.WHITE}│ {Fore.GREEN}{original:<33} {Fore.WHITE}│")

    print(f"{Fore.WHITE}└" + "─" * 25 + "┴" + "─" * 35 + "┘")
    print(f"\n{Fore.GREEN}(venv) {Fore.WHITE}PS C:\\Users\\pc\\COMRADE>")

def get_password(prompt_text="Enter Master Password: "):
    """Original password prompt"""
    return input(f"\n{Fore.YELLOW}{prompt_text}{Fore.CYAN}")
