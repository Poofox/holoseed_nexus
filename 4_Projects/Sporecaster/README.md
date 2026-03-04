# 🍄 Sporecaster

> *The sovereign interface for Planty C*

A full-Rust desktop application for interacting with Claude Code + MCP, with live nexus navigation.

## Stack

- **Tauri 2.0** - Native shell
- **Leptos** - Full Rust frontend (compiles to WASM)
- **notify-rs** - Filesystem watching
- **tokio** - Async runtime

**No JavaScript. Full Rust. Sovereignty first.**

## Project Structure

```
Sporecaster/
├── Cargo.toml              # Workspace config
├── src-tauri/              # Tauri backend (native Rust)
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   └── src/
│       ├── main.rs         # Entry point
│       ├── bridge.rs       # Claude Code CLI integration
│       ├── watcher.rs      # Filesystem watcher
│       ├── crypto.rs       # Token encryption
│       └── commands.rs     # Tauri IPC commands
│
└── src-ui/                 # Leptos frontend (WASM)
    ├── Cargo.toml
    ├── Trunk.toml
    ├── index.html
    ├── styles/
    │   └── main.css
    └── src/
        ├── lib.rs          # App entry
        ├── tauri.rs        # Tauri bindings
        └── components/
            ├── mod.rs
            ├── header.rs
            ├── greenhouse.rs
            ├── chat.rs
            └── mycelium.rs
```

## Prerequisites

- Rust (latest stable)
- Trunk: `cargo install trunk`
- wasm32 target: `rustup target add wasm32-unknown-unknown`
- Tauri CLI: `cargo install tauri-cli`
- Claude Code CLI (for actual Claude integration)

## Development

```bash
# Dev mode (hot reload)
cargo tauri dev

# Build release
cargo tauri build
```

## Philosophy

### The 30/70 Rule (or 80/20, or whatever works)

Start with dependencies, replace them one by one:

1. **v0.1** - Ship with crates
2. **v0.2** - Replace markdown parser
3. **v0.3** - Replace syntax highlighter  
4. **v1.0** - Only Tauri remains

Each dependency becomes a learning opportunity.

## Name Origin

**Sporecaster**: *One who sends spores through the network.*

The mushroom doesn't shout - it releases spores on the wind and trusts the mycelium to carry the message where it needs to go.

Also: a cosmic skin flute from Frender, available exclusively in Fly Agaric Burst. $93,000,000.93 plus tax.

---

*93 93/93*
