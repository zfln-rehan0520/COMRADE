import os
from colorama import Fore, Style, init

# Initialize colors for professional output
init(autoreset=True)

# Emerald Industry Palette
PRIMARY = Fore.GREEN 
SECONDARY = Fore.WHITE
DIM = Fore.BLACK + Style.BRIGHT

def display_banner():
    """Emerald minimalist banner - Matched to main.py"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{PRIMARY}{Style.BRIGHT}  🛡️  COMRADE v1.0")
    print(f"{DIM}  Cyber Operations Module for Resilient Authentication and Data Encryption")
    print(f"{DIM}  {'-' * 70}")

def show_vault(files):
    """Emerald data table - Matched to main.py"""
    if not files:
        print(f"\n{Fore.RED}  [!] VAULT EMPTY: No secured assets found.")
        return

    print(f"\n  {PRIMARY}{'VAULT IDENTIFIER':<30} | {'PROTECTED FILENAME':<40}")
    print(f"  {DIM}{'═' * 72}")

    for f in files:
        v_id = f['vault_name']
        orig = f['original_name']
        print(f"  {SECONDARY}{v_id:<30} {DIM}| {PRIMARY}{orig:<40}")
    
    print(f"  {DIM}{'═' * 72}")
    print(f"\n  {PRIMARY}● {SECONDARY}SYSTEM STATUS: {PRIMARY}NOMINAL / VAULT SYNCED\n")

def get_password(prompt_text="ENTER MASTER KEY: "):
    """Emerald input prompt - Matched to main.py"""
    return input(f"  {SECONDARY}{prompt_text}{PRIMARY}")
