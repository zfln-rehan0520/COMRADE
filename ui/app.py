import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.file_manager import save_file, extract_file, list_secured_files
import os

# Industry Grade Theme Settings
ctk.set_appearance_mode("Dark")

class FileCard(ctk.CTkFrame):
    """A professional UI component for individual vault assets."""
    def __init__(self, master, vault_id, original_name, extract_callback):
        super().__init__(master, fg_color="#1E1E26", corner_radius=8, height=60)
        self.pack(fill="x", padx=10, pady=5)
        
        # ID Section
        self.id_label = ctk.CTkLabel(self, text=vault_id[:16]+"...", font=("Consolas", 12), text_color="#94A3B8")
        self.id_label.pack(side="left", padx=20)
        
        # Name Section
        self.name_label = ctk.CTkLabel(self, text=original_name, font=("Inter", 13, "bold"), text_color="#E2E8F0")
        self.name_label.pack(side="left", padx=20, expand=True, anchor="w")
        
        # Action Button
        self.btn_action = ctk.CTkButton(
            self, text="EXTRACT", width=80, height=28, font=("Inter", 11, "bold"),
            fg_color="#3B82F6", hover_color="#2563EB",
            command=lambda: extract_callback(vault_id)
        )
        self.btn_action.pack(side="right", padx=20)

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("COMRADE | Advanced Cryptographic Suite")
        self.geometry("1100x750")
        self.configure(fg_color="#0B0B0E")

        # --- HEADER ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=(40, 20))

        self.title_brand = ctk.CTkLabel(self.header, text="COMRADE", font=ctk.CTkFont(size=36, weight="bold"), text_color="#3B82F6")
        self.title_brand.pack(side="left")
        
        self.meta_info = ctk.CTkFrame(self.header, fg_color="transparent")
        self.meta_info.pack(side="left", padx=30)
        
        ctk.CTkLabel(self.meta_info, text="Cyber Operations Module for Resilient Authentication and Data Encryption", 
                     font=("Inter", 12), text_color="#64748B").pack(anchor="w")
        ctk.CTkLabel(self.meta_info, text="DESIGNED BY MOHAMMED REHAN | CORE v1.0", 
                     font=("Consolas", 11), text_color="#3B82F6").pack(anchor="w")

        # --- TOP ACTION BAR ---
        self.toolbar = ctk.CTkFrame(self, fg_color="#16161E", height=80, corner_radius=12)
        self.toolbar.pack(fill="x", padx=40, pady=10)
        
        self.btn_lock = ctk.CTkButton(self.toolbar, text="+ SECURE ASSET", font=("Inter", 13, "bold"),
                                      fg_color="#3B82F6", hover_color="#2563EB", height=45, width=180,
                                      command=self.ui_secure_file)
        self.btn_lock.pack(side="left", padx=20, pady=15)

        self.btn_sync = ctk.CTkButton(self.toolbar, text="RE-SCAN ENGINE", font=("Inter", 12),
                                      fg_color="transparent", border_width=1, border_color="#3F3F46",
                                      height=45, width=150, command=self.refresh_vault)
        self.btn_sync.pack(side="right", padx=20, pady=15)

        # --- VAULT DATA SECTION ---
        self.container = ctk.CTkScrollableFrame(self, fg_color="#111118", label_text="ENCRYPTED DATA STORAGE", 
                                                label_font=("Inter", 14, "bold"), label_text_color="#94A3B8")
        self.container.pack(fill="both", expand=True, padx=40, pady=20)

        # --- STATUS FOOTER ---
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=40, pady=(0, 20))
        
        self.status_led = ctk.CTkLabel(self.footer, text="●", text_color="#10B981", font=("Inter", 14))
        self.status_led.pack(side="left")
        
        self.status_text = ctk.CTkLabel(self.footer, text="SYSTEM NOMINAL | ZERO-TRUST ACTIVE", 
                                        font=("Consolas", 11), text_color="#64748B")
        self.status_text.pack(side="left", padx=10)

        self.refresh_vault()

    def update_status(self, text, color="#64748B"):
        self.status_text.configure(text=text.upper(), text_color=color)

    def refresh_vault(self):
        # Clear existing cards
        for widget in self.container.winfo_children():
            widget.destroy()
            
        files = list_secured_files()
        if not files:
            ctk.CTkLabel(self.container, text="No assets currently secured in the vault.", 
                         font=("Inter", 13), text_color="#3F3F46").pack(pady=40)
        else:
            for f in files:
                FileCard(self.container, f['vault_name'], f['original_name'], self.ui_extract_file)
        
        self.update_status("Vault Synced", "#10B981")

    def ui_secure_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            password = ctk.CTkInputDialog(text="Enter Master Password:", title="Auth").get_input()
            if password:
                try:
                    self.update_status("Encrypting Payload...", "#3B82F6")
                    save_file(file_path, password)
                    self.refresh_vault()
                    messagebox.showinfo("Success", "File successfully secured.")
                except Exception as e:
                    messagebox.showerror("Fault", str(e))
                    self.update_status("Error Occurred", "#EF4444")

    def ui_extract_file(self, vault_id):
        password = ctk.CTkInputDialog(text="Enter Decryption Key:", title="Secure Extraction").get_input()
        if password:
            try:
                self.update_status("Decrypting Asset...", "#3B82F6")
                extract_file(vault_id, password)
                messagebox.showinfo("Restored", "Asset has been successfully decrypted.")
                self.update_status("Decryption Complete", "#10B981")
            except Exception as e:
                messagebox.showerror("Access Denied", "Invalid Key.")
                self.update_status("Decryption Failed", "#EF4444")

if __name__ == "__main__":
    app = ComradeApp()
    app.mainloop()
