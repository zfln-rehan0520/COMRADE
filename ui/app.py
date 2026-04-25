import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage
from core.file_manager import save_file, extract_file, list_secured_files, delete_vault_file
import os

# --- BRANDING LOGIC ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") # Set as base for Cyan accents

class FileCard(ctk.CTkFrame):
    """Component for individual assets with Extract and Delete options."""
    def __init__(self, master, vault_id, original_name, extract_callback, delete_callback):
        super().__init__(master, fg_color="#18181B", corner_radius=6, height=60, border_width=1, border_color="#00FFFF")
        self.pack(fill="x", padx=10, pady=5)
        
        # ID Section
        self.id_label = ctk.CTkLabel(self, text=vault_id[:12]+"...", font=("Consolas", 12), text_color="#71717A")
        self.id_label.pack(side="left", padx=20)
        
        # Name Section
        self.name_label = ctk.CTkLabel(self, text=original_name, font=("Inter", 13, "bold"), text_color="#F4F4F5")
        self.name_label.pack(side="left", padx=20, expand=True, anchor="w")
        
        # --- BUTTON GROUP ---
        # Extract Button (Cyan)
        self.btn_extract = ctk.CTkButton(
            self, text="Extract", width=70, height=30, font=("Inter", 11, "bold"),
            fg_color="#00FFFF", hover_color="#00CCCC", text_color="#000000",
            command=lambda: extract_callback(vault_id)
        )
        self.btn_extract.pack(side="right", padx=(5, 20))

        # Delete Button (Danger Red)
        self.btn_delete = ctk.CTkButton(
            self, text="Delete", width=70, height=30, font=("Inter", 11, "bold"),
            fg_color="#EF4444", hover_color="#B91C1C", text_color="#FFFFFF",
            command=lambda: delete_callback(vault_id)
        )
        self.btn_delete.pack(side="right", padx=5)

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("COMRADE |  A Brother That Guards Your Data")
        self.geometry("1100x750")
        self.configure(fg_color="#09090B")

        # Icon handling
        try:
            self.icon_path = os.path.join(os.getcwd(), "assets", "logo.png")
            self.icon_img = PhotoImage(file=self.icon_path)
            self.iconphoto(True, self.icon_img) 
        except Exception:
            pass

        # --- HEADER ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=(40, 20))

        self.title_brand = ctk.CTkLabel(self.header, text="COMRADE", font=ctk.CTkFont(size=38, weight="bold"), text_color="#00FFFF")
        self.title_brand.pack(side="left")
        
        self.meta_info = ctk.CTkFrame(self.header, fg_color="transparent")
        self.meta_info.pack(side="left", padx=30)
        
        ctk.CTkLabel(self.meta_info, text="Cyber Operations Module for Resilient Authentication and Data Encryption", 
                     font=("Inter", 12), text_color="#F4F4F5").pack(anchor="w")
        ctk.CTkLabel(self.meta_info, text="COMRADE V1.0 | DESIGNED BY MOHAMMED REHAN { github_id : zfln-rehan0520 }", 
                     font=("Consolas", 11, "bold"), text_color="#00FFFF").pack(anchor="w")

        # --- REPO TOOLBAR ---
        self.toolbar = ctk.CTkFrame(self, fg_color="#18181B", height=80, corner_radius=8, border_width=1, border_color="#27272A")
        self.toolbar.pack(fill="x", padx=40, pady=10)
        
        self.btn_lock = ctk.CTkButton(self.toolbar, text="+ Secure New Asset", font=("Inter", 13, "bold"),
                                      fg_color="#00FFFF", hover_color="#00CCCC", text_color="#000000",
                                      height=48, width=200, command=self.ui_secure_file)
        self.btn_lock.pack(side="left", padx=20, pady=15)

        self.btn_sync = ctk.CTkButton(self.toolbar, text="Rescan Engine", font=("Inter", 12, "bold"),
                                      fg_color="#27272A", border_width=1, border_color="#3F3F46",
                                      text_color="#F4F4F5", hover_color="#3F3F46",
                                      height=48, width=150, command=self.refresh_vault)
        self.btn_sync.pack(side="right", padx=20, pady=15)

        # --- ASSET LIST ---
        self.container = ctk.CTkScrollableFrame(self, fg_color="#09090B", label_text="ENCRYPTED REPOSITORY", 
                                                label_font=("Inter", 14, "bold"), label_text_color="#F4F4F5",
                                                border_width=1, border_color="#18181B")
        self.container.pack(fill="both", expand=True, padx=40, pady=20)

        # --- FOOTER ---
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=40, pady=(0, 20))
        
        self.status_led = ctk.CTkLabel(self.footer, text="●", text_color="#00FFFF", font=("Inter", 16))
        self.status_led.pack(side="left")
        
        self.status_text = ctk.CTkLabel(self.footer, text="ENGINE STATUS: STANDBY", 
                                        font=("Consolas", 11), text_color="#71717A")
        self.status_text.pack(side="left", padx=10)

    def update_status(self, text, color="#71717A"):
        self.status_text.configure(text=text.upper(), text_color=color)

    def refresh_vault(self):
        """Demands password before revealing the encrypted repository."""
        dialog = ctk.CTkInputDialog(text="Enter Master Key to Sync Vault:", title="Auth Required")
        # Try to force icon on the popup
        try:
            dialog.after(10, lambda: dialog.iconphoto(False, self.icon_img))
        except: pass
        
        password = dialog.get_input()
        
        if password:
            for widget in self.container.winfo_children():
                widget.destroy()
            
            try:
                # FIXED: Now passes password to the backend
                files = list_secured_files(password)
                
                if not files:
                    self.update_status("Access Denied / Empty", "#EF4444")
                    ctk.CTkLabel(self.container, text="No encrypted assets found or wrong key.", 
                                 font=("Consolas", 13), text_color="#27272A").pack(pady=60)
                else:
                    for f in files:
                        FileCard(self.container, f['vault_name'], f['original_name'], 
                                 self.ui_extract_file, self.ui_delete_file)
                    self.update_status("Vault Decrypted", "#00FFFF")
            except Exception as e:
                messagebox.showerror("Error", f"Sync failed: {e}")
        else:
            self.update_status("Login Required", "#71717A")

    def ui_secure_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            password = ctk.CTkInputDialog(text="Create Encryption Key:", title="Zero-Trust Auth").get_input()
            if password:
                try:
                    self.update_status("Committing Asset...", "#00FFFF")
                    save_file(file_path, password)
                    # We don't refresh automatically because we need the password again
                    messagebox.showinfo("Success", "Asset secured. Click Rescan to view updated list.")
                    self.update_status("Commit Success", "#34D399")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    self.update_status("Commit Failed", "#EF4444")

    def ui
