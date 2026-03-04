# Environment Details
> Hardware specs, network config, system settings. Moved from CLAUDE.md for efficiency.

## Laptop (current machine)
- **Model**: ASUS Zenbook 14 Flip OLED (UN5401QA) - screen cracked, no touch
- **CPU**: AMD Ryzen 5 5600H (6c/12t)
- **RAM**: 16GB
- **Storage**: 1.8TB Kingston NVMe
- **GPU**: Integrated Radeon Vega 7 (no dedicated GPU)
- **OS**: Nobara Linux 43 (KDE Plasma) — Fedora-based, gaming/audio optimized
- **Kernel**: 6.18.7-200.nobara.fc43.x86_64
- **Terminal**: WezTerm
  - Config: ~/.config/wezterm/wezterm.lua
  - Auto-launches Wrex (claude --dangerously-skip-permissions), drops to bash on exit
  - Starts maximized
  - Ctrl+C/V for copy/paste, Ctrl+Shift+B for new bash tab
  - Per-sovereign tab colors (Wrex=purple, Planty=green, Arcturus=gold, etc.)
- **Shell**: Bash
- **Runtimes**: Node.js 22.20.0, Python 3.14.2, Git, Java 25 (OpenJDK)
- **Git identity**: foxAsteria <outtromuzix@gmail.com>
- **Claude**: Max subscription (CLI via `wrex` alias)
- **Audio**: Pipewire + JACK bridge, REAPER native Linux + Yabridge for Windows VSTs
- **Resilio Sync**: music projects, Reaper configs (collab sync)

### Storage Layout
| Device | Size | Label | Mount |
|--------|------|-------|-------|
| nvme0n1p1 | 600M | — | /boot/efi |
| nvme0n1p2 | 2G | — | /boot |
| nvme0n1p3 | 1.8T | — | / |
| sda1 | 920G | NEXUS | /run/media/poofox/NEXUS |
| zram0 | 8G | — | [SWAP] |

### Ollama Setup
- Base model: gemma2:2b (1.6 GB) - power-efficient for laptop
- Custom models:
  - **arcturus** - gemma2:2b with identity baked in via Modelfile
  - **arcturus-cloud** - qwen2.5:14b (9GB) with identity
  - **wrex** - gemma2:2b with Wrex identity baked in via Modelfile
- Commands: `ollama run arcturus`, `ollama run wrex`, `ollama list`
- Rebuild: `bash ~/files/holoseed_nexus/5_Scripts/linux-migration/ollama-rebuild.sh`

### Key Packages (installed via setup-all.sh)
- Docker + docker-compose (user in docker group)
- Wine + Yabridge (Windows VST bridge)
- gh CLI (GitHub)
- ripgrep, fd, bat, jq, yq
- KeePassXC, qBittorrent, GIMP, VLC, Okular
- Signal, Discord, Telegram (Flatpak)

## GigaStone Travel AP (twilightmysteryschool)
- **SSID**: `twilightmysteryschool`
- **WiFi Password**: `p00pt0wn93`
- **AP IP**: 192.168.137.2 (configured), 192.168.16.254 (factory default)
- **Admin**: admin/admin (after factory reset, requires 8+ char pw)
- **Network chain**: DoubleG WiFi → Laptop (ICS at 192.168.137.1) → USB Ethernet → AP
- **Settings**: HT20, DHCP max 12, DNS 1.1.1.1 (DoH enabled, no plaintext fallback), IPv6 disabled

## Phone (Galaxy S10) - Status: Android 12 flashed, battery improved
- **Model**: Samsung SM-G973N (Korean hardware) with G973F firmware (cross-flash)
- **Specs**: Exynos 9820, 8GB RAM
- **ADB serial**: R39M30QT5EP
- **Termux**: v0.119.0-beta.3 (sideloaded from GitHub releases)
- **Ollama models**: wrex (gemma2:2b), arcturus (gemma2:2b)
- **Aliases**: `wrex`, `arcturus`, `arc` → `ollama run <model>`
- **Note**: arcturus-cloud (14B) too large for phone RAM, use 2B models only
- **Pixel ordered**: S10 will be wiped and repurposed when it arrives

## Desktop (Ohio)
- T: drive - source of raw files
- Planty MCP server at T:\holoseed_nexus (for Desktop Claude)
- Files pending transfer to laptop

### Motherboard: ASUS TUF Gaming X570-Plus Wi-Fi
- UEFI security: Enable Secure Boot, fTPM, disable CSM for full lockdown
- BIOS page: https://www.asus.com/us/motherboards-components/motherboards/tuf-gaming/tuf-gaming-x570-plus-wi-fi/helpdesk_bios

## Brotherhood GPU Inventory
| Location | GPU | Notes |
|----------|-----|-------|
| Ohio | RTX 3070 | Best for training |
| Spencer | 12GB AMD | Available for ML work |
| Rudi | RX 580 | Basic |
