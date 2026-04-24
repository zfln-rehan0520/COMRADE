import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.file_manager import save_file, extract_file, list_secured_files
import os

# Set the theme to professional dark
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("COMRADE | Zero-Trust Encryption Suite")
        self.geometry("1000x600")

        # Configure grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="LYBERNET", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.sub_label = ctk.CTkLabel(self.sidebar_frame, text="COMRADE v1.0", font=ctk.CTkFont(size=12))
        self.sub_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.btn_secure = ctk.CTkButton(self.sidebar_frame, text="🔒 Secure File", command=self.ui_secure_file)
        self.btn_secure.grid(row=2, column=0, padx=20, pady=10)

        self.btn_extract = ctk.CTkButton(self.sidebar_frame, text="🔓 Extract File", command=self.ui_extract_file)
        self.btn_extract.grid(row=3, column=0, padx=20, pady=10)

        self.btn_refresh = ctk.CTkButton(self.sidebar_frame, text="🔄 Refresh Vault", fg_color="transparent", border_width=1, command=self.refresh_list)
        self.btn_refresh.grid(row=4, column=0, padx=20, pady=10)

        # --- MAIN CONTENT ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.header_label = ctk.CTkLabel(self.main_frame, text="Protected Assets", font=ctk.CTkFont(size=18, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Vault Table / List
        self.vault_display = ctk.CTkTextbox(self.main_frame, font=("Consolas", 13), border_width=1)
        self.vault_display.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Status Bar
        self.status_bar = ctk.CTkLabel(self.main_frame, text="Status: Ready", font=ctk.CTkFont(size=11), text_color="gray")
        self.status_bar.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.refresh_list()

    def update_status(self, msg, color="gray"):
        self.status_bar.configure(text=f"Status: {msg}", text_color=color)

    def refresh_list(self):
        self.vault_display.configure(state="normal")
        self.vault_display.delete("1.0", "end")
        files = list_secured_files()
        
        header = f"{'VAULT ID':<25} | {'ORIGINAL FILENAME':<30}\n"
        separator = "-" * 60 + "\n"
        self.vault_display.insert("end", header + separator)

        for f in files:
            line = f"{f['vault_name']:<25} | {f['original_name']:<30}\n"
            self.vault_display.insert("end", line)
        
        self.vault_display.configure(state="disabled")
        self.update_status("Vault list updated.")

    def ui_secure_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            password = ctk.CTkInputDialog(text="Enter Master Password:", title="Zero-Trust Auth").get_input()
            if password:
                try:
                    self.update_status("Encrypting...", "blue")
                    save_file(file_path, password)
                    messagebox.showinfo("Success", "Asset secured in vault.")
                    self.refresh_list()
                    self.update_status("Asset secured.", "green")
                except Exception as e:
                    messagebox.showerror("Security Error", str(e))
                    self.update_status("Encryption failed.", "red")

    def ui_extract_file(self):
        vault_id = ctk.CTkInputDialog(text="Paste Vault ID:", title="Extraction").get_input()
        if vault_id:
            password = ctk.CTkInputDialog(text="Enter Master Password:", title="Zero-Trust Auth").get_input()
            if password:
                try:
                    self.update_status("Decrypting...", "blue")
                    path = extract_file(vault_id, password)
                    messagebox.showinfo("Success", f"File restored to current directory.")
                    self.update_status("Decryption successful.", "green")
                except Exception as e:
                    messagebox.showerror("Security Error", "Decryption failed. Check password/ID.")
                    self.update_status("Decryption failed.", "red")

if __name__ == "__main__":
    app = ComradeApp()
    app.mainloop()
