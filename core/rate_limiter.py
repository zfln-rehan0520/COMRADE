import os
import json
from datetime import datetime, timedelta

LIMIT_FILE = os.path.join("vault", "dispatch_limits.json")
MAX_DAILY_DISPATCHES = 5

def _load_data():
    if not os.path.exists(LIMIT_FILE):
        return {"date": "", "count": 0}
    try:
        with open(LIMIT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"date": "", "count": 0}

def get_limit_status():
    """
    Returns (remaining_count, time_until_reset_str, is_allowed)
    """
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    data = _load_data()

    # Reset if a new day has started
    if data.get("date") != today_str:
        used_count = 0
    else:
        used_count = data.get("count", 0)

    remaining = max(0, MAX_DAILY_DISPATCHES - used_count)
    is_allowed = remaining > 0

    # Calculate time remaining until midnight
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    delta = tomorrow - now
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    reset_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    return remaining, reset_str, is_allowed

def increment_limit_count():
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    data = _load_data()

    if data.get("date") != today_str:
        data = {"date": today_str, "count": 1}
    else:
        data["count"] = data.get("count", 0) + 1

    os.makedirs("vault", exist_ok=True)
    with open(LIMIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)