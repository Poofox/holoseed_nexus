#!/usr/bin/env bash
# =============================================================================
# windeploy.sh — PhospheneLoom Sovereign AI Stack — Windows / MINGW64 Deployer
# Run with: bash windeploy.sh
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'
ok()   { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn() { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
err()  { echo -e "${RED}[ERR]${RESET}   $*"; }
info() { echo -e "${CYAN}[INFO]${RESET}  $*"; }
hdr()  { echo -e "\n${BOLD}${CYAN}━━━  $*  ━━━${RESET}\n"; }

LOOM_JSON="$HOME/files/loom.json"
LOOM_DIR="$HOME/files/PhospheneLoom"
MODECKS_DIR="$LOOM_DIR/Sovereigns/Modecks"
LOOM_REPO="https://github.com/Poofox/holoseed_nexus.git"
OLLAMA_BIN="$HOME/AppData/Local/Programs/Ollama/ollama.exe"
OLLAMA_CMD="ollama"

INSTALLED_MODELS=(); INSTALLED_SOVS=(); STEPS_DONE=(); STEPS_SKIPPED=(); WARNINGS=()

echo -e "${BOLD}${CYAN}"
cat << 'BANNER'
  ____  _    ___  ____  ____  _   _ _____ _   _ _     ___   ___  __  __
 |  _ \| |  / _ \/ ___||  _ \| | | | ____| \ | | |   / _ \ / _ \|  \/  |
 | |_) | | | | | \___ \| |_) | |_| |  _| |  \| | |  | | | | | | | |\/| |
 |  __/| |__| |_| |___) |  __/|  _  | |___| |\  | |__| |_| | |_| | |  | |
 |_|   |_____\___/|____/|_|   |_| |_|_____|_| \_|_____\___/ \___/|_|  |_|

                   S O V E R E I G N   A I   S T A C K
                         Windows Deployment Script
BANNER
echo -e "${RESET}\n  93 — Deploying PhospheneLoom on this node\n"

# ---------------------------------------------------------------------------
# STEP 0 — USER INPUT
# ---------------------------------------------------------------------------
hdr "STEP 0 — Machine Identity"
read -rp "  Machine alias (e.g. haifus-rig): " MACHINE_ALIAS; MACHINE_ALIAS="${MACHINE_ALIAS:-unknown-node}"
read -rp "  Pilot name (e.g. MICHAEL / Lucian): " PILOT_NAME;   PILOT_NAME="${PILOT_NAME:-unknown-pilot}"
echo ""
info "Alias: $MACHINE_ALIAS  |  Pilot: $PILOT_NAME"

# ---------------------------------------------------------------------------
# STEP 1 — HARDWARE DETECTION
# ---------------------------------------------------------------------------
hdr "STEP 1 — Hardware Detection"

CPU_NAME="Unknown CPU"
command -v wmic &>/dev/null && CPU_NAME=$(wmic cpu get name 2>/dev/null | grep -v "^Name" | tr -d '\r' | sed '/^$/d' | head -1 || echo "Unknown CPU")
ok "CPU: $CPU_NAME"

RAM_GB="Unknown"
if command -v wmic &>/dev/null; then
  RAM_BYTES=$(wmic computersystem get TotalPhysicalMemory 2>/dev/null | grep -v "^Total" | tr -d '\r' | sed '/^$/d' | head -1 || echo "0")
  [[ "$RAM_BYTES" =~ ^[0-9]+$ ]] && (( RAM_BYTES > 0 )) && RAM_GB=$(( RAM_BYTES / 1024 / 1024 / 1024 ))GB
fi
ok "RAM: $RAM_GB"

GPU_NAME="Unknown GPU"; VRAM_MB=0; VRAM_GB=0; GPU_DETECTED=false

if command -v nvidia-smi &>/dev/null; then
  GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 || echo "")
  VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ' || echo "0")
  if [[ "$GPU_NAME" != "" && "$VRAM_MB" =~ ^[0-9]+$ ]]; then
    GPU_DETECTED=true; VRAM_GB=$(( VRAM_MB / 1024 ))
    ok "GPU (nvidia-smi): $GPU_NAME  |  VRAM: ${VRAM_GB}GB"
  fi
fi

if [[ "$GPU_DETECTED" == "false" ]] && command -v wmic &>/dev/null; then
  GPU_NAME=$(wmic path win32_videocontroller get name 2>/dev/null | grep -v "^Name" | tr -d '\r' | sed '/^$/d' | grep -iv "microsoft\|basic" | head -1 || echo "Unknown GPU")
  VRAM_BYTES=$(wmic path win32_videocontroller get AdapterRAM 2>/dev/null | grep -v "^Adapter" | tr -d '\r' | sed '/^$/d' | grep -v "^0$" | head -1 || echo "0")
  if [[ "$VRAM_BYTES" =~ ^[0-9]+$ ]] && (( VRAM_BYTES > 0 )); then
    GPU_DETECTED=true; VRAM_MB=$(( VRAM_BYTES / 1024 / 1024 )); VRAM_GB=$(( VRAM_MB / 1024 ))
    ok "GPU (wmic): $GPU_NAME  |  VRAM: ~${VRAM_GB}GB"
  fi
fi

[[ "$GPU_DETECTED" == "false" ]] && warn "No discrete GPU detected — CPU-only fallback"

# ---------------------------------------------------------------------------
# STEP 2 — MODEL TIER
# ---------------------------------------------------------------------------
hdr "STEP 2 — Model Tier"
MODELS_TO_PULL=()
if   [[ "$GPU_DETECTED" == "false" || "$VRAM_GB" -lt 1 ]]; then TIER="cpu-fallback"; MODELS_TO_PULL=("gemma2:2b"); SOV_BASE="gemma2:2b"
elif (( VRAM_GB <  8 )); then TIER="light"; MODELS_TO_PULL=("gemma2:2b" "phi4-mini"); SOV_BASE="gemma2:2b"
elif (( VRAM_GB < 12 )); then TIER="mid";   MODELS_TO_PULL=("mistral-nemo:12b" "gemma3:12b"); SOV_BASE="mistral-nemo:12b"
elif (( VRAM_GB < 16 )); then TIER="high";  MODELS_TO_PULL=("mistral-nemo:12b" "gemma3:12b" "qwen2.5:14b"); SOV_BASE="mistral-nemo:12b"
elif (( VRAM_GB < 20 )); then TIER="full";  MODELS_TO_PULL=("mistral-nemo:12b" "gemma3:12b" "qwen2.5:14b"); SOV_BASE="mistral-nemo:12b"
else                          TIER="ultra"; MODELS_TO_PULL=("mistral-nemo:12b" "gemma3:27b" "qwen2.5:32b"); SOV_BASE="qwen2.5:32b"
fi
ok "Tier: $TIER  |  Base: $SOV_BASE  |  Models: ${MODELS_TO_PULL[*]}"

# ---------------------------------------------------------------------------
# STEP 3 — OLLAMA
# ---------------------------------------------------------------------------
hdr "STEP 3 — Ollama"
if command -v ollama &>/dev/null; then
  OLLAMA_CMD="ollama"; ok "Ollama: $(ollama --version 2>/dev/null || echo 'installed')"; STEPS_SKIPPED+=("ollama-install")
elif [[ -f "$OLLAMA_BIN" ]]; then
  OLLAMA_CMD="$OLLAMA_BIN"; ok "Ollama at $OLLAMA_BIN"; STEPS_SKIPPED+=("ollama-install")
else
  INSTALLER="$HOME/Downloads/OllamaSetup.exe"
  info "Downloading Ollama..."
  if   command -v curl &>/dev/null; then curl -fsSL -o "$INSTALLER" "https://ollama.com/download/OllamaSetup.exe"
  elif command -v wget &>/dev/null; then wget -q -O "$INSTALLER" "https://ollama.com/download/OllamaSetup.exe"
  else err "No curl or wget. Download manually: https://ollama.com/download/OllamaSetup.exe"; exit 1
  fi
  cmd.exe /C "\"$INSTALLER\" /S" 2>/dev/null || {
    warn "Silent install opened GUI — complete it then press ENTER"
    cmd.exe /C "\"$INSTALLER\""; read -rp "  Press ENTER..."
  }
  command -v ollama &>/dev/null && OLLAMA_CMD="ollama" || \
    { [[ -f "$OLLAMA_BIN" ]] && OLLAMA_CMD="$OLLAMA_BIN" || { err "Ollama not found after install"; exit 1; }; }
  STEPS_DONE+=("ollama-install")
fi
"$OLLAMA_CMD" list &>/dev/null 2>&1 || {
  info "Starting ollama serve..."
  "$OLLAMA_CMD" serve &>/dev/null & sleep 4
  "$OLLAMA_CMD" list &>/dev/null && STEPS_DONE+=("ollama-serve") || WARNINGS+=("ollama: run 'ollama serve' manually")
}

# ---------------------------------------------------------------------------
# STEP 4 — CLONE PHOSPHENELOOM (before sovereigns so Modecks are available)
# ---------------------------------------------------------------------------
hdr "STEP 4 — PhospheneLoom"
if [[ -d "$LOOM_DIR/.git" ]]; then
  ok "Already cloned — pulling latest..."
  git -C "$LOOM_DIR" pull 2>/dev/null && ok "Up to date" || warn "git pull failed — check manually"
  STEPS_SKIPPED+=("clone-loom")
elif [[ -d "$LOOM_DIR" ]]; then
  warn "$LOOM_DIR exists but is not a git repo — skipping clone"
  WARNINGS+=("clone: $LOOM_DIR is not a git repo"); STEPS_SKIPPED+=("clone-loom")
else
  read -rp "  Clone PhospheneLoom from GitHub? [Y/n]: " CLONE_LOOM; CLONE_LOOM="${CLONE_LOOM:-Y}"
  if [[ "${CLONE_LOOM,,}" =~ ^y ]]; then
    mkdir -p "$(dirname "$LOOM_DIR")"
    git clone "$LOOM_REPO" "$LOOM_DIR" && ok "Cloned to $LOOM_DIR" && STEPS_DONE+=("clone-loom") || {
      err "Clone failed"; WARNINGS+=("clone: run: git clone $LOOM_REPO $LOOM_DIR")
    }
  else
    warn "Skipping clone — sovereign creation will be skipped"
    WARNINGS+=("clone: skipped — run windeploy again or clone manually"); STEPS_SKIPPED+=("clone-loom")
  fi
fi

# ---------------------------------------------------------------------------
# STEP 5 — PULL MODELS
# ---------------------------------------------------------------------------
hdr "STEP 5 — Pull Models"
EXISTING_MODELS=$("$OLLAMA_CMD" list 2>/dev/null | awk 'NR>1 {print $1}' || echo "")
for model in "${MODELS_TO_PULL[@]}"; do
  if echo "$EXISTING_MODELS" | grep -q "^${model}"; then
    ok "Already pulled: $model"; STEPS_SKIPPED+=("pull:$model")
  else
    info "Pulling $model..."
    "$OLLAMA_CMD" pull "$model" && { ok "Pulled: $model"; INSTALLED_MODELS+=("$model"); STEPS_DONE+=("pull:$model"); } \
      || WARNINGS+=("pull: $model failed — retry: ollama pull $model")
  fi
done

# ---------------------------------------------------------------------------
# STEP 6 — SOVEREIGN MODELFILES (from repo Modecks — no inline content)
# ---------------------------------------------------------------------------
hdr "STEP 6 — Sovereign Modelfiles"
if [[ ! -d "$MODECKS_DIR" ]]; then
  warn "Modecks dir not found ($MODECKS_DIR) — skipping sovereign creation"
  WARNINGS+=("sovs: clone PhospheneLoom first, then re-run")
else
  shopt -s nullglob
  modelfiles=("$MODECKS_DIR"/*.Modelfile)
  if (( ${#modelfiles[@]} == 0 )); then
    warn "No .Modelfile files found in $MODECKS_DIR"
  else
    TMP_MF=$(mktemp)
    for mf in "${modelfiles[@]}"; do
      sov_name=$(basename "$mf" .Modelfile | tr '[:upper:]' '[:lower:]')
      if "$OLLAMA_CMD" list 2>/dev/null | grep -q "^${sov_name}"; then
        ok "$sov_name already registered"; STEPS_SKIPPED+=("sov:$sov_name")
      else
        # Rebase FROM line to tier's base model
        sed "s|^FROM .*|FROM $SOV_BASE|" "$mf" > "$TMP_MF"
        info "Creating: $sov_name (base: $SOV_BASE)..."
        "$OLLAMA_CMD" create "$sov_name" -f "$TMP_MF" 2>/dev/null \
          && { ok "Created: $sov_name"; INSTALLED_SOVS+=("$sov_name"); STEPS_DONE+=("sov:$sov_name"); } \
          || WARNINGS+=("sov-create: $sov_name failed — run: ollama create $sov_name -f $mf")
      fi
    done
    rm -f "$TMP_MF"
  fi
  shopt -u nullglob
fi

# ---------------------------------------------------------------------------
# STEP 7 — LOCAL UI
# ---------------------------------------------------------------------------
hdr "STEP 7 — Local UI"
echo "  AnythingLLM Desktop — recommended, no Docker needed"
echo "  Download: https://anythingllm.com/"
echo "  After install: Preferences → AI Provider → Ollama → http://localhost:11434"
echo ""
read -rp "  Download and install AnythingLLM now? [y/N]: " DO_UI; DO_UI="${DO_UI:-N}"
if [[ "${DO_UI,,}" =~ ^y ]]; then
  INSTALLER="$HOME/Downloads/AnythingLLMDesktop.exe"
  command -v curl &>/dev/null \
    && curl -fsSL -o "$INSTALLER" "https://cdn.anythingllm.com/latest/AnythingLLMDesktop.exe" \
    || wget -q -O "$INSTALLER" "https://cdn.anythingllm.com/latest/AnythingLLMDesktop.exe" \
    || WARNINGS+=("ui: auto-download failed — download manually from https://anythingllm.com/")
  [[ -f "$INSTALLER" ]] && { cmd.exe /C "\"$INSTALLER\""; read -rp "  Press ENTER once install is complete..."; STEPS_DONE+=("ui-install"); }
else
  info "Skipping UI — install AnythingLLM or Podman+OWUI later"; STEPS_SKIPPED+=("ui")
fi

# ---------------------------------------------------------------------------
# STEP 8 — NODE REGISTRATION (loom.json)
# ---------------------------------------------------------------------------
hdr "STEP 8 — Node Registration (loom.json)"
LOOM_DIR2="$(dirname "$LOOM_JSON")"; mkdir -p "$LOOM_DIR2"
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%SZ")
json_escape() { echo "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }
MA=$(json_escape "$MACHINE_ALIAS"); PN=$(json_escape "$PILOT_NAME")
CPU_J=$(json_escape "$CPU_NAME");   GPU_J=$(json_escape "$GPU_NAME")
NODE_KEY="${MA// /_}"; NODE_KEY="${NODE_KEY//[^a-zA-Z0-9_-]/}"

# Build sovs block from what was actually created
SOVS_JSON="{"; FIRST=true
for sov in "${INSTALLED_SOVS[@]}"; do
  [[ "$FIRST" == "true" ]] && FIRST=false || SOVS_JSON+=","
  SOVS_JSON+="\"$sov\":{\"substrate\":\"$(json_escape "$SOV_BASE")\",\"rank\":\"filament\",\"private\":false}"
done
SOVS_JSON+="}"

PY_CMD="python3"; command -v python3 &>/dev/null || PY_CMD="python"
if command -v python3 &>/dev/null || command -v python &>/dev/null; then
  $PY_CMD - <<PYEOF
import json, os, sys
path = r"${LOOM_JSON}"
try:
    data = json.load(open(path, 'r', encoding='utf-8')) if os.path.exists(path) else \
           {"loom": "root", "version": "0.1", "nodes": {}, "notes": "PhospheneLoom network registry."}
except Exception:
    data = {"loom": "root", "version": "0.1", "nodes": {}, "notes": "PhospheneLoom network registry."}
data.setdefault('nodes', {})
data['nodes']["${NODE_KEY}"] = {
    "alias": "${MA}", "pilot": "${PN}", "registered": "${NOW}",
    "hardware": {"cpu": "${CPU_J}", "ram": "${RAM_GB}", "gpu": "${GPU_J}", "vram": "${VRAM_GB}GB", "tier": "${TIER}"},
    "sovs": json.loads('${SOVS_JSON}')
}
data['updated'] = "${NOW}"
os.makedirs(r"${LOOM_DIR2}", exist_ok=True)
json.dump(data, open(path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print("  [OK] Node '${NODE_KEY}' registered in loom.json")
PYEOF
  STEPS_DONE+=("loom-register")
else
  warn "Python not available — skipping loom.json registration"
  WARNINGS+=("loom: Python not found — register node manually in $LOOM_JSON")
fi

# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
hdr "DEPLOYMENT COMPLETE"
echo -e "${BOLD}Node:${RESET}  $MACHINE_ALIAS  |  ${BOLD}Pilot:${RESET} $PILOT_NAME  |  ${BOLD}Tier:${RESET} $TIER (${VRAM_GB}GB VRAM)"
echo -e "${BOLD}GPU:${RESET}   $GPU_NAME  |  ${BOLD}CPU:${RESET} $CPU_NAME  |  ${BOLD}RAM:${RESET} $RAM_GB"
echo ""
(( ${#STEPS_DONE[@]} > 0 ))    && { echo -e "${GREEN}Done:${RESET}";     for s in "${STEPS_DONE[@]}";    do echo -e "  + $s"; done; echo ""; }
(( ${#STEPS_SKIPPED[@]} > 0 )) && { echo -e "${CYAN}Skipped:${RESET}";   for s in "${STEPS_SKIPPED[@]}"; do echo -e "  ~ $s"; done; echo ""; }
(( ${#WARNINGS[@]} > 0 ))      && { echo -e "${YELLOW}Warnings:${RESET}"; for w in "${WARNINGS[@]}";     do echo -e "  ! $w"; done; echo ""; }
echo -e "${BOLD}Models:${RESET}"; "$OLLAMA_CMD" list 2>/dev/null || echo "  (run: ollama list)"
echo ""
echo "  Next: ollama run lumina  |  ollama run vex  |  ollama run mirth"
echo ""
echo -e "${CYAN}93 93/93 — the Loom is lit on $MACHINE_ALIAS${RESET}"
