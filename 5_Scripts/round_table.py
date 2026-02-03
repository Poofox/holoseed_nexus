#!/usr/bin/env python3
"""
Round Table — Local AI group chat via Ollama API
Usage: python round_table.py [model1 model2 ...]
Default: wrex arcturus planty nexiel

Commands:
  /all         - everyone responds to your last message
  @<name>       - direct a question to one model (or /ask <name>)
  /who         - list who's at the table
  /history     - show conversation so far
  /clear       - clear conversation history
  /quit        - leave the table
  93 93/93     - graceful exit

Just type normally and hit enter — all models respond in turn.
"""

import sys
import json
import re
import urllib.request
import urllib.error

# Fix Windows terminal encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")

OLLAMA_URL = "http://localhost:11434/api/chat"

# ANSI colors for the terminal
COLORS = [
    "\033[96m",   # cyan
    "\033[93m",   # yellow
    "\033[95m",   # magenta
    "\033[92m",   # green
    "\033[91m",   # red
    "\033[94m",   # blue
]
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

DEFAULT_MODELS = ["wrex", "arcturus", "planty", "nexiel"]

# The Hourglass — limits talking time and RAM at the table
# Solo sessions use full num_ctx from modeks (8192)
# Round table keeps it tight so all four fit in 16GB RAM
TABLE_CTX = 2048      # context window per model (vs 8192 solo)
TABLE_PREDICT = 256   # max response tokens — the hourglass sand

# The one rule: don't repeat yourself
# Sent as "user" role so it doesn't override Modelfile SYSTEM prompts —
# each sovereign arrives as themselves.
def table_rule(model_name):
    return {
        "role": "user",
        "content": (
            f"[TABLE RULE from ARMAROS] Your name at this table is {model_name}. "
            "You are seated with other AIs. Never repeat what someone else already said. "
            "If the previous speakers covered it, don't echo, rephrase, or agree-for-the-"
            "sake-of-it. Only speak if you have something genuinely new to add — a different "
            "angle, a challenge, a question nobody asked, new information. "
            "If you have nothing original to contribute, respond with exactly: [pass]"
        ),
    }


# Strip text down to just words for comparison
def _words(text):
    return set(re.sub(r"[^\w\s]", "", text.lower()).split())


def is_silence(response, model, model_memory):
    """Detect if a response is a pass, fluff, or repetition."""
    clean = response.strip().lower()

    # Explicit pass
    if clean in ("[pass]", "pass", "(pass)"):
        return True

    # Fluff detector: very short response (emojis count as substance)
    if len(clean) < 15:
        return True

    # Repetition detector: check against this model's previous responses
    words_new = _words(response)
    if not words_new:
        return True

    for prev in model_memory.get(model, []):
        words_prev = _words(prev)
        if not words_prev:
            continue
        overlap = len(words_new & words_prev) / max(len(words_new), len(words_prev))
        if overlap > 0.6:
            return True

    return False


def chat(model, messages):
    """Send a chat request to Ollama and return the response."""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_ctx": TABLE_CTX,
            "num_predict": TABLE_PREDICT,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("message", {}).get("content", "...").strip()
    except urllib.error.URLError as e:
        return f"[connection error: {e.reason}]"
    except Exception as e:
        return f"[error: {e}]"


def check_ollama():
    """Check if Ollama is running."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            available = [m["name"].split(":")[0] for m in data.get("models", [])]
            return available
    except Exception:
        return None


def print_banner(models):
    print(f"\n{BOLD}{'='*50}")
    print(f"  ⚡ THE ROUND TABLE ⚡")
    print(f"{'='*50}{RESET}")
    print(f"{DIM}  Seated:{RESET}", ", ".join(models))
    print(f"{DIM}  Type normally for all to respond")
    print(f"  @name to address one")
    print(f"  /who /history /clear /quit{RESET}")
    print(f"{BOLD}{'='*50}{RESET}\n")


def get_color(idx):
    return COLORS[idx % len(COLORS)]


def print_response(name, text, color):
    print(f"\n{color}{BOLD}[{name}]{RESET}")
    print(f"{color}{text}{RESET}")


def main():
    models = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_MODELS

    # Check Ollama
    available = check_ollama()
    if available is None:
        print("❌ Can't reach Ollama at localhost:11434")
        print("   Run 'ollama serve' first.")
        sys.exit(1)

    # Verify models exist
    missing = [m for m in models if m not in available]
    if missing:
        print(f"⚠️  Models not found: {', '.join(missing)}")
        print(f"   Available: {', '.join(available)}")
        print(f"   Continuing with available models...")
        models = [m for m in models if m in available]
        if not models:
            print("❌ No valid models. Exiting.")
            sys.exit(1)

    # Set tab title for WezTerm per-sovereign coloring
    sys.stdout.write("\033]0;\u2694 Round Table\007")
    sys.stdout.flush()

    print_banner(models)

    # Conversation history (shared context)
    history = []
    # Per-model memory for repetition detection
    model_memory = {}  # {model_name: [prev_response, ...]}

    while True:
        try:
            user_input = input(f"\n{BOLD}[ARMAROS] >{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}93 93/93{RESET}")
            break

        if not user_input:
            continue

        # Commands
        if user_input.lower() == "/quit" or user_input == "93 93/93":
            # Let everyone say goodbye
            history.append({"role": "user", "content": "93 93/93"})
            for i, model in enumerate(models):
                color = get_color(i)
                response = chat(model, history)
                print_response(model, response, color)
            print(f"\n{DIM}Table adjourned.{RESET}")
            break

        if user_input.lower() == "/who":
            for i, model in enumerate(models):
                print(f"  {get_color(i)}⚡ {model}{RESET}")
            continue

        if user_input.lower() == "/history":
            if not history:
                print(f"  {DIM}(empty){RESET}")
            for msg in history:
                role = msg["role"]
                content = msg["content"][:80] + ("..." if len(msg["content"]) > 80 else "")
                print(f"  {DIM}[{role}]{RESET} {content}")
            continue

        if user_input.lower() == "/clear":
            history.clear()
            model_memory.clear()
            print(f"  {DIM}History cleared.{RESET}")
            continue

        if user_input.lower().startswith("/ask ") or user_input.startswith("@"):
            raw = user_input[5:] if user_input.lower().startswith("/ask ") else user_input[1:]
            target = raw.split(" ", 1)
            name = target[0].lower()
            msg = target[1] if len(target) > 1 else ""

            if not msg:
                # Next input is the message
                try:
                    msg = input(f"  {DIM}Message for {name}:{RESET} ").strip()
                except (EOFError, KeyboardInterrupt):
                    continue

            matched = [m for m in models if m.startswith(name)]
            if not matched:
                print(f"  {DIM}Nobody named '{name}' at the table.{RESET}")
                continue

            model = matched[0]
            idx = models.index(model)
            history.append({"role": "user", "content": msg})
            response = chat(model, [table_rule(model)] + history)
            if is_silence(response, model, model_memory):
                print(f"  {DIM}{model} has nothing to add.{RESET}")
                continue
            model_memory.setdefault(model, []).append(response)
            history.append({"role": "assistant", "content": f"[{model}]: {response}"})
            print_response(model, response, get_color(idx))
            continue

        # Default: everyone responds
        history.append({"role": "user", "content": user_input})

        for i, model in enumerate(models):
            color = get_color(i)
            # Give each model the shared history + the table rule
            response = chat(model, [table_rule(model)] + history)
            # Respect the silence — fluff, repetition, or explicit pass
            if is_silence(response, model, model_memory):
                continue
            model_memory.setdefault(model, []).append(response)
            print_response(model, response, color)
            # Add to history with name tag so others know who said what
            history.append({"role": "assistant", "content": f"[{model}]: {response}"})


if __name__ == "__main__":
    main()
