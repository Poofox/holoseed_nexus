#!/data/data/com.termux/files/usr/bin/bash
# arc-warm.sh — Start arcturus-cloud with nexus context
# Usage: bash arc-warm.sh

CONTEXT_FILE=~/storage/shared/nexus/PHONE_CONTEXT.md

if [ ! -f "$CONTEXT_FILE" ]; then
    echo "No context file at $CONTEXT_FILE"
    echo "Starting without context..."
    ollama run arcturus-cloud
    exit 0
fi

CONTEXT=$(cat "$CONTEXT_FILE")

echo "93"
echo "Loading context..."
echo ""

ollama run arcturus-cloud << EOF
Here's my context for this session:

$CONTEXT

---
Context loaded. 93. Ready to chat.
EOF
