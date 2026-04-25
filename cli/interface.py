import os
from colorama import Fore, Style, init
from core.file_manager import list_secured_files # Import the data fetcher

# Initialize colorama
init(autoreset=True)

from colorama import Fore, Style, init

init(autoreset=True)

def display_banner():
    """Renders the official COMRADE Cyber-Operations Branding."""
    cyan = Fore.CYAN
    white = Fore.WHITE
    dim = Style.DIM
    reset = Style.RESET_ALL

    print(f"\n{cyan}{'='*85}")
    print(f"{cyan}  ██████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ██████╗ ███████╗")
    print(f"{cyan} ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝")
    print(f"{cyan} ██║     ██║   ██║██╔████╔██║██████╔╝███████║██║  ██║█████╗  ")
    print(f"{cyan} ██║     ██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║██║  ██║██╔══╝  ")
    print(f"{cyan} ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║██████╔╝███████╗")
    print(f"{cyan}  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝")
    print(f"{cyan}{'='*85}")
    
    # Metadata Branding (Matches your GUI exactly)
    print(f"{white}  Cyber Operations Module for Resilient Authentication, Defense and Encryption")
   print(f"   {cyan}comrade-V1.0 {white}| DESIGNED BY {cyan}MOHAMMED REHAN {white}{{ Github_id :- {cyan}zfln-rehan0520 {white} }}")
    print(f"{cyan}{'='*85}\n")

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

from colorama import Fore, Style

def get_password(prompt_text="ENTER MASTER KEY: "):
    # We wrap the prompt in Fore.CYAN to match your brand
    # Then we use Style.RESET_ALL so the user's typing stays white/default
    styled_prompt = f"{Fore.CYAN}{prompt_text}{Style.RESET_ALL}"
    
    # If you are using 'maskpass' or 'getpass' for hidden typing:
    import maskpass
    return maskpass.askpass(prompt=styled_prompt, mask="*")
