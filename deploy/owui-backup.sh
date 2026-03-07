#!/usr/bin/env bash
# =============================================================================
# owui-backup.sh — PhospheneLoom OWUI Chat History Backup
# Exports the open-webui Podman volume, encrypts with GPG AES256.
# Run with: bash owui-backup.sh [output-directory]
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
   ___  _    _ _   _ ___ ____    _    ____ _  ___   _ ____
  / _ \| |  | | | | |_ _| __ )  / \  / ___| |/ / | | |  _ \
 | | | | |  | | | | || ||  _ \ / _ \| |   | ' /| | | | |_) |
 | |_| | |__| | |_| || || |_) / ___ \ |___| . \| |_| |  __/
  \___/|_____/ \___/|___|____/_/   \_\____|_|\_\\___/|_|

                   O W U I   C H A T   B A C K U P
BANNER
echo -e "${RESET}"
echo -e "  Exports + encrypts the open-webui Podman volume\n"

# ---------------------------------------------------------------------------
# ARGS / OUTPUT PATH
# ---------------------------------------------------------------------------
OUTPUT_DIR="${1:-$PWD}"

# Strip trailing slash for consistency
OUTPUT_DIR="${OUTPUT_DIR%/}"

if [[ ! -d "$OUTPUT_DIR" ]]; then
  err "Output directory does not exist: $OUTPUT_DIR"
  echo "  Usage: bash owui-backup.sh [output-directory]"
  exit 1
fi

DATE_STAMP=$(date +"%Y%m%d")
ARCHIVE_NAME="owui-backup-${DATE_STAMP}.tar.gz"
ENCRYPTED_NAME="${ARCHIVE_NAME}.gpg"
ARCHIVE_PATH="${OUTPUT_DIR}/${ARCHIVE_NAME}"
ENCRYPTED_PATH="${OUTPUT_DIR}/${ENCRYPTED_NAME}"

# ---------------------------------------------------------------------------
# PRE-FLIGHT CHECKS
# ---------------------------------------------------------------------------
hdr "Pre-flight Checks"

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

# Check the volume exists
if ! podman volume inspect open-webui &>/dev/null 2>&1; then
  err "Podman volume 'open-webui' not found."
  echo "  Is OWUI set up on this machine? Run windeploy.sh first."
  exit 1
fi
ok "Volume 'open-webui' found"

# Warn if output file already exists
if [[ -f "$ENCRYPTED_PATH" ]]; then
  warn "Output file already exists: $ENCRYPTED_PATH"
  read -rp "  Overwrite? [y/N]: " OVERWRITE
  OVERWRITE="${OVERWRITE:-N}"
  if [[ ! "${OVERWRITE,,}" =~ ^y ]]; then
    info "Backup cancelled."
    exit 0
  fi
  rm -f "$ENCRYPTED_PATH"
fi

# ---------------------------------------------------------------------------
# EXPORT VOLUME
# ---------------------------------------------------------------------------
hdr "Exporting Volume"

info "Exporting 'open-webui' volume to tar archive..."
info "This may take a moment depending on chat history size..."

# Use a temporary helper container to tar the volume contents
# --rm: clean up the container after use
# alpine is minimal and widely available
if podman run --rm \
    -v open-webui:/data:ro \
    -v "${OUTPUT_DIR}:/output" \
    docker.io/library/alpine:latest \
    tar czf "/output/${ARCHIVE_NAME}" -C /data . ; then
  ok "Volume exported: $ARCHIVE_PATH"
else
  err "Volume export failed."
  rm -f "$ARCHIVE_PATH"
  exit 1
fi

# Sanity check — archive should be non-empty
ARCHIVE_SIZE=$(du -sh "$ARCHIVE_PATH" 2>/dev/null | cut -f1 || echo "unknown")
info "Archive size: $ARCHIVE_SIZE"

# ---------------------------------------------------------------------------
# ENCRYPT WITH GPG
# ---------------------------------------------------------------------------
hdr "Encrypting Backup"

info "Encrypting with GPG AES256 symmetric encryption..."
echo -e "  ${YELLOW}You will be prompted for a passphrase twice.${RESET}"
echo -e "  ${YELLOW}Store this passphrase somewhere safe — without it the backup is unrecoverable.${RESET}"
echo ""

if gpg --symmetric \
       --cipher-algo AES256 \
       --output "$ENCRYPTED_PATH" \
       "$ARCHIVE_PATH" ; then
  ok "Encrypted: $ENCRYPTED_PATH"
else
  err "GPG encryption failed."
  rm -f "$ARCHIVE_PATH"
  exit 1
fi

# Remove the unencrypted archive now that we have the .gpg
rm -f "$ARCHIVE_PATH"
ok "Unencrypted archive removed"

# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
hdr "Backup Complete"

FINAL_SIZE=$(du -sh "$ENCRYPTED_PATH" 2>/dev/null | cut -f1 || echo "unknown")

echo -e "${BOLD}File:${RESET}  $ENCRYPTED_PATH"
echo -e "${BOLD}Size:${RESET}  $FINAL_SIZE"
echo ""
echo -e "  To restore on another machine:"
echo -e "  ${CYAN}bash owui-restore.sh $ENCRYPTED_PATH${RESET}"
echo ""
echo -e "${CYAN}93 93/93 — chat history preserved${RESET}"
