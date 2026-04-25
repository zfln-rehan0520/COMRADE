import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage
from core.file_manager import save_file, extract_file, list_secured_files, delete_vault_file
import os

# --- BRANDING CONFIG ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FileCard(ctk.CTkFrame):
    """Refined component for individual assets with Electric Cyan branding."""
    def __init__(self, master, vault_id, original_name, extract_cb, delete_cb):
        super().__init__(master, fg_color="#18181B", corner_radius=8, height=75, 
                         border_width=1, border_color="#00FFFF")
        self.pack(fill="x", padx=15, pady=8)
        self.pack_propagate(False) # Maintains fixed height

        # ID Section (Dimmed/Cyber Look)
        self.id_label = ctk.CTkLabel(self, text=vault_id[:12]+"...", 
                                     font=("Consolas", 12), text_color="#71717A")
        self.id_label.pack(side="left", padx=(20, 10))
        
        # Name Section (Prominent)
        self.name_label = ctk.CTkLabel(self, text=original_name, 
                                       font=("Inter", 14, "bold"), text_color="#F4F4F5")
        self.name_label.pack(side="left", padx=20, expand=True, anchor="w")
        
        # --- BUTTON GROUP ---
        self.btn_extract = ctk.CTkButton(
            self, text="Extract", width=85, height=32, font=("Inter", 12, "bold"),
            fg_color="#00FFFF", hover_color="#00CCCC", text_color="#000000",
            command=lambda: extract_cb(vault_id)
        )
        self.btn_extract.pack(side="right", padx=(5, 20))

        self.btn_delete = ctk.CTkButton(
            self, text="Delete", width=85, height=32, font=("Inter", 12, "bold"),
            fg_color="#EF4444", hover_color="#B91C1C", text_color="#FFFFFF",
            command=lambda: delete_cb(vault_id)
        )
        self.btn_delete.pack(side="right", padx=5)

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. WINDOW CONFIG
        self.title("COMRADE | A Brother That Guards Your Data")
        self.geometry("1100x750")
        self.configure(fg_color="#09090B")

        # 2. LOAD SYSTEM ASSETS
        try:
            self.icon_path = os.path.join(os.getcwd(), "assets", "logo.png")
            self.icon_img = PhotoImage(file=self.icon_path)
            self.iconphoto(True, self.icon_img)
        except: 
            self.icon_img = None

       # 3. HEADER & TOOLBAR
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=(40, 20))

        # Main Title
        self.title_brand = ctk.CTkLabel(
            self.header, 
            text="COMRADE", 
            font=("Inter", 42, "bold"), 
            text_color="#00FFFF"
        )
        self.title_brand.pack(side="left", anchor="n")

        # Branding Metadata Block
        self.branding_box = ctk.CTkFrame(self.header, fg_color="transparent")
        self.branding_box.pack(side="left", padx=30)

        self.full_name = ctk.CTkLabel(
            self.branding_box, 
            text="Cyber Operations Module for Resilient Authentication, Defense and Encryption",
            font=("Inter", 13), 
            text_color="#F4F4F5"
        )
        self.full_name.pack(anchor="w")

        self.version_tag = ctk.CTkLabel(
            self.branding_box, 
            text=" comrade-V1.0 | DESIGNED BY MOHAMMED REHAN { zfln-rehan0520 }",
            font=("Consolas", 11, "bold"), 
            text_color="#00FFFF"
        )
        self.version_tag.pack(anchor="w")

        # --- TOOLBAR ---
        self.toolbar = ctk.CTkFrame(self, fg_color="#18181B", height=80, corner_radius=8,
                                    border_width=1, border_color="#27272A")
        self.toolbar.pack(fill="x", padx=40, pady=10)
        
        # ... (keep your existing buttons here) ...

        # 4. ENCRYPTED REPOSITORY CONTAINER
        self.container = ctk.CTkScrollableFrame(
            self, fg_color="#09090B", label_text="ENCRYPTED REPOSITORY", 
            label_font=("Inter", 14, "bold"), label_text_color="#00FFFF",
            border_width=1, border_color="#18181B"
        )
        self.container.pack(fill="both", expand=True, padx=40, pady=(10, 20))

        # 5. STATUS FOOTER
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=40, pady=(0, 20))
        
        self.status_text = ctk.CTkLabel(self.footer, text="ENGINE STANDBY", 
                                        font=("Consolas", 11), text_color="#71717A")
        self.status_text.pack(side="left", padx=10)

        # 6. INITIALIZE REPOSITORY
        self.refresh_vault()

    def update_status(self, text, color="#71717A"):
        self.status_text.configure(text=text.upper(), text_color=color)

    def refresh_vault(self):
        """Clears and reloads the file cards from the manifest."""
        for widget in self.container.winfo_children():
            widget.destroy()
        
        try:
            files = list_secured_files()
            if not files:
                self.update_status("Repository Empty", "#71717A")
                ctk.CTkLabel(self.container, text="No encrypted assets found.", 
                             font=("Consolas", 13), text_color="#27272A").pack(pady=60)
            else:
                for f in files:
                    FileCard(self.container, f['vault_name'], f['original_name'], 
                             self.ui_extract_file, self.ui_delete_file)
                self.update_status("Engine Active", "#00FFFF")
        except Exception as e:
            self.update_status("Engine Error", "#EF4444")
            messagebox.showerror("Error", f"Failed to load vault: {e}")

    def ui_secure_file(self):
        path = filedialog.askopenfilename()
        if path:
            pw = ctk.CTkInputDialog(text="Create Master Key for Encryption:", title="Auth").get_input()
            if pw:
                try:
                    self.update_status("Securing Asset...", "#00FFFF")
                    save_file(path, pw)
                    self.refresh_vault()
                    messagebox.showinfo("Success", "Asset successfully committed to vault.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    self.update_status("Secure Failed", "#EF4444")

    def ui_extract_file(self, vault_id):
        dialog = ctk.CTkInputDialog(text="ENTER MASTER KEY:", title="Auth Required")
        pw = dialog.get_input()
        if pw:
            try:
                self.update_status("Decrypting...", "#00FFFF")
                extract_file(vault_id, pw)
                messagebox.showinfo("Success", "Asset decrypted successfully.")
                self.update_status("Extraction Success", "#00FFFF")
            except:
                messagebox.showerror("Denied", "Invalid Master Key.")
                self.update_status("Auth Failed", "#EF4444")

    def ui_delete_file(self, vault_id):
        dialog = ctk.CTkInputDialog(text="ENTER MASTER KEY TO AUTHORIZE WIPE:", title="Security")
        pw = dialog.get_input()
        if pw:
            if messagebox.askyesno("Final Warning", f"Permanently wipe {vault_id}?\nThis cannot be undone."):
                try:
                    self.update_status("Wiping Asset...", "#EF4444")
                    # Verified: Backend requires 'pw' to authorize the delete
                    delete_vault_file(vault_id, pw)
                    self.refresh_vault()
                    messagebox.showinfo("Wiped", "Asset permanently erased.")
                except Exception as e:
                    messagebox.showerror("Access Denied", str(e))
                    self.update_status("Wipe Denied", "#EF4444")

if __name__ == "__main__":
    app = ComradeApp()
    app.mainloop()
