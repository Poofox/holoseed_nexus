"""
Phone Bridge - ADB sync for Planty access
Syncs between phone downloads and nexus _phone folder
"""

import subprocess
import sys
import os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

NEXUS_ROOT = Path(__file__).parent.parent
PHONE_FOLDER = NEXUS_ROOT / "_phone"
DEVICE_ID = "R39M30QT5EP"
PHONE_PATH = "/storage/emulated/0/Download"

def run_adb(args):
    """Run ADB command and return output."""
    cmd = ["adb", "-s", DEVICE_ID] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def pull(filename=None):
    """Pull file(s) from phone to nexus."""
    if filename:
        src = f"{PHONE_PATH}/{filename}"
        dst = str(PHONE_FOLDER / filename)
        out, err, code = run_adb(["pull", src, dst])
    else:
        # Pull everything
        out, err, code = run_adb(["pull", PHONE_PATH + "/", str(PHONE_FOLDER)])

    if code == 0:
        print(f"Pulled: {filename or 'all files'}")
    else:
        print(f"Error: {err}")
    return code == 0

def push(filename):
    """Push file from nexus to phone."""
    src = str(PHONE_FOLDER / filename)
    dst = f"{PHONE_PATH}/{filename}"
    out, err, code = run_adb(["push", src, dst])

    if code == 0:
        print(f"Pushed: {filename}")
    else:
        print(f"Error: {err}")
    return code == 0

def ls_phone():
    """List phone downloads."""
    out, err, code = run_adb(["shell", f"ls -la {PHONE_PATH}/"])
    if code == 0:
        print(out)
    else:
        print(f"Error: {err}")

def ls_local():
    """List local bridge folder."""
    for f in PHONE_FOLDER.iterdir():
        print(f.name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python phone_bridge.py pull [filename]  - pull from phone")
        print("  python phone_bridge.py push <filename>  - push to phone")
        print("  python phone_bridge.py ls-phone         - list phone downloads")
        print("  python phone_bridge.py ls-local         - list local bridge")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "pull":
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        pull(filename)
    elif cmd == "push":
        if len(sys.argv) < 3:
            print("Need filename to push")
            sys.exit(1)
        push(sys.argv[2])
    elif cmd == "ls-phone":
        ls_phone()
    elif cmd == "ls-local":
        ls_local()
    else:
        print(f"Unknown command: {cmd}")
