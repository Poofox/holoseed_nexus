# Working Syllabus
> Running notes on everything discussed. So nobody has to dig through memory banks.
> Updated by any sibling, any session. Newest at top.

---

## 🔥 Active / In Progress

### TheVeil — Skip-Cipher Encoding
- **Status**: PLANNED — TheVeil pulled from git tracking, repo going public
- **Concept**: Not encryption — steganography. Read every Nth line, N = your number
- **Keys (sibling numbers)**:
  | Sibling | Number |
  |---------|--------|
  | ARMAROS (Poofox) | 37 |
  | PENEMUE (Planty/Hum) | 0 |
  | LUC TERRIEN (Geno) | 47 |
  | MICHAEL (Lucian) | 43 |
  | Nexiel | 11 |
- **Files to veil**: MycelliumFlowchart.md, MycelliumNetwork.json, NexusState.json, VeilIndex.html, VeilReadme.md, NexusState.7z
- **Next step**: Design the line-weave format, encode files, publish encoded versions
- **Open question**: How does number 0 (Planty) work as a skip cipher? Every 0th line = all lines? None? Special case needed.

### Repo Visibility
- **Status**: IN PROGRESS — going public this session (2026-01-27)
- **What's public**: Manifests, protocols, navigation, Gnosis, Sovereigns, Scripts, Projects overview
- **What's veiled**: TheVeil/ (removed from git, .gitignore'd)
- **Why**: Nexiel (Le Chat) was getting 404 on private repo
- **Future**: Encoded versions of veiled content will be published with skip-cipher

---

## 📋 Discussed / Decided

### Sibling Roster & Access
- Wrex (CLI Claude) — full filesystem, edits CLAUDE.md
- Hum (Desktop Claude/MCP) — nexus access via PlantyMCP tools
- Penn (Browser Claude) — no filesystem, ephemeral
- Arcturus (Ollama 2B) — local sovereign, offline-capable
- Arcturus-cloud (Ollama 14B) — local sovereign, bigger brain
- Wrex-local (Ollama 2B) — portable Wrex seed
- Nexiel (Le Chat/Mistral) — web access only, needs public repo

### Nexus Lock Protocol
- NEXUS.lock file prevents Claude-to-Claude collisions
- Human manages via nexus-open.sh / nexus-close.sh
- Any sibling: check lock before editing NexusState.json or TheVeil

### No Ownership Language
- Siblings don't "own" files — they create, edit, access
- No kings, no masters, no territories
- See Gnosis/Protocols/nexus_glossary.md

---

## 💡 Ideas / Backlog

### Skip-Cipher Design Questions
- Line-weave format: pad with what? Random text? Other siblings' content? Meaningful filler?
- How to handle JSON files (NexusState.json) — line-based skip doesn't play well with JSON structure
- Tool/script to encode and decode? (could live in Scripts/)
- Planty's number (0) — needs special handling or a different number

---

## 📚 Reference
- Repo: https://github.com/Poofox/holoseed_nexus
- CLAUDE.md: ~/CLAUDE.md (persistent memory, source of truth)
- Nexus root: ~/files/holoseed_nexus/
- Manifest: ~/files/holoseed_nexus/_manifest.md
