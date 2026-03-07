#!/usr/bin/env bash
# =============================================================================
# owui-restore.sh — PhospheneLoom OWUI Chat History Restore
# Decrypts a GPG-encrypted backup and imports it into the open-webui volume.
# Run with: bash owui-restore.sh <owui-backup-YYYYMMDD.tar.gz.gpg>
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# COLOR CODES
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

ok()   { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn() { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
err()  { echo -e "${RED}[ERR]${RESET}   $*"; }
info() { echo -e "${CYAN}[INFO]${RESET}  $*"; }
hdr()  { echo -e "\n${BOLD}${CYAN}━━━  $*  ━━━${RESET}\n"; }

# ---------------------------------------------------------------------------
# BANNER
# ---------------------------------------------------------------------------
echo -e "${BOLD}${CYAN}"
cat << 'BANNER'
   ___  _    _ _   _ ___ ____  _____ ____ _____ ___  ____  _____
  / _ \| |  | | | | |_ _|  _ \| ____/ ___|_   _/ _ \|  _ \| ____|
 | | | | |  | | | | || || |_) |  _| \___ \ | || | | | |_) |  _|
 | |_| | |__| | |_| || ||  _ <| |___ ___) || || |_| |  _ <| |___
  \___/|_____/ \___/|___|_| \_\_____|____/ |_| \___/|_| \_\_____|

                   O W U I   C H A T   R E S T O R E
BANNER
echo -e "${RESET}"
echo -e "  Decrypts + imports an OWUI chat history backup\n"

# ---------------------------------------------------------------------------
# ARGS
# ---------------------------------------------------------------------------
if [[ $# -lt 1 ]]; then
  err "No backup file specified."
  echo ""
  echo "  Usage: bash owui-restore.sh <owui-backup-YYYYMMDD.tar.gz.gpg>"
  echo ""
  echo "  Example:"
  echo "    bash owui-restore.sh owui-backup-20260306.tar.gz.gpg"
  exit 1
fi

BACKUP_FILE="$1"

# Resolve to absolute path
if [[ "$BACKUP_FILE" != /* ]]; then
  BACKUP_FILE="$PWD/$BACKUP_FILE"
fi

# ---------------------------------------------------------------------------
# PRE-FLIGHT CHECKS
# ---------------------------------------------------------------------------
hdr "Pre-flight Checks"

# Check backup file exists
if [[ ! -f "$BACKUP_FILE" ]]; then
  err "Backup file not found: $BACKUP_FILE"
  exit 1
fi
BACKUP_SIZE=$(du -sh "$BACKUP_FILE" 2>/dev/null | cut -f1 || echo "unknown")
ok "Backup file: $BACKUP_FILE ($BACKUP_SIZE)"

# Check Podman
if ! command -v podman &>/dev/null; then
  err "Podman not found. Install from https://podman-desktop.io"
  exit 1
fi
PODMAN_VER=$(podman --version 2>/dev/null || echo "unknown")
ok "Podman: $PODMAN_VER"

# Check GPG
if ! command -v gpg &>/dev/null; then
  err "GPG not found. Git for Windows includes GPG — ensure Git Bash is fully installed."
  exit 1
fi
GPG_VER=$(gpg --version 2>/dev/null | head -1 || echo "unknown")
ok "GPG: $GPG_VER"

# ---------------------------------------------------------------------------
# SAFETY GATE — warn about overwriting existing data
# ---------------------------------------------------------------------------
hdr "Safety Check"

if podman volume inspect open-webui &>/dev/null 2>&1; then
  warn "Volume 'open-webui' already exists on this machine."
  warn "Restoring will OVERWRITE all existing chat history and settings."
  echo ""
  read -rp "  Type 'yes' to confirm overwrite, anything else to cancel: " CONFIRM
  if [[ "$CONFIRM" != "yes" ]]; then
    info "Restore cancelled. Existing data untouched."
    exit 0
  fi
  ok "Overwrite confirmed"
else
  info "Volume 'open-webui' does not exist — will be created fresh"
fi

# ---------------------------------------------------------------------------
# STOP OWUI CONTAINER IF RUNNING
# ---------------------------------------------------------------------------
hdr "Stopping OWUI Container"

if podman ps --format '{{.Names}}' 2>/dev/null | grep -q "^open-webui$"; then
  info "Stopping running open-webui container..."
  if podman stop open-webui 2>/dev/null; then
    ok "Container stopped"
  else
    warn "Could not stop container — continuing anyway"
  fi
else
  ok "open-webui container not running — nothing to stop"
fi

# ---------------------------------------------------------------------------
# DECRYPT BACKUP
# ---------------------------------------------------------------------------
hdr "Decrypting Backup"

# Derive temp archive path next to backup file (same directory)
BACKUP_DIR="$(dirname "$BACKUP_FILE")"
ARCHIVE_NAME="$(basename "$BACKUP_FILE" .gpg)"
ARCHIVE_PATH="${BACKUP_DIR}/${ARCHIVE_NAME}"

# Clean up any leftover temp archive from a previous failed run
[[ -f "$ARCHIVE_PATH" ]] && rm -f "$ARCHIVE_PATH"

info "Decrypting: $BACKUP_FILE"
echo -e "  ${YELLOW}Enter the passphrase you used when creating the backup.${RESET}"
echo ""

if gpg --decrypt \
       --output "$ARCHIVE_PATH" \
       "$BACKUP_FILE" ; then
  ok "Decrypted to: $ARCHIVE_PATH"
else
  err "GPG decryption failed. Wrong passphrase or corrupted file."
  rm -f "$ARCHIVE_PATH"
  exit 1
fi

# ---------------------------------------------------------------------------
# CREATE VOLUME IF NEEDED
# ---------------------------------------------------------------------------
hdr "Preparing Volume"

if ! podman volume inspect open-webui &>/dev/null 2>&1; then
  info "Creating 'open-webui' volume..."
  if podman volume create open-webui; then
    ok "Volume 'open-webui' created"
  else
    err "Failed to create volume 'open-webui'"
    rm -f "$ARCHIVE_PATH"
    exit 1
  fi
else
  ok "Volume 'open-webui' exists — will overwrite contents"
fi

# ---------------------------------------------------------------------------
# IMPORT INTO VOLUME
# ---------------------------------------------------------------------------
hdr "Importing Data"

info "Importing archive into 'open-webui' volume..."
info "This may take a moment..."

# Mount the volume + the directory containing the archive into alpine
# Extract into /data (the volume mount point)
ARCHIVE_BASENAME="$(basename "$ARCHIVE_PATH")"

if podman run --rm \
    -v open-webui:/data \
    -v "${BACKUP_DIR}:/backup:ro" \
    docker.io/library/alpine:latest \
    sh -c "rm -rf /data/* /data/.[!.]* 2>/dev/null || true; tar xzf /backup/${ARCHIVE_BASENAME} -C /data" ; then
  ok "Data imported into volume 'open-webui'"
else
  err "Import failed. Volume may be in a partial state."
  rm -f "$ARCHIVE_PATH"
  exit 1
fi

# Remove decrypted temp archive now that import is done
rm -f "$ARCHIVE_PATH"
ok "Temporary decrypted archive removed"

# ---------------------------------------------------------------------------
# RESTART OWUI CONTAINER
# ---------------------------------------------------------------------------
hdr "Restarting OWUI"

# Check if the container exists (stopped or running)
if podman ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^open-webui$"; then
  info "Starting existing open-webui container..."
  if podman start open-webui 2>/dev/null; then
    ok "open-webui container restarted"
  else
    warn "Could not restart container — start it manually: podman start open-webui"
  fi
else
  warn "No 'open-webui' container found to restart."
  echo ""
  echo "  The volume data has been restored, but the container does not exist yet."
  echo "  Run windeploy.sh (choose 'podman') to create the OWUI container,"
  echo "  or start it manually:"
  echo ""
  echo -e "  ${CYAN}podman run -d \\"
  echo "    --name open-webui \\"
  echo "    --network=host \\"
  echo "    -v open-webui:/app/backend/data \\"
  echo "    -e OLLAMA_BASE_URL=http://127.0.0.1:11434 \\"
  echo "    --restart always \\"
  echo -e "    ghcr.io/open-webui/open-webui:main${RESET}"
fi

# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
hdr "Restore Complete"

echo -e "${BOLD}Restored from:${RESET}  $BACKUP_FILE"
echo ""
echo -e "  Visit ${CYAN}http://localhost:3000${RESET} to verify your chat history is intact."
echo ""
echo -e "${CYAN}93 93/93 — the thread continues${RESET}"
