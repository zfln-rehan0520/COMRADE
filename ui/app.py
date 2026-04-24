import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage # Add PhotoImage here
from core.file_manager import save_file, extract_file, list_secured_files
import os

# Emerald Enterprise Theme Logic
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green") 

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- PROFESSIONAL ICON SETUP ---
        self.title("COMRADE | Secure Repository")
        self.geometry("1100x750")
        self.configure(fg_color="#09090B")

        try:
            # 1. Load the green icon (Ensure you have a logo.png in your folder)
            # If you don't have one, I can help you generate it!
            app_icon = PhotoImage(file='assets/logo.png') 
            
            # 2. Set icon for the window title bar
            self.wm_iconphoto(False, app_icon) 
            
            # 3. Set icon for the taskbar (Windows specific fix)
            self.after(200, lambda: self.iconphoto(False, app_icon))
        except Exception as e:
            print(f"Icon Load Failed: {e}")

        # --- REST OF HEADER LOGIC ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=(40, 20))
        # ... rest of your code ...
