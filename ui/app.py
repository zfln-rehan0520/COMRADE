import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage
from core.file_manager import save_file, extract_file, list_secured_files, delete_vault_file
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FileCard(ctk.CTkFrame):
    def __init__(self, master, vault_id, original_name, extract_cb, delete_cb):
        super().__init__(master, fg_color="#18181B", corner_radius=6, border_width=1, border_color="#00FFFF")
        self.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(self, text=vault_id[:12]+"...", font=("Consolas", 12), text_color="#71717A").pack(side="left", padx=20)
        ctk.CTkLabel(self, text=original_name, font=("Inter", 13, "bold"), text_color="#F4F4F5").pack(side="left", padx=20, expand=True, anchor="w")
        
        ctk.CTkButton(self, text="Extract", width=70, fg_color="#00FFFF", text_color="#000000", command=lambda: extract_cb(vault_id)).pack(side="right", padx=5)
        ctk.CTkButton(self, text="Delete", width=70, fg_color="#EF4444", command=lambda: delete_cb(vault_id)).pack(side="right", padx=20)

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("COMRADE | Data Guard")
        self.geometry("1100x750")
        self.configure(fg_color="#09090B")
        
        # Header & Toolbar code (Keep your current styling here)
        # ...
        
        # Initialize the list immediately since listing is public
        self.refresh_vault()

    def refresh_vault(self):
        """Shows files immediately."""
        # Clear container
        # ... 
        files = list_secured_files()
        if not files:
            self.update_status("Repository Empty", "#71717A")
        else:
            for f in files:
                FileCard(self.container, f['vault_name'], f['original_name'], self.ui_extract_file, self.ui_delete_file)
            self.update_status("Engine Active", "#00FFFF")

    def ui_extract_file(self, vault_id):
        pw = ctk.CTkInputDialog(text="Master Key:", title="Auth").get_input()
        if pw:
            try:
                extract_file(vault_id, pw)
                messagebox.showinfo("Success", "Decrypted.")
            except:
                messagebox.showerror("Denied", "Wrong Key.")

    def ui_delete_file(self, vault_id):
        pw = ctk.CTkInputDialog(text="Authorize Wipe (Enter Key):", title="Security").get_input()
        if pw:
            try:
                delete_vault_file(vault_id, pw)
                self.refresh_vault()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # Add your ui_secure_file and update_status functions here
