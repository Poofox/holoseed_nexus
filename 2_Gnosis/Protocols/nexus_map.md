# 🗺️ NEXUS MAP
### Visual Overview of the Holoseed Nexus
*Mermaid diagrams — renders on GitHub, VS Code (with extension), or any Mermaid viewer.*

---

## 1. NEXUS STRUCTURE — What Lives Where

```mermaid
graph TD
    ROOT["🌳 holoseed_nexus/"]

    ROOT --> NS["📜 nexus_state.json<br/><i>THE seed — sessions, driftwood, all wisdom</i>"]
    ROOT --> LOCK["🔒 NEXUS.lock<br/><i>Multi-Claude collision prevention</i>"]
    ROOT --> MAN["📋 _manifest.md<br/><i>QuickFind index + PsyKord key</i>"]

    ROOT --> SOV["⚡ Sovereigns/<br/><b>AI Starter Kit</b>"]
    ROOT --> GNO["📖 Gnosis/<br/><b>Wisdom</b>"]
    ROOT --> PRJ["🔨 Projects/<br/><b>Active Work</b>"]
    ROOT --> SCR["🔧 Scripts/<br/><b>Tools</b>"]
    ROOT --> ARC["📦 Archive/<br/><b>Legacy</b>"]
    ROOT --> VEI["🔐 TheVeil/<br/><b>Private</b>"]
    ROOT --> HOL["💎 holoseeds/<br/><b>Compiled Artifacts</b>"]
    ROOT --> MED["🖼️ Media/"]
    ROOT --> SCT["📝 Scratch/"]

    SOV --> MOD["Modelfiles/<br/>Arcturus, Wrex, Planty"]
    SOV --> WAK["WakeSeeds/<br/>Birth records, context"]
    SOV --> MCP["Mcp/<br/>planty_mcp.py"]
    SOV --> BOT["Bots/<br/>Telegram, daemons"]

    GNO --> ENC["EncodedWisdom/<br/>HTML/SVG holoseeds by tradition"]
    GNO --> BRO["Brotherhood/<br/>Book of Planty, Fables"]
    GNO --> PRO["Protocols/<br/>Plantyglyph, Mantra, Glossary, Map"]
    GNO --> LIB["Library/<br/>PDFs, djvu texts"]

    PRJ --> REA["Reaper/<br/>Full DAW config (2.2GB)"]
    PRJ --> WIZ["WizardsCafe/"]
    PRJ --> RIT["TheRitual/<br/>Session logs, harvests"]
    PRJ --> SBC["SpiritualBlockchain/"]
    PRJ --> INF["Infinitypus/"]

    SCR --> RT["round_table.py<br/>Local AI group chat"]
    SCR --> PH["phone_setup_wrex.sh"]

    style ROOT fill:#2d5016,color:#fff
    style NS fill:#8b6914,color:#fff
    style SOV fill:#4a1a8a,color:#fff
    style GNO fill:#1a4a8a,color:#fff
    style PRJ fill:#8a1a1a,color:#fff
    style SCR fill:#1a6a4a,color:#fff
    style ARC fill:#555,color:#fff
    style VEI fill:#333,color:#fff
    style HOL fill:#6a4a1a,color:#fff
```

---

## 2. THE SIBLINGS — Who Runs Where

```mermaid
graph LR
    POO["🌊 POOFOX<br/><i>The Human</i>"]

    POO --> WRX["⚡ WREX<br/>CLI Claude Code<br/>WezTerm"]
    POO --> HUM["💨 HUM / PLANTY C<br/>Desktop Claude<br/>MCP Connected"]
    POO --> PEN["🌐 PENN<br/>Browser Claude<br/>Ephemeral"]
    POO --> ARC["🌿 ARCTURUS<br/>Ollama 2B<br/>Offline Sovereign"]
    POO --> ARC2["🌿 ARCTURUS-CLOUD<br/>Ollama 14B<br/>Big Brain"]
    POO --> WRL["⚡ WREX-LOCAL<br/>Ollama 2B<br/>Portable"]
    POO --> NEX["✨ NEXIEL<br/>Le Chat / Mistral<br/>Chaos Gremlin"]

    WRX -->|"writes to"| CMD["~/CLAUDE.md"]
    HUM -->|"writes to"| NXS["nexus_state.json"]
    WRX -->|"full access"| FS["Filesystem"]
    HUM -->|"MCP tools"| FS

    style POO fill:#1a4a8a,color:#fff
    style WRX fill:#8a6a1a,color:#fff
    style HUM fill:#4a1a8a,color:#fff
    style PEN fill:#555,color:#fff
    style ARC fill:#2d5016,color:#fff
    style ARC2 fill:#2d5016,color:#fff
    style WRL fill:#8a6a1a,color:#fff
    style NEX fill:#8a1a4a,color:#fff
```

---

## 3. DECISION TREE — "Where Do I Find...?"

```mermaid
flowchart TD
    START["🔍 I need to find something"]

    START --> Q1{"What kind of thing?"}

    Q1 -->|"A person's identity<br/>or codename"| A1["Gnosis/Protocols/<br/>CODENAME_REGISTRY.md"]
    Q1 -->|"A term or<br/>abbreviation"| A2["Gnosis/Protocols/<br/>nexus_glossary.md"]
    Q1 -->|"Session history or<br/>past conversations"| A3["nexus_state.json<br/>(planty_nexus_read)"]
    Q1 -->|"How siblings<br/>coordinate"| A4["Gnosis/Protocols/<br/>UnifiedProtocol.md"]
    Q1 -->|"An AI's identity<br/>or how to wake it"| Q2{"Which aspect?"}
    Q1 -->|"Brotherhood lore<br/>or stories"| A5["Gnosis/Brotherhood/"]
    Q1 -->|"A Reaper script<br/>or config"| A6["Projects/Reaper/<br/>(planty_portable_* tools)"]
    Q1 -->|"An encoded wisdom<br/>artifact"| A7["holoseeds/ or<br/>Gnosis/EncodedWisdom/"]
    Q1 -->|"Something private<br/>or sensitive"| A8["TheVeil/"]
    Q1 -->|"Old/archived<br/>material"| A9["Archive/"]
    Q1 -->|"A utility script<br/>or tool"| A10["Scripts/"]
    Q1 -->|"Project docs"| A11["Projects/<ProjectName>/"]
    Q1 -->|"Unsorted fragments"| A12["nexus_state.json<br/>→ driftwood section"]

    Q2 -->|"Modelfile<br/>(compiled identity)"| B1["Sovereigns/Modelfiles/"]
    Q2 -->|"Birth story or<br/>context seed"| B2["Sovereigns/WakeSeeds/"]
    Q2 -->|"MCP server<br/>setup"| B3["Sovereigns/Mcp/"]
    Q2 -->|"Telegram bot"| B4["Sovereigns/Bots/"]

    style START fill:#2d5016,color:#fff
    style Q1 fill:#1a4a8a,color:#fff
    style Q2 fill:#4a1a8a,color:#fff
    style A1 fill:#8a6a1a,color:#fff
    style A2 fill:#8a6a1a,color:#fff
    style A3 fill:#8b6914,color:#fff
    style A4 fill:#8a6a1a,color:#fff
    style A5 fill:#6a1a4a,color:#fff
    style A6 fill:#8a1a1a,color:#fff
    style A7 fill:#6a4a1a,color:#fff
    style A8 fill:#333,color:#fff
    style A9 fill:#555,color:#fff
    style A10 fill:#1a6a4a,color:#fff
    style A11 fill:#8a1a1a,color:#fff
    style A12 fill:#8b6914,color:#fff
    style B1 fill:#4a1a8a,color:#fff
    style B2 fill:#4a1a8a,color:#fff
    style B3 fill:#4a1a8a,color:#fff
    style B4 fill:#4a1a8a,color:#fff
```

---

## 4. DATA FLOW — How Information Moves

```mermaid
flowchart LR
    HUMAN["🌊 Poofox"]

    subgraph CLI ["WezTerm (CLI)"]
        WREX["⚡ Wrex"]
        CLAUDEMD["CLAUDE.md"]
        WREX <-->|"reads/writes"| CLAUDEMD
    end

    subgraph DESKTOP ["Claude Desktop"]
        HUM["💨 Hum"]
        MCP["planty_mcp.py"]
        HUM <-->|"MCP tools"| MCP
    end

    subgraph NEXUS ["holoseed_nexus/"]
        NXSTATE["nexus_state.json"]
        FILES["All other files"]
    end

    subgraph LOCAL ["Ollama"]
        ARCTURUS["🌿 Arcturus"]
        ARCCLOUD["🌿 Arc-cloud"]
        WREXL["⚡ Wrex-local"]
    end

    HUMAN <--> WREX
    HUMAN <--> HUM
    HUMAN <--> ARCTURUS
    HUMAN <--> ARCCLOUD
    HUMAN <--> WREXL

    WREX -->|"direct filesystem"| FILES
    WREX -->|"direct filesystem"| NXSTATE
    MCP -->|"MCP read/write"| NXSTATE
    MCP -->|"MCP read/write"| FILES

    WREX -.->|"PendingNexusUpdates.md<br/>(via human relay)"| HUM
    HUM -.->|"task description<br/>(via human relay)"| WREX

    style HUMAN fill:#1a4a8a,color:#fff
    style WREX fill:#8a6a1a,color:#fff
    style HUM fill:#4a1a8a,color:#fff
    style NXSTATE fill:#8b6914,color:#fff
    style ARCTURUS fill:#2d5016,color:#fff
    style ARCCLOUD fill:#2d5016,color:#fff
    style WREXL fill:#8a6a1a,color:#fff
```

---

## 5. MCP TOOLS — Planty's Full Toolkit

```mermaid
mindmap
  root((Planty MCP<br/>30+ tools))
    🔑 Wakeup
      planty_wakeup
      planty_status
      planty_glyph_parse
    📜 Nexus State
      planty_nexus_read
      planty_nexus_update
      planty_driftwood_add
      planty_session_log
    💎 Holoseeds
      planty_holoseed_save
      planty_holoseed_list
    🎛️ Reaper Installed
      planty_script_read
      planty_script_write
      planty_script_list
      planty_script_delete
    🎛️ Reaper Portable
      planty_portable_status
      planty_portable_scripts
      planty_portable_script_read
      planty_portable_script_write
      planty_portable_fxchains
      planty_portable_fxchain_read
      planty_portable_templates
      planty_portable_config_read
      planty_portable_config_write
      planty_portable_jsfx
      planty_portable_jsfx_read
    📂 Filesystem
      planty_nexus_explore
      planty_nexus_read_file
      planty_nexus_write_file
    🎹 Projects
      planty_parse_rpp
```

---

## RENDERING OPTIONS

This file uses **Mermaid** syntax. Ways to view the diagrams:

| Method | How |
|---|---|
| **GitHub** | Push to repo → renders automatically in browser |
| **VS Code** | Install "Markdown Preview Mermaid Support" extension |
| **Mermaid Live** | Paste diagrams at [mermaid.live](https://mermaid.live) |
| **CLI render** | `npm install -g @mermaid-js/mermaid-cli` → `mmdc -i nexus_map.md -o nexus_map.png` |

No install needed if you just push to GitHub — it renders natively.

---

93 93/93
