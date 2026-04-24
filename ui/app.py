import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.file_manager import save_file, extract_file, list_secured_files
import os

# Ultra-Pro Branding & Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("COMRADE | Advanced Data Encryption Suite")
        self.geometry("1100x700")

        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Background Frame (Container)
        self.bg_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f0f12")
        self.bg_frame.grid(row=0, column=0, sticky="nsew")
        self.bg_frame.grid_columnconfigure(0, weight=1)
        self.bg_frame.grid_rowconfigure(1, weight=1)

        # --- HEADER SECTION ---
        self.header_frame = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=40, pady=(30, 10), sticky="ew")

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="COMRADE", 
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color="#3b82f6"
        )
        self.title_label.pack(side="left")

        self.tagline_label = ctk.CTkLabel(
            self.header_frame, 
            text="Cyber Operations Module for Resilient Authentication and Data Encryption", 
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="#94a3b8"
        )
        self.tagline_label.pack(side="left", padx=20, pady=(10, 0))

        # --- ACTION RIBBON ---
        self.action_frame = ctk.CTkFrame(self.bg_frame, fg_color="#1a1a1e", height=60, corner_radius=12)
        self.action_frame.grid(row=1, column=0, padx=40, pady=10, sticky="new")
        
        self.btn_secure = ctk.CTkButton(
            self.action_frame, text="🔒 SECURE ASSET", 
            command=self.ui_secure_file, width=160, height=40,
            font=ctk.CTkFont(weight="bold"), fg_color="#2563eb", hover_color="#1d4ed8"
        )
        self.btn_secure.pack(side="left", padx=20, pady=10)

        self.btn_extract = ctk.CTkButton(
            self.action_frame, text="🔓 EXTRACT ASSET", 
            command=self.ui_extract_file, width=160, height=40,
            font=ctk.CTkFont(weight="bold"), fg_color="transparent", border_width=2, border_color="#3f3f46"
        )
        self.btn_extract.pack(side="left", padx=5, pady=10)

        self.btn_refresh = ctk.CTkButton(
            self.action_frame, text="RE-SCAN VAULT", 
            command=self.refresh_list, width=120, height=40,
            font=ctk.CTkFont(size=11), fg_color="transparent", text_color="#71717a"
        )
        self.btn_refresh.pack(side="right", padx=20, pady=10)

        # --- DATA DISPLAY ---
        self.vault_container = ctk.CTkFrame(self.bg_frame, fg_color="#1a1a1e", corner_radius=12)
        self.vault_container.grid(row=2, column=0, padx=40, pady=(10, 40), sticky="nsew")
        self.vault_container.grid_columnconfigure(0, weight=1)
        self.vault_container.grid_rowconfigure(0, weight=1)

        self.vault_display = ctk.CTkTextbox(
            self.vault_container, 
            font=("Consolas", 14), 
            fg_color="transparent", 
            text_color="#e2e8f0",
            border_width=0
        )
        self.vault_display.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # --- FOOTER ---
        self.status_bar = ctk.CTkLabel(
            self.bg_frame, 
            text="SYSTEM STATUS: NOMINAL", 
            font=("Consolas", 10), 
            text_color="#4ade80"
        )
        self.status_bar.grid(row=3, column=0, padx=50, pady=(0, 20), sticky="w")

        self.refresh_list()

    def update_status(self, msg, color="#94a3b8"):
        self.status_bar.configure(text=f"SYSTEM STATUS: {msg.upper()}", text_color=color)

    def refresh_list(self):
        self.vault_display.configure(state="normal")
        self.vault_display.delete("1.0", "end")
        files = list_secured_files()
        
        header = f"{'VAULT IDENTIFIER':<30} | {'PROTECTED FILENAME':<40}\n"
        separator = "═" * 80 + "\n"
        self.vault_display.insert("end", header + separator)

        for f in files:
            line = f"{f['vault_name']:<30} | {f['original_name']:<40}\n"
            self.vault_display.insert("end", line)
        
        self.vault_display.configure(state="disabled")
        self.update_status("Vault Synced", "#4ade80")

    def ui_secure_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            password = ctk.CTkInputDialog(text="Enter Cryptographic Key (Password):", title="Authentication Required").get_input()
            if password:
                try:
                    self.update_status("Encrypting Payload...", "#3b82f6")
                    save_file(file_path, password)
                    messagebox.showinfo("Encrypted", "Asset successfully moved to Zero-Trust storage.")
                    self.refresh_list()
                except Exception as e:
                    messagebox.showerror("Fault", str(e))
                    self.update_status("Operation Failed", "#f87171")

    def ui_extract_file(self):
        vault_id = ctk.CTkInputDialog(text="Input Target Vault ID:", title="Decryption Sequence").get_input()
        if vault_id:
            password = ctk.CTkInputDialog(text="Enter Cryptographic Key:", title="Authentication Required").get_input()
            if password:
                try:
                    self.update_status("Reconstructing Asset...", "#3b82f6")
                    path = extract_file(vault_id, password)
                    messagebox.showinfo("Restored", "Asset has been successfully decrypted and restored.")
                    self.update_status("Extraction Complete", "#4ade80")
                except Exception as e:
                    messagebox.showerror("Access Denied", "Invalid Key or corrupted Vault ID.")
                    self.update_status("Extraction Fault", "#f87171")

if __name__ == "__main__":
    app = ComradeApp()
    app.mainloop()
