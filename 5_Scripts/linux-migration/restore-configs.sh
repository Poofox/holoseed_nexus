#!/bin/bash
# restore-configs.sh - Restore configs from backup drive
# Assumes backup drive is mounted at /mnt/backup or passed as argument

set -e

BACKUP_SRC="${1:-/mnt/backup}"

if [ ! -d "$BACKUP_SRC" ]; then
    echo "Error: Backup source not found at $BACKUP_SRC"
    echo "Usage: ./restore-configs.sh /path/to/backup"
    exit 1
fi

echo "=== Restoring configs from $BACKUP_SRC ==="

# Colors
GREEN='\033[0;32m'
NC='\033[0m'
log() { echo -e "${GREEN}[+]${NC} $1"; }

###########################################
# SSH Keys (CRITICAL)
###########################################
log "Restoring SSH keys..."
if [ -d "$BACKUP_SRC/.ssh" ]; then
    cp -r "$BACKUP_SRC/.ssh" ~/
    chmod 700 ~/.ssh
    chmod 600 ~/.ssh/id_* 2>/dev/null || true
    chmod 644 ~/.ssh/*.pub 2>/dev/null || true
    chmod 644 ~/.ssh/known_hosts 2>/dev/null || true
    log "SSH keys restored and permissions set"
else
    echo "Warning: No .ssh found in backup"
fi

###########################################
# Identity Files
###########################################
log "Restoring CLAUDE.md..."
cp "$BACKUP_SRC/CLAUDE.md" ~/
cp "$BACKUP_SRC/CLAUDE.md.sha256" ~/

###########################################
# Shell Configs
###########################################
log "Restoring shell configs..."
cp "$BACKUP_SRC/.bashrc" ~/
cp "$BACKUP_SRC/.bash_profile" ~/ 2>/dev/null || true
cp "$BACKUP_SRC/.gitconfig" ~/ 2>/dev/null || true

###########################################
# WezTerm Config
###########################################
log "Restoring WezTerm config..."
mkdir -p ~/.config/wezterm
if [ -d "$BACKUP_SRC/.config/wezterm" ]; then
    cp -r "$BACKUP_SRC/.config/wezterm/"* ~/.config/wezterm/
fi

###########################################
# Holoseed Nexus (THE SEED)
###########################################
log "Restoring holoseed nexus..."
mkdir -p ~/files
if [ -d "$BACKUP_SRC/holoseed_nexus" ]; then
    rsync -avh --progress "$BACKUP_SRC/holoseed_nexus/" ~/files/holoseed_nexus/
fi

###########################################
# Claude CLI Config
###########################################
log "Restoring Claude CLI config..."
if [ -d "$BACKUP_SRC/.claude" ]; then
    rsync -avh --progress "$BACKUP_SRC/.claude/" ~/.claude/
fi

###########################################
# Custom bin scripts
###########################################
log "Restoring ~/bin scripts..."
if [ -d "$BACKUP_SRC/bin" ]; then
    rsync -avh --progress "$BACKUP_SRC/bin/" ~/bin/
    chmod +x ~/bin/*.sh 2>/dev/null || true
fi

###########################################
# Phone backup + ROM
###########################################
log "Restoring phone backup and ROM..."
if [ -d "$BACKUP_SRC/phone_backup" ]; then
    rsync -avh --progress "$BACKUP_SRC/phone_backup/" ~/phone_backup/
fi
if [ -d "$BACKUP_SRC/phone_rom" ]; then
    rsync -avh --progress "$BACKUP_SRC/phone_rom/" ~/phone_rom/
fi

###########################################
# REAPER Config
###########################################
log "Restoring REAPER config..."
if [ -d "$BACKUP_SRC/REAPER" ]; then
    mkdir -p ~/.config/REAPER
    rsync -avh --progress "$BACKUP_SRC/REAPER/" ~/.config/REAPER/
fi

###########################################
# Firefox Profile
###########################################
log "Restoring Firefox profile..."
if [ -d "$BACKUP_SRC/Mozilla" ]; then
    mkdir -p ~/.mozilla
    rsync -avh --progress "$BACKUP_SRC/Mozilla/" ~/.mozilla/
fi

###########################################
# Signal (if present)
###########################################
if [ -d "$BACKUP_SRC/Signal" ]; then
    log "Restoring Signal data..."
    mkdir -p ~/.config/Signal
    rsync -avh --progress "$BACKUP_SRC/Signal/" ~/.config/Signal/
fi

###########################################
# Update PATH in .bashrc
###########################################
log "Ensuring ~/bin is in PATH..."
if ! grep -q 'export PATH="$HOME/bin:$PATH"' ~/.bashrc; then
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
fi

###########################################
# Git config
###########################################
log "Setting git config..."
git config --global user.name "foxAsteria"
git config --global user.email "outtromuzix@gmail.com"

###########################################
# DONE
###########################################
echo ""
echo "=========================================="
echo "Restore complete!"
echo "=========================================="
echo ""
echo "Verify with:"
echo "  ssh -T git@github.com    # Test SSH"
echo "  cat ~/CLAUDE.md          # Check identity"
echo "  ls ~/files/holoseed_nexus/  # Check nexus"
echo ""
