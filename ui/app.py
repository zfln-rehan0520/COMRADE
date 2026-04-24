import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.file_manager import save_file, extract_file, list_secured_files
import os

# GitHub Enterprise Theme Logic
ctk.set_appearance_mode("Dark")

class FileCard(ctk.CTkFrame):
    """Component for individual assets with GitHub-style aesthetics."""
    def __init__(self, master, vault_id, original_name, extract_callback):
        # Using GitHub's specific surface and border colors
        super().__init__(master, fg_color="#161B22", corner_radius=6, height=60, border_width=1, border_color="#30363D")
        self.pack(fill="x", padx=10, pady=5)
        
        # ID Section (Subtle and clean)
        self.id_label = ctk.CTkLabel(self, text=vault_id[:12]+"...", font=("Consolas", 12), text_color="#8B949E")
        self.id_label.pack(side="left", padx=20)
        
        # Name Section
        self.name_label = ctk.CTkLabel(self, text=original_name, font=("Inter", 13, "bold"), text_color="#C9D1D9")
        self.name_label.pack(side="left", padx=20, expand=True, anchor="w")
        
        # Action Button (GitHub-style Coral/Orange)
        self.btn_action = ctk.CTkButton(
            self, text="Extract", width=90, height=32, font=("Inter", 11, "bold"),
            fg_color="#F78166", hover_color="#FF7B72", text_color="#0D1117",
            command=lambda: extract_callback(vault_id)
        )
        self.btn_action.pack(side="right", padx=20)

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("COMRADE | Secure Repository")
        self.geometry("1100x750")
        self.configure(fg_color="#0D1117")

        # --- HEADER ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=(40, 20))

        self.title_brand = ctk.CTkLabel(self.header, text="COMRADE", font=ctk.CTkFont(size=38, weight="bold"), text_color="#F78166")
        self.title_brand.pack(side="left")
        
        self.meta_info = ctk.CTkFrame(self.header, fg_color="transparent")
        self.meta_info.pack(side="left", padx=30)
        
        ctk.CTkLabel(self.meta_info, text="Cyber Operations Module for Resilient Authentication and Data Encryption", 
                     font=("Inter", 12), text_color="#8B949E").pack(anchor="w")
        ctk.CTkLabel(self.meta_info, text="DESIGNED BY MOHAMMED REHAN | CORE v1.0", 
                     font=("Consolas", 11, "bold"), text_color="#F78166").pack(anchor="w")

        # --- REPO TOOLBAR ---
        self.toolbar = ctk.CTkFrame(self, fg_color="#161B22", height=80, corner_radius=8, border_width=1, border_color="#30363D")
        self.toolbar.pack(fill="x", padx=40, pady=10)
        
        self.btn_lock = ctk.CTkButton(self.toolbar, text="+ Secure New Asset", font=("Inter", 13, "bold"),
                                      fg_color="#238636", hover_color="#2EA043", text_color="#FFFFFF", # GitHub Green for 'New'
                                      height=48, width=200, command=self.ui_secure_file)
        self.btn_lock.pack(side="left", padx=20, pady=15)

        self.btn_sync = ctk.CTkButton(self.toolbar, text="Rescan Engine", font=("Inter", 12, "bold"),
                                      fg_color="#21262D", border_width=1, border_color="#30363D",
                                      text_color="#C9D1D9", hover_color="#30363D",
                                      height=48, width=150, command=self.refresh_vault)
        self.btn_sync.pack(side="right", padx=20, pady=15)

        # --- ASSET LIST ---
        self.container = ctk.CTkScrollableFrame(self, fg_color="#0D1117", label_text="ENCRYPTED REPOSITORY", 
                                                label_font=("Inter", 14, "bold"), label_text_color="#8B949E",
                                                border_width=1, border_color="#161B22")
        self.container.pack(fill="both", expand=True, padx=40, pady=20)

        # --- FOOTER ---
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=40, pady=(0, 20))
        
        self.status_led = ctk.CTkLabel(self.footer, text="●", text_color="#3FB950", font=("Inter", 16))
        self.status_led.pack(side="left")
        
        self.status_text = ctk.CTkLabel(self.footer, text="ENGINE STATUS: ACTIVE", 
                                        font=("Consolas", 11), text_color="#8B949E")
        self.status_text.pack(side="left", padx=10)

        self.refresh_vault()

    def update_status(self, text, color="#8B949E"):
        self.status_text.configure(text=text.upper(), text_color=color)

    def refresh_vault(self):
        for widget in self.container.winfo_children():
            widget.destroy()
            
        files = list_secured_files()
        if not files:
            ctk.CTkLabel(self.container, text="No encrypted assets found in this branch.", 
                         font=("Consolas", 13), text_color="#30363D").pack(pady=60)
        else:
            for f in files:
                FileCard(self.container, f['vault_name'], f['original_name'], self.ui_extract_file)
        
        self.update_status("Vault Synced", "#3FB950")

    def ui_secure_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            password = ctk.CTkInputDialog(text="Confirm Encryption Key:", title="Zero-Trust Auth").get_input()
            if password:
                try:
                    self.update_status("Committing Asset...", "#F78166")
                    save_file(file_path, password)
                    self.refresh_vault()
                    messagebox.showinfo("Success", "Asset successfully encrypted and committed to vault.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    self.update_status("Commit Failed", "#FF7B72")

    def ui_extract_file(self, vault_id):
        password = ctk.CTkInputDialog(text="Enter Extraction Key:", title="Auth Required").get_input()
        if password:
            try:
                self.update_status("Pulling Asset...", "#F78166")
                extract_file(vault_id, password)
                messagebox.showinfo("Restored", "Asset has been successfully decrypted.")
                self.update_status("Extraction Complete", "#3FB950")
            except Exception as e:
                messagebox.showerror("Denied", "Invalid cryptographic key.")
                self.update_status("Auth Failed", "#FF7B72")

if __name__ == "__main__":
    app = ComradeApp()
    app.mainloop()
