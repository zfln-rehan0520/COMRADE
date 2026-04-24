from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from core.file_manager import list_secured_files

console = Console()

def display_banner():
    console.print(Panel.fit("🛡️  [bold cyan]COMRADE: ZERO-TRUST VAULT[/bold cyan] 🛡️", border_style="blue"))

def show_vault():
    files = list_secured_files()
    if not files:
        console.print("[yellow]Vault is empty.[/yellow]")
        return

    table = Table(title="Secured Files")
    table.add_column("Vault ID", style="dim")
    table.add_column("Original Filename", style="green")

    for f in files:
        table.add_row(f['vault_name'], f['original_name'])

    console.print(table)

def get_password(prompt="Enter Master Password: "):
    # In a real CLI, use getpass to hide typing
    import getpass
    return getpass.getpass(prompt)
