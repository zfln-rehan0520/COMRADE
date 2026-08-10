import json
import secrets
import string

import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.credentials import decrypt_individual_pass, encrypt_individual_pass, load_credentials, save_credentials

BG_MAIN = "#09090B"
BG_SURFACE = "#18181B"
BG_SURFACE_LIGHT = "#27272A"
ACCENT = "#00D4FF"
TEXT_PRIMARY = "#FAFAFA"
TEXT_SECONDARY = "#A1A1AA"
DANGER = "#EF4444"
WARNING = "#FF9800"


class CredentialCard(ctk.CTkFrame):
    def __init__(self, master, account_name, reveal_cb, delete_cb):
        super().__init__(master, fg_color=BG_SURFACE_LIGHT, corner_radius=8, height=55)
        self.pack(fill="x", padx=10, pady=6)
        self.pack_propagate(False)

        ctk.CTkLabel(self, text=account_name, font=("Consolas", 14, "bold"), text_color=TEXT_PRIMARY).pack(side="left", padx=15)

        ctk.CTkButton(
            self, text="DELETE", width=70, height=30, font=("Inter", 11, "bold"),
            fg_color="transparent", border_width=1, border_color=DANGER,
            text_color=DANGER, hover_color="#3F1D1D", corner_radius=15,
            command=lambda: delete_cb(account_name),
        ).pack(side="right", padx=(5, 15))

        ctk.CTkButton(
            self, text="UNVEIL / COPY", width=120, height=30, font=("Inter", 11, "bold"),
            fg_color="transparent", border_width=1, border_color=ACCENT,
            text_color=ACCENT, hover_color=BG_SURFACE, corner_radius=15,
            command=lambda: reveal_cb(account_name),
        ).pack(side="right", padx=5)


class SecurePassVault(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("COMRADE | Zero-Knowledge Credential Vault")
        self.geometry("750x600")
        self.configure(fg_color=BG_MAIN)
        self.attributes("-topmost", True)

        self.credentials = load_credentials() or {}
        self._build_ui()

    def _build_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(top_frame, text="NATIVE CRYPTO-VAULT", font=("Consolas", 16, "bold"), text_color=ACCENT).pack(side="left")

        ctk.CTkButton(
            top_frame, text="RESTORE VAULT", width=110, height=32, font=("Inter", 11, "bold"),
            fg_color="transparent", border_width=1, border_color=TEXT_SECONDARY,
            text_color=TEXT_SECONDARY, hover_color=BG_SURFACE_LIGHT, corner_radius=16,
            command=self.restore_vault,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            top_frame, text="BACKUP VAULT", width=110, height=32, font=("Inter", 11, "bold"),
            fg_color="transparent", border_width=1, border_color=ACCENT,
            text_color=ACCENT, hover_color=BG_SURFACE_LIGHT, corner_radius=16,
            command=self.backup_vault,
        ).pack(side="right", padx=5)

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=BG_SURFACE, corner_radius=10, border_width=1, border_color=BG_SURFACE_LIGHT)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=5)

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=20)

        self.btn_add = ctk.CTkButton(
            bottom_frame, text="+ GENERATE & ADD NEW CREDENTIAL", font=("Inter", 13, "bold"),
            fg_color="transparent", border_width=1, border_color=ACCENT, text_color=ACCENT,
            hover_color=BG_SURFACE_LIGHT, height=45, corner_radius=22,
            command=self.open_add_window,
        )
        self.btn_add.pack(fill="x", expand=True, padx=20)

        self.refresh_list()

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.credentials:
            ctk.CTkLabel(self.list_frame, text="No encrypted credentials found.", text_color=TEXT_SECONDARY, font=("Inter", 14)).pack(pady=50)
            return

        for account in sorted(self.credentials.keys()):
            CredentialCard(self.list_frame, account, self.action_reveal, self.action_delete)

    def action_reveal(self, account):
        encrypted = self.credentials.get(account)
        dialog = ctk.CTkInputDialog(text=f"Enter dedicated encryption key for [{account}]:", title="Auth Required")
        item_key = dialog.get_input()

        if not item_key:
            return

        plain = decrypt_individual_pass(encrypted, item_key)
        if not plain:
            messagebox.showerror("Access Denied", "Cryptographic mismatch. Invalid key.", parent=self)
            return

        self.clipboard_clear()
        self.clipboard_append(plain)
        self.update()
        self.after(10000, self.wipe_clipboard)

        messagebox.showinfo(
            "Payload Decrypted",
            f"Account: {account}\n\nPassword: {plain}\n\n[Copied to clipboard. Memory auto-wipes in 10 seconds]",
            parent=self,
        )

    def action_delete(self, account):
        dialog = ctk.CTkInputDialog(text=f"Verify item key to authorize deletion of [{account}]:", title="Security Override")
        item_key = dialog.get_input()

        if not item_key:
            return

        encrypted = self.credentials.get(account)
        plain = decrypt_individual_pass(encrypted, item_key)

        if not plain:
            messagebox.showerror("Access Denied", "Cryptographic mismatch. Invalid key. Deletion blocked.", parent=self)
            return

        if messagebox.askyesno("Confirm", f"Permanently wipe {account} credential?", parent=self):
            del self.credentials[account]
            if save_credentials(self.credentials):
                self.refresh_list()

    def wipe_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append("")
        self.update()

    def open_add_window(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Deploy Secure Asset")
        popup.geometry("450x540")
        popup.configure(fg_color=BG_MAIN)
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="NEW ENCRYPTED ENTRY", font=("Consolas", 16, "bold"), text_color=TEXT_PRIMARY).pack(pady=(25, 10))

        card = ctk.CTkFrame(popup, fg_color=BG_SURFACE, corner_radius=12, border_width=1, border_color=BG_SURFACE_LIGHT)
        card.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        ctk.CTkLabel(card, text="ACCOUNT / SERVICE", font=("Inter", 11, "bold"), text_color=ACCENT).pack(anchor="w", padx=25, pady=(20, 2))
        account_entry = ctk.CTkEntry(
            card, font=("Consolas", 13), width=340, height=38,
            fg_color=BG_MAIN, border_width=1, border_color=BG_SURFACE_LIGHT,
            corner_radius=6, placeholder_text="e.g., ProtonMail, AWS Root",
        )
        account_entry.pack(padx=25, pady=(0, 15))

        ctk.CTkLabel(card, text="DEDICATED ENCRYPTION KEY", font=("Inter", 11, "bold"), text_color=WARNING).pack(anchor="w", padx=25, pady=(5, 2))
        item_key_entry = ctk.CTkEntry(
            card, font=("Consolas", 13), width=340, height=38,
            fg_color=BG_MAIN, border_width=1, border_color=BG_SURFACE_LIGHT,
            show="*", corner_radius=6, placeholder_text="Strictly memorize this key",
        )
        item_key_entry.pack(padx=25, pady=(0, 15))

        ctk.CTkLabel(card, text="PASSWORD", font=("Inter", 11, "bold"), text_color=ACCENT).pack(anchor="w", padx=25, pady=(5, 2))
        password_entry = ctk.CTkEntry(
            card, font=("Consolas", 13), width=340, height=38,
            fg_color=BG_MAIN, border_width=1, border_color=BG_SURFACE_LIGHT,
            corner_radius=6, placeholder_text="Enter or generate payload",
        )
        password_entry.pack(padx=25, pady=(0, 20))

        def generate_pass():
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
            while True:
                pwd = "".join(secrets.choice(alphabet) for _ in range(20))
                if (any(c.islower() for c in pwd) and any(c.isupper() for c in pwd)
                        and sum(c.isdigit() for c in pwd) >= 2 and any(c in "!@#$%^&*-_=+" for c in pwd)):
                    break
            password_entry.delete(0, "end")
            password_entry.insert(0, pwd)

        ctk.CTkButton(
            card, text="⚡ GENERATE SECURE PASSWORD (20 chars)", font=("Inter", 11, "bold"), width=340, height=35,
            fg_color="transparent", border_width=1, border_color=WARNING, text_color=WARNING,
            hover_color=BG_MAIN, corner_radius=18, command=generate_pass,
        ).pack(padx=25, pady=(0, 15))

        def save_and_close():
            acc = account_entry.get().strip()
            item_key = item_key_entry.get()
            pwd = password_entry.get()

            if not acc or not item_key or not pwd:
                messagebox.showerror("Error", "All fields are required.", parent=popup)
                return

            enc = encrypt_individual_pass(pwd, item_key)
            if not enc:
                messagebox.showerror("Error", "Crypto calculation failed.", parent=popup)
                return

            self.credentials[acc] = enc
            if save_credentials(self.credentials):
                self.refresh_list()
                popup.destroy()
            else:
                messagebox.showerror("Error", "Failed to commit to disk.", parent=popup)

        ctk.CTkButton(
            card, text="ENCRYPT & COMMIT", font=("Inter", 12, "bold"), width=340, height=42,
            fg_color=ACCENT, text_color=BG_MAIN, hover_color="#00A2D6",
            corner_radius=21, command=save_and_close,
        ).pack(padx=25, pady=(0, 25))

    def backup_vault(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Backup", "*.json")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.credentials, f, indent=4)
            messagebox.showinfo("Backup", f"Vault encrypted state exported to:\n{path}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def restore_vault(self):
        """Validates the backup file's structure before merging, to avoid corrupting the vault."""
        path = filedialog.askopenfilename(filetypes=[("JSON Backup", "*.json")])
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                messagebox.showerror("Restore Error", "Invalid backup format: Expected a JSON object.", parent=self)
                return

            validated_entries = {
                key: val for key, val in data.items()
                if isinstance(key, str) and isinstance(val, str) and (val.startswith("B64:") or len(val) > 0)
            }

            if not validated_entries:
                messagebox.showerror("Restore Error", "No valid encrypted vault entries found in backup.", parent=self)
                return

            confirm = messagebox.askyesno(
                "Confirm Restore",
                f"Found {len(validated_entries)} valid entry/entries. Integrate into current vault?",
                parent=self,
            )
            if not confirm:
                return

            self.credentials.update(validated_entries)
            if save_credentials(self.credentials):
                self.refresh_list()
                messagebox.showinfo("Restore Success", f"Successfully restored {len(validated_entries)} entries.", parent=self)
            else:
                messagebox.showerror("Restore Error", "Failed to commit restored entries to disk.", parent=self)

        except json.JSONDecodeError:
            messagebox.showerror("Restore Error", "Failed to parse backup: Invalid JSON syntax.", parent=self)
        except Exception as e:
            messagebox.showerror("Restore Error", f"Failed to restore: {e}", parent=self)
