import os
from colorama import Fore, Style, init

init(autoreset=True)


def display_banner():
    """Renders the official COMRADE Cyber-Operations branding."""
    cyan = Fore.CYAN
    white = Fore.WHITE

    print(f"\n{cyan}{'='*85}")
    print(f"{cyan}   ██████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ██████╗ ███████╗")
    print(f"{cyan}  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝")
    print(f"{cyan}  ██║     ██║   ██║██╔████╔██║██████╔╝███████║██║  ██║█████╗  ")
    print(f"{cyan}  ██║     ██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║██║  ██║██╔══╝  ")
    print(f"{cyan}  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║██████╔╝███████╗")
    print(f"{cyan}   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝")
    print(f"{cyan}{'='*85}")

    print(f"{white}   Cyber Operations Module for Resilient Authentication, Defense and Encryption")
    print(f"   {cyan}comrade-V1.10 {white}| DESIGNED BY {cyan}MOHAMMED REHAN {white}{{ Github_id :- {cyan}zfln-rehan0520 {white}}}")
    print(f"{cyan}{'='*85}\n")


def show_vault(files: list) -> None:
    """Renders a formatted table of secured vault assets."""
    if not files:
        print(f"\n{Fore.RED}  [!] No files found in the vault.")
        return

    print(f"{Fore.WHITE}┌" + "─" * 25 + "┬" + "─" * 45 + "┐")
    print(f"{Fore.WHITE}│ {Style.BRIGHT}Vault ID                {Fore.WHITE}│ {Style.BRIGHT}Original Path                               {Fore.WHITE}│")
    print(f"{Fore.WHITE}├" + "─" * 25 + "┼" + "─" * 45 + "┤")

    for f in files:
        vault_id   = f['vault_name']
        original   = f['original_name']
        # Truncate long paths for display
        display    = original if len(original) <= 43 else "…" + original[-42:]
        print(f"{Fore.WHITE}│ {Fore.WHITE}{vault_id:<23} {Fore.WHITE}│ {Fore.GREEN}{display:<43} {Fore.WHITE}│")

    print(f"{Fore.WHITE}└" + "─" * 25 + "┴" + "─" * 45 + "┘")
    print(f"\n{Fore.GREEN}● {Fore.WHITE}STATUS: {Fore.GREEN}ENCRYPTION ENGINE NOMINAL\n")


def get_password(prompt_text: str = "ENTER MASTER KEY: ") -> str:
    """Prompts for a password with masked input."""
    styled_prompt = f"{Fore.CYAN}{prompt_text}{Style.RESET_ALL}"
    try:
        import maskpass
        return maskpass.askpass(prompt=styled_prompt, mask="*")
    except ImportError:
        import getpass
        return getpass.getpass(prompt=styled_prompt)


def confirm_password(prompt_text: str = "CONFIRM MASTER KEY: ") -> str:
    """Secondary password prompt for confirmation (used during encryption)."""
    return get_password(prompt_text)
