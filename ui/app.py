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
        
        # 1. WINDOW CONFIG
        self.title("COMRADE | Data Guard")
        self.geometry("1100x750")
        self.configure(fg_color="#09090B")

        # 2. LOAD ASSETS
        try:
            self.icon_path = os.path.join(os.getcwd(), "assets", "logo.png")
            self.icon_img = PhotoImage(file=self.icon_path)
            self.iconphoto(True, self.icon_img)
        except: self.icon_img = None

        # 3. HEADER & TOOLBAR
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=(40, 20))
        ctk.CTkLabel(self.header, text="COMRADE", font=("Inter", 38, "bold"), text_color="#00FFFF").pack(side="left")

        self.toolbar = ctk.CTkFrame(self, fg_color="#18181B", height=80, corner_radius=8)
        self.toolbar.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkButton(self.toolbar, text="+ Secure New Asset", fg_color="#00FFFF", text_color="#000000", 
                      command=self.ui_secure_file).pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(self.toolbar, text="Rescan Engine", fg_color="#27272A", 
                      command=self.refresh_vault).pack(side="right", padx=20, pady=15)

        # 4. CREATE CONTAINER (Must happen before refresh_vault)
        self.container = ctk.CTkScrollableFrame(self, fg_color="#09090B", label_text="ENCRYPTED REPOSITORY", 
                                                label_text_color="#F4F4F5", border_width=1, border_color="#18181B")
        self.container.pack(fill="both", expand=True, padx=40, pady=20)

        # 5. FOOTER
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=40, pady=(0, 20))
        self.status_text = ctk.CTkLabel(self.footer, text="ENGINE STANDBY", font=("Consolas", 11), text_color="#71717A")
        self.status_text.pack(side="left", padx=10)

        # 6. NOW INITIALIZE REPOSITORY
        self.refresh_vault()

    def update_status(self, text, color="#71717A"):
        self.status_text.configure(text=text.upper(), text_color=color)

    def refresh_vault(self):
        """Clears and reloads the file cards."""
        for widget in self.container.winfo_children():
            widget.destroy()
        
        files = list_secured_files()
        if not files:
            self.update_status("Repository Empty", "#71717A")
            ctk.CTkLabel(self.container, text="No assets found.", font=("Consolas", 13), text_color="#27272A").pack(pady=60)
        else:
            for f in files:
                FileCard(self.container, f['vault_name'], f['original_name'], self.ui_extract_file, self.ui_delete_file)
            self.update_status("Engine Active", "#00FFFF")

    def ui_secure_file(self):
        path = filedialog.askopenfilename()
        if path:
            pw = ctk.CTkInputDialog(text="Create Key:", title="Auth").get_input()
            if pw:
                save_file(path, pw)
                self.refresh_vault()

    def ui_extract_file(self, vault_id):
        dialog = ctk.CTkInputDialog(text="ENTER MASTER KEY:", title="Auth Required")
        pw = dialog.get_input()
        if pw:
            try:
                extract_file(vault_id, pw)
                messagebox.showinfo("Success", "Decrypted.")
            except:
                messagebox.showerror("Denied", "Invalid Key.")

    def ui_delete_file(self, vault_id):
        dialog = ctk.CTkInputDialog(text="ENTER MASTER KEY TO WIPE:", title="Security")
        pw = dialog.get_input()
        if pw:
            if messagebox.askyesno("Final Warning", "Permanently erase?"):
                try:
                    delete_vault_file(vault_id, pw)
                    self.refresh_vault()
                except Exception as e:
                    messagebox.showerror("Access Denied", str(e))
