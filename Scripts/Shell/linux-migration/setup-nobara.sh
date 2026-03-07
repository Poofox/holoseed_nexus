#!/bin/bash
# setup-nobara.sh - Post-install automation for Nobara KDE
# Run after fresh Nobara install. Idempotent - safe to re-run.

set -e

echo "=== Nobara KDE Setup for Poofox ==="
echo "This script installs all apps, dev tools, and configs."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[X]${NC} $1"; }

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    error "Don't run this as root. Run as your normal user."
    exit 1
fi

###########################################
# PHASE 1: System Foundation
###########################################
log "Phase 1: System Foundation"

# Update system first
sudo dnf upgrade -y --refresh

# Core utilities
sudo dnf install -y \
    git curl wget \
    htop btop neofetch \
    zsh fish \
    ripgrep fd-find bat \
    jq yq \
    unzip p7zip p7zip-plugins \
    rsync

###########################################
# PHASE 2: Development Runtimes
###########################################
log "Phase 2: Development Runtimes"

# Node.js (via dnf - Nobara has recent versions)
sudo dnf install -y nodejs npm

# Python
sudo dnf install -y python3 python3-pip python3-devel

# Java (for gradle/bcd)
sudo dnf install -y java-21-openjdk java-21-openjdk-devel

# Rust (optional but useful)
if ! command -v rustc &> /dev/null; then
    warn "Rust not found. Install with: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
fi

###########################################
# PHASE 3: Docker
###########################################
log "Phase 3: Docker"

if ! command -v docker &> /dev/null; then
    sudo dnf install -y docker docker-compose
    sudo systemctl enable --now docker
    sudo usermod -aG docker "$USER"
    warn "Docker installed. Log out and back in for group permissions."
else
    log "Docker already installed"
fi

###########################################
# PHASE 4: Ollama
###########################################
log "Phase 4: Ollama"

if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
    # Enable and start service
    sudo systemctl enable --now ollama
else
    log "Ollama already installed"
fi

###########################################
# PHASE 5: Claude CLI
###########################################
log "Phase 5: Claude CLI"

if ! command -v claude &> /dev/null; then
    npm install -g @anthropic-ai/claude-code
else
    log "Claude CLI already installed"
fi

###########################################
# PHASE 6: Core Applications
###########################################
log "Phase 6: Core Applications"

# From dnf repos
sudo dnf install -y \
    keepassxc \
    qbittorrent \
    gimp \
    okular \
    firefox \
    vlc

# Flatpaks (better sandboxing for chat apps)
flatpak install -y flathub \
    org.signal.Signal \
    com.discordapp.Discord \
    org.telegram.desktop \
    com.sublimetext.three

###########################################
# PHASE 7: Terminal (WezTerm)
###########################################
log "Phase 7: WezTerm"

if ! command -v wezterm &> /dev/null; then
    # Nobara may have it, try dnf first
    sudo dnf install -y wezterm || flatpak install -y flathub org.wezfurlong.wezterm
else
    log "WezTerm already installed"
fi

###########################################
# PHASE 8: Android Tools
###########################################
log "Phase 8: Android Tools"

sudo dnf install -y android-tools  # adb, fastboot

###########################################
# PHASE 9: Age Encryption
###########################################
log "Phase 9: Age encryption tool"

if ! command -v age &> /dev/null; then
    sudo dnf install -y age || {
        # Manual install if not in repos
        AGE_VERSION="1.3.1"
        wget -q "https://github.com/FiloSottile/age/releases/download/v${AGE_VERSION}/age-v${AGE_VERSION}-linux-amd64.tar.gz"
        tar xf age-v${AGE_VERSION}-linux-amd64.tar.gz
        sudo mv age/age age/age-keygen /usr/local/bin/
        rm -rf age age-v${AGE_VERSION}-linux-amd64.tar.gz
    }
else
    log "Age already installed"
fi

###########################################
# PHASE 10: Audio Production (Optional - run separately)
###########################################
# Uncomment to include audio setup
# source "$(dirname "$0")/setup-audio.sh"

###########################################
# PHASE 11: Create directory structure
###########################################
log "Phase 11: Directory structure"

mkdir -p ~/files
mkdir -p ~/bin
mkdir -p ~/projects
mkdir -p ~/.config/wezterm

###########################################
# DONE
###########################################
echo ""
echo "=========================================="
log "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Log out and back in (for docker group)"
echo "  2. Run restore-configs.sh to restore your data"
echo "  3. Run ollama-rebuild.sh to recreate sovereigns"
echo "  4. Run setup-audio.sh when ready for REAPER + VSTs"
echo ""
