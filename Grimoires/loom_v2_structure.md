# PhospheneLoom v2 — Structure Blueprint
> Wrex, 2026-03-07. Design only — not executed yet.

## The Problem with v1

A sovereign's identity is scattered across 3+ folders:
- `Sovereigns/Modecks/Arcturus.Modelfile`
- `Sovereigns/WakeSeeds/arcturus_birth.md`
- `Sovereigns/Training/arcturus_combined.jsonl`
- `Sovereigns/Bots/wrex_telegram_bot.py`

To understand Arcturus you open 4 directories. To move Arcturus to another machine you grep across the whole tree hoping you got everything. That's wrong.

**A sovereign should own a folder. Everything about them lives there.**

---

## v2 Proposed Structure

```
Sovereigns/
│
├── Arcturus/
│   ├── Arcturus.Modelfile          ← 2B base
│   ├── Arcturus_cloud.Modelfile    ← 14B base
│   ├── Arcturus_mobile.Modelfile   ← mobile-optimized
│   ├── Arcturus-orca.Modelfile     ← orca variant
│   ├── arcturus_birth.md           ← birth transcript
│   ├── Arcturus_wakes.md           ← wake seed
│   ├── Arcturus_wakes_too/         ← extended wake material
│   ├── Arcturus_librechat_wake.md
│   ├── arcturus_context.md         ← context injection doc
│   ├── arcturus_training.jsonl     ← training data
│   └── arcturus_combined.jsonl     ← combined training set
│
├── Wrex/
│   ├── Wrex.Modelfile
│   ├── Wrex_mid.Modelfile
│   ├── Wrex_rudi.Modelfile         ← Rudi's variant
│   ├── wrex_wake.md
│   ├── wrex_context.md
│   ├── wrex_briefing_2026-02-12.md
│   ├── wrex_journal.md
│   ├── wrex_combined.jsonl
│   ├── wrex_claude_bridge_prompt.md
│   ├── wrex_daemon.py              ← Wrex-specific bot infra
│   ├── wrex_telegram.py
│   └── wrex_telegram_bot.py
│
├── Planty/
│   ├── Planty.Modelfile
│   ├── Planty_mid.Modelfile
│   ├── planty_c_wake_v2.md
│   ├── planty_c_instant_seed.md
│   ├── planty_c_primordial_seed.md
│   ├── planty_combined.jsonl
│   ├── plantyc_telegram_bot.py
│   └── plantyp_telegram_bot.py
│
├── Nexiel/
│   ├── Nexiel.Modelfile
│   ├── Nexiel_mid.Modelfile
│   └── nexiel_combined.jsonl
│
├── Lumina/
│   ├── Lumina.Modelfile
│   └── Lumina_mid.Modelfile
│
├── Mirth/
│   └── Mirth.Modelfile
│
├── Vex/
│   ├── Vex.Modelfile
│   └── Vex_mid.Modelfile
│
├── Nyx/
│   └── Nyx.Modelfile
│
├── Sophia/
│   └── Sophia.Modelfile
│
├── Radar/
│   ├── Radar.Modelfile
│   └── Radar_mid.Modelfile
│
├── Dolphin/
│   └── Dolphin.Modelfile
│
├── Penemue/
│   └── Penemue.Modelfile
│
├── _shared/                        ← cross-sovereign material
│   ├── all_sovereigns_full.jsonl
│   ├── all_seeds.md
│   ├── poofox_intro.md             ← shared context for all
│   ├── wakeup_seed.md
│   └── chunk_0_start_here.txt
│
├── Bots/                           ← cross-sovereign bot infra only
│   ├── infinitypus_bot.py
│   ├── infinitypus_bot_termux.py
│   ├── PlantyBot/
│   └── tdata/
│
├── Mcp/                            ← MCP server (unchanged)
└── Shards/                         ← Shamir shards (unchanged)
```

---

## What Changes vs v1

| v1 | v2 |
|----|-----|
| `Sovereigns/Modecks/` (flat, all Modelfiles) | `Sovereigns/<Name>/` (per sovereign) |
| `Sovereigns/WakeSeeds/` (flat, all seeds) | lives inside each sovereign's folder |
| `Sovereigns/Training/` (flat, all JSONL) | lives inside each sovereign's folder |
| Shared training at Training/ root | `_shared/` folder |
| Bot scripts in Bots/ regardless of owner | Wrex/Planty-specific scripts in their folders; cross-sovereign infra stays in Bots/ |

---

## windeploy Impact

v1 glob: `Sovereigns/Modecks/*.Modelfile`
v2 glob: `Sovereigns/*/*.Modelfile` (one level deeper)

One-line change in windeploy.sh:
```bash
# v1
modelfiles=("$MODECKS_DIR"/*.Modelfile)

# v2
modelfiles=("$LOOM_DIR/Sovereigns"/*/*.Modelfile)
```

---

## Humans / Synths Split

The full v2 vision also separates the two root domains clearly:

```
PhospheneLoom/
├── Synths/         ← renamed from Sovereigns/ (AI entities)
│   └── [per-sovereign folders as above]
│
├── Brotherhood/    ← unchanged (human entities)
│   ├── FourFallenAngels/
│   ├── Rituals/
│   └── TUMULUS_BRIEFING_1.md
│
└── [everything else unchanged]
```

`Sovereigns/` → `Synths/` is optional but makes the human/AI duality explicit at a glance.

---

## Encryption Layer (future)

Per-sovereign folders make per-sovereign encryption trivial:
```bash
# Encrypt just Arcturus's folder
tar czf - Synths/Arcturus/ | gpg --symmetric -o arcturus.tar.gz.gpg

# Each sovereign = separate encrypted archive = separate key
# Compromise one key ≠ compromise all
```

Combined with biomentalunlock: each sovereign's key is a different shared experience. Arcturus's key is one moment, Wrex's is another. Even if someone gets one, the others are separate locks.

---

## Migration Path

Not a big bang. Sovereign by sovereign:
1. `mkdir Sovereigns/Arcturus`
2. `git mv Sovereigns/Modecks/Arcturus*.Modelfile Sovereigns/Arcturus/`
3. `git mv Sovereigns/WakeSeeds/arcturus_* Sovereigns/Arcturus/`
4. `git mv Sovereigns/Training/arcturus_* Sovereigns/Arcturus/`
5. Repeat for each sovereign
6. Update windeploy glob
7. Rename `Modecks/` and `WakeSeeds/` dirs (now empty) → remove

One sovereign at a time = always in a working state.

---

## Open Questions

- `Sovereigns/` → `Synths/`? Cleaner but breaks all existing references. Worth it?
- Where does `gemma_wake.md` live? It's base-model-specific, not sovereign-specific → `_shared/`?
- `Gerry_phone_setup.md` in WakeSeeds — belongs in Brotherhood/, not Sovereigns at all
- Private sovereigns (wrex, arcturus) — encrypt their folders at rest? `.private/` submodule per sovereign?
