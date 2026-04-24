import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.file_manager import save_file, extract_file, list_secured_files
import os

# Industry Standard Industrial Theme
ctk.set_appearance_mode("Dark")

class FileCard(ctk.CTkFrame):
    """Component for individual vault assets with High-Alert styling."""
    def __init__(self, master, vault_id, original_name, extract_callback):
        super().__init__(master, fg_color="#1C1917", corner_radius=6, height=60, border_width=1, border_color="#292524")
        self.pack(fill="x", padx=10, pady=5)
        
        # ID Section (Monospace for data integrity feel)
        self.id_label = ctk.CTkLabel(self, text=vault_id[:12]+"...", font=("Consolas", 12), text_color="#78716C")
        self.id_label.pack(side="left", padx=20)
        
        # Name Section
        self.name_label = ctk.CTkLabel(self, text=original_name, font=("Inter", 13, "bold"), text_color="#FAFAF9")
        self.name_label.pack(side="left", padx=20, expand=True, anchor="w")
        
        # Action Button (Deep Safety Orange)
        self.btn_action = ctk.CTkButton(
            self, text="EXTRACT", width=90, height=32, font=("Inter", 11, "bold"),
            fg_color="#FF6B00", hover_color="#CC5500", text_color="#0C0A09",
            command=lambda: extract_callback(vault_id)
        )
        self.btn_action.pack(side="right", padx=20)

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("COMRADE | A reliable guardian for your data")
        self.geometry("1100x750")
        self.configure(fg_color="#0C0A09")

        # --- HEADER ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=(40, 20))

        self.title_brand = ctk.CTkLabel(self.header, text="COMRADE", font=ctk.CTkFont(size=38, weight="bold"), text_color="#FF6B00")
        self.title_brand.pack(side="left")
        
        self.meta_info = ctk.CTkFrame(self.header, fg_color="transparent")
        self.meta_info.pack(side="left", padx=30)
        
        ctk.CTkLabel(self.meta_info, text="Cyber Operations Module for Resilient Authentication and Data Encryption", 
                     font=("Inter", 12), text_color="#78716C").pack(anchor="w")
        ctk.CTkLabel(self.meta_info, text="DESIGNED BY MOHAMMED REHAN | CORE v1.0", 
                     font=("Consolas", 11, "bold"), text_color="#FFB380").pack(anchor="w")

        # --- TOOLBAR ---
        self.toolbar = ctk.CTkFrame(self, fg_color="#1C1917", height=80, corner_radius=8, border_width=1, border_color="#292524")
        self.toolbar.pack(fill="x", padx=40, pady=10)
        
        self.btn_lock = ctk.CTkButton(self.toolbar, text="+ SECURE NEW ASSET", font=("Inter", 13, "bold"),
                                      fg_color="#FF6B00", hover_color="#CC5500", text_color="#0C0A09",
                                      height=48, width=200, command=self.ui_secure_file)
        self.btn_lock.pack(side="left", padx=20, pady=15)

        self.btn_sync = ctk.CTkButton(self.toolbar, text="RE-SCAN ENGINE", font=("Inter", 12, "bold"),
                                      fg_color="transparent", border_width=2, border_color="#FF6B00",
                                      text_color="#FF6B00", hover_color="#292524",
                                      height=48, width=150, command=self.refresh_vault)
        self.btn_sync.pack(side="right", padx=20, pady=15)

        # --- DATA SECTION ---
        self.container = ctk.CTkScrollableFrame(self, fg_color="#0C0A09", label_text="ENCRYPTED DATA STORAGE", 
                                                label_font=("Inter", 14, "bold"), label_text_color="#78716C",
                                                border_width=1, border_color="#1C1917")
        self.container.pack(fill="both", expand=True, padx=40, pady=20)

        # --- FOOTER ---
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=40, pady=(0, 20))
        
        self.status_led = ctk.CTkLabel(self.footer, text="●", text_color="#FFB380", font=("Inter", 16))
        self.status_led.pack(side="left")
        
        self.status_text = ctk.CTkLabel(self.footer, text="SYSTEM STATUS: NOMINAL", 
                                        font=("Consolas", 11), text_color="#78716C")
        self.status_text.pack(side="left", padx=10)

        self.refresh_vault()

    def update_status(self, text, color="#78716C"):
        self.status_text.configure(text=text.upper(), text_color=color)

    def refresh_vault(self):
        for widget in self.container.winfo_children():
            widget.destroy()
            
        files = list_secured_files()
        if not files:
            ctk.CTkLabel(self.container, text="[ EMPTY VAULT - NO ASSETS DETECTED ]", 
                         font=("Consolas", 13), text_color="#292524").pack(pady=60)
        else:
            for f in files:
                FileCard(self.container, f['vault_name'], f['original_name'], self.ui_extract_file)
        
        self.update_status("Vault Synced", "#FFB380")

    def ui_secure_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            password = ctk.CTkInputDialog(text="Enter Master Password:", title="Zero-Trust Auth").get_input()
            if password:
                try:
                    self.update_status("Encrypting Payload...", "#FF6B00")
                    save_file(file_path, password)
                    self.refresh_vault()
                    messagebox.showinfo("Secured", "Encryption payload complete. Asset stored.")
                except Exception as e:
                    messagebox.showerror("Critical Fault", str(e))
                    self.update_status("Error Occurred", "#EF4444")

    def ui_extract_file(self, vault_id):
        password = ctk.CTkInputDialog(text="Enter Decryption Key:", title="Auth Required").get_input()
        if password:
            try:
                self.update_status("Decrypting Payload...", "#FF6B00")
                extract_file(vault_id, password)
                messagebox.showinfo("Restored", "Asset has been successfully decrypted.")
                self.update_status("Extraction Complete", "#FFB380")
            except Exception as e:
                messagebox.showerror("Access Denied", "Invalid Cryptographic Key.")
                self.update_status("Auth Failed", "#EF4444")

if __name__ == "__main__":
    app = ComradeApp()
    app.mainloop()
