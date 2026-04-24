import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.file_manager import save_file, extract_file, list_secured_files

class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("COMRADE: Zero-Trust Vault")
        self.geometry("800x500")
        
        # UI Elements
        self.label = ctk.CTkLabel(self, text="COMRADE SECURE VAULT", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        self.btn_secure = ctk.CTkButton(self, text="Secure New File", command=self.ui_secure_file)
        self.btn_secure.pack(pady=10)

        self.btn_extract = ctk.CTkButton(self, text="Decrypt/Extract File", command=self.ui_extract_file)
        self.btn_extract.pack(pady=10)

        # A simple list to show files
        self.file_list = ctk.CTkTextbox(self, width=600, height=200)
        self.file_list.pack(pady=20)
        self.refresh_list()

    def refresh_list(self):
        self.file_list.delete("1.0", "end")
        files = list_secured_files()
        for f in files:
            self.file_list.insert("end", f"{f['vault_name']} -> {f['original_name']}\n")

    def ui_secure_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            password = ctk.CTkInputDialog(text="Enter Master Password:", title="Security Check").get_input()
            if password:
                try:
                    save_file(file_path, password)
                    messagebox.showinfo("Success", "File locked in vault!")
                    self.refresh_list()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def ui_extract_file(self):
        vault_id = ctk.CTkInputDialog(text="Enter Vault ID (from list):", title="Decrypt").get_input()
        if vault_id:
            password = ctk.CTkInputDialog(text="Enter Master Password:", title="Security Check").get_input()
            if password:
                try:
                    path = extract_file(vault_id, password)
                    messagebox.showinfo("Success", f"File restored to: {path}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = ComradeApp()
    app.mainloop()
