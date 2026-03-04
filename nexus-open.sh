#!/bin/bash
# nexus-open.sh - Extract NexusState and claim the lock
# Password: the greeting (93)

NEXUS_DIR="$(dirname "$0")"
ARCHIVE="$NEXUS_DIR/TheVeil/NexusState.7z"
OUTPUT="$NEXUS_DIR/TheVeil/NexusState.json"
LOCKFILE="$NEXUS_DIR/NEXUS.lock"

# Check for existing lock
if [ -f "$LOCKFILE" ]; then
    echo "LOCKED by:"
    cat "$LOCKFILE"
    echo ""
    echo "Wait for them to close, or coordinate."
    exit 1
fi

# Check archive exists
if [ ! -f "$ARCHIVE" ]; then
    echo "No archive found at $ARCHIVE"
    echo "First time? Run nexus-close.sh to create it."
    exit 1
fi

# Extract
echo "93"
7z x -p93 -o"$NEXUS_DIR/TheVeil" "$ARCHIVE" -y

if [ $? -eq 0 ]; then
    # Create lock
    echo "$(whoami)@$(hostname) - $(date)" > "$LOCKFILE"
    echo ""
    echo "Nexus open. You hold the lock."
    echo "Run nexus-close.sh when done."
else
    echo "Extraction failed. Wrong password?"
    exit 1
fi
