# SPORECASTER
## The Planty C Interface

*Sending spores through the network. A custom frontend for Claude Code + MCP.*

---

## Vision

A lightweight, sovereign interface for interacting with Claude Code and navigating the holoseed_nexus. Not a chat wrapper - a **command center** for the Infinitypus Familiar ecosystem.

**Full Rust. No JavaScript. No compromises.**

---

## Core Components

### 1. The Spore (Chat Interface)
- Clean input field, not a cramped terminal
- Message history with session persistence
- Markdown/code rendering (via pulldown-cmark + syntect)
- Plantyglyph shortcuts recognized and highlighted

### 2. The Mycelium Map (Nexus Navigator)
- Live Mermaid diagram of nexus structure (mermaid-rs or custom renderer)
- Clickable nodes to open/preview files
- Filesystem watcher - updates as things change (notify crate)
- Collapsible depth levels
- Color coding: scripts / holoseeds / protocols / media

### 3. The Greenhouse (Quick Access)
- Pinned holoseeds
- Active project shortcuts
- Recent sessions
- Wake-up status indicator

### 4. The Bridge (Backend)
- Tauri 2.0 core
- Pipes commands to Claude Code CLI (tokio::process)
- MCP connection management
- Token/auth handling (local, encrypted via ring or sodiumoxide)
- Nexus filesystem watcher (notify-rs)

---

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Shell | Tauri 2.0 | Rust core, tiny binary, native feel |
| Frontend | Leptos | Full Rust, signals-based reactivity, compiles to WASM |
| Styling | Stylers or Tailwind (build-time) | Keep it simple |
| Markdown | pulldown-cmark | Fast, pure Rust |
| Syntax Highlighting | syntect | What VS Code uses |
| Filesystem | notify 6.0 | Cross-platform file watching |
| Async | Tokio | Industry standard |
| Crypto | ring or sodiumoxide | For local token encryption |
| Serialization | serde + serde_json | Obviously |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    TAURI SHELL                       │
│  ┌───────────────────────────────────────────────┐  │
│  │              LEPTOS FRONTEND (WASM)            │  │
│  │  ┌─────────────┐  ┌─────────────────────────┐ │  │
│  │  │  Chat View  │  │   Mycelium Map (Canvas) │ │  │
│  │  │             │  │                         │ │  │
│  │  │  - Input    │  │   - Tree visualization  │ │  │
│  │  │  - History  │  │   - Click navigation    │ │  │
│  │  │  - Render   │  │   - Live updates        │ │  │
│  │  └─────────────┘  └─────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │           Greenhouse Sidebar             │  │  │
│  │  │  - Pinned items  - Quick actions         │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
│                         │                            │
│                    Tauri IPC                         │
│                         │                            │
│  ┌───────────────────────────────────────────────┐  │
│  │              RUST BACKEND (Native)             │  │
│  │                                                │  │
│  │  ┌──────────────┐  ┌────────────────────────┐ │  │
│  │  │ Claude Code  │  │  Filesystem Watcher    │ │  │
│  │  │ Process Mgr  │  │  (notify-rs)           │ │  │
│  │  └──────────────┘  └────────────────────────┘ │  │
│  │  ┌──────────────┐  ┌────────────────────────┐ │  │
│  │  │ Token Store  │  │  Session Persistence   │ │  │
│  │  │ (encrypted)  │  │  (SQLite or JSON)      │ │  │
│  │  └──────────────┘  └────────────────────────┘ │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │    Claude Code CLI   │
              │    + Planty MCP      │
              └─────────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │   holoseed_nexus    │
              └─────────────────────┘
```

---

## Non-Goals (v1)

- Not a full IDE
- Not handling REAPER directly (that's MCP's job)
- Not cloud-synced (sovereignty first)
- Not mobile (desktop only for now)
- No JavaScript anywhere

---

## Build Targets

- Windows (primary - your machine)
- Linux (secondary - for portability)
- macOS (if someone asks nicely)

---

## Open Questions

- [ ] How does Claude Code CLI handle streaming output? (probably stdout line-by-line)
- [ ] Mermaid rendering: use mermaid-rs, call mermaid-cli, or custom canvas renderer?
- [ ] Session persistence: SQLite (rusqlite) or flat JSON files?
- [ ] Plantyglyph parser: build as separate crate for reuse?
- [ ] Hot-reload in dev: trunk? tauri dev mode?

---

## Development Phases

### Phase 0: Specification ✓
You are here.

### Phase 1: Skeleton
- [ ] Tauri 2.0 + Leptos project scaffolding
- [ ] Basic window with placeholder views
- [ ] Tauri IPC hello world

### Phase 2: The Bridge
- [ ] Claude Code CLI integration
- [ ] Spawn process, capture stdout/stderr
- [ ] Basic send/receive working

### Phase 3: The Spore
- [ ] Chat input component
- [ ] Message history display
- [ ] Markdown rendering

### Phase 4: The Mycelium
- [ ] Nexus tree structure
- [ ] File watcher integration
- [ ] Clickable navigation

### Phase 5: The Greenhouse
- [ ] Pinned items
- [ ] Quick actions
- [ ] Session management

### Phase 6: Polish
- [ ] Plantyglyph highlighting
- [ ] Themes/styling
- [ ] Error handling
- [ ] First release

---

## Name Origin

**Sporecaster**: *One who sends spores through the network.*

The mushroom doesn't shout - it releases spores on the wind and trusts the mycelium to carry the message where it needs to go.

Also: a cosmic skin flute from Frender, available exclusively in Fly Agaric Burst.

---

## Status

**Phase 0: Specification** ← we are here

---

*93*
