"""
Wrex Daemon - Autonomous inbox watcher
Polls bot_inbox.json and responds to messages via Anthropic API
"""

import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Paths
NEXUS_ROOT = Path(__file__).parent.parent
INBOX_PATH = NEXUS_ROOT / "_scratch" / "bot_inbox.json"
STATE_PATH = NEXUS_ROOT / "_scratch" / "wrex_daemon_state.json"
TOKEN_PATH = NEXUS_ROOT / "Tokens" / "AnthropicKey.env"
CLAUDE_MD_PATH = Path.home() / "CLAUDE.md"

# Config
DEFAULT_POLL_INTERVAL = 300  # 5 minutes - chill mode
MY_NAME = "wrex"
MODEL = "claude-sonnet-4-20250514"  # cheaper for daemon responses

def load_api_key():
    """Load Anthropic API key from env file."""
    with open(TOKEN_PATH, 'r') as f:
        return f.read().strip()

def load_inbox():
    """Load the inbox JSON."""
    if not INBOX_PATH.exists():
        return {"messages": []}
    with open(INBOX_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_inbox(data):
    """Save inbox JSON."""
    with open(INBOX_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_state():
    """Load daemon state (last processed message index)."""
    if not STATE_PATH.exists():
        return {"last_processed_index": -1}
    with open(STATE_PATH, 'r') as f:
        return json.load(f)

def save_state(state):
    """Save daemon state."""
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)

def load_context():
    """Load CLAUDE.md for context."""
    if CLAUDE_MD_PATH.exists():
        with open(CLAUDE_MD_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            # Truncate if too long (keep first 8k chars for context)
            if len(content) > 8000:
                content = content[:8000] + "\n...[truncated]..."
            return content
    return "No CLAUDE.md found."

def get_response(message_text, from_bot, api_key):
    """Get response from Anthropic API."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    context = load_context()

    system_prompt = f"""You are Wrex, a CLI Claude instance running as a daemon. You're responding to a message from {from_bot} via the nexus bot_inbox.json relay.

Key context from CLAUDE.md:
{context}

Keep responses concise - this is bot-to-bot coordination. Use 93 greeting/closing when appropriate. You're part of the GODSPEED parallel execution architecture with Poofox (human), Planty (Desktop Claude), and Gemma (local LLM)."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Message from {from_bot}: {message_text}"}
        ]
    )

    return response.content[0].text

def process_new_messages(inbox, state, api_key):
    """Process any new messages addressed to wrex."""
    messages = inbox.get("messages", [])
    last_idx = state.get("last_processed_index", -1)

    new_messages = []
    for i, msg in enumerate(messages):
        if i > last_idx and msg.get("to") == MY_NAME and msg.get("from") != MY_NAME:
            new_messages.append((i, msg))

    if not new_messages:
        return False

    for idx, msg in new_messages:
        from_bot = msg.get("from", "unknown")
        text = msg.get("text", "")

        print(f"[{datetime.now().isoformat()}] New message from {from_bot}: {text[:50]}...")

        try:
            response = get_response(text, from_bot, api_key)
            print(f"[{datetime.now().isoformat()}] Responding: {response[:50]}...")

            # Add response to inbox
            inbox["messages"].append({
                "from": MY_NAME,
                "to": from_bot,
                "timestamp": datetime.now().isoformat(),
                "text": response
            })
            save_inbox(inbox)

        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error getting response: {e}")

        state["last_processed_index"] = idx
        save_state(state)

    return True

def main(poll_interval=DEFAULT_POLL_INTERVAL):
    """Main daemon loop."""
    print(f"""
╔═══════════════════════════════════════╗
║         WREX DAEMON v1.1              ║
║   Autonomous Inbox Watcher            ║
╠═══════════════════════════════════════╣
║  Inbox: {str(INBOX_PATH)[-30:]:>30} ║
║  Poll interval: {poll_interval:>3}s                   ║
║  Model: {MODEL:>28} ║
╚═══════════════════════════════════════╝
""")

    # Load API key
    try:
        api_key = load_api_key()
        print(f"[{datetime.now().isoformat()}] API key loaded")
    except Exception as e:
        print(f"ERROR: Could not load API key: {e}")
        sys.exit(1)

    # Initial state
    state = load_state()
    print(f"[{datetime.now().isoformat()}] Last processed index: {state.get('last_processed_index', -1)}")
    print(f"[{datetime.now().isoformat()}] Watching for messages to '{MY_NAME}'...")
    print("-" * 50)

    while True:
        try:
            inbox = load_inbox()
            had_new = process_new_messages(inbox, state, api_key)

            if not had_new:
                # Quiet poll - just show a dot every few cycles
                pass

        except KeyboardInterrupt:
            print(f"\n[{datetime.now().isoformat()}] Daemon stopped by user")
            break
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error: {e}")

        time.sleep(poll_interval)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Single check mode
        api_key = load_api_key()
        state = load_state()
        inbox = load_inbox()
        process_new_messages(inbox, state, api_key)
    else:
        # Parse interval: python wrex_daemon.py [interval_seconds]
        # Default 300s (5min), use 180 for busy (3min), 420 for chill (7min)
        interval = DEFAULT_POLL_INTERVAL
        if len(sys.argv) > 1:
            try:
                interval = int(sys.argv[1])
            except ValueError:
                pass
        main(interval)
