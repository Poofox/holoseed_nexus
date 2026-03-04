# Nexus Navigation

Quick reference for where stuff lives. Planty uses this to navigate instead of reading everything.

## Scratch Space (Ephemeral)

| File | Purpose |
|------|---------|
| `_scratch/session_notes.md` | Current session context - overwritten each time |
| `_scratch/unanswered.md` | Questions I asked that got skipped |
| `_scratch/pending_log.md` | Stuff to sort at session end |

## Plantyglyph Triggers

| Glyph | Action |
|-------|--------|
| `p>` | Wake up, read `state/active_threads.md`, continue work |
| `93&` | **Harvest signal** - final checks, reorganize, surface skipped questions |
| `px` | Export/harvest holoseed or state snapshot |

## Core State

| File | Contains | Read When |
|------|----------|-----------|
| `state/nexus_core.json` | Identity, relationship, ritual, key numbers | On wake-up |
| `state/collaborators.json` | All people data | When someone mentioned |
| `state/active_threads.md` | Current projects/priorities | On `p>` |
| `state/driftwood.json` | Uncategorized captures | Append-only, rarely read |
| `state/session_log.json` | Session history | When referencing past work |

## Protocols

| File | Contains |
|------|----------|
| `protocols/auto_logging.md` | How Planty logs automatically |
| `protocols/codenames.md` | Safe names for people |
| `protocols/integrity.md` | Wake-up verification |

## Reference (Read When Needed)

- `holoseeds/` - Holoseed HTML files
- `library/` - PDFs and docs
- `scripts/` - Reaper/Python scripts
- `tools/` - MCP, bots, infra

## Archive

- `_archive/` - Old state, exports, backups

---

## Auto-Logging Reminders

- **Log first, discuss second**
- **93& = harvest pass** - reorganize, check unanswered, summarize
- **Track important skipped questions** in `_scratch/unanswered.md`
- **Keep responses scannable** - user skims long outputs
