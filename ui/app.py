import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage
from tkcalendar import DateEntry
import pytz
import os
import socket
import threading
import traceback
import webbrowser
import json
from datetime import datetime

from core.file_manager import save_file, extract_file, list_secured_files, delete_vault_file
from network.comrade_irc import ComradeComms
from ai.engine import ComradeAI
from core.encryption import encrypt_text, decrypt_text
from ui.pass_vault import SecurePassVault
from core.inviter import send_chatroom_invite, get_limit_status

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- ENTERPRISE SOC COLOR PALETTE ---
BG_MAIN = "#0d1117"       
BG_SURFACE = "#11161d"    
BG_SURFACE_LIGHT = "#1e242b" 
ACCENT = "#38bdf8"        
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#64748b"
DANGER = "#EF4444"
SUCCESS = "#4ade80"

# --- GLOBAL SINGLETON STATE FOR AI ENGINE ---
global_comrade_ai = None
_ai_boot_in_progress = False


class InviteWindow(ctk.CTkToplevel):
    """Isolated Top-Level Window for Dispatching Chatroom Invitations with Interactive Date, Time, and Timezone Pickers"""
    def __init__(self, master):
        super().__init__(master)
        
        self.title("COMRADE | Dispatch Invitation")
        self.geometry("540x740")
        self.configure(fg_color=BG_MAIN)
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # Header
        tk_title = ctk.CTkLabel(
            self, text="📡 DISPATCH CHATROOM INVITE",
            font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
            text_color=ACCENT
        )
        tk_title.pack(pady=(20, 10))

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # 1. Recipient Email Input
        ctk.CTkLabel(scroll_frame, text="Recipient Email *:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=10)
        self.email_entry = ctk.CTkEntry(scroll_frame, placeholder_text="target@domain.com", fg_color=BG_SURFACE, border_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, height=36)
        self.email_entry.pack(fill="x", padx=10, pady=(2, 8))

        # 2. Host Input (User Entered)
        ctk.CTkLabel(scroll_frame, text="Host *:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=10)
        self.host_entry = ctk.CTkEntry(scroll_frame, placeholder_text="organizer name", fg_color=BG_SURFACE, border_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, height=36)
        self.host_entry.pack(fill="x", padx=10, pady=(2, 8))

        # 3. Chat Room Name Input (User Entered)
        ctk.CTkLabel(scroll_frame, text="Chat Room Name *:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=10)
        self.room_entry = ctk.CTkEntry(scroll_frame, placeholder_text="anonymous", fg_color=BG_SURFACE, border_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, height=36)
        self.room_entry.pack(fill="x", padx=10, pady=(2, 8))

        # --- 4. CALENDAR DATE SELECTION ---
        ctk.CTkLabel(scroll_frame, text="Date (Calendar Picker) *:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=10)
        
        date_container = ctk.CTkFrame(scroll_frame, fg_color=BG_SURFACE, border_width=1, border_color=BG_SURFACE_LIGHT, height=38)
        date_container.pack(fill="x", padx=10, pady=(2, 8))
        date_container.pack_propagate(False)

        self.date_picker = DateEntry(
            date_container, 
            date_pattern="yyyy-mm-dd",
            background="#1e242b", 
            foreground="#ffffff", 
            headersbackground="#0d1117",
            headersforeground="#38bdf8",
            bordercolor="#1e242b",
            normalbackground="#11161d",
            normalforeground="#ffffff",
            selectbackground="#0369a1",
            selectforeground="#ffffff",
            font=("Consolas", 10)
        )
        self.date_picker.pack(fill="both", expand=True, padx=5, pady=5)

        # --- 5. TIME SCROLL SELECTION (HH : MM : AM/PM) ---
        ctk.CTkLabel(scroll_frame, text="Time Selection *:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=10)
        
        time_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        time_frame.pack(fill="x", padx=10, pady=(2, 8))

        now = datetime.now()
        cur_hour = now.strftime("%I")
        cur_minute = f"{round(now.minute / 5) * 5:02d}"
        if cur_minute == "60": cur_minute = "55"
        cur_ampm = now.strftime("%p")

        # Hours Dropdown
        hours = [f"{i:02d}" for i in range(1, 13)]
        self.hour_option = ctk.CTkOptionMenu(time_frame, values=hours, fg_color=BG_SURFACE, button_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, width=80)
        self.hour_option.set(cur_hour)
        self.hour_option.pack(side="left", padx=(0, 5))

        ctk.CTkLabel(time_frame, text=":", font=ctk.CTkFont(size=14, weight="bold"), text_color=ACCENT).pack(side="left", padx=2)

        # Minutes Dropdown
        minutes = [f"{i:02d}" for i in range(0, 60, 5)]
        self.minute_option = ctk.CTkOptionMenu(time_frame, values=minutes, fg_color=BG_SURFACE, button_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, width=80)
        self.minute_option.set(cur_minute)
        self.minute_option.pack(side="left", padx=5)

        # AM / PM Dropdown
        self.ampm_option = ctk.CTkOptionMenu(time_frame, values=["AM", "PM"], fg_color=BG_SURFACE, button_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, width=80)
        self.ampm_option.set(cur_ampm)
        self.ampm_option.pack(side="left", padx=(5, 0))

        # --- 6. GLOBAL TIMEZONE SELECTOR ---
        ctk.CTkLabel(scroll_frame, text="Global Region / Timezone *:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=10)
        
        all_timezones = sorted(pytz.all_timezones)
        common_tzs = ["Asia/Kolkata (IST)", "UTC", "America/New_York (EST)", "Europe/London (GMT)", "Asia/Tokyo (JST)", "Australia/Sydney (AEST)"] + all_timezones

        self.tz_option = ctk.CTkOptionMenu(
            scroll_frame, 
            values=common_tzs, 
            fg_color=BG_SURFACE, 
            button_color=BG_SURFACE_LIGHT, 
            text_color=TEXT_PRIMARY,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_SURFACE_LIGHT,
            height=36
        )
        self.tz_option.set("Asia/Kolkata (IST)")
        self.tz_option.pack(fill="x", padx=10, pady=(2, 8))

        # 7. Message Body Input with Smart Placeholder
        ctk.CTkLabel(scroll_frame, text="Message (Body Section) *:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=10)
        self.msg_textbox = ctk.CTkTextbox(scroll_frame, fg_color=BG_SURFACE, border_color=BG_SURFACE_LIGHT, text_color="#64748b", height=80)
        
        self.placeholder_text = "Join us for a secure operative briefing..."
        self.msg_textbox.insert("1.0", self.placeholder_text)
        self.msg_textbox.pack(fill="x", padx=10, pady=(2, 12))

        def _on_focus_in(event):
            if self.msg_textbox.get("1.0", "end-1c") == self.placeholder_text:
                self.msg_textbox.delete("1.0", "end")
                self.msg_textbox.configure(text_color=TEXT_PRIMARY)

        def _on_focus_out(event):
            if not self.msg_textbox.get("1.0", "end-1c").strip():
                self.msg_textbox.insert("1.0", self.placeholder_text)
                self.msg_textbox.configure(text_color="#64748b")

        self.msg_textbox.bind("<FocusIn>", _on_focus_in)
        self.msg_textbox.bind("<FocusOut>", _on_focus_out)

        # Quota Indicator & Reset Timer Label
        self.quota_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color=ACCENT)
        self.quota_label.pack(pady=(5, 2))
        self.update_quota_ui()

        # Dispatch Button
        self.send_btn = ctk.CTkButton(
            self, text="SEND INVITATION", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0369a1", hover_color="#0284c7", text_color=TEXT_PRIMARY,
            height=42, command=self.start_dispatch
        )
        self.send_btn.pack(fill="x", padx=30, pady=(5, 5))

        # Status Line
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY)
        self.status_label.pack(pady=(0, 10))

    def update_quota_ui(self):
        """Refreshes remaining quota and countdown display."""
        remaining, reset_in, _ = get_limit_status()
        self.quota_label.configure(text=f"Quota Remaining: {remaining}/5  •  Resets in: {reset_in}")

    def start_dispatch(self):
        email = self.email_entry.get().strip()
        host = self.host_entry.get().strip()
        room = self.room_entry.get().strip()
        
        # Combine Calendar date, Time scroll options, and Timezone
        date_str = self.date_picker.get_date().strftime("%Y-%m-%d")
        time_str = f"{self.hour_option.get()}:{self.minute_option.get()} {self.ampm_option.get()} {self.tz_option.get()}"
        
        msg_body = self.msg_textbox.get("1.0", "end-1c").strip()
        if msg_body == self.placeholder_text:
            msg_body = ""

        # Enforce mandatory field checks
        if not email or not host or not room or not date_str or not time_str or not msg_body:
            messagebox.showwarning("Mandatory Fields Blank", "All fields are mandatory. Please complete every field.", parent=self)
            return

        remaining, reset_in, is_allowed = get_limit_status()
        if not is_allowed:
            messagebox.showerror("Quota Exceeded", f"Daily dispatch limit reached (0/5 remaining).\n\nResets in: {reset_in}", parent=self)
            return

        self.send_btn.configure(state="disabled", text="DISPATCHING...")
        self.status_label.configure(text="Sending Invitation...", text_color=ACCENT)

        threading.Thread(
            target=self._send_in_background,
            args=(email, host, room, date_str, time_str, msg_body),
            daemon=True
        ).start()

    def _send_in_background(self, email, host, room, date_str, time_str, msg_body):
        result = send_chatroom_invite(
            recipient_email=email,
            host_url=host,
            chatroom_name=room,
            event_date=date_str,
            event_time=time_str,
            custom_message=msg_body,
            app_user_name="Operator"
        )
        self.after(0, lambda: self._on_dispatch_complete(result))

    def _on_dispatch_complete(self, result):
        self.send_btn.configure(state="normal", text="SEND INVITATION")
        self.update_quota_ui()
        
        if result.get("success"):
            messagebox.showinfo("Success", "Invitation dispatched successfully!", parent=self)
            self.destroy()
        else:
            error_msg = result.get("error", "Unknown error.")
            self.status_label.configure(text="Dispatch Failed", text_color=DANGER)
            messagebox.showerror("Dispatch Error", f"Failed to send invite:\n\n{error_msg}", parent=self)


class CommsWindow(ctk.CTkToplevel):
    """Isolated Top-Level Window for the Secure IRC Sidecar"""
    def __init__(self, master):
        super().__init__(master)
        
        self.title("COMRADE | Secure Relay")
        self.geometry("750x550")
        self.configure(fg_color=BG_MAIN)
        self.attributes("-topmost", True)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        self.nick_entry = ctk.CTkEntry(
            top_frame, placeholder_text="Operator Handle (e.g. Spectre)",
            fg_color=BG_SURFACE, border_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, height=35
        )
        self.nick_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.key_entry = ctk.CTkEntry(
            top_frame, placeholder_text="Room Secret Key", show="*",
            fg_color=BG_SURFACE, border_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, height=35
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        
        self.connect_btn = ctk.CTkButton(
            top_frame, text="CONNECT TO RELAY", font=("Inter", 12, "bold"),
            fg_color=BG_SURFACE_LIGHT, hover_color=ACCENT, text_color=TEXT_PRIMARY,
            height=35, command=self.toggle_connection
        )
        self.connect_btn.pack(side="right")

        self.chat_log = ctk.CTkTextbox(
            self, state="disabled", wrap="word", fg_color=BG_SURFACE,
            text_color=TEXT_SECONDARY, font=("Consolas", 13)
        )
        self.chat_log.pack(pady=10, padx=20, fill="both", expand=True)

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(pady=(10, 20), padx=20, fill="x")
        
        self.msg_entry = ctk.CTkEntry(
            bottom_frame, placeholder_text="Type encrypted payload...", fg_color=BG_SURFACE,
            border_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, height=40
        )
        self.msg_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self.send_chat_message())
        
        self.send_btn = ctk.CTkButton(
            bottom_frame, text="TRANSMIT", font=("Inter", 12, "bold"), fg_color=ACCENT,
            hover_color="#0284c7", text_color=BG_MAIN, height=40, command=self.send_chat_message
        )
        self.send_btn.pack(side="right")

        self.comms = ComradeComms(
            server="127.0.0.1", port=6667, channel="#secure",
            ui_callback=self.update_chat_ui, encrypt_func=encrypt_text, decrypt_func=decrypt_text  
        )
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_connection(self):
        if not self.comms.running:
            secret = self.key_entry.get().strip()
            handle = self.nick_entry.get().strip() or "Operator"

            if not secret:
                messagebox.showwarning("Connection Denied", "Room Secret Key cannot be blank.", parent=self)
                return
            
            success, msg = self.comms.connect(secret_key=secret, nickname=handle)
            if success:
                self.connect_btn.configure(text="DISCONNECT", fg_color=DANGER, hover_color="#C53030")
                self.key_entry.configure(state="disabled")
                self.nick_entry.configure(state="disabled")
                self.update_chat_ui(f"[SYSTEM]: SECURE LINK ESTABLISHED AS '{handle}'.")
            else:
                self.update_chat_ui(f"[SYSTEM ERROR]: {msg}")
        else:
            self.comms.disconnect()
            self.connect_btn.configure(text="CONNECT TO RELAY", fg_color=BG_SURFACE_LIGHT, hover_color=ACCENT)
            self.key_entry.configure(state="normal")
            self.nick_entry.configure(state="normal")
            self.update_chat_ui("[SYSTEM]: CONNECTION SEVERED.")

    def send_chat_message(self):
        msg = self.msg_entry.get().strip()
        if not self.comms.running:
            self.update_chat_ui("[ERROR]: NOT CONNECTED TO RELAY.")
            return
            
        if msg:
            success, err = self.comms.send_message(msg)
            if success:
                self.msg_entry.delete(0, 'end')
            else:
                self.update_chat_ui(f"[ERROR]: {err}")

    def update_chat_ui(self, message):
        def _update():
            self.chat_log.configure(state="normal")
            self.chat_log.insert("end", message + "\n")
            self.chat_log.configure(state="disabled")
            self.chat_log.yview("end") 
        self.after(0, _update)

    def on_close(self):
        if self.comms.running:
            self.comms.disconnect()
        self.destroy()


class FileCard(ctk.CTkFrame):
    def __init__(self, master, vault_id, original_name, extract_cb, delete_cb):
        super().__init__(master, fg_color=BG_SURFACE_LIGHT, corner_radius=6)
        self.pack(fill="x", padx=10, pady=5)
        
        safe_id = str(vault_id)
        display_id = safe_id[:12] + "..." if len(safe_id) > 12 else safe_id
        
        raw_name = str(original_name) if original_name else "Encrypted Asset"
        clean_name = os.path.basename(raw_name)
        display_name = clean_name[:28] + "..." if len(clean_name) > 28 else clean_name

        self.btn_delete = ctk.CTkButton(
            self, text="WIPE", width=60, height=28, font=("Inter", 11, "bold"),
            fg_color="transparent", hover_color="#3F1D1D", text_color=DANGER,
            border_width=1, border_color=DANGER, corner_radius=4,
            command=lambda v=safe_id: delete_cb(v)
        )
        self.btn_delete.pack(side="right", padx=(5, 15), pady=10)

        self.btn_extract = ctk.CTkButton(
            self, text="EXTRACT", width=80, height=28, font=("Inter", 11, "bold"),
            fg_color="#0369a1", hover_color="#0284c7", text_color=TEXT_PRIMARY,
            corner_radius=4, command=lambda v=safe_id: extract_cb(v)
        )
        self.btn_extract.pack(side="right", padx=5, pady=10)

        self.id_label = ctk.CTkLabel(self, text=display_id, font=("Consolas", 12), text_color=TEXT_SECONDARY)
        self.id_label.pack(side="left", padx=(15, 10), pady=10)
        
        self.name_label = ctk.CTkLabel(self, text=display_name, font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY)
        self.name_label.pack(side="left", padx=10, pady=10)


class ComradeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("COMRADE | Cyber Operations Module for Resilient Authentication and Data Encryption")
        self.geometry("1280x750")
        self.configure(fg_color=BG_MAIN)

        self.loaded_cards = []
        self.empty_msg = None

        try:
            self.icon_path = os.path.join(os.getcwd(), "assets", "logo.png")
            self.icon_img = PhotoImage(file=self.icon_path)
            self.iconphoto(True, self.icon_img)
        except Exception: 
            pass

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.setup_sidebar()
        self.setup_main_content()
        self.refresh_all_cards()

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=BG_SURFACE, border_width=1, border_color=BG_SURFACE_LIGHT)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(12, weight=1) 

        # Brand Title Header
        self.brand_label = ctk.CTkLabel(
            self.sidebar_frame, text="COMRADE\nA Brother That Guards Your Data", 
            font=ctk.CTkFont(family="Trebuchet MS", size=16, weight="bold"), text_color=ACCENT, justify="left"
        )
        self.brand_label.grid(row=0, column=0, padx=20, pady=(25, 10), sticky="w")

        # Line Under Brand Title
        self.brand_separator = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color=BG_SURFACE_LIGHT)
        self.brand_separator.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        # --- RE-ORDERED NAVIGATION BUTTONS ---
        # 1. DASHBOARD (Centered Text)
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar_frame, text="DASHBOARD", fg_color="#183b5e", hover_color=BG_SURFACE_LIGHT,
            text_color=ACCENT, anchor="center", height=38, corner_radius=6,
            command=self.nav_dashboard
        )
        self.btn_dashboard.grid(row=2, column=0, padx=15, pady=2, sticky="ew")

        # 2. SECUREPASS
        self.btn_secure_pass = ctk.CTkButton(
            self.sidebar_frame, text="SECUREPASS", fg_color="transparent", hover_color=BG_SURFACE_LIGHT,
            text_color=TEXT_PRIMARY, anchor="w", height=38, corner_radius=6,
            command=self.nav_secure_pass
        )
        self.btn_secure_pass.grid(row=3, column=0, padx=15, pady=2, sticky="ew")

        # 3. COMRADE AI
        self.btn_ai = ctk.CTkButton(
            self.sidebar_frame, text="COMRADE AI", fg_color="transparent", hover_color=BG_SURFACE_LIGHT,
            text_color=TEXT_PRIMARY, anchor="w", height=38, corner_radius=6,
            command=self.nav_ai_terminal
        )
        self.btn_ai.grid(row=4, column=0, padx=15, pady=2, sticky="ew")

        # 4. CHAT ROOM
        self.btn_comms = ctk.CTkButton(
            self.sidebar_frame, text="CHAT ROOM", fg_color="transparent", hover_color=BG_SURFACE_LIGHT,
            text_color=TEXT_PRIMARY, anchor="w", height=38, corner_radius=6,
            command=self.nav_comms_terminal
        )
        self.btn_comms.grid(row=5, column=0, padx=15, pady=2, sticky="ew")

        # 5. SEND INVITATION
        self.btn_invitation = ctk.CTkButton(
            self.sidebar_frame, text="SEND INVITATION", fg_color="transparent", hover_color=BG_SURFACE_LIGHT,
            text_color=TEXT_PRIMARY, anchor="w", height=38, corner_radius=6,
            command=self.nav_send_invitation
        )
        self.btn_invitation.grid(row=6, column=0, padx=15, pady=2, sticky="ew")

        # Bottom-pinned navigation
        self.btn_github = ctk.CTkButton(
            self.sidebar_frame, text="GITHUB", fg_color="transparent", hover_color=BG_SURFACE_LIGHT,
            text_color=TEXT_PRIMARY, anchor="w", height=32, command=self.open_github
        )
        self.btn_github.grid(row=13, column=0, padx=15, pady=1, sticky="ew")

        self.btn_docs = ctk.CTkButton(
            self.sidebar_frame, text="DOCUMENTATION", fg_color="transparent", hover_color=BG_SURFACE_LIGHT,
            text_color=TEXT_PRIMARY, anchor="w", height=32, command=self.open_docs
        )
        self.btn_docs.grid(row=14, column=0, padx=15, pady=1, sticky="ew")

        self.footer_label = ctk.CTkLabel(
            self.sidebar_frame, text="COMRADE v1.20\nOpen Source", 
            text_color=TEXT_SECONDARY, justify="left", font=ctk.CTkFont(size=11)
        )
        self.footer_label.grid(row=15, column=0, padx=25, pady=(10, 25), sticky="w")

    def set_active_nav_button(self, active_btn):
        """Resets all navigation buttons and highlights the active clicked button."""
        nav_buttons = [
            self.btn_dashboard, 
            self.btn_secure_pass, 
            self.btn_ai, 
            self.btn_comms, 
            self.btn_invitation
        ]
        
        for btn in nav_buttons:
            if btn == active_btn:
                btn.configure(fg_color="#183b5e", text_color=ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_PRIMARY)

    def nav_dashboard(self):
        self.set_active_nav_button(self.btn_dashboard)
        self.update_status("Dashboard Active", SUCCESS)
        self.refresh_all_cards()

    def nav_secure_pass(self):
        self.set_active_nav_button(self.btn_secure_pass)
        self.open_secure_pass()

    def nav_ai_terminal(self):
        self.set_active_nav_button(self.btn_ai)
        self.open_ai_terminal()

    def nav_comms_terminal(self):
        self.set_active_nav_button(self.btn_comms)
        self.open_comms_terminal()

    def nav_send_invitation(self):
        self.set_active_nav_button(self.btn_invitation)
        self.send_invitation()

    def setup_main_content(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=35, pady=30)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1) 

        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)

        welcome_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        welcome_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(welcome_frame, text="Welcome back,", text_color=TEXT_SECONDARY, font=ctk.CTkFont(size=14)).pack(anchor="w")
        ctk.CTkLabel(welcome_frame, text="Operator.", text_color=TEXT_PRIMARY, font=ctk.CTkFont(size=36, weight="bold")).pack(anchor="w")

        self.status_indicator = ctk.CTkLabel(self.header_frame, text="● SYSTEM SECURE", text_color=SUCCESS, font=ctk.CTkFont(size=12, weight="bold"))
        self.status_indicator.grid(row=0, column=1, sticky="e")

        # --- 4 STATUS CARDS CONTAINER ---
        self.cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.val_assets = ctk.StringVar(value="0")
        self.val_passwords = ctk.StringVar(value="0")
        self.val_ai_status = ctk.StringVar(value="Checking...")
        self.val_irc_status = ctk.StringVar(value="Checking...")

        self.sub_assets = ctk.StringVar(value="Active files")
        self.sub_passwords = ctk.StringVar(value="Stored Passwords")
        self.sub_ai_status = ctk.StringVar(value="Local Engine")
        self.sub_irc_status = ctk.StringVar(value="Port 6667")

        # Build Cards
        self.card0 = self.build_status_card(0, "SECURED ASSETS", self.val_assets, self.sub_assets, self.refresh_vault)
        self.card1 = self.build_status_card(1, "PASSWORDS SECURED", self.val_passwords, self.sub_passwords, self.refresh_passwords_card)
        self.card2 = self.build_status_card(2, "COMRADE AI STATUS", self.val_ai_status, self.sub_ai_status, self.refresh_ai_card)
        self.card3 = self.build_status_card(3, "CHAT ROOM RELAY", self.val_irc_status, self.sub_irc_status, self.refresh_irc_card)

        # Secured Repository Frame
        self.repo_outer = ctk.CTkFrame(self.main_frame, fg_color=BG_SURFACE, corner_radius=8, border_width=1, border_color=BG_SURFACE_LIGHT)
        self.repo_outer.grid(row=2, column=0, sticky="nsew")
        self.repo_outer.grid_rowconfigure(1, weight=1)
        self.repo_outer.grid_columnconfigure(0, weight=1)

        repo_header = ctk.CTkFrame(self.repo_outer, fg_color="transparent", height=50)
        repo_header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(repo_header, text="Secured Repository", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
        
        self.btn_secure_new = ctk.CTkButton(
            repo_header, text="+ Secure New Asset", fg_color="#0369a1", hover_color="#0284c7",
            font=ctk.CTkFont(weight="bold"), height=34, command=self.ui_secure_file
        )
        self.btn_secure_new.pack(side="right")
        
        self.btn_refresh = ctk.CTkButton(
            repo_header, text="↺", width=42, height=34, font=("Inter", 16, "bold"),
            fg_color="transparent", border_width=1, border_color=BG_SURFACE_LIGHT,
            hover_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, corner_radius=6,
            command=self.refresh_vault
        )
        self.btn_refresh.pack(side="right", padx=10)

        self.container = ctk.CTkScrollableFrame(self.repo_outer, fg_color="transparent")
        self.container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def build_status_card(self, col, title, value_var, subtext_var, refresh_cmd):
        card = ctk.CTkFrame(self.cards_frame, fg_color=BG_SURFACE, corner_radius=8, border_width=1, border_color=BG_SURFACE_LIGHT)
        card.grid(row=0, column=col, padx=(0 if col==0 else 5, 0 if col==3 else 5), sticky="ew")

        card_top = ctk.CTkFrame(card, fg_color="transparent")
        card_top.pack(fill="x", padx=12, pady=(12, 2))

        lbl_title = ctk.CTkLabel(card_top, text=title, text_color=ACCENT, font=ctk.CTkFont(size=10, weight="bold"))
        lbl_title.pack(side="left")

        btn_card_refresh = ctk.CTkButton(
            card_top, text="↺", width=34, height=28, font=("Inter", 15, "bold"),
            fg_color="transparent", border_width=1, border_color=BG_SURFACE_LIGHT,
            hover_color=BG_SURFACE_LIGHT, text_color=TEXT_PRIMARY, corner_radius=6,
            command=refresh_cmd
        )
        btn_card_refresh.pack(side="right")

        lbl_val = ctk.CTkLabel(card, textvariable=value_var, text_color=TEXT_PRIMARY, font=ctk.CTkFont(size=22, weight="bold"))
        lbl_val.pack(anchor="w", padx=12)

        lbl_sub = ctk.CTkLabel(card, textvariable=subtext_var, text_color=TEXT_SECONDARY, font=ctk.CTkFont(size=11))
        lbl_sub.pack(anchor="w", padx=12, pady=(0, 12))

        return card

    def refresh_all_cards(self):
        self.refresh_vault()
        self.refresh_passwords_card()
        self.refresh_ai_card()
        self.refresh_irc_card()

    def refresh_passwords_card(self):
        try:
            vault_dir = os.path.join(os.getcwd(), "vault")
            possible_files = ["credentials.json", "passwords.json", "passwords.dat", "vault.json"]
            count = 0
            found_vault = False

            for fname in possible_files:
                target_path = os.path.join(vault_dir, fname)
                if os.path.exists(target_path):
                    found_vault = True
                    try:
                        with open(target_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                count = len(data.keys())
                            elif isinstance(data, list):
                                count = len(data)
                        break
                    except Exception:
                        size = os.path.getsize(target_path)
                        if size > 0:
                            count = max(1, size // 64)
                        break

            if not found_vault and hasattr(self, 'pass_vault_instance'):
                if hasattr(self.pass_vault_instance, 'credentials'):
                    count = len(self.pass_vault_instance.credentials)

            self.val_passwords.set(str(count))
            self.sub_passwords.set("Stored Passwords" if count > 0 else "No Passwords")
        except Exception:
            self.val_passwords.set("0")
            self.sub_passwords.set("Vault Offline")

    def refresh_ai_card(self):
        global global_comrade_ai, _ai_boot_in_progress

        if global_comrade_ai is not None:
            self.val_ai_status.set("Online")
            self.sub_ai_status.set("Ollama Engine Ready")
            return

        if _ai_boot_in_progress:
            self.val_ai_status.set("Initialising")
            self.sub_ai_status.set("Booting Daemon...")
            return

        _ai_boot_in_progress = True
        self.val_ai_status.set("Initialising")
        self.sub_ai_status.set("Booting Daemon...")

        def _boot_worker():
            global global_comrade_ai, _ai_boot_in_progress
            try:
                global_comrade_ai = ComradeAI()
                self.after(0, lambda: self.val_ai_status.set("Online"))
                self.after(0, lambda: self.sub_ai_status.set("Ollama Engine Ready"))
            except Exception as e:
                print(f"[AI BOOT ERROR]: {e}")
                self.after(0, lambda: self.val_ai_status.set("Offline"))
                self.after(0, lambda: self.sub_ai_status.set("Service Stopped"))
            finally:
                _ai_boot_in_progress = False

        threading.Thread(target=_boot_worker, daemon=True).start()

    def refresh_irc_card(self):
        def _check():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5)
                res = s.connect_ex(("127.0.0.1", 6667))
                s.close()

                if res == 0:
                    self.val_irc_status.set("Online")
                    self.sub_irc_status.set("Stealth Relay Ready")
                else:
                    self.val_irc_status.set("Standby")
                    self.sub_irc_status.set("Port 6667 Closed")
            except Exception:
                self.val_irc_status.set("Offline")
                self.sub_irc_status.set("Relay Unreachable")

        self.val_irc_status.set("Scanning...")
        threading.Thread(target=_check, daemon=True).start()

    def update_status(self, text, color=SUCCESS):
        self.status_indicator.configure(text=f"● {text.upper()}", text_color=color)

    def send_invitation(self):
        """Launches the updated invitation modal dialog."""
        InviteWindow(self)
        self.update_status("Invitation Terminal Active", ACCENT)

    def open_github(self):
        webbrowser.open("https://github.com")

    def open_docs(self):
        webbrowser.open("https://github.com")

    def open_secure_pass(self):
        self.pass_vault_instance = SecurePassVault(self)
        self.update_status("Credential Vault Active", ACCENT)
        self.refresh_passwords_card()
        
    def open_comms_terminal(self):
        CommsWindow(self)
        self.update_status("Secure Relay Active", ACCENT)
        self.refresh_irc_card()

    def open_ai_terminal(self):
        self.update_status("AI Subsystem Active", ACCENT)
        ai_window = ctk.CTkToplevel(self)
        ai_window.title("COMRADE AI Subsystem")
        ai_window.geometry("800x650")
        ai_window.configure(fg_color=BG_MAIN)
        ai_window.attributes("-topmost", True)

        chat_box = ctk.CTkTextbox(ai_window, fg_color=BG_SURFACE, text_color=TEXT_PRIMARY, 
                                font=("Inter", 14), border_width=1, border_color=BG_SURFACE_LIGHT, wrap="word")
        chat_box.pack(fill="both", expand=True, padx=30, pady=(30, 15))
        
        chat_box.tag_config("sys_label", foreground=TEXT_SECONDARY)
        chat_box.tag_config("user_label", foreground=TEXT_PRIMARY)
        chat_box.tag_config("ai_label", foreground=ACCENT)
        chat_box.tag_config("divider", foreground=BG_SURFACE_LIGHT)
        
        separator = "────────────────────────────────────────────────────────────────────────\n\n"
        chat_box.insert("end", "COMRADE AI (Beta)\n", "sys_label")
        chat_box.insert("end", "⚠️ COMRADE AI can make mistakes, Verify critical output.\n\n", "sys_label")
        chat_box.insert("end", separator, "divider")
        chat_box.configure(state="disabled")

        input_container = ctk.CTkFrame(ai_window, fg_color="transparent")
        input_container.pack(fill="x", padx=30, pady=(0, 30))

        input_frame = ctk.CTkFrame(input_container, fg_color=BG_SURFACE, corner_radius=8, 
                                   border_width=1, border_color=BG_SURFACE_LIGHT, height=50)
        input_frame.pack(fill="x", expand=True)
        input_frame.pack_propagate(False)

        entry = ctk.CTkEntry(input_frame, placeholder_text="Ask COMRADE anything...", 
                             font=("Inter", 13), fg_color="transparent", border_width=0, text_color=TEXT_PRIMARY)
        entry.pack(side="left", fill="both", expand=True, padx=(20, 10), pady=2)

        btn_send = ctk.CTkButton(input_frame, text="SEND ➔", width=70, height=35,
                                 fg_color="transparent", hover_color=BG_SURFACE_LIGHT, text_color=ACCENT, 
                                 font=("Inter", 12, "bold"), corner_radius=6)
        btn_send.pack(side="right", padx=(0, 8), pady=7)

        engine = global_comrade_ai if global_comrade_ai else ComradeAI()

        def gui_typewriter(text, index=0):
            if not ai_window.winfo_exists(): return 
            chat_box.configure(state="normal")
            if index < len(text):
                chat_box.insert("end", text[index])
                chat_box.see("end")
                chat_box.configure(state="disabled")
                ai_window.after(15, gui_typewriter, text, index + 1)
            else:
                chat_box.insert("end", f"\n\n{separator}", "divider")
                chat_box.configure(state="disabled")
                chat_box.see("end")
                entry.configure(state="normal")
                btn_send.configure(state="normal")
                entry.focus()

        def fetch_response_thread(user_text):
            sys_prompt = "You are COMRADE, an advanced cyber-operations AI. Keep answers concise, tactical, and highly technical."
            response = engine.ask(user_text, system_context=sys_prompt)
            ai_window.after(0, gui_typewriter, response)

        def send_message(event=None):
            user_text = entry.get()
            if not user_text.strip(): return
            
            entry.delete(0, "end")
            entry.configure(state="disabled")
            btn_send.configure(state="disabled")
            
            chat_box.configure(state="normal")
            chat_box.insert("end", "YOU: ", "user_label")
            chat_box.insert("end", f"{user_text}\n\n")
            chat_box.insert("end", "COMRADE: ", "ai_label")
            chat_box.configure(state="disabled")
            chat_box.see("end")
            threading.Thread(target=fetch_response_thread, args=(user_text,), daemon=True).start()

        btn_send.configure(command=send_message)
        entry.bind("<Return>", send_message)

    def refresh_vault(self):
        """Purges all widgets inside container before re-evaluating vault state."""
        for child in self.container.winfo_children():
            try:
                child.pack_forget()
                child.destroy()
            except Exception:
                pass

        self.loaded_cards.clear()
        self.empty_msg = None

        try:
            files = list_secured_files()
            valid_files = [f for f in files if f]
            
            if not valid_files:
                self.val_assets.set("0")
                self.update_status("System Secure", SUCCESS)
                self.empty_msg = ctk.CTkLabel(
                    self.container, 
                    text="Your vault is empty\nSecure and store your encrypted assets locally.", 
                    font=("Inter", 14), text_color=TEXT_SECONDARY
                )
                self.empty_msg.pack(pady=80)
            else:
                self.val_assets.set(str(len(valid_files)))
                for f in valid_files:
                    try:
                        if isinstance(f, dict):
                            v_id = str(f.get('vault_name', f.get('id', f.get('vault_id', 'Unknown'))))
                            o_name = str(f.get('original_name', f.get('name', f.get('filename', 'Encrypted Asset'))))
                        else:
                            v_id = str(f)
                            o_name = "Encrypted Asset"
                        
                        card = FileCard(self.container, v_id, o_name, 
                                        self.ui_extract_file, self.ui_delete_file)
                        self.loaded_cards.append(card)
                    except Exception as card_err:
                        print(f"[GUI WARNING] Skipped rendering card: {card_err}")

                self.update_status("System Secure", SUCCESS)
        except Exception as e:
            self.update_status("Vault Error", DANGER)
            print(f"\n[GUI ERROR] Vault Refresh Failed: {e}")
            traceback.print_exc()

    def ui_secure_file(self):
        path = filedialog.askopenfilename()
        if path:
            pw = ctk.CTkInputDialog(text="Create Master Key for Encryption:", title="Auth").get_input()
            if pw:
                def _worker():
                    try:
                        self.after(0, lambda: self.update_status("Securing Asset...", ACCENT))
                        save_file(path, pw)
                        self.after(0, self.refresh_vault)
                    except Exception as e:
                        self.after(0, lambda: messagebox.showerror("Error", str(e)))
                        self.after(0, lambda: self.update_status("Secure Failed", DANGER))

                threading.Thread(target=_worker, daemon=True).start()

    def ui_extract_file(self, vault_id):
        dialog = ctk.CTkInputDialog(text="ENTER MASTER KEY:", title="Auth Required")
        pw = dialog.get_input()
        if pw:
            def _worker():
                try:
                    self.after(0, lambda: self.update_status("Decrypting...", ACCENT))
                    extract_file(vault_id, pw)
                    self.after(0, lambda: messagebox.showinfo("Success", "Asset decrypted successfully."))
                    self.after(0, self.refresh_vault)
                    self.after(0, lambda: self.update_status("Extraction Success", SUCCESS))
                except Exception:
                    self.after(0, lambda: messagebox.showerror("Denied", "Invalid Master Key."))
                    self.after(0, lambda: self.update_status("Auth Failed", DANGER))

            threading.Thread(target=_worker, daemon=True).start()

    def ui_delete_file(self, vault_id):
        dialog = ctk.CTkInputDialog(text="ENTER MASTER KEY TO AUTHORIZE WIPE:", title="Security")
        pw = dialog.get_input()
        if pw:
            if messagebox.askyesno("Final Warning", f"Permanently wipe {vault_id}?\nThis cannot be undone."):
                def _worker():
                    try:
                        self.after(0, lambda: self.update_status("Wiping Asset...", DANGER))
                        delete_vault_file(vault_id, pw)
                        self.after(0, self.refresh_vault)
                    except Exception as e:
                        self.after(0, lambda: messagebox.showerror("Access Denied", str(e)))
                        self.after(0, lambda: self.update_status("Wipe Denied", DANGER))

                threading.Thread(target=_worker, daemon=True).start()


if __name__ == "__main__":
    app = ComradeApp()
    app.mainloop()