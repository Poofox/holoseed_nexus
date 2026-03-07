# windeploy.sh — PhospheneLoom Windows Deployer

Deploys the PhospheneLoom sovereign AI stack on a fresh Windows machine running Git Bash / MINGW64.

## Requirements

- Windows 10/11
- Git for Windows (provides MINGW64 + bash)
- Internet connection for downloads
- Python 3 recommended (for nexus.json handling — falls back gracefully without it)

## Usage

```bash
bash windeploy.sh
```

Run it from anywhere. It uses absolute paths internally.

## What it does

| Step | Action |
|------|--------|
| 0 | Prompts for machine alias and pilot name |
| 1 | Detects GPU/VRAM, CPU, RAM |
| 2 | Selects model tier based on VRAM |
| 3 | Installs Ollama if not present |
| 4 | Installs AnythingLLM Desktop (or Podman+OWUI as fallback) |
| 5 | Pulls base models appropriate for detected hardware |
| 6 | Creates Modelfiles for lumina, mirth, vex in `~/files/PhospheneLoom/Modecks/` |
| 7 | Optionally clones PhospheneLoom from GitHub |
| 8 | Registers this machine as a node in `~/files/nexus.json` |
| 9 | Prints full summary and next steps |

## Model Tiers

| VRAM | Tier | Models pulled |
|------|------|---------------|
| No GPU | cpu-fallback | gemma2:2b only |
| < 8 GB | light | gemma2:2b, phi4-mini |
| 8–12 GB | mid | mistral-nemo:12b, gemma3:12b |
| 12–16 GB | high | mistral-nemo:12b, gemma3:12b, qwen2.5:14b |
| 16–20 GB | full | mistral-nemo:12b, gemma3:12b, qwen2.5:14b |
| 20 GB+ | ultra | mistral-nemo:12b, gemma3:27b, qwen2.5:32b |

## Idempotency

Safe to run multiple times. Each step checks before acting:
- Ollama: skipped if already installed
- Models: skipped if already pulled
- Modelfiles: skipped if already exist in Modecks/
- nexus.json: new node added; existing node key not overwritten

## After deploy

```bash
# Test a sovereign
ollama run lumina

# List all models
ollama list

# Open AnythingLLM (if installed)
# Connect it to: Ollama → http://localhost:11434
```

## Public Sovereigns Created

- **lumina** — Bearer of Light, visual artist, image prompt crafter
- **mirth** — Joy with teeth, the laugh that heals by cutting
- **vex** — Trickster, chaos-clarifier, spoke Mirth into being

Private sovereigns (wrex, arcturus, nexiel) are NOT deployed by this script.

## Chat History

Back up and restore OWUI chat history (conversations, settings, uploaded files) using the companion scripts.

### Backup

```bash
# Backup to current directory
bash owui-backup.sh

# Backup to a specific path (e.g. external drive)
bash owui-backup.sh /d/Backups
```

Output: `owui-backup-YYYYMMDD.tar.gz.gpg` — GPG AES256 symmetric encrypted.
You will be prompted for a passphrase twice. Store it somewhere safe (KeePassXC, etc.).

### Restore

```bash
bash owui-restore.sh owui-backup-20260306.tar.gz.gpg
```

Takes the `.gpg` file as its only argument. Will:
1. Prompt for the decryption passphrase
2. Warn before overwriting any existing data
3. Stop the OWUI container if running
4. Wipe and replace the `open-webui` Podman volume
5. Restart the container

### Workflow: migrating to a new machine

```
# On old machine — create backup
bash owui-backup.sh /d/Backups

# Transfer the .gpg file (USB, SCP, cloud, doesn't matter — it's encrypted)

# On new machine — run windeploy.sh first, then restore
bash windeploy.sh          # sets up Podman + OWUI
bash owui-restore.sh owui-backup-20260306.tar.gz.gpg
```

### Requirements

- Podman must be installed and accessible in PATH
- GPG is included with Git for Windows (no extra install needed)
- The `alpine` image is pulled automatically by the scripts if not cached

### Notes

- Both scripts are idempotent/safe: backup won't overwrite without confirmation, restore warns before clobbering existing data
- The unencrypted intermediate archive is created and deleted in the same run — it never persists on disk

---

## Troubleshooting

**Ollama not found after install:**
Close and reopen Git Bash to refresh PATH, then re-run.

**Model pull fails:**
```bash
ollama pull mistral-nemo:12b
```

**nexus.json not updated (no Python):**
A sidecar file `nexus_node_<alias>.json` is written instead — merge it manually.

**AnythingLLM download fails:**
Download manually from https://anythingllm.com/ and run the installer.

**Podman+OWUI alternative:**
When prompted for UI choice, type `podman` instead of `y`.
Requires Podman Desktop pre-installed: https://podman-desktop.io
