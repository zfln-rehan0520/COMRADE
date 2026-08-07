import tkinter as tk
from tkinter import messagebox
import threading
from core.inviter import send_chatroom_invite

class InviteModal(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("COMRADE - Send Invitation")
        self.geometry("460x400")
        self.configure(bg="#0b1329")  # Matching COMRADE dark theme
        self.resizable(False, False)
        
        # Center modal over main window
        self.transient(parent)
        self.grab_set()

        # Header
        tk.Label(
            self, 
            text="📡 DISPATCH CHATROOM INVITE", 
            font=("Consolas", 12, "bold"), 
            fg="#38bdf8", 
            bg="#0b1329"
        ).pack(pady=(22, 15))

        # Recipient Email Input
        tk.Label(self, text="Recipient Email:", font=("Consolas", 9, "bold"), fg="#94a3b8", bg="#0b1329").pack(anchor="w", padx=35)
        self.email_entry = tk.Entry(self, font=("Consolas", 10), bg="#1e293b", fg="#ffffff", insertbackground="white", relief="flat")
        self.email_entry.pack(fill="x", padx=35, pady=(2, 12), ipady=6)

        # Target Room Input
        tk.Label(self, text="Target Channel Name:", font=("Consolas", 9, "bold"), fg="#94a3b8", bg="#0b1329").pack(anchor="w", padx=35)
        self.room_entry = tk.Entry(self, font=("Consolas", 10), bg="#1e293b", fg="#ffffff", insertbackground="white", relief="flat")
        self.room_entry.insert(0, "#stealth-ops")
        self.room_entry.pack(fill="x", padx=35, pady=(2, 12), ipady=6)

        # Target Link Input
        tk.Label(self, text="Chatroom Link:", font=("Consolas", 9, "bold"), fg="#94a3b8", bg="#0b1329").pack(anchor="w", padx=35)
        self.link_entry = tk.Entry(self, font=("Consolas", 10), bg="#1e293b", fg="#ffffff", insertbackground="white", relief="flat")
        self.link_entry.insert(0, "http://127.0.0.1:6667")
        self.link_entry.pack(fill="x", padx=35, pady=(2, 18), ipady=6)

        # Submit Button
        self.send_btn = tk.Button(
            self, 
            text="DISPATCH INVITATION", 
            font=("Consolas", 10, "bold"), 
            bg="#0284c7", 
            fg="white", 
            activebackground="#0369a1", 
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.start_dispatch
        )
        self.send_btn.pack(fill="x", padx=35, ipady=8)

        # Status Line
        self.status_label = tk.Label(self, text="", font=("Consolas", 9), fg="#94a3b8", bg="#0b1329")
        self.status_label.pack(pady=12)

    def start_dispatch(self):
        email = self.email_entry.get().strip()
        room = self.room_entry.get().strip()
        link = self.link_entry.get().strip()

        if not email or not room or not link:
            messagebox.showwarning("Input Required", "Please fill in all fields.", parent=self)
            return

        self.send_btn.config(state="disabled", text="DISPATCHING...")
        self.status_label.config(text="Sending invitation...", fg="#38bdf8")

        # Run send logic in background thread to avoid freezing UI
        threading.Thread(
            target=self._send_in_background, 
            args=(email, room, link), 
            daemon=True
        ).start()

    def _send_in_background(self, email, room, link):
        result = send_chatroom_invite(
            recipient_email=email,
            chatroom_name=room,
            chatroom_link=link,
            client_ip="127.0.0.1"
        )
        self.after(0, lambda: self._on_dispatch_complete(result))

    def _on_dispatch_complete(self, result):
        self.send_btn.config(state="normal", text="DISPATCH INVITATION")
        if result.get("success"):
            operator = result.get("operator", "Operator")
            messagebox.showinfo("Success", f"Invitation sent successfully!\n\nLogged as: {operator}", parent=self)
            self.destroy()
        else:
            error_msg = result.get("error", "Unknown error.")
            self.status_label.config(text="Dispatch Failed", fg="#ef4444")
            messagebox.showerror("Dispatch Error", f"Error: {error_msg}", parent=self)