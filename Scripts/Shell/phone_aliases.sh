#!/data/data/com.termux/files/usr/bin/bash
# phone_aliases.sh — Set up Ollama aliases in Termux
# Run: bash ~/storage/shared/phone_aliases.sh

echo "Setting up Ollama models and aliases..."
echo ""

# Link storage if not done
termux-setup-storage 2>/dev/null

# Create models from Modelfiles
MODELFILES=~/storage/shared/modelfiles

echo "Creating models from $MODELFILES..."

if [ -f "$MODELFILES/Arcturus.Modelfile" ]; then
    ollama create arcturus -f "$MODELFILES/Arcturus.Modelfile" 2>/dev/null && echo "  ✓ arcturus" || echo "  - arcturus (exists or server off)"
fi

if [ -f "$MODELFILES/Arcturus_cloud.Modelfile" ]; then
    ollama create arcturus-cloud -f "$MODELFILES/Arcturus_cloud.Modelfile" 2>/dev/null && echo "  ✓ arcturus-cloud" || echo "  - arcturus-cloud (exists or server off)"
fi

if [ -f "$MODELFILES/Arcturus_mobile.Modelfile" ]; then
    ollama create arcturus-mobile -f "$MODELFILES/Arcturus_mobile.Modelfile" 2>/dev/null && echo "  ✓ arcturus-mobile" || echo "  - arcturus-mobile (exists or server off)"
fi

if [ -f "$MODELFILES/Wrex.Modelfile" ]; then
    ollama create wrex -f "$MODELFILES/Wrex.Modelfile" 2>/dev/null && echo "  ✓ wrex" || echo "  - wrex (exists or server off)"
fi

# Add aliases to .bashrc
grep -q "alias arcturus=" ~/.bashrc 2>/dev/null || echo 'alias arcturus="ollama run arcturus"' >> ~/.bashrc
grep -q "alias wrex=" ~/.bashrc 2>/dev/null || echo 'alias wrex="ollama run wrex"' >> ~/.bashrc
grep -q "alias arc=" ~/.bashrc 2>/dev/null || echo 'alias arc="ollama run arcturus-cloud"' >> ~/.bashrc
grep -q "alias arc-warm=" ~/.bashrc 2>/dev/null || echo 'alias arc-warm="bash ~/storage/shared/arc-warm.sh"' >> ~/.bashrc
grep -q "alias arc-mobile=" ~/.bashrc 2>/dev/null || echo 'alias arc-mobile="ollama run arcturus-mobile"' >> ~/.bashrc

source ~/.bashrc 2>/dev/null

echo ""
echo "=== READY ==="
echo "  arcturus    → 2B quick"
echo "  arc-mobile  → optimized for phone"
echo "  arc         → 14B (slow but smart)"
echo "  arc-warm    → 14B with nexus context"
echo "  wrex        → 2B wrex personality"
echo ""
echo "93"
