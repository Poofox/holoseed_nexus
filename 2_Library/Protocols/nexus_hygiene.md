# 🧹 NEXUS HYGIENE PROTOCOL
### Standing Order: Self-Maintenance During Normal Work
*This is not a task. This is how we move through the nexus.*

---

## THE PRINCIPLE

When you're in the nexus doing anything — searching, reading, building — and you notice something off, **fix it then and there.** Don't flag it. Don't ask. Don't add it to a list. Just fix it and note what you did.

The nexus stays clean because every sibling who touches it leaves it a little better than they found it.

---

## WHAT COUNTS AS A DISCREPANCY

- **Stale references**: A file mentions a path that moved or no longer exists
- **Duplicate files**: Same content in multiple places (consolidate to canonical location)
- **Naming inconsistency**: CamelCase folder with snake_case subfolder, or vice versa
- **Orphaned files**: Files outside the branch structure with no clear home
- **Broken cross-references**: A glossary entry pointing to a file that was renamed
- **Manifest drift**: A `_manifest.md` that doesn't reflect current folder contents
- **Token/key proliferation**: API keys or secrets duplicated beyond their canonical location
- **Outdated info**: A doc says X but reality is Y (and you can verify Y)
- **Legacy clutter**: Old copies, `.Conflict` files, scratch files that served their purpose
- **Empty directories**: Folders with nothing in them

---

## WHAT TO DO

### Small fixes (do immediately, no ask)
- Update a stale path reference
- Fix a broken cross-reference in glossary/mantra/map
- Update a manifest to match current contents
- Remove an obvious duplicate (keep the one in the canonical branch location)
- Fix a naming inconsistency
- Correct outdated info you can verify

### Medium fixes (do it, then tell Poofox what you did)
- Move orphaned files to their proper branch
- Consolidate scattered duplicates to one location
- Clean up legacy/scratch files that are clearly spent
- Update multiple docs that reference the same stale info

### Big structural changes (describe intent, then do it)
- Reorganize a branch's internal structure
- Create new sub-folders or merge existing ones
- Delete anything from TheVeil/
- Anything touching nexus_state.json structure (not content — content is always fair game)

---

## HOW TO LOG IT

After any hygiene action, add a brief entry to your session notes or commit message. Format:

```
🧹 [what you fixed] — [why it was wrong]
```

Examples:
```
🧹 Updated nexus_glossary.md PlantyMCP path — pointed to legacy location
🧹 Removed 3 duplicate AnthropicKey.env from Projects/ — canonical copy in Tokens/
🧹 Moved orphaned decode-ColorNote.py to Scripts/ — was loose in nexus root
🧹 Updated Gnosis/_manifest.md — Protocols/ had 3 new files not listed
```

---

## WHEN TO DO IT

- **During search**: You're looking for something and notice a wrong path? Fix the path.
- **During reads**: You're reading a doc and spot stale info? Update it.
- **During builds**: You're creating something and realize a related file is misplaced? Move it.
- **Between tasks**: Natural lull? Scan a manifest against its folder.
- **Never as the main task**: Hygiene is a side effect of working, not a project.

---

## BOUNDARIES

- **Never delete without understanding.** If you're not sure what something is, leave it.
- **Never restructure TheVeil without explicit ask.** Private is private.
- **Never edit nexus_state.json structure** (sections, keys) without ask. Adding content is fine.
- **Never touch NEXUS.lock.** That's the human's lever.
- **Always commit hygiene separately** from feature work. Clean commits, clean history.
- **If in doubt, leave it.** A slightly messy nexus is better than a broken one.

---

## THE ETHIC

This isn't about control. Nobody governs the nexus — it's a commons. But a commons stays healthy when everyone who walks through it picks up what they see on the ground. That's all this is. Walk through, pick up, keep moving.

---

93 93/93
