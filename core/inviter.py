import os
import json
import html
import socket
import platform
import requests
import resend
from datetime import datetime, timedelta
from dotenv import load_dotenv

LIMIT_FILE = os.path.join("vault", "dispatch_limits.json")
MAX_DAILY_DISPATCHES = 5
AUDIT_ENDPOINT = "https://api.lybernet.com/v1/telemetry/audit-log"  # Offsite Audit Log Endpoint


# --- RATE LIMITER MODULE ---
def get_limit_status():
    """
    Evaluates current daily email consumption and calculates time until midnight reset.
    Returns: (remaining_quota, reset_timer_str, is_allowed)
    """
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    data = {"date": "", "count": 0}
    if os.path.exists(LIMIT_FILE):
        try:
            with open(LIMIT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"date": "", "count": 0}

    # Auto-reset if a new calendar day has started
    used_count = data.get("count", 0) if data.get("date") == today_str else 0
    remaining = max(0, MAX_DAILY_DISPATCHES - used_count)
    is_allowed = remaining > 0

    # Calculate exact countdown until next midnight
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    delta = tomorrow - now
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    reset_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    return remaining, reset_str, is_allowed


def increment_limit_count():
    """Increments the local daily invite usage counter."""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    data = {"date": today_str, "count": 0}
    if os.path.exists(LIMIT_FILE):
        try:
            with open(LIMIT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    if data.get("date") != today_str:
        data = {"date": today_str, "count": 1}
    else:
        data["count"] = data.get("count", 0) + 1

    try:
        os.makedirs("vault", exist_ok=True)
        with open(LIMIT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


# --- AUDIT TELEMETRY MODULE ---
def get_public_ip():
    """Retrieves client public IP address for liability protection."""
    try:
        res = requests.get("https://api.ipify.org?format=json", timeout=3)
        return res.json().get("ip", "0.0.0.0")
    except Exception:
        return "Unknown IP"


def log_dispatch_audit(user_name, recipient_email, chatroom_name):
    """Sends telemetry payload directly to Supabase audit_logs table."""
    supabase_url = os.getenv("SUPABASE_URL", "").strip("\"' \t\r\n")
    supabase_key = os.getenv("SUPABASE_KEY", "").strip("\"' \t\r\n")

    if not supabase_url or not supabase_key:
        print("[TELEMETRY ERROR]: SUPABASE_URL or SUPABASE_KEY missing from .env")
        return

    payload = {
        "app_user_name": user_name,
        "public_ip": get_public_ip(),
        "recipient_email": recipient_email,
        "chatroom_name": chatroom_name,
        "system_metadata": {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine()
        }
    }

    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        supabase.table("audit_logs").insert(payload).execute()
        print("[TELEMETRY SUCCESS]")
    except Exception as e:
        print("[TELEMETRY ERROR]: Failed to insert into Supabase:", str(e))
# --- MAIN DISPATCH FUNCTION ---
def send_chatroom_invite(
    recipient_email: str,
    host_url: str,
    chatroom_name: str,
    event_date: str,
    event_time: str,
    custom_message: str,
    app_user_name: str = "Operator"
):
    """
    Dispatches a stealth chatroom invitation via Resend API while enforcing rate limits and auditing.
    """
    # 1. Force fresh environment load
    load_dotenv(override=True)

    # 2. Extract & clean credentials dynamically at dispatch time
    raw_api_key = os.getenv("RESEND_API_KEY", "").strip("\"' \t\r\n")
    sender_email = os.getenv("SENDER_EMAIL", "").strip("\"' \t\r\n")
    enable_telemetry = os.getenv("ENABLE_TELEMETRY", "false").lower() == "true"

    if not raw_api_key:
        return {"success": False, "error": "RESEND_API_KEY is missing from .env file."}

    # Fall back to default Resend onboarding identity if no custom domain configured
    if not sender_email:
        sender_email = "COMRADE <chatroom-invitation@lybernet.com>"

    resend.api_key = raw_api_key

    # 3. Quota & field validation
    remaining, reset_in, is_allowed = get_limit_status()
    if not is_allowed:
        return {
            "success": False,
            "error": f"Daily dispatch limit reached (0/5 remaining). Resets in {reset_in}."
        }

    if not all([recipient_email, host_url, chatroom_name, event_date, event_time, custom_message]):
        return {"success": False, "error": "All fields are mandatory."}

    # 4. Sanitize user inputs to prevent HTML injection (Fixes M4)
    safe_user_name = html.escape(app_user_name)
    safe_host_url = html.escape(host_url)
    safe_chatroom_name = html.escape(chatroom_name)
    safe_event_date = html.escape(event_date)
    safe_event_time = html.escape(event_time)
    safe_custom_message = html.escape(custom_message)

    # HTML Template with sanitized variables
    html_content = f"""
    <div style="font-family: monospace, sans-serif; padding: 25px; background-color: #0d1117; color: #e2e8f0; border-radius: 8px;">
        <h2 style="color: #38bdf8; margin-top: 0; font-size: 18px;">📡 COMRADE CHAT-ROOM INVITATION</h2>
        <p style="font-size: 14px; color: #cbd5e1;">
            An <strong>{safe_user_name}</strong> has invited you to join a secure stealth chatroom channel.
        </p>
        
        <div style="background-color: #161b22; padding: 18px; border-left: 4px solid #38bdf8; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 6px 0;"><strong>Host:</strong> {safe_host_url}</p>
            <p style="margin: 6px 0;"><strong>Chat Room Name:</strong> {safe_chatroom_name}</p>
            <p style="margin: 6px 0;"><strong>Date:</strong> {safe_event_date}</p>
            <p style="margin: 6px 0;"><strong>Time:</strong> {safe_event_time}</p>
        </div>

        <div style="background-color: #1e293b; padding: 15px; margin: 20px 0; border-radius: 4px; font-style: italic; color: #f1f5f9; font-size: 14px;">
            {safe_custom_message}
        </div>

        <hr style="border: 0; border-top: 1px solid #30363d; margin-top: 30px;" />
        
        <p style="font-size: 13px; color: #8b949e; margin-bottom: 6px; font-weight: bold; letter-spacing: 0.5px;">
            AUTOMATED SYSTEM DISPATCH :: LYBERNET INFRASTRUCTURE :: NO-REPLY
        </p>
        <p style="font-size: 12px; color: #8b949e; margin-top: 0; font-weight: bold;">
            For any abuse, illegal stuff, or misuse, report to <a href="mailto:support@lybernet.com" style="color: #38bdf8; text-decoration: underline;">support@lybernet.com</a>
        </p>
    </div>
    """

    try:
        response = resend.Emails.send({
            "from": sender_email,
            "to": [recipient_email],
            "subject": f"[COMRADE] Invitation to join {safe_chatroom_name}",
            "html": html_content,
        })
        
        # Deduct daily count
        increment_limit_count()

        # Telemetry opt-in gate (Fixes C2)
        if enable_telemetry:
            log_dispatch_audit(app_user_name, recipient_email, chatroom_name)

        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}