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

| VRAM | Models pulled |
|------|---------------|
| No GPU | gemma2:2b only |
| < 8 GB | gemma2:2b, phi4-mini |
| 8–12 GB | mistral-nemo:12b, gemma3:12b |
| 12–16 GB | mistral-nemo:12b, gemma3:12b, qwen2.5:14b |
| 16 GB+ | mistral-nemo:12b, gemma3:12b, qwen2.5:14b |

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
