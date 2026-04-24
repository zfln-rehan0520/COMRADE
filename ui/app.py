import customtkinter as ctk
from core.file_manager import list_secured_files

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("COMRADE - Secure Vault")
        self.geometry("700x450")

        # Layout Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="COMRADE", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20, padx=10)

        self.btn_secure = ctk.CTkButton(self.sidebar, text="Secure File", command=self.secure_file_event)
        self.btn_secure.pack(pady=10, padx=10)

        # Main Dashboard Area
        self.main_frame = ctk.CTkScrollableFrame(self, label_text="Your Secured Vault")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.refresh_vault()

    def refresh_vault(self):
        """Clears and reloads the file list in the UI."""
        files = list_secured_files()
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if not files:
            label = ctk.CTkLabel(self.main_frame, text="No files found in vault.")
            label.pack(pady=20)
        else:
            for f in files:
                btn = ctk.CTkButton(self.main_frame, text=f['original_name'], fg_color="transparent", border_width=1)
                btn.pack(pady=5, fill="x")

    def secure_file_event(self):
        # Placeholder for the file selection dialog
        print("Secure File button clicked")

if __name__ == "__main__":
    app = ComradeApp()
    app.mainloop()
