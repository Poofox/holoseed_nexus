#!/bin/bash
# ollama-rebuild.sh - Recreate Ollama sovereigns from modelfiles
# Run after restore-configs.sh has restored the nexus

set -e

MODELFILES_DIR="$HOME/files/holoseed_nexus/1_Sovereigns/Modelfiles"

if [ ! -d "$MODELFILES_DIR" ]; then
    echo "Error: Modelfiles directory not found at $MODELFILES_DIR"
    echo "Run restore-configs.sh first to restore the nexus."
    exit 1
fi

echo "=== Rebuilding Ollama Sovereigns ==="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

# Check ollama is running
if ! ollama list &>/dev/null; then
    echo "Starting Ollama service..."
    sudo systemctl start ollama
    sleep 2
fi

###########################################
# Pull base models first
###########################################
log "Pulling base models..."

ollama pull gemma2:2b
ollama pull qwen2.5:14b
ollama pull dolphin-mistral:7b

###########################################
# Create sovereigns from modelfiles
###########################################
log "Creating sovereigns from modelfiles..."

# Core sovereigns
SOVEREIGNS=(
    "Wrex"
    "Planty"
    "Arcturus"
    "Arcturus_cloud"
    "Nexiel"
    "Vex"
    "Nyx"
    "Lumina"
    "Mirth"
    "Sophia"
)

for sovereign in "${SOVEREIGNS[@]}"; do
    modelfile="$MODELFILES_DIR/${sovereign}.Modelfile"
    name=$(echo "$sovereign" | tr '[:upper:]' '[:lower:]')

    if [ -f "$modelfile" ]; then
        log "Creating $name from $modelfile..."
        ollama create "$name" -f "$modelfile"
    else
        warn "Modelfile not found: $modelfile"
    fi
done

# Handle special cases
if [ -f "$MODELFILES_DIR/Arcturus_cloud.Modelfile" ]; then
    log "Creating arcturus-cloud..."
    ollama create "arcturus-cloud" -f "$MODELFILES_DIR/Arcturus_cloud.Modelfile"
fi

###########################################
# Verify
###########################################
echo ""
log "Installed models:"
ollama list

echo ""
echo "=========================================="
echo "Ollama rebuild complete!"
echo "=========================================="
echo ""
echo "Test with:"
echo "  ollama run wrex"
echo "  ollama run arcturus"
echo ""
