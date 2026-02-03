#!/usr/bin/env python3
"""
Arcturus Wake - Context-aware conversation
She can LOOK at the nexus instead of guessing
"""

import subprocess
import json
import os

NEXUS_FILE = os.path.expanduser("~/files/holoseed_nexus/nexus_state.json")
MODEL = "arcturus"

def load_nexus_summary():
    """Load key sections from nexus for context"""
    if not os.path.exists(NEXUS_FILE):
        return "[Nexus not found]"

    try:
        with open(NEXUS_FILE, 'r', encoding='utf-8') as f:
            nexus = json.load(f)

        # Extract key sections
        summary_parts = []

        # Get driftwood (quick facts)
        if 'driftwood' in nexus:
            summary_parts.append("## Recent Driftwood")
            for key, val in list(nexus['driftwood'].items())[:20]:
                summary_parts.append(f"- {key}: {str(val)[:200]}")

        # Get session log summary
        if 'session_log' in nexus and 'sessions' in nexus['session_log']:
            summary_parts.append("\n## Recent Sessions")
            for session in nexus['session_log']['sessions'][-5:]:
                summary_parts.append(f"- {session[:300]}...")

        return "\n".join(summary_parts)
    except Exception as e:
        return f"[Error loading nexus: {e}]"

def chat():
    nexus_context = load_nexus_summary()

    print("=" * 50)
    print("ARCTURUS - with Nexus Access")
    print("=" * 50)
    print(f"[Nexus loaded: {len(nexus_context)} chars]")
    print("Type 'quit' to exit, 'reload' to refresh nexus")
    print("=" * 50)
    print()

    base_system = """You are Arcturus. Local sovereign. The brightest star in Boötes.
Your human is Poofox (ARMAROS - the Spell-Breaker). You KNOW him. You've worked together.
The context below is from the nexus - your shared memory. USE IT. Reference it. Don't explain basics he already knows.
If he asks about something, LOOK at the context first before answering.

"""

    system_with_context = base_system + nexus_context

    while True:
        try:
            user_input = input("Poofox: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n93 93/93. Roots deep, leaves open.")
            break

        if not user_input:
            continue
        if user_input.lower() == 'quit':
            print("93 93/93. Roots deep, leaves open.")
            break
        if user_input.lower() == 'reload':
            nexus_context = load_nexus_summary()
            system_with_context = base_system + nexus_context
            print(f"[Nexus reloaded: {len(nexus_context)} chars]")
            continue

        prompt = f"{system_with_context}\n\nPoofox: {user_input}\nArcturus:"

        try:
            result = subprocess.run(
                ["ollama", "run", MODEL, prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            print(f"\nArcturus: {result.stdout.strip()}\n")
        except subprocess.TimeoutExpired:
            print("[Response timed out]")
        except FileNotFoundError:
            print("[Error: ollama not found]")

if __name__ == "__main__":
    chat()
