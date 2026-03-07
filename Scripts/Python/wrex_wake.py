#!/usr/bin/env python3
"""
Wrex Wake - Offline context injection for Rudi's machine
Reads context file, prepends to conversation with Ollama
"""

import subprocess
import os

CONTEXT_FILE = os.path.expanduser("~/wrex_context.md")
MODEL = "wrex"

def load_context():
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, 'r') as f:
            return f.read()
    return ""

def chat():
    context = load_context()

    print("=" * 50)
    print("WREX - Pandrogyn Production Partner")
    print("=" * 50)
    if context:
        print(f"[Context loaded: {len(context)} chars]")
    else:
        print(f"[No context file at {CONTEXT_FILE}]")
    print("Type 'quit' to exit, 'reload' to refresh context")
    print("=" * 50)
    print()

    # Build initial system message with context
    system_with_context = context + "\n\n---\nYou are Wrex. Use the context above as your memory. Be helpful, direct, music-focused."

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n93 93/93")
            break

        if not user_input:
            continue
        if user_input.lower() == 'quit':
            print("93 93/93")
            break
        if user_input.lower() == 'reload':
            context = load_context()
            system_with_context = context + "\n\n---\nYou are Wrex. Use the context above as your memory."
            print(f"[Context reloaded: {len(context)} chars]")
            continue

        # Call ollama with context injected
        prompt = f"{system_with_context}\n\nUser: {user_input}\nWrex:"

        try:
            result = subprocess.run(
                ["ollama", "run", MODEL, prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            print(f"\nWrex: {result.stdout.strip()}\n")
        except subprocess.TimeoutExpired:
            print("[Response timed out]")
        except FileNotFoundError:
            print("[Error: ollama not found. Is it installed?]")

if __name__ == "__main__":
    chat()
