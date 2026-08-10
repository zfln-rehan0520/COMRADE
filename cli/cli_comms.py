import os
import sys
import time
from datetime import datetime

from rich.console import Console
from rich.theme import Theme

from core.encryption import decrypt_text, encrypt_text
from core.relay_manager import boot_stealth_relay
from network.comrade_irc import ComradeComms

custom_theme = Theme({
    "sys": "bold #00D4FF",
    "error": "bold #EF4444",
    "time": "dim white",
    "me": "bold #00D4FF",
    "other": "bold #A1A1AA",
})
console = Console(theme=custom_theme)


def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")


def terminal_ui_callback(message):
    """Rewrites the current input line with formatted incoming/outgoing chat text."""
    sys.stdout.write("\r\033[K")

    time_str = f"[{get_timestamp()}]"

    if message.startswith("[System Error]"):
        console.print(f"[time]{time_str}[/time] [error]{message}[/error]")
    elif message.startswith("[System"):
        console.print(f"[time]{time_str}[/time] [sys]{message}[/sys]")
    elif message.startswith("[You]:"):
        text = message.replace("[You]:", "").strip()
        console.print(f"[time]{time_str}[/time] [me]YOU:[/me] {text}")
    else:
        parts = message.split("]:", 1)
        if len(parts) == 2:
            user = parts[0].replace("[", "").strip()
            text = parts[1].strip()
            console.print(f"[time]{time_str}[/time] [other]{user}:[/other] {text}")
        else:
            console.print(f"[time]{time_str}[/time] {message}")

    if not message.startswith("[You]:") and "[System Error]" not in message:
        console.print("[sys]MSG >[/sys] ", end="")
        sys.stdout.flush()


def boot_secure_cli():
    os.system("cls" if os.name == "nt" else "clear")

    banner = """[bold #00D4FF]
=========================================================================================
  ██████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ██████╗ ███████╗
 ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝
 ██║     ██║   ██║██╔████╔██║██████╔╝███████║██║  ██║█████╗  
 ██║     ██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║██║  ██║██╔══╝  
 ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║██████╔╝███████╗
  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝
=========================================================================================[/]
 [bold white]Cyber Operations Module for Resilient Authentication, Defense and Encryption[/]
 [bold #00D4FF]comrade-V1.10[/] [bold white]| DESIGNED BY MOHAMMED REHAN { Github_id :- zfln-rehan0520 }[/]
[bold #00D4FF]=========================================================================================[/]
"""
    console.print(banner)

    console.print(f"[[time]{get_timestamp()}[/time]] [sys]Starting secure session...[/sys]\n")
    console.print(f"[[time]{get_timestamp()}[/time]] [sys]Starting local relay...[/sys]")
    relay_process, status = boot_stealth_relay()

    if not relay_process:
        console.print(f"[[time]{get_timestamp()}[/time]] [error]Could not start local relay: {status}[/error]")
        sys.exit(1)

    room_key = console.input("[sys]Enter Room Secret Key:[/sys] ")
    nickname = console.input("[sys]Enter Operator Alias:[/sys] ")

    comms = ComradeComms(
        server="127.0.0.1",
        port=6667,
        channel="#secure",
        ui_callback=terminal_ui_callback,
        encrypt_func=encrypt_text,
        decrypt_func=decrypt_text,
    )

    console.print(f"\n[[time]{get_timestamp()}[/time]] [sys]Connecting to relay...[/sys]")
    success, conn_msg = comms.connect(secret_key=room_key, nickname=nickname)

    if not success:
        console.print(f"[[time]{get_timestamp()}[/time]] [error]Connection refused: {conn_msg}[/error]")
        sys.exit(1)

    console.print(f"[[time]{get_timestamp()}[/time]] [sys]Connected.[/sys]")
    console.print(f"[[time]{get_timestamp()}[/time]] [sys]Type '/exit' to disconnect.[/sys]\n")
    console.print("[dim]" + "━" * 60 + "[/dim]")

    time.sleep(0.5)

    try:
        while True:
            console.print("[sys]MSG >[/sys] ", end="")
            msg = input()

            if msg.strip().lower() == "/exit":
                break

            if msg.strip() and comms.running:
                comms.send_message(msg)

    except KeyboardInterrupt:
        console.print(f"\n[[time]{get_timestamp()}[/time]] [error]Interrupted.[/error]")

    comms.disconnect()
    console.print(f"\n[[time]{get_timestamp()}[/time]] [sys]Connection closed.[/sys]")
    console.print("[dim]" + "━" * 60 + "[/dim]")


if __name__ == "__main__":
    boot_secure_cli()
