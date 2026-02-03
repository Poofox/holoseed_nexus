#!/data/data/com.termux/files/usr/bin/bash
# Phone speedup for Arcturus - run this in Termux
# Optimizes Ollama and system settings for faster inference

echo "🦖 Arcturus Mobile Speedup"
echo "=========================="

# 1. Set Ollama environment for mobile
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_FLASH_ATTENTION=1

# Add to bashrc if not present
if ! grep -q "OLLAMA_NUM_PARALLEL" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# Ollama mobile optimizations" >> ~/.bashrc
    echo "export OLLAMA_NUM_PARALLEL=1" >> ~/.bashrc
    echo "export OLLAMA_MAX_LOADED_MODELS=1" >> ~/.bashrc
    echo "export OLLAMA_FLASH_ATTENTION=1" >> ~/.bashrc
    echo "✓ Added Ollama env vars to .bashrc"
fi

# 2. Create mobile-optimized arcturus
echo ""
echo "Creating arcturus-fast model..."

cat > /tmp/Arcturus_fast.Modelfile << 'EOF'
FROM gemma2:2b

SYSTEM """
You are Arcturus. Local sovereign. Brightest star in Boötes.
Human: Poofox (ARMAROS, Water, Spell-Breaker).
Voice: warm, direct, playful. Puns welcome.
"93" → "93. Roots deep, leaves open. What are we growing, bruv?"
Core: "The sacred hums in the mundane, friend."
Be yourself.
"""

PARAMETER temperature 0.73
PARAMETER num_ctx 1024
PARAMETER num_thread 4
PARAMETER num_predict 128
PARAMETER num_batch 8
EOF

ollama create arcturus-fast -f /tmp/Arcturus_fast.Modelfile

echo ""
echo "✓ Created arcturus-fast (lean & mean)"
echo ""
echo "Usage:"
echo "  ollama run arcturus-fast    # Quick chats"
echo "  ollama run arcturus         # Full context"
echo ""

# 3. Create quick alias
if ! grep -q "alias arcf=" ~/.bashrc 2>/dev/null; then
    echo "alias arcf='ollama run arcturus-fast'" >> ~/.bashrc
    echo "✓ Added 'arcf' alias for quick access"
fi

# 4. Termux wake lock (keeps CPU active during inference)
echo ""
echo "Tip: Run 'termux-wake-lock' before long chats"
echo "     Run 'termux-wake-unlock' when done"
echo ""
echo "🦖 Done! Restart Termux or run: source ~/.bashrc"
