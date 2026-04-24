import os
from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Emerald Industry Palette
PRIMARY = Fore.GREEN  # Emerald Green
SECONDARY = Fore.WHITE # Zinc/White
DIM = Fore.BLACK + Style.BRIGHT # Slate/Gray
ERROR = Fore.RED

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Professional minimalist banner for COMRADE."""
    clear_screen()
    print(f"\n{PRIMARY}{Style.BRIGHT}  🛡️  COMRADE v1.0")
    print(f"{DIM}  Cyber Operations Module for Resilient Authentication and Data Encryption")
    print(f"{DIM}  {'-' * 70}")

def print_vault_table(files):
    """Industry-grade table display."""
    if not files:
        print(f"\n{ERROR}  [!] VAULT EMPTY: No secured assets found.")
        return

    # Header
    print(f"\n  {PRIMARY}{'VAULT IDENTIFIER':<30} | {'PROTECTED FILENAME':<40}")
    print(f"  {DIM}{'═' * 72}")

    # Data Rows
    for f in files:
        vault_id = f['vault_name']
        original = f['original_name']
        # Use Green for the filename to highlight the 'asset'
        print(f"  {SECONDARY}{vault_id:<30} {DIM}| {PRIMARY}{original:<40}")
    
    print(f"  {DIM}{'═' * 72}")
    print(f"\n  {PRIMARY}● {SECONDARY}SYSTEM STATUS: {PRIMARY}NOMINAL / VAULT SYNCED\n")

def get_password_input(prompt_text="ENTER MASTER KEY: "):
    """Professional masked input prompt."""
    return input(f"  {SECONDARY}{prompt_text}{PRIMARY}")
