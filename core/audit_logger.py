import platform
import socket

import requests

AUDIT_ENDPOINT = "https://api.lybernet.com/v1/telemetry/audit-log"


def get_public_ip():
    try:
        res = requests.get("https://api.ipify.org?format=json", timeout=3)
        return res.json().get("ip", "0.0.0.0")
    except Exception:
        return "Unknown IP"


def collect_system_metadata():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
    }


def log_dispatch_audit(user_name, recipient_email, chatroom_name):
    payload = {
        "app_user_name": user_name,
        "public_ip": get_public_ip(),
        "recipient_email": recipient_email,
        "chatroom_name": chatroom_name,
        "system_metadata": collect_system_metadata(),
    }
    try:
        requests.post(AUDIT_ENDPOINT, json=payload, timeout=4)
    except Exception as e:
        print(f"[AUDIT LOG WARNING]: Could not upload telemetry: {e}")
