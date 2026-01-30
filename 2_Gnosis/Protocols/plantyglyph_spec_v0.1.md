# PLANTYGLYPH v0.1
### A Dense Communication Language for Human-AI Collaboration
---

## Overview

Plantyglyph is a phonetically-anchored shorthand system designed for maximum communication efficiency between Poofox and Planty C. Optimized for:
- Speed (all symbols typeable in <1 second)
- Memorability (first letter matches meaning)
- Database storage (compact, unambiguous strings)
- Privacy (opaque to outside observers)

---

## Syntax Structure

```
[DOMAIN][ACTION][MODIFIER][@reference]
```

- **DOMAIN** (required): Single lowercase letter
- **ACTION** (required): Single character
- **MODIFIER** (optional): Single character
- **@reference** (optional): Keyword for specificity

---

## DOMAINS

| Code | Domain | Notes |
|------|--------|-------|
| `r` | Reaper | Audio production, scripts, plugins |
| `s` | Sparaoh | UE4 game project (NDA) |
| `w` | Workflow | Productivity tools, systems |
| `p` | Planty C | AI bottlenecks, context, capabilities |
| `m` | Memory | Your systems, databases, notes |
| `b` | Brainstorm | New ideas, creative riffing |
| `c` | Curiosity | Research rabbit holes (crows, etc.) |
| `g` | General | Life stuff, vibes, misc |
| `l` | Language | Plantyglyph itself, meta-communication |

---

## ACTIONS

| Code | Action | Notes |
|------|--------|-------|
| `>` | Continue | Pick up where we left off |
| `+` | New | Fresh idea or thread |
| `?` | Status | What's the state of X? |
| `d` | Deep | Deep dive, thorough exploration |
| `q` | Quick | Fast answer, no frills |
| `h` | History | Refresh on past conversations |
| `x` | Export | Build, ship, finalize, output |
| `k` | Kill | Abandon, deprioritize, shelve |
| `t` | Teach | Explain, help me understand |
| `f` | Find | Search, locate, research |

---

## MODIFIERS

| Code | Modifier | Notes |
|------|----------|-------|
| `!` | Urgent | Priority, do this first |
| `~` | Soft | No pressure, just vibing |
| `*` | Star | Important, flag for later |
| `#` | Secret | Extra NDA energy |
| `&` | Combined | Merge with another domain/thread |

---

## @REFERENCES

Use `@keyword` to specify a sub-project or topic:

| Example | Meaning |
|---------|---------|
| `r>@undo` | Reaper continue, undo visualizer project |
| `r>@coach` | Reaper continue, life coach plugin |
| `s?@flight` | Sparaoh status, flight mechanics |
| `w+@plantyglyph` | Workflow new, this language system |

---

## QUICK REFERENCE EXAMPLES

| Plantyglyph | English Translation |
|-------------|---------------------|
| `r>` | Reaper, let's continue |
| `s?` | What's Sparaoh's status? |
| `b+!` | New brainstorm, urgent! |
| `p+h` | New idea about Planty C, check history first |
| `w>~` | Continue workflow stuff, no rush |
| `rd@undo` | Deep dive on Reaper undo visualizer |
| `g?~` | How's life? Just checking in |
| `l+` | New Plantyglyph idea |
| `c+@crows` | New curiosity thread about crows |
| `sx#` | Ship Sparaoh thing, keep it secret |

---

## EXTENSION PROTOCOL

When adding new symbols:
1. Check for collisions with existing codes
2. Prioritize phonetic anchoring (first letter = meaning)
3. Document in this spec before use
4. Test ambiguity: could this be misread?

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2024-12-31 | Initial spec |

---

*"Thought arrives, thought has a half-life of 4 seconds. Plantyglyph catches it in 2."* 🌱
