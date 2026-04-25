import os
from colorama import Fore, Style, init
from core.file_manager import list_secured_files # Import the data fetcher

# Initialize colorama
init(autoreset=True)

def display_banner():
    """Classic Blue Box Banner"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.CYAN}{Style.BRIGHT}╔" + "═" * 50 + "╗")
    print(f"{Fore.CYAN}{Style.BRIGHT}║ {Fore.WHITE}🛡️ COMRADE: A Brother That Guards Your Data 🛡️       {Fore.CYAN}║")
    print(f"{Fore.CYAN}{Style.BRIGHT}╚" + "═" * 50 + "╝")
    print(f"\n{Style.DIM}{Fore.WHITE}                Secured Files")

def show_vault(files=None):
    """Refined Classic Table - Now fetches data automatically if missing"""
    
    # If main.py didn't pass files, let's fetch them ourselves to prevent the crash
    if files is None:
        files = list_secured_files()

    if not files:
        print(f"\n{Fore.RED}  [!] No files found in the vault.")
        return

    # Table Header
    print(f"{Fore.WHITE}┌" + "─" * 25 + "┬" + "─" * 45 + "┐")
    print(f"{Fore.WHITE}│ {Style.BRIGHT}Vault ID                {Fore.WHITE}│ {Style.BRIGHT}Original Filename                           {Fore.WHITE}│")
    print(f"{Fore.WHITE}├" + "─" * 25 + "┼" + "─" * 45 + "┤")

    # Data Rows
    for f in files:
        vault_id = f['vault_name']
        original = f['original_name']
        # Adjusted width to match the header
        print(f"{Fore.WHITE}│ {Fore.WHITE}{vault_id:<23} {Fore.WHITE}│ {Fore.GREEN}{original:<43} {Fore.WHITE}│")

    print(f"{Fore.WHITE}└" + "─" * 25 + "┴" + "─" * 45 + "┘")
    print(f"\n{Fore.GREEN}● {Fore.WHITE}STATUS: {Fore.GREEN}ENCRYPTION ENGINE NOMINAL\n")

def get_password(prompt_text="Enter Master Password: "):
    """Classic password prompt"""
    return input(f"\n{Fore.YELLOW}{prompt_text}{Fore.CYAN}")
