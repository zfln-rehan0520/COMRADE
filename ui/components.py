import customtkinter as ctk

class PasswordDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Enter Password", callback=None):
        super().__init__(master)
        self.title(title)
        self.geometry("300x150")
        self.callback = callback

        self.label = ctk.CTkLabel(self, text="Master Password:")
        self.label.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.pack(pady=10, padx=20, fill="x")

        self.submit_btn = ctk.CTkButton(self, text="Unlock", command=self.submit)
        self.submit_btn.pack(pady=10)

    def submit(self):
        password = self.password_entry.get()
        if self.callback:
            self.callback(password)
        self.destroy()
