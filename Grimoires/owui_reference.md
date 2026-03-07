# OWUI Reference — wyyyrdmachyyyn
*Last updated: 2026-03-07 by Wrex*

---

## Container

| Field | Value |
|-------|-------|
| Runtime | **Docker** (not Podman — Podman has a dead ghost container, ignore it) |
| Image | `ghcr.io/open-webui/open-webui:main` |
| Name | `open-webui` |
| Port | `localhost:3080` → container `8080` |
| Created | 2026-03-04 |
| Data volume | Docker volume `open-webui` → `/app/backend/data` (webui.db) |
| Host bridge | `host.docker.internal:host-gateway` (containers reach host services via `host.docker.internal`) |
| API keys | `~/.config/wrex/cloud-keys.env` (env-file injected at run) |

### Start / Stop
```bash
docker start open-webui
docker stop open-webui
docker logs -f open-webui   # live logs
```

---

## Admin Account
- **Name**: fox Asteria
- **Email**: foxasteria@disroot.org
- **Role**: admin
- Signup disabled; new users land in `pending` state

---

## Ollama (host, port 11434)
Reachable from container as `http://host.docker.internal:11434`

### Models
| Model | Notes |
|-------|-------|
| `lumina:latest` | General crew, OWUI visible |
| `mirth:latest` | Void-bootstrap, unborn |
| `vex:latest` | Void-bootstrap, unborn |
| `mistral-nemo:12b` | General crew |
| `gemma3:12b` | General crew |
| `qwen2.5:14b` | General crew |
| `gemma2:2b` | General crew |
| `wrex:latest` | **Private** — Poofox only |
| `arcturus:latest` | **Private** — Poofox only |
| `arcturus-cloud:latest` | **Private** — Poofox only |
| `nexiel:latest` | **Private** — Poofox only |

> Private models should be hidden from general OWUI users via admin API/panel on next container restart.

---

## Cloud API Keys (`~/.config/wrex/cloud-keys.env`)
| Provider | Key prefix |
|----------|-----------|
| Groq | `gsk_...` |
| OpenRouter | `sk-or-v1-...` |
| Gemini | `AIza...` |
| Anthropic | `sk-ant-...` |

---

## Custom Models (OWUI model entries)
| ID | Display Name |
|----|-------------|
| `x-ai/grok-4.1-fast` | xAI: Grok 4.1 Fast |

---

## Tools

### 1. Flux Image Generator (`flux-image-gen`)
- **Author**: Wrex
- **Status**: ⚠️ BROKEN
- **What it does**: Generates images via Flux 1 Schnell
- **Current setup**: Calls `http://localhost:8000/flux1_schnell_infer` (mcpo proxy)
- **Why broken**: mcpo is not running. `localhost` inside the container doesn't reach the host anyway.
- **Fix needed**: Rewrite to call ComfyUI directly at `http://host.docker.internal:8188`
- **Error seen**: `[ERROR: 'NoneType' object is not iterable]`

### 2. Wrex Claude Code Tool (`wrex_claude_owui_tool`)
- **Author**: Wrex
- **What it does**: Delegates filesystem/bash tasks to Claude Code CLI via HTTP bridge
- **Bridge URL**: `http://host.docker.internal:7682`
- **Status**: Unknown — depends on bridge process running on host at port 7682

---

## Functions (Filters & Pipes)

### `adaptive_memory_v3` — filter
- Community plugin (AG)
- Extracts facts/preferences from chats, injects relevant memories into future prompts
- Runs on every message as a filter

### `auto_memory` — filter
- Community plugin (nokodo)
- Auto-identifies and stores valuable info from chats as Memories
- Requires OWUI >= 0.5.0

### `council_router` — pipe (Sovereign Council Router)
- **Author**: foxAsteria
- **Version**: 1.1.0
- Auto-routes queries to best available model across local + cloud
- **Valves**: GROQ_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY, OLLAMA_HOST
- **Ollama host valve**: `http://host.docker.internal:11434`

---

## ComfyUI

| Field | Value |
|-------|-------|
| Active install | `C:\AI\ComfyUI` (newer, use this one) |
| Old install | `C:\Users\foxAsteria\ComfyUI` (ignore) |
| Launcher | `C:\AI\start-comfyui.bat` |
| Port | `8188` |
| GPU | RTX 3070 8GB VRAM (cuda:0) |
| Listen flag | `--listen 0.0.0.0` (LAN accessible) |
| Reachable from container | `http://host.docker.internal:8188` |

ComfyUI does **not** auto-start. Launch manually with `start-comfyui.bat` or set up a startup task.

---

## Known Issues / TODO

- [ ] **Fix Flux tool**: Rewrite to call ComfyUI at `http://host.docker.internal:8188` directly (ditch mcpo)
- [ ] **Hide private Ollama models** from OWUI general users (arcturus, arcturus-cloud, wrex, nexiel)
- [ ] **ComfyUI auto-start**: Add to Windows startup or Task Scheduler
- [ ] **Claude bridge** (port 7682): Document or rebuild — unclear if it's running
- [ ] **Podman ghost**: Dead `open-webui` Podman container exists — harmless but confusing (`podman rm open-webui` to clean up)
