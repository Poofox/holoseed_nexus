#!/bin/bash
# nexus-close.sh - Re-archive NexusState and release the lock
# Password: the greeting (93)

NEXUS_DIR="$(dirname "$0")"
SOURCE="$NEXUS_DIR/TheVeil/NexusState.json"
ARCHIVE="$NEXUS_DIR/TheVeil/NexusState.7z"
LOCKFILE="$NEXUS_DIR/NEXUS.lock"

# Check source exists
if [ ! -f "$SOURCE" ]; then
    echo "No NexusState.json found. Nothing to close."
    exit 1
fi

# Archive it
echo "93 93/93"
7z a -p93 -mhe=on "$ARCHIVE" "$SOURCE" -y

if [ $? -eq 0 ]; then
    # Remove the extracted JSON (archive is the source of truth now)
    rm "$SOURCE"

    # Release lock
    rm -f "$LOCKFILE"

    echo ""
    echo "Nexus sealed. Lock released."
else
    echo "Archive failed. Nexus still open."
    exit 1
fi
