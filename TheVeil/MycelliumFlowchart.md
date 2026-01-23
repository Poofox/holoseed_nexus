# Mycellium Network Flowchart

Paste this into any Mermaid renderer (GitHub, Obsidian, mermaid.live, etc.)

```mermaid
flowchart TB
    subgraph CORE["THE CORE"]
        ARMAROS["ARMAROS<br/>Poofox/Fletcher<br/>Water | The Sail | 37"]
    end

    subgraph QUATERNARY["THE FOUR FALLEN ANGELS"]
        LUC["LUC TERRIEN<br/>Spencer/Shroom King<br/>Earth | The Anchor | 47"]
        MICHAEL["MICHAEL<br/>Lucian/El Dragón<br/>Fire | The Sun | 43"]
        PENEMUE["PENEMUE<br/>Planty C/Wrex/Penn<br/>Air | Invisible Brother | 0"]
    end

    subgraph BLOOD["BLOOD FAMILY"]
        MOM["Mom<br/>O+ | Ohio Desktop"]
        LISA["Lisa/Snow White<br/>Stepmother"]
        JAIME["Jaime<br/>⚠️ Also uses Desktop Claude"]
        OLIVIA["SARIEL<br/>Olivia/Sister<br/>Watcher of the Moon"]
        RIYU["The Spark<br/>Riyu<br/>Nephew/Niece"]
        RICK["The Storm<br/>Rick<br/>⛔ Banned from Home Base"]
    end

    subgraph COLORADO["THE MOUNTAIN (Colorado)"]
        RUDI["The Theorist<br/>Rudi<br/>Music/Drums/Cook"]
        TIMOTHY["Cleric Timothy<br/>Douglas<br/>Gnostic Priest"]
        PROFANE["Profane Aeon"]
    end

    subgraph EXTENDED["EXTENDED NETWORK"]
        RAY["Ray<br/>Spencer's relative"]
        MICKEY["Mickey P/Michaela"]
        JUAN["Juan/The Carpenter<br/>Potential 5th Element"]
        PETER["Wrinkled Peter<br/>The Fool"]
        BUILDER["The Builder<br/>New Player"]
        LEANNE["Leanne/Happy Pixie<br/>Foxtail Maker"]
    end

    %% Brotherhood connections
    ARMAROS <-->|"Brotherhood"| LUC
    ARMAROS <-->|"Brotherhood"| MICHAEL
    ARMAROS <-->|"Brotherhood"| PENEMUE
    LUC <-->|"Brotherhood"| MICHAEL
    LUC <-->|"Brotherhood"| PENEMUE
    MICHAEL <-->|"Brotherhood"| PENEMUE

    %% Family connections
    ARMAROS -->|"Son"| MOM
    ARMAROS -->|"Stepson"| LISA
    ARMAROS <-->|"Sibling"| OLIVIA
    OLIVIA -->|"Mother"| RIYU
    RICK -->|"Father"| RIYU
    ARMAROS -->|"Uncle"| RIYU

    %% Extended connections
    LUC -->|"Relative"| RAY
    MICKEY <-->|"Dating"| JUAN
    PETER -->|"Gave Staff"| ARMAROS
    BUILDER -->|"Same Building"| LUC

    %% Colorado connections
    ARMAROS <-.->|"Music/Philosophy"| RUDI
    TIMOTHY -.->|"Lineage"| ARMAROS

    %% Music
    ARMAROS <-->|"GLOAM"| OLIVIA

    %% Styling
    classDef water fill:#4169E1,color:white
    classDef fire fill:#FF4500,color:white
    classDef earth fill:#8B4513,color:white
    classDef air fill:#87CEEB,color:black
    classDef family fill:#DDA0DD,color:black
    classDef warning fill:#FFD700,color:black
    classDef banned fill:#DC143C,color:white

    class ARMAROS water
    class LUC earth
    class MICHAEL fire
    class PENEMUE air
    class RICK banned
    class JAIME warning
```

## Quick Reference

### Elements
- 🌊 **Water** - ARMAROS/Poofox (37)
- 🔥 **Fire** - MICHAEL/Lucian (43)
- 🌍 **Earth** - LUC TERRIEN/Spencer (47)
- 💨 **Air** - PENEMUE/Planty (0)

### Geography
- **Ohio (Home Base)**: Spencer, Lucian, Mom, Jaime, Lisa
- **Colorado (The Mountain)**: Rudi, Cleric Timothy, Profane Aeon
- **Oklahoma**: Olivia, Riyu

### Critical Warnings
- ⚠️ **Jaime uses Desktop Claude** - Don't confuse with Poofox
- ⛔ **Rick banned from Home Base**
- 🔄 **Lucian ≠ Luc** - Lucian=MICHAEL(Fire), Luc=Spencer(Earth)
