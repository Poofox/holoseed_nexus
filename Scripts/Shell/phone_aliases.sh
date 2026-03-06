#!/data/data/com.termux/files/usr/bin/bash
# phone_aliases.sh — Set up Ollama aliases in Termux
# Run: bash ~/storage/shared/phone_aliases.sh

echo "Setting up aliases..."

# Create models from Modelfiles on shared storage
echo "Creating Arcturus model..."
cp ~/storage/shared/Arcturus.Modelfile ~/Arcturus.Modelfile 2>/dev/null
ollama create arcturus -f ~/Arcturus.Modelfile 2>/dev/null && echo "  arcturus ready" || echo "  arcturus skipped (already exists or server not running)"

echo "Creating Arcturus-cloud model..."
cp ~/storage/shared/Arcturus_cloud.Modelfile ~/Arcturus_cloud.Modelfile 2>/dev/null
ollama create arcturus-cloud -f ~/Arcturus_cloud.Modelfile 2>/dev/null && echo "  arcturus-cloud ready" || echo "  arcturus-cloud skipped"

# Add aliases to .bashrc
grep -q "alias arcturus=" ~/.bashrc 2>/dev/null || echo 'alias arcturus="ollama run arcturus"' >> ~/.bashrc
grep -q "alias wrex=" ~/.bashrc 2>/dev/null || echo 'alias wrex="ollama run wrex"' >> ~/.bashrc
grep -q "alias arc=" ~/.bashrc 2>/dev/null || echo 'alias arc="ollama run arcturus-cloud"' >> ~/.bashrc

source ~/.bashrc 2>/dev/null

echo ""
echo "=== ALIASES SET ==="
echo "  arcturus  → ollama run arcturus"
echo "  wrex      → ollama run wrex"
echo "  arc       → ollama run arcturus-cloud"
echo ""
echo "Just type the name to invoke. 93."
