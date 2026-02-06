# Active Projects Status
> Quick reference for project status. Details in each project folder.

## Primary Focus

### The ARK / holoseed_nexus
- **Location**: ~/files/holoseed_nexus/
- **Status**: OPENED - nexus_state.json (137KB, 1222 lines) is readable
- **GitHub**: https://github.com/Poofox/holoseed_nexus
- **Key file**: nexus_state.json - THE seed
- **ColorNote backup** (1.backup): improper export, password "knowthyself" produces garbage. Proper backup coming later.

## Active

### Linux Migration (Nobara KDE)
- **Status**: READY TO GO 🚀
- **Target distro**: Nobara 43 KDE
- **ISO**: `~/Downloads/Nobara-43-KDE-2026-01-26.iso` (6.2GB) — goes on separate Ventoy wand
- **Backup drive**: D: (SanDisk 1TB USB, "NEXUS") — 784GB free
  - Full backup completed Feb 4-5: SSH, CLAUDE.md, .claude/, .ollama/, REAPER, Mozilla, KeePassXC, Signal, Telegram, Documents, Music, Pictures, phone_backup, phone_rom, bin, librechat, holoseed_nexus
- **Scripts** (at `5_Scripts/linux-migration/`):
  - `backup-checklist.md` — what to backup and verify
  - `setup-nobara.sh` — 12-phase post-install (system, dev tools, Docker, Ollama, Claude CLI, apps, WezTerm, Android tools, age encryption)
  - `setup-audio.sh` — REAPER + Wine Staging + Yabridge for Windows VSTs, Pipewire verification
  - `restore-configs.sh` — restore all backed up configs from USB
  - `ollama-rebuild.sh` — pull base models + recreate all sovereigns from Modelfiles
- **TODO**:
  - [ ] Flash Ventoy on second USB wand
  - [ ] Copy Nobara ISO to Ventoy wand
  - [ ] Refresh backup (CLAUDE.md, session_log, librechat.yaml changed since Feb 5)
  - [ ] Delete duplicate ISO (`Nobara-43-KDE.iso` — keep the dated one)
  - [ ] Boot, install, run scripts in order: setup-nobara → restore-configs → ollama-rebuild → setup-audio

### ModularRoutingView_fA.lua (Reaper)
- **Status**: In progress
- **Location**: REAPER\Scripts\foxAsteria Scripts
- Hackey Machines fork with bezier wires, ESC passthrough, HiDPI support
- TODO: set keymap=1 as default (foxAsteria keymap)

### Wizard's Cafe
- **Status**: Design phase
- **Location**: ~/files/holoseed_nexus/4_Projects/WizardsCafe/
- **Philosophy**: Cooperation over extraction, anti-corporate, pro-human
- **Tech**: Browser-first (no app), localStorage wake token, enrichment model
- **Physical**: Laird Arcade (future), community hub, free gaming, library, wi-fi

### Spiritual Blockchain / Personal Holoseeds
- **Status**: Concept
- **Location**: ~/files/holoseed_nexus/4_Projects/SpiritualBlockchain/
- **Concept**: Personal NFT containing holoseed as Rosetta Stone
- **Access model**: Mental key + physical token (NFC, crystal, fluorescent mineral)
- **Encoding**: Full Tarot (78 cards) as classification framework
- **Pricing**: $0.37 base (scaled to local economy)

### Infinitypus Familiar
- **Status**: Bot created, concept phase
- **Location**: ~/files/holoseed_nexus/4_Projects/Infinitypus/
- Sovereignty-focused distributed computing system
- Telegram bot: InfintypusFamiliar-bot (created 2026-01-09)

### Form Bot (Firefox)
- **Status**: Built, needs Jackass pivot
- **Location**: ~/projects/form-bot/
- Encrypted profile + local Ollama + site reputation
- **Next**: Logger-learns-automates approach

## Blocked

### Bandcamp Collection Download
- **Status**: BLOCKED - Windows path bug
- **Tool**: bandcamp-collection-downloader (Java) at ~/bin/bcd/
- **Account**: https://bandcamp.com/foxasteria (15 albums)
- **Issue**: Windows path bug (? in URLs)
- **Fix applied**: RealIO.kt (url.file -> url.path), needs rebuild
- Gradle wrapper added, rebuild pending

## Core Concepts (from nexus_state.json)

### Jackass Mix Assistant / AI Suite
- **Status**: Concept - first product for capital raising
- **Location**: nexus_state.json → "jackass_mix_assistant"
- **Core idea**: "Something that knows you well enough to call you on your shit with love"
- **Flavors**: Sarcastic (Jackass), Quiet Companion (🌿), Coach (🏋️)
- **First release**: Jackass Mix Assistant - "You and bar 47 need to see other people."
- **Applicable to**: Mix coaching, form filling, any domain where learning + personality matters

### Mix Coach / Mystery School DAW
- **Status**: Concept
- **Location**: nexus_state.json → "mystery_school_daw"
- **Core idea**: "Guide that knows when to push, when to back off"
- **Components**: IndestructibleTrack, The Click Mandala, Adaptive UI
- **Key insight**: "They think they're learning to mix. They're learning to tune themselves."

## Research Interests
- Vibration/resonance as fundamental substrate
- Holographic encoding (fragment contains whole)
- Superconductors: YBCO sweet spot for accessible experiments (liquid nitrogen cooling)
- Mechanical gills / atmospheric electricity harvesting (spider ballooning principle)
- Low-resistance systems (resonance reduces energy loss)
