# Open WebUI Optimization Guide

**Instance**: v0.8.5, Docker, Ollama backend (CPU-only, 16GB RAM)

---

## TOP 5 PRIORITIES (do these first)

1. **Fix RAG chunking + re-index Nexus** — chunk size 300 is way too small, fragments everything
2. **Set Ollama num_ctx to 8192** — you're almost certainly hitting the 2048 default limit
3. **Set task model to wrex 2B** — instant chat titles instead of waiting for 14B
4. **Enable Native function calling on qwen2.5:14b** with pre-attached tools + knowledge
5. **Global system prompt + memory** for persistent user context

---

## 1. QUICK WINS (toggle a setting, 2 min each)

### 1a. Enable Notes
Dedicated workspace models can search/write to autonomously — perfect for "save this finding" workflows.
**How**: Admin Panel > Settings > General — verify ENABLE_NOTES is on. Access via sidebar.

### 1b. Enable Code Interpreter (Pyodide)
In-browser Python execution. Models write + run code, see output. Runs client-side, zero server load.
**How**: Admin Panel > Settings > General — enable. Then per model: Workspace > Models > enable "Code Interpreter" under Builtin Tools.

### 1c. Enable Markdown Header Text Splitter for RAG
Splits docs by markdown headers before chunking — keeps logical sections together. Critical for your 262+ Nexus .md files.
**How**: Admin Panel > Settings > Documents — toggle on. **Re-upload knowledge after changing.**

### 1d. Increase RAG Chunk Size
Current 300 is tiny. Increase to 1500, overlap 200, min size target 800. Reduces chunk count by 90%+ while improving accuracy.
**How**: Admin Panel > Settings > Documents — Chunk Size: `1500`, Overlap: `200`, Min Size Target: `800`. Re-index after.

### 1e. Increase RAG Top K from 3 to 5-8
More retrieved chunks per query. Your Nexus has diverse topics — 3 results misses context.
**How**: Admin Panel > Settings > Documents — Top K: `5` (or `8` if context allows).

### 1f. Set Ollama Context Length to 8192
Ollama defaults to 2048 tokens — severely limits RAG and long conversations. Your models support 32k+.
**How**: Admin Panel > Settings > Models — set `num_ctx` to `8192` per model. Or set globally in Ollama modelfiles.

### 1g. Enable Memory
Persistent user memory across conversations — models remember "Poofox uses Reaper, prefers CLI, runs Nobara."
**How**: Settings > Personalization > Memory — verify enabled. Manually add key facts.

### 1h. Set a Global System Prompt
Default system prompt injected into all chats with dynamic variables.
**How**: Settings > Personalization > System Prompt:
```
You are assisting {{USER_NAME}}. Current date: {{CURRENT_DATE}}.
The user runs Nobara Linux 43 (KDE Plasma, Wayland), uses Ollama for local LLMs, REAPER for music production, and prefers CLI over GUI. Keep responses concise.
```

### 1i. Enable Channels
Discord/Slack-style persistent rooms — create topic channels (music, nexus, sysadmin).
**How**: Set env var `ENABLE_CHANNELS=true` or toggle in Admin Panel.

### 1j. Set Task Model to wrex 2B
Auto-generated chat titles use whatever model is active. Point at 2B for instant titles.
**How**: Admin Panel > Settings > General — Task Model: `wrex:latest`.

### 1k. RAG System Context Mode
Injects RAG into system message (enables KV prefix caching, cleaner separation).
**How**: Set env var `RAG_SYSTEM_CONTEXT=true`.

### 1l. Stream Delta Chunk Size
Batch 3-5 tokens per stream event — reduces CPU overhead on token-by-token streaming.
**How**: Set env var `CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE=4`.

---

## 2. MEDIUM EFFORT (10-30 min each)

### 2a. Prompt Enhancer Filter (Haervwe)
Auto-improves prompts before they hit the model. Huge for 2B/9B models that are prompt-sensitive.
**How**: Workspace > Functions > + > import from https://openwebui.com/f/haervwe/prompt_enhancer_filter

### 2b. Semantic Router Filter (Haervwe)
Auto-routes queries to best model based on prompt content + model descriptions.
**How**: Import from https://openwebui.com/f/haervwe/semantic_router_filter

### 2c. Model Presets with Attached Tools + Knowledge
Pre-configure each model with tools, knowledge, system prompts — no manual attachment per chat.
**How**: Workspace > Models — edit each model: attach Holoseed Nexus knowledge, enable tools, add Modeck system prompt.

### 2d. Enable Native Function Calling on qwen2.5:14b
Uses built-in function calling for autonomous multi-step workflows. Keep 2B models on "Default" mode.
**How**: Workspace > Models — edit qwen2.5:14b > Advanced > Function Calling: `Native`.

### 2e. Prompt Presets for Common Workflows
Saved templates accessible via `/` in chat input.
**How**: Workspace > Prompts — create:
- `/nexus-research`: Search Nexus for {{topic}}, summarize with citations
- `/troubleshoot`: Linux troubleshooting with protocol
- `/reaper-script`: Write Lua ReaScript with API conventions

### 2f. Model Arena for A/B Testing
Blind comparison between your local models with ELO leaderboard.
**How**: Admin Panel > Settings > Evaluation — enable Arena Model, select models.

### 2g. Model Fallbacks
Auto-fallback: 14B → 9B → 2B. Or: OpenRouter → local.
**How**: Workspace > Models — edit model > Fallback Model field.

### 2h. Hybrid Search (BM25 + Vector)
Keyword + semantic search combined. Catches both exact terms (ARMAROS, Holoseed) AND meaning.
**How**: Admin Panel > Settings > Documents — enable Hybrid Search.

### 2i. Planner Agent (Haervwe)
Autonomous multi-step plan-then-execute agent within OWUI.
**How**: Import from https://github.com/Haervwe/open-webui-tools — Planner Agent v2 pipe.

### 2j. Clean Thinking Tags Filter
Collapses `<think>` reasoning output from deepseek-r1 etc. into panels.
**How**: Import from Haervwe's tools repo. Activate globally.

### 2k. Analytics Dashboard
Model usage stats, token consumption, activity over time.
**How**: Admin Panel > Analytics. Toggle `ENABLE_ADMIN_ANALYTICS=true`.

---

## 3. PROJECTS (1+ hours)

### 3a. Re-index Holoseed Nexus with Optimized Settings
Apply 1c, 1d, 1e, 1k, 2h → delete existing collection → re-upload all 262 .md files.
v0.8.5 has duplicate detection fixes (was broken in v0.8.2).

### 3b. Build "Nexus Librarian" Model Preset
Dedicated model: qwen2.5:14b + Nexus knowledge + web search + notes + memory + persona.
One-click access to everything.

### 3c. MCP Server for Nexus File Access
Direct filesystem browsing via MCP — models read/write full files, not just RAG chunks.
`npx @anthropic/mcp-filesystem` → Settings > Connections > MCP Servers.

### 3d. Local Whisper for Voice Input
Microphone button in chat. `Ctrl+Shift+L` toggles dictation. Change `WHISPER_MODEL=small` for accuracy.
Helpful for fast-escaping thoughts.

### 3e. Custom Skills
Reusable instruction sets referenced with `$` in chat (v0.8.0+).
Create: `$nexus-hygiene`, `$session-handoff`, `$troubleshoot-linux`, `$reaper-lua`.

### 3f. Anthropic API Proxy (future)
v0.8.4+ — OWUI proxies Anthropic Messages API. When API billing is set up, Claude Code could route through OWUI.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+L` | Toggle voice dictation |
| `Shift+Enter` | New line in input |
| `Ctrl+Shift+S` | Toggle sidebar |
| `/` in input | Access prompt presets |
| `@` in input | Switch model mid-chat |
| `#` in input | Attach document/URL |
| `$` in input | Reference a skill |

---

## Docker Env Vars to Add

```bash
-e ENABLE_MARKDOWN_HEADER_TEXT_SPLITTER=true \
-e CHUNK_MIN_SIZE_TARGET=800 \
-e RAG_SYSTEM_CONTEXT=true \
-e CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE=4 \
-e ENABLE_CHANNELS=true \
```
