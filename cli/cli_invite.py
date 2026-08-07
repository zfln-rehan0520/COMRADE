import os
import sys
import argparse

# Ensure parent directory (project root) is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.inviter import send_chatroom_invite

def main():
    parser = argparse.ArgumentParser(
        prog="comrade-invite",
        description="COMRADE CLI Stealth Invitation Dispatcher"
    )
    
    parser.add_argument("-r", "--recipient", required=True, help="Recipient email address")
    parser.add_argument("-H", "--host", required=True, help="Host address/URL (e.g., https://127.0.0.1:6667)")
    parser.add_argument("-c", "--chatroom", required=True, help="Chatroom channel name")
    parser.add_argument("-d", "--date", required=True, help="Event Date (YYYY-MM-DD)")
    parser.add_argument("-t", "--time", required=True, help="Event Time (e.g., 09:00 PM)")
    parser.add_argument("-m", "--message", required=True, help="Custom invitation message")
    parser.add_argument("-u", "--user", default="Operator", help="Operator display name (Default: Operator)")

    args = parser.parse_args()

    print("\n📡 [COMRADE CLI] Dispatching stealth invitation...")
    
    res = send_chatroom_invite(
        recipient_email=args.recipient,
        host_url=args.host,
        chatroom_name=args.chatroom,
        event_date=args.date,
        event_time=args.time,
        custom_message=args.message,
        app_user_name=args.user
    )

    if res.get("success"):
        print(f"✅ Invitation successfully dispatched to {args.recipient}!\n")
    else:
        print(f"❌ Dispatch failed: {res.get('error')}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()