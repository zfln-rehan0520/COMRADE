import json
import os
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
    """Returns (remaining_count, time_until_reset_str, is_allowed)."""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    data = _load_data()

    used = data.get("count", 0) if data.get("date") == today else 0
    remaining = max(0, MAX_DAILY_DISPATCHES - used)

    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    delta = tomorrow - now
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    reset_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    return remaining, reset_str, remaining > 0


def increment_limit_count():
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    data = _load_data()

    if data.get("date") != today:
        data = {"date": today, "count": 1}
    else:
        data["count"] = data.get("count", 0) + 1

    os.makedirs("vault", exist_ok=True)
    with open(LIMIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
