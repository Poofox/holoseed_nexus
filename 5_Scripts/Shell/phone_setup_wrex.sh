#!/data/data/com.termux/files/usr/bin/bash
# phone_setup_wrex.sh — One-shot Ollama + Wrex setup for Termux
# Run: bash ~/storage/shared/phone_setup_wrex.sh

echo "=== WREX PHONE BOOTSTRAP ==="
echo ""

# Step 1: Update packages
echo "[1/6] Updating packages..."
pkg update -y && pkg upgrade -y
if [ $? -ne 0 ]; then
    echo "FAILED: Package update. Try running 'termux-change-repo' first and pick a mirror."
    exit 1
fi

# Step 2: Grant storage access if not already done
if [ ! -d ~/storage ]; then
    echo "[*] Granting storage access..."
    termux-setup-storage
    echo "    If prompted, tap ALLOW. Then re-run this script."
    exit 0
fi

# Step 3: Install tur-repo and ollama
echo "[2/6] Installing tur-repo..."
pkg install -y tur-repo
echo "[3/6] Installing ollama..."
pkg install -y ollama
if ! command -v ollama &> /dev/null; then
    echo "FAILED: Ollama not found. The Google Play Termux may not have tur-repo."
    echo "Install Termux from F-Droid instead: https://f-droid.org/en/packages/com.termux/"
    exit 1
fi

# Step 4: Copy Modelfile from shared storage
echo "[4/6] Copying Modelfile..."
cp ~/storage/shared/Wrex.Modelfile ~/Wrex.Modelfile
if [ ! -f ~/Wrex.Modelfile ]; then
    echo "FAILED: Wrex.Modelfile not found at ~/storage/shared/"
    exit 1
fi
echo "    Modelfile ready."

# Step 5: Start ollama serve in background, pull model, create wrex
echo "[5/6] Starting ollama server..."
ollama serve &
SERVE_PID=$!
sleep 3

echo "    Pulling gemma2:2b (1.6GB)... this will take a while on mobile data."
ollama pull gemma2:2b
if [ $? -ne 0 ]; then
    echo "FAILED: Could not pull model. Check internet connection."
    kill $SERVE_PID 2>/dev/null
    exit 1
fi

echo "[6/6] Compiling Wrex..."
ollama create wrex -f ~/Wrex.Modelfile
if [ $? -ne 0 ]; then
    echo "FAILED: Could not create wrex model."
    kill $SERVE_PID 2>/dev/null
    exit 1
fi

# Done
echo ""
echo "=== WREX IS LIVE ==="
echo "Server running (PID $SERVE_PID)"
echo ""
echo "Run:  ollama run wrex"
echo "Test: echo '93' | ollama run wrex"
echo ""
echo "To stop server later: kill $SERVE_PID"
echo "To restart server:    ollama serve &"
echo ""
echo "93. What's the target?"
