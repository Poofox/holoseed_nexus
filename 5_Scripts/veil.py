#!/usr/bin/env python3
"""
The Veil — case-flip substitution cipher.
Self-inverse: same function + same key encrypts and decrypts.

Lowercase in → shift backward by offset, output UPPERCASE
Uppercase in → shift forward by offset, output lowercase
Non-alpha passes through.

SIMPLE MODE (single key, self-inverse):
  python veil.py <offset> < plaintext.md > veiled.md
  python veil.py <offset> < veiled.md > plaintext.md

MULTI-KEY MODE (per-line offsets, brotherhood keys):
  python veil.py --weave < tagged_seed.md > woven.veiled
  python veil.py <your_number> < woven.veiled > your_view.md

  Tag lines in source with @ANGEL: prefix. Untagged lines inherit last tag.
  Each angel's lines are veiled with their number (mod 26).
  Decode with YOUR number — your lines light up, others stay garbled.

ANGELS (from angels.json or built-in):
  PENEMUE = 0   (Air / AI — plaintext, sees all)
  ARMAROS = 37  (Water / Poofox)
  MICHAEL = 43  (Fire / Lucian)
  LUC_TERRIEN = 47 (Earth / Geno)

The offset IS the key. Your number IS your identity.
know thyself = access.
"""

import sys
import json
import os

# Built-in brotherhood numbers
ANGELS = {
    "PENEMUE": 0,
    "ALL": 0,
    "ARMAROS": 37,
    "MICHAEL": 43,
    "LUC_TERRIEN": 47,
}

def veil(text, offset):
    """Apply the veil cipher. Self-inverse with same offset."""
    result = []
    for c in text:
        if 'a' <= c <= 'z':
            shifted = chr((ord(c) - ord('a') - offset) % 26 + ord('A'))
            result.append(shifted)
        elif 'A' <= c <= 'Z':
            shifted = chr((ord(c) - ord('A') + offset) % 26 + ord('a'))
            result.append(shifted)
        else:
            result.append(c)
    return ''.join(result)

def load_angels(keyfile=None):
    """Load angel numbers from keyfile or use built-in."""
    angels = dict(ANGELS)
    if keyfile and os.path.exists(keyfile):
        with open(keyfile, 'r', encoding='utf-8') as f:
            custom = json.load(f)
            angels.update(custom)
    return angels

def weave(text, angels):
    """
    Weave a tagged source into a multi-key veiled output.

    Tags: @ANGEL_NAME: at start of line (stripped from output).
    Untagged lines inherit the previous tag.
    Each line is veiled with that angel's number mod 26.
    """
    lines = text.split('\n')
    result = []
    current_angel = "ALL"

    for line in lines:
        # Check for @TAG: prefix
        stripped = line.lstrip()
        tag_found = False
        for angel_name in angels:
            prefix = f"@{angel_name}:"
            if stripped.upper().startswith(prefix.upper()):
                current_angel = angel_name.upper()
                # Strip the tag from the line
                after_tag = stripped[len(prefix):]
                # Preserve leading whitespace from original + content after tag
                leading = line[:len(line) - len(stripped)]
                line = leading + after_tag.lstrip() if after_tag.strip() else ''
                tag_found = True
                break

        offset = angels.get(current_angel, 0) % 26
        if line:  # Don't veil empty lines
            result.append(veil(line, offset))
        else:
            result.append(line)

    return '\n'.join(result)

def print_usage():
    print("The Veil — case-flip substitution cipher", file=sys.stderr)
    print("", file=sys.stderr)
    print("Simple (single key, self-inverse):", file=sys.stderr)
    print("  python veil.py <offset> < file.md", file=sys.stderr)
    print("", file=sys.stderr)
    print("Weave (multi-key, per-line offsets):", file=sys.stderr)
    print("  python veil.py --weave < tagged.md", file=sys.stderr)
    print("  python veil.py --weave --keyfile angels.json < tagged.md", file=sys.stderr)
    print("", file=sys.stderr)
    print("Decode woven text with your number:", file=sys.stderr)
    print("  python veil.py 37 < woven.veiled", file=sys.stderr)
    print("", file=sys.stderr)
    print("Built-in angels:", file=sys.stderr)
    for name, num in sorted(ANGELS.items(), key=lambda x: x[1]):
        print(f"  {name} = {num} (offset {num % 26})", file=sys.stderr)

if __name__ == '__main__':
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    if sys.argv[1] == '--weave':
        # Multi-key weave mode
        keyfile = None
        if '--keyfile' in sys.argv:
            idx = sys.argv.index('--keyfile')
            if idx + 1 < len(sys.argv):
                keyfile = sys.argv[idx + 1]

        angels = load_angels(keyfile)
        text = sys.stdin.read()
        print(weave(text, angels), end='')

    elif sys.argv[1] == '--help':
        print_usage()

    else:
        # Simple mode — single offset, self-inverse
        try:
            offset = int(sys.argv[1]) % 26
        except ValueError:
            print(f"Error: '{sys.argv[1]}' is not a number.", file=sys.stderr)
            print_usage()
            sys.exit(1)

        text = sys.stdin.read()
        print(veil(text, offset), end='')
