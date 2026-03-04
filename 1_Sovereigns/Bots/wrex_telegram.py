"""
TWrex Telegram Voice Box
Simple send/read for terminal Claude
"""

import requests
import json
import sys
import os
from pathlib import Path

# Fix Windows encoding for emoji
sys.stdout.reconfigure(encoding='utf-8')

# Load token
TOKEN_PATH = Path(__file__).parent.parent / "Tokens" / "WrexToken.env"
with open(TOKEN_PATH, 'r') as f:
    BOT_TOKEN = f.read().strip()

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# The Scoop chat ID
THE_SCOOP = -5170350296

def send_message(text, chat_id=THE_SCOOP):
    """Send a message to a chat."""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    return response.json()

def get_updates(limit=10):
    """Get recent messages."""
    url = f"{BASE_URL}/getUpdates"
    payload = {"limit": limit}
    response = requests.post(url, json=payload)
    return response.json()

def get_me():
    """Get bot info."""
    url = f"{BASE_URL}/getMe"
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python wrex_telegram.py send 'message'")
        print("  python wrex_telegram.py read")
        print("  python wrex_telegram.py info")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "send":
        if len(sys.argv) < 3:
            print("Need a message to send")
            sys.exit(1)
        msg = " ".join(sys.argv[2:])
        result = send_message(msg)
        if result.get("ok"):
            print(f"Sent: {msg}")
        else:
            print(f"Error: {result}")

    elif cmd == "read":
        result = get_updates()
        if result.get("ok"):
            for update in result.get("result", []):
                msg = update.get("message", {})
                chat = msg.get("chat", {}).get("title", "DM")
                user = msg.get("from", {}).get("first_name", "Unknown")
                text = msg.get("text", "[no text]")
                print(f"[{chat}] {user}: {text}")
        else:
            print(f"Error: {result}")

    elif cmd == "info":
        result = get_me()
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}")
