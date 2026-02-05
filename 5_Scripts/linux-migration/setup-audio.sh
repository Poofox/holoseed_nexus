#!/bin/bash
# setup-audio.sh - Audio production setup for Nobara KDE
# REAPER + Wine + Yabridge for Windows VSTs
# Run LAST after everything else is working

set -e

echo "=== Audio Production Setup ==="
echo "This installs REAPER and Wine/Yabridge for Windows VSTs."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

###########################################
# PHASE 1: Verify Pipewire (should be default on Nobara)
###########################################
log "Checking Pipewire..."
if systemctl --user is-active pipewire &>/dev/null; then
    log "Pipewire is running"
else
    warn "Pipewire not running. Check audio subsystem."
fi

# Install low-latency tools
sudo dnf install -y \
    pipewire-jack-audio-connection-kit \
    qpwgraph \
    helvum

###########################################
# PHASE 2: REAPER
###########################################
log "Installing REAPER..."

# Option 1: Flatpak (sandboxed, may have VST path issues)
# flatpak install -y flathub com.reaper.Reaper

# Option 2: Native install (recommended for VST compatibility)
if ! command -v reaper &>/dev/null; then
    REAPER_VERSION="7.31"
    REAPER_URL="https://www.reaper.fm/files/7.x/reaper${REAPER_VERSION//.}_linux_x86_64.tar.xz"

    cd /tmp
    wget -q "$REAPER_URL" -O reaper.tar.xz
    tar xf reaper.tar.xz
    cd reaper_linux_x86_64
    sudo ./install-reaper.sh --install /opt --integrate-desktop
    cd ~
    rm -rf /tmp/reaper*

    log "REAPER installed to /opt/REAPER"
else
    log "REAPER already installed"
fi

###########################################
# PHASE 3: Wine Staging
###########################################
log "Installing Wine Staging..."

sudo dnf install -y \
    wine \
    wine-staging \
    winetricks \
    wine-mono \
    wine-gecko

# Initialize wine prefix
if [ ! -d ~/.wine ]; then
    log "Initializing Wine prefix..."
    WINEPREFIX=~/.wine WINEARCH=win64 wineboot --init
fi

###########################################
# PHASE 4: Yabridge
###########################################
log "Installing Yabridge..."

# Enable COPR repo for yabridge
sudo dnf copr enable -y patrickl/yabridge
sudo dnf install -y yabridge yabridgectl

# Configure yabridge paths
# These are where Windows VST installers typically put plugins
log "Configuring yabridge plugin paths..."

# VST2 paths
yabridgectl add ~/.wine/drive_c/Program\ Files/Steinberg/VstPlugins 2>/dev/null || true
yabridgectl add ~/.wine/drive_c/Program\ Files/VSTPlugins 2>/dev/null || true
yabridgectl add ~/.wine/drive_c/Program\ Files/Common\ Files/VST2 2>/dev/null || true

# VST3 paths
yabridgectl add ~/.wine/drive_c/Program\ Files/Common\ Files/VST3 2>/dev/null || true

log "Yabridge configured. After installing Windows VSTs, run: yabridgectl sync"

###########################################
# PHASE 5: Create VST directories
###########################################
log "Creating VST directory structure..."

mkdir -p ~/.wine/drive_c/Program\ Files/Steinberg/VstPlugins
mkdir -p ~/.wine/drive_c/Program\ Files/VSTPlugins
mkdir -p ~/.wine/drive_c/Program\ Files/Common\ Files/VST2
mkdir -p ~/.wine/drive_c/Program\ Files/Common\ Files/VST3

###########################################
# PHASE 6: Notes for VST Installation
###########################################

echo ""
echo "=========================================="
log "Audio setup complete!"
echo "=========================================="
echo ""
echo "REAPER: Run 'reaper' from terminal or find in app menu"
echo ""
echo "To install Windows VSTs:"
echo "  1. Download the Windows VST installer"
echo "  2. Run: wine /path/to/installer.exe"
echo "  3. After install: yabridgectl sync"
echo "  4. Rescan plugins in REAPER"
echo ""
echo "Common VST paths in Wine:"
echo "  VST2: ~/.wine/drive_c/Program Files/VSTPlugins/"
echo "  VST3: ~/.wine/drive_c/Program Files/Common Files/VST3/"
echo ""
echo "For Native Instruments:"
echo "  1. Install Native Access via wine"
echo "  2. Log in and install plugins"
echo "  3. yabridgectl sync"
echo ""
warn "NI under Wine can be finicky. Check winehq.org for compatibility."
echo ""
