import logging
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage, simpledialog
from core.file_manager import save_file, extract_file, list_secured_files, delete_vault_file

logger = logging.getLogger(__name__)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PasswordDialog(ctk.CTkToplevel):
    """A secure, modal password input dialog with optional confirmation field."""

    def __init__(self, master, title: str, prompt: str, confirm: bool = False):
        super().__init__(master)
        self.title(title)
        self.geometry("400x220" if confirm else "400x160")
        self.resizable(False, False)
        self.configure(fg_color="#09090B")
        self.grab_set()  # Make modal

        self.result = None
        self._confirm_mode = confirm

        ctk.CTkLabel(self, text=prompt, font=("Inter", 13), text_color="#F4F4F5").pack(pady=(20, 5))
        self._entry1 = ctk.CTkEntry(self, show="●", width=300, font=("Consolas", 13))
        self._entry1.pack(pady=5)
        self._entry1.focus()

        if confirm:
            ctk.CTkLabel(self, text="Confirm Key:", font=("Inter", 13), text_color="#F4F4F5").pack(pady=(10, 5))
            self._entry2 = ctk.CTkEntry(self, show="●", width=300, font=("Consolas", 13))
            self._entry2.pack(pady=5)

        ctk.CTkButton(self, text="CONFIRM", fg_color="#00FFFF", text_color="#000000",
                      hover_color="#00CCCC", font=("Inter", 12, "bold"),
                      command=self._submit).pack(pady=15)

        self.bind("<Return>", lambda e: self._submit())
        self.wait_window()

    def _submit(self):
        pw = self._entry1.get()
        if not pw:
            messagebox.showwarning("Input Required", "Master key cannot be empty.", parent=self)
            return
        if self._confirm_mode:
            pw2 = self._entry2.get()
            if pw != pw2:
                messagebox.showerror("Mismatch", "Keys do not match. Please try again.", parent=self)
                self._entry1.delete(0, "end")
                self._entry2.delete(0, "end")
                self._entry1.focus()
                return
        self.result = pw
        self.destroy()


class FileCard(ctk.CTkFrame):
    """Card component for a single vault asset."""

    def __init__(self, master, vault_id: str, original_name: str, extract_cb, delete_cb):
        super().__init__(master, fg_color="#18181B", corner_radius=8, height=75,
                         border_width=1, border_color="#00FFFF")
        self.pack(fill="x", padx=15, pady=8)
        self.pack_propagate(False)

        # Vault ID (dimmed)
        ctk.CTkLabel(self, text=vault_id[:12] + "…", font=("Consolas", 12),
                     text_color="#71717A").pack(side="left", padx=(20, 10))

        # Original path (truncated display)
        display_name = os.path.basename(original_name)
        ctk.CTkLabel(self, text=display_name, font=("Inter", 14, "bold"),
                     text_color="#F4F4F5").pack(side="left", padx=20, expand=True, anchor="w")

        ctk.CTkButton(self, text="DELETE", width=90, height=35, font=("Inter", 12, "bold"),
                      fg_color="#EF4444", hover_color="#B91C1C", text_color="#FFFFFF",
                      command=lambda: delete_cb(vault_id)).pack(side="right", padx=(5, 20))

        ctk.CTkButton(self, text="EXTRACT", width=90, height=35, font=("Inter", 12, "bold"),
                      fg_color="#00FFFF", hover_color="#00CCCC", text_color="#000000",
                      command=lambda: extract_cb(vault_id)).pack(side="right", padx=5)


class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("COMRADE | A Brother That Guards Your Data")
        self.geometry("1100x750")
        self.configure(fg_color="#09090B")

        # Load icon
        try:
            icon_path = os.path.join(os.getcwd(), "assets", "logo.png")
            self._icon_img = PhotoImage(file=icon_path)
            self.iconphoto(True, self._icon_img)
        except Exception:
            self._icon_img = None

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))

        ctk.CTkLabel(header, text="COMRADE", font=("Inter", 42, "bold"),
                     text_color="#00FFFF").pack(side="left", anchor="n")

        branding = ctk.CTkFrame(header, fg_color="transparent")
        branding.pack(side="left", padx=30)
        ctk.CTkLabel(branding, font=("Inter", 13), text_color="#F4F4F5",
                     text="Cyber Operations Module for Resilient Authentication, Defense and Encryption"
                     ).pack(anchor="w")
        ctk.CTkLabel(branding, font=("Consolas", 11, "bold"), text_color="#00FFFF",
                     text="comrade-V1.1 | DESIGNED BY MOHAMMED REHAN { Github_id :- zfln-rehan0520 }"
                     ).pack(anchor="w")

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="#18181B", height=80, corner_radius=8,
                               border_width=1, border_color="#27272A")
        toolbar.pack(fill="x", padx=40, pady=10)
        toolbar.pack_propagate(False)

        ctk.CTkButton(toolbar, text="+ SECURE NEW ASSET", height=45, width=200,
                      fg_color="#00FFFF", hover_color="#00CCCC", text_color="#000000",
                      font=("Inter", 13, "bold"),
                      command=self.ui_secure_file).pack(side="left", padx=20, pady=15)

        ctk.CTkButton(toolbar, text="RESCAN ENGINE", height=45, width=150,
                      fg_color="#27272A", hover_color="#3F3F46", text_color="#F4F4F5",
                      font=("Inter", 12, "bold"),
                      command=self.ui_rescan).pack(side="right", padx=20, pady=15)

        # Vault container
        self.container = ctk.CTkScrollableFrame(
            self, fg_color="#09090B",
            label_text="ENCRYPTED REPOSITORY",
            label_font=("Inter", 14, "bold"),
            label_text_color="#F0F8FF",
            border_width=1, border_color="#18181B"
        )
        self.container.pack(fill="both", expand=True, padx=40, pady=(10, 20))

        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=40, pady=(0, 20))
        self._status_label = ctk.CTkLabel(footer, text="ENGINE STANDBY",
                                          font=("Consolas", 11), text_color="#71717A")
        self._status_label.pack(side="left", padx=10)

        self._show_empty_state()
        self._update_status("Engine ready — enter master key to load vault", "#71717A")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _update_status(self, text: str, color: str = "#71717A") -> None:
        self._status_label.configure(text=text.upper(), text_color=color)

    def _clear_container(self) -> None:
        for w in self.container.winfo_children():
            w.destroy()

    def _show_empty_state(self) -> None:
        self._clear_container()
        ctk.CTkLabel(self.container, text="No encrypted assets loaded.\nSecure a file or rescan to unlock the vault.",
                     font=("Consolas", 13), text_color="#27272A", justify="center").pack(pady=60)

    def _ask_password(self, title: str, prompt: str, confirm: bool = False):
        dlg = PasswordDialog(self, title=title, prompt=prompt, confirm=confirm)
        return dlg.result

    # ------------------------------------------------------------------
    # UI Actions
    # ------------------------------------------------------------------

    def ui_rescan(self) -> None:
        """Prompt for master key and reload vault contents."""
        pw = self._ask_password("Unlock Vault", "Enter Master Key to load vault:")
        if not pw:
            return
        self._clear_container()
        try:
            files = list_secured_files(pw)
            if not files:
                self._show_empty_state()
                self._update_status("Vault is empty", "#71717A")
            else:
                for f in files:
                    FileCard(self.container, f["vault_name"], f["original_name"],
                             self.ui_extract_file, self.ui_delete_file)
                self._update_status(f"Vault loaded — {len(files)} asset(s)", "#00FFFF")
        except RuntimeError:
            messagebox.showerror("Access Denied", "Invalid master key or corrupted manifest.")
            self._update_status("Auth Failed", "#EF4444")
        except Exception as e:
            logger.exception("Unexpected error during vault scan")
            messagebox.showerror("Error", f"Failed to load vault: {e}")
            self._update_status("Engine Error", "#EF4444")

    def ui_secure_file(self) -> None:
        path = filedialog.askopenfilename()
        if not path:
            return
        pw = self._ask_password("Create Master Key", "Create Master Key for encryption:", confirm=True)
        if not pw:
            return
        try:
            self._update_status("Securing asset…", "#00FFFF")
            save_file(path, pw)
            messagebox.showinfo("Success", "Asset successfully committed to vault.\nOriginal file has been securely wiped.")
            self._update_status("Asset secured", "#00FFFF")
        except FileNotFoundError as e:
            messagebox.showerror("File Not Found", str(e))
            self._update_status("Secure Failed", "#EF4444")
        except Exception as e:
            logger.exception("Error securing file")
            messagebox.showerror("Error", str(e))
            self._update_status("Secure Failed", "#EF4444")

    def ui_extract_file(self, vault_id: str) -> None:
        pw = self._ask_password("Authorization Required", "Enter Master Key to extract:")
        if not pw:
            return
        try:
            self._update_status("Decrypting…", "#00FFFF")
            path = extract_file(vault_id, pw)
            messagebox.showinfo("Success", f"Asset restored to:\n{path}")
            self._update_status("Extraction complete", "#00FFFF")
            # Remove card from view
            self.ui_rescan_silent(pw)
        except KeyError:
            messagebox.showerror("Not Found", "Asset not found in manifest.")
        except Exception as e:
            logger.exception("Extraction failed")
            messagebox.showerror("Access Denied", "Invalid master key.")
            self._update_status("Auth Failed", "#EF4444")

    def ui_delete_file(self, vault_id: str) -> None:
        pw = self._ask_password("Authorize Wipe", "Enter Master Key to authorize permanent wipe:")
        if not pw:
            return
        if not messagebox.askyesno("Final Warning", f"Permanently wipe {vault_id}?\nThis CANNOT be undone."):
            return
        try:
            self._update_status("Wiping asset…", "#EF4444")
            delete_vault_file(vault_id, pw)
            messagebox.showinfo("Wiped", "Asset permanently and securely erased.")
            self.ui_rescan_silent(pw)
        except (KeyError, ValueError) as e:
            messagebox.showerror("Access Denied", str(e))
            self._update_status("Wipe Denied", "#EF4444")
        except Exception as e:
            logger.exception("Delete failed")
            messagebox.showerror("Error", str(e))
            self._update_status("Engine Error", "#EF4444")

    def ui_rescan_silent(self, password: str) -> None:
        """Refresh vault display using a known-good password (no prompt)."""
        self._clear_container()
        try:
            files = list_secured_files(password)
            if not files:
                self._show_empty_state()
                self._update_status("Vault is now empty", "#71717A")
            else:
                for f in files:
                    FileCard(self.container, f["vault_name"], f["original_name"],
                             self.ui_extract_file, self.ui_delete_file)
                self._update_status(f"{len(files)} asset(s) in vault", "#00FFFF")
        except Exception:
            pass  # Silent — don't double-error after a successful operation


if __name__ == "__main__":
    app = ComradeApp()
    app.mainloop()
