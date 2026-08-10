import getpass
import json
import os
import platform
import secrets
import shutil
import socket
import string
import sys
import threading
import time
import tkinter as tk

from colorama import Fore, init

from ai.engine import ComradeAI
from cli.interface import display_banner, get_password, show_vault
from core.config import VAULT_DIR
from core.credentials import decrypt_individual_pass, encrypt_individual_pass, load_credentials, save_credentials
from core.file_manager import delete_vault_file, extract_file, list_secured_files, save_file
from core.relay_manager import boot_stealth_relay

init(autoreset=True)

vault_handle = None


def secure_wipe(file_path):
    """Overwrites the file in place with random bytes before deleting it."""
    if not os.path.exists(file_path):
        return
    try:
        size = os.path.getsize(file_path)
        if size > 0:
            with open(file_path, "r+b", buffering=0) as f:
                f.write(secrets.token_bytes(size))
        os.remove(file_path)
    except Exception:
        try:
            os.remove(file_path)
        except Exception:
            pass


def apply_operational_lock():
    """Grabs an exclusive lock on the vault manifest so two instances can't race."""
    global vault_handle
    manifest_path = os.path.join(VAULT_DIR, ".vault_manifest")
    if not os.path.exists(manifest_path):
        return
    try:
        vault_handle = open(manifest_path, "a")
        if platform.system() != "Windows":
            import fcntl
            fcntl.flock(vault_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (ImportError, IOError):
        pass


def release_lock():
    global vault_handle
    if not vault_handle:
        return
    if platform.system() != "Windows":
        try:
            import fcntl
            fcntl.flock(vault_handle, fcntl.LOCK_UN)
        except Exception:
            pass
    try:
        vault_handle.close()
    except Exception:
        pass
    vault_handle = None


def stream_response(text, delay=0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def launch_gui():
    try:
        display_banner()
        print(f"{Fore.CYAN}[SYSTEM]: Starting local relay...")
        relay_process, status = boot_stealth_relay()

        if not relay_process:
            print(f"{Fore.YELLOW}[SYSTEM WARNING]: Secure relay failed to start -> {status}")
        else:
            print(f"{Fore.GREEN}[SYSTEM]: Relay online.")

        from ui.app import ComradeApp
        app = ComradeApp()
        app.mainloop()
    except Exception as e:
        print(f"{Fore.RED}GUI Fatal Error: {e}")


def launch_securepass():
    """Terminal front-end for the credential vault."""
    display_banner()
    print(f"{Fore.CYAN}🔐 Accessing Secure Local Credential Vault...")
    try:
        creds = load_credentials()

        if not creds:
            print(f"{Fore.YELLOW}[!] Credential database is currently empty.")
        else:
            print(f"\n{Fore.CYAN}=== SECURED ACCOUNTS AVAILABLE ===")
            accounts = sorted(creds.keys())
            for idx, account in enumerate(accounts, 1):
                print(f" {Fore.WHITE}[{idx}] {account}")
            print(f"{Fore.CYAN}==================================")

        prompt_text = f"\n{Fore.YELLOW}Enter item number, [A]dd, [D]elete, [B]ackup, [R]estore, or [C]ancel: {Fore.WHITE}"
        choice = input(prompt_text).strip()

        if choice.lower() == "c" or not choice:
            return

        elif choice.lower() == "a":
            print(f"\n{Fore.CYAN}--- ADD CREDENTIAL ---")
            acc = input(f"{Fore.WHITE}Account / Service Label: ").strip()
            if not acc:
                print(f"{Fore.RED}❌ Aborted. Label required.")
                return

            item_key = getpass.getpass(f"{Fore.YELLOW}Dedicated Encryption Key (Hidden): {Fore.WHITE}")
            if not item_key:
                print(f"{Fore.RED}❌ Aborted. Encryption key required.")
                return

            gen_choice = input(f"{Fore.WHITE}Type [G] to auto-generate a password, or hit Enter to type your own: ").strip()

            if gen_choice.lower() == "g":
                alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
                while True:
                    pwd = "".join(secrets.choice(alphabet) for _ in range(20))
                    if (any(c.islower() for c in pwd) and any(c.isupper() for c in pwd)
                            and sum(c.isdigit() for c in pwd) >= 2 and any(c in "!@#$%^&*-_=+" for c in pwd)):
                        break
                print(f"{Fore.GREEN}⚡ Generated a strong password.")
            else:
                pwd = getpass.getpass(f"{Fore.WHITE}Enter Password (Hidden): ")

            enc = encrypt_individual_pass(pwd, item_key)
            if not enc:
                print(f"{Fore.RED}❌ Encryption failed.")
                return

            creds[acc] = enc
            if save_credentials(creds):
                print(f"\n{Fore.GREEN}✅ [{acc}] encrypted and saved to vault.")
            else:
                print(f"\n{Fore.RED}❌ Failed to write to disk.")
            return

        elif choice.lower() == "d":
            print(f"\n{Fore.RED}--- DELETE CREDENTIAL ---")
            del_choice = input(f"{Fore.WHITE}Enter the item number to delete: ").strip()
            try:
                idx = int(del_choice) - 1
                accounts = sorted(creds.keys())
                if 0 <= idx < len(accounts):
                    target = accounts[idx]
                    encrypted = creds[target]

                    item_key = getpass.getpass(f"{Fore.YELLOW}Verify dedicated key for [{target}]: {Fore.WHITE}")
                    plain = decrypt_individual_pass(encrypted, item_key)

                    if not plain:
                        print(f"{Fore.RED}❌ Access denied. Wrong key.")
                        return

                    confirm = input(f"{Fore.RED}Permanently delete [{target}]? (y/n): {Fore.WHITE}").strip()
                    if confirm.lower() == "y":
                        del creds[target]
                        if save_credentials(creds):
                            print(f"\n{Fore.GREEN}✅ [{target}] deleted.")
                        else:
                            print(f"\n{Fore.RED}❌ Failed to save changes.")
                    else:
                        print(f"\n{Fore.YELLOW}Deletion cancelled.")
                else:
                    print(f"{Fore.RED}❌ That item number doesn't exist.")
            except ValueError:
                print(f"{Fore.RED}❌ Invalid input.")
            return

        elif choice.lower() == "b":
            print(f"\n{Fore.CYAN}--- BACKUP VAULT ---")
            dest_path = input(f"{Fore.WHITE}Enter destination directory path (e.g., D:\\Backups): ").strip()
            if not os.path.exists(dest_path):
                print(f"{Fore.RED}❌ Path does not exist. Aborting.")
                return

            backup_file = os.path.join(dest_path, "comrade_backup.json")
            try:
                shutil.copy(".comrade_credentials.json", backup_file)
                print(f"\n{Fore.GREEN}✅ Backed up to:\n{backup_file}")
            except Exception as e:
                print(f"\n{Fore.RED}❌ Backup failed: {e}")
            return

        elif choice.lower() == "r":
            print(f"\n{Fore.CYAN}--- RESTORE VAULT ---")
            src_path = input(f"{Fore.WHITE}Enter full path to backup file: ").strip()
            if not os.path.exists(src_path) or not src_path.endswith(".json"):
                print(f"{Fore.RED}❌ Invalid file or path. Aborting.")
                return

            try:
                with open(src_path, "r") as f:
                    imported = json.load(f)

                creds.update(imported)
                if save_credentials(creds):
                    print(f"\n{Fore.GREEN}✅ Restore complete.")
                else:
                    print(f"\n{Fore.RED}❌ Could not save merged data.")
            except Exception as e:
                print(f"\n{Fore.RED}❌ Restore failed: {e}")
            return

        else:
            try:
                idx = int(choice) - 1
                accounts = sorted(creds.keys())
                if 0 <= idx < len(accounts):
                    target = accounts[idx]
                    encrypted = creds[target]

                    item_key = getpass.getpass(f"{Fore.CYAN}Enter dedicated encryption key for [{target}]: {Fore.WHITE}")
                    plain = decrypt_individual_pass(encrypted, item_key)

                    if not plain:
                        print(f"{Fore.RED}❌ Access denied. Wrong key.")
                        return

                    r = tk.Tk()
                    r.withdraw()
                    r.clipboard_clear()
                    r.clipboard_append(plain)
                    r.update()

                    print(f"\n{Fore.GREEN}✅ Password for {target} copied to clipboard.")
                    print(f"{Fore.RED}⚠️ Clipboard will clear in 10 seconds.")

                    time.sleep(10)
                    r.clipboard_clear()
                    r.clipboard_append("")
                    r.update()
                    r.destroy()
                    print(f"{Fore.GREEN}🛡️ Clipboard cleared.")
                else:
                    print(f"{Fore.RED}❌ That item number doesn't exist.")
            except ValueError:
                print(f"{Fore.RED}❌ Invalid input.")
    except Exception as e:
        print(f"{Fore.RED}❌ Something went wrong -> {e}")


def launch_ai():
    display_banner()
    print(f"{Fore.CYAN}🤖 COMRADE AI [OFFLINE & LOCAL]")
    print(f"{Fore.YELLOW}Type 'exit' or 'quit' to end the session.\n")

    ai_engine = ComradeAI()
    system_prompt = "You are COMRADE, an advanced cyber-operations AI. Keep answers concise, tactical, and highly technical."

    while True:
        try:
            user_input = input(f"{Fore.CYAN}YOU: {Fore.WHITE}")

            if user_input.lower() in ["exit", "quit"]:
                ai_engine.wipe_memory()
                print(f"{Fore.CYAN}Ending session and clearing memory...{Fore.RESET}")
                break

            sys.stdout.write(f"{Fore.CYAN}Thinking...{Fore.RESET}")
            sys.stdout.flush()

            response = ai_engine.ask(user_input, system_context=system_prompt)

            sys.stdout.write("\r" + " " * 20 + "\r")
            sys.stdout.flush()

            print(f"{Fore.GREEN}COMRADE: {Fore.WHITE}", end="")
            stream_response(response)
            print(f"\n{Fore.CYAN}" + "─" * 60 + "\n")

        except KeyboardInterrupt:
            ai_engine.wipe_memory()
            print(f"\n{Fore.CYAN}Session aborted. Memory cleared.{Fore.RESET}")
            break


def launch_chat():
    display_banner()
    print(f"{Fore.CYAN}📡 COMRADE Relay Chat [PORT 6667]")

    nick = input(f"{Fore.YELLOW}Enter Operator Nickname: {Fore.WHITE}").strip()
    if not nick:
        nick = f"Operator_{secrets.token_hex(2)}"

    channel = input(f"{Fore.YELLOW}Enter Secure Channel [#secure]: {Fore.WHITE}").strip()
    if not channel:
        channel = "#secure"
    if not channel.startswith("#"):
        channel = f"#{channel}"

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 6667))

        client.sendall(f"NICK {nick}\r\n".encode("utf-8"))
        client.sendall(f"USER {nick} 0 * :{nick}\r\n".encode("utf-8"))
        client.sendall(f"JOIN {channel}\r\n".encode("utf-8"))

        print(f"{Fore.GREEN}✅ Connected to Relay. Joined {channel} as {nick}.")
        print(f"{Fore.YELLOW}Type your message and press ENTER. Type 'exit' to disconnect.\n")

        stop_event = threading.Event()

        def receive_loop():
            while not stop_event.is_set():
                try:
                    data = client.recv(2048).decode("utf-8", errors="ignore")
                    if not data:
                        break
                    for line in data.split("\r\n"):
                        if line.startswith("PING"):
                            client.sendall(f"PONG {line.split()[1]}\r\n".encode("utf-8"))
                        elif "PRIVMSG" in line:
                            parts = line.split(" PRIVMSG ")
                            sender = parts[0].split("!")[0][1:]
                            msg = parts[1].split(" :", 1)[1]
                            if sender != nick:
                                print(f"\n{Fore.GREEN}[{channel}] {sender}: {Fore.WHITE}{msg}")
                                sys.stdout.write(f"{Fore.CYAN}[{nick}] > {Fore.WHITE}")
                                sys.stdout.flush()
                except Exception:
                    break

        t = threading.Thread(target=receive_loop, daemon=True)
        t.start()

        while True:
            msg = input(f"{Fore.CYAN}[{nick}] > {Fore.WHITE}")
            if msg.lower() in ["exit", "quit", "/quit"]:
                stop_event.set()
                client.sendall(b"QUIT :Disconnecting\r\n")
                client.close()
                print(f"{Fore.YELLOW}Disconnected from relay.")
                break
            if msg.strip():
                client.sendall(f"PRIVMSG {channel} :{msg}\r\n".encode("utf-8"))

    except Exception as e:
        print(f"{Fore.RED}❌ Relay Connection Failed -> {e}")
        print(f"{Fore.YELLOW}Ensure Ergo daemon is running: .\\ergo.exe run")


def run_audit():
    try:
        import audit
        print(f"{Fore.CYAN}[+] Running security audit...")
        if hasattr(audit, "main"):
            audit.main()
    except ImportError:
        print(f"{Fore.RED}❌ Error: audit module not found.")


def main():
    apply_operational_lock()

    args = sys.argv[1:]

    if not args:
        launch_gui()
        return

    command = args[0].lower()

    if command == "gui":
        launch_gui()

    elif command == "ai":
        launch_ai()

    elif command == "securepass":
        launch_securepass()

    elif command == "chat":
        launch_chat()

    elif command == "audit":
        run_audit()

    elif command == "run":
        if len(args) < 2:
            display_banner()
            print(f"{Fore.RED}❌ 'run' needs a subsystem target.")
            print(f"{Fore.YELLOW}Valid targets: {Fore.WHITE}gui, ai, securepass, chat")
            return

        subsystem = args[1].lower()
        if subsystem == "gui":
            launch_gui()
        elif subsystem == "securepass":
            launch_securepass()
        elif subsystem == "ai":
            launch_ai()
        elif subsystem == "chat":
            launch_chat()
        else:
            display_banner()
            print(f"{Fore.RED}❌ Unknown subsystem: {subsystem}")
            print(f"{Fore.YELLOW}Valid targets: {Fore.WHITE}gui, ai, securepass, chat")

    elif command == "secure":
        if len(args) < 2:
            display_banner()
            print(f"{Fore.RED}❌ File path required. Example: comrade secure document.pdf")
            return

        display_banner()
        password = get_password("CREATE MASTER KEY FOR THIS ASSET: ")
        try:
            original_path = args[1]
            name = save_file(original_path, password)
            secure_wipe(original_path)
            apply_operational_lock()
            print(f"\n{Fore.GREEN}✅ Secured as: {name} {Fore.WHITE}(original file wiped)")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}")

    elif command == "list":
        display_banner()
        files = list_secured_files()
        if not files:
            print(f"{Fore.YELLOW}[!] Vault is empty.")
        else:
            show_vault(files)

    elif command == "extract":
        if len(args) < 2:
            display_banner()
            print(f"{Fore.RED}❌ Vault ID required. Example: comrade extract a1b2c3d4")
            return

        display_banner()
        password = get_password("ENTER MASTER KEY TO UNLOCK ASSET: ")
        try:
            path = extract_file(args[1], password)
        except Exception:
            print(f"{Fore.RED}❌ Denied: Invalid Key.")
            return

        print(f"{Fore.CYAN}🧹 Cleaning up vault residue...")
        try:
            release_lock()
            delete_vault_file(args[1], password)
            apply_operational_lock()
        except Exception as cleanup_error:
            apply_operational_lock()
            print(f"{Fore.YELLOW}[!] Cleanup warning: could not remove vault entry cleanly ({cleanup_error})")

        print(f"\n{Fore.GREEN}✅ Restored to: {path}")

    elif command == "remove":
        if len(args) < 2:
            display_banner()
            print(f"{Fore.RED}❌ Vault ID required.")
            return

        display_banner()
        print(f"{Fore.RED}⚠️ AUTHORIZATION REQUIRED")
        password = get_password("ENTER MASTER KEY TO AUTHORIZE WIPE: ")
        if password:
            try:
                release_lock()
                delete_vault_file(args[1], password)
                apply_operational_lock()
                print(f"\n{Fore.GREEN}🗑️ Asset {args[1]} permanently erased.")
            except Exception as e:
                apply_operational_lock()
                print(f"\n{Fore.RED}❌ Denied: {e}")

    else:
        display_banner()
        print(f"{Fore.RED}❌ Unrecognized command: '{command}'")
        print(f"\n{Fore.YELLOW}Available commands:")
        print(f"  {Fore.WHITE}comrade gui | ai | securepass | chat | audit")
        print(f"  {Fore.WHITE}comrade list")
        print(f"  {Fore.WHITE}comrade secure <file_path>")
        print(f"  {Fore.WHITE}comrade extract <vault_id>")
        print(f"  {Fore.WHITE}comrade remove <vault_id>")


if __name__ == "__main__":
    main()
