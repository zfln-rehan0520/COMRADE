import os
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Emerald & Zinc Industry Palette
PRIMARY = Fore.GREEN 
SECONDARY = Fore.WHITE
DIM = Fore.BLACK + Style.BRIGHT
ERROR = Fore.RED

def display_banner():
    """Emerald minimalist banner - Clean & Industrial"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{PRIMARY}{Style.BRIGHT}  🛡️  COMRADE v1.0")
    print(f"{DIM}  Cyber Operations Module for Resilient Authentication and Data Encryption")
    print(f"{DIM}  {'-' * 70}")

def show_vault(files):
    """Emerald data table for secured assets"""
    if not files:
        print(f"\n{ERROR}  [!] VAULT EMPTY: No secured assets found.")
        return

    print(f"\n  {PRIMARY}{'VAULT IDENTIFIER':<30} | {'PROTECTED FILENAME':<40}")
    print(f"  {DIM}{'═' * 72}")

    for f in files:
        v_id = f['vault_name']
        orig = f['original_name']
        # White for ID, Green for the filename asset
        print(f"  {SECONDARY}{v_id:<30} {DIM}| {PRIMARY}{orig:<40}")
    
    print(f"  {DIM}{'═' * 72}")
    print(f"\n  {PRIMARY}● {SECONDARY}SYSTEM STATUS: {PRIMARY}NOMINAL / VAULT SYNCED\n")

def get_password(prompt_text="ENTER MASTER KEY: "):
    """Professional masked input prompt"""
    return input(f"  {SECONDARY}{prompt_text}{PRIMARY}")
