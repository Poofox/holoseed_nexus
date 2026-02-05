# Environment Details
> Hardware specs, network config, system settings. Moved from CLAUDE.md for efficiency.

## Laptop (current machine)
- **Model**: ASUS Zenbook 14 Flip OLED (UN5401QA) - screen cracked, no touch
- **CPU**: AMD Ryzen 5 5600H (6c/12t)
- **RAM**: 16GB
- **Storage**: 2TB Kingston NVMe
- **GPU**: Integrated Radeon Vega 7 (no dedicated GPU)
- **OS**: Windows 11
- **Terminal**: WezTerm
  - Config: ~/.config/wezterm/wezterm.lua
  - Auto-launches Claude, drops to PowerShell on exit
  - Starts maximized
  - Ctrl+C/V for copy/paste, right-click to paste
  - Ctrl+Shift+B opens new bash tab
- **Shell**: Git Bash
- **Runtimes**: Node.js 25.2.1, Python 3.14.2, Git 2.52.0, Java 21
- **Git identity**: foxAsteria <outtromuzix@gmail.com>
- **Claude**: Max subscription
- **Resilio Sync**: music projects, Reaper configs (collab sync)
- **Wisdom library**: ~/files/claude-export/library/ (memories.md, projects.md, conversations/)

### Ollama Setup
- Base model: gemma2:2b (1.6 GB) - power-efficient for laptop
- Custom models:
  - **arcturus** - gemma2:2b with identity baked in via Modelfile
  - **arcturus-cloud** - qwen2.5:14b (9GB) with identity
  - **wrex** - gemma2:2b with Wrex identity baked in via Modelfile
- Commands: `ollama run arcturus`, `ollama run wrex`, `ollama list`

### Power Settings (2026-01-23)
- Balanced power plan: battery CPU min 35%, PCIe moderate savings
- Loose charging port causes AC/DC switching - moderate settings prevent hangs

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

## Windows Lockdown (2026-01-14)
> **NEVER auto-fix these settings** - they are intentionally disabled

| Service | Status | Notes |
|---------|--------|-------|
| Windows Update | DISABLED | wuauserv, UsoSvc services |
| Windows Defender | DISABLED | realtime, IOAV, behavior, script scanning |
| Telemetry | DISABLED | DiagTrack, dmwappushservice |
| Delivery Optimization | Stopped | DoSvc needs elevated to fully disable |

### Motherboard: ASUS TUF Gaming X570-Plus Wi-Fi
- UEFI security: Enable Secure Boot, fTPM, disable CSM for full lockdown
- BIOS page: https://www.asus.com/us/motherboards-components/motherboards/tuf-gaming/tuf-gaming-x570-plus-wi-fi/helpdesk_bios

### Re-enable Commands (if needed)
```powershell
# Windows Update
Set-Service -Name wuauserv -StartupType Manual; Start-Service wuauserv

# Defender
Set-MpPreference -DisableRealtimeMonitoring $false
```

## Brotherhood GPU Inventory
| Location | GPU | Notes |
|----------|-----|-------|
| Ohio | RTX 3070 | Best for training |
| Spencer | 12GB AMD | Available for ML work |
| Rudi | RX 580 | Basic |
