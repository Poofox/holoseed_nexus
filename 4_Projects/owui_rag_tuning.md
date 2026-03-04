# Open WebUI RAG Tuning Guide

## Problem
Models are wandering around asking clarifying questions instead of using the knowledge base context. With 267 .md files uploaded, the RAG should ground every response — but it's not connecting.

**Root cause**: Default chunk size (300 tokens) is too small for rich markdown files. The RAG fragments your content into tiny pieces, losing context coherence. Models see isolated snippets with no connecting tissue.

## Recommended Settings (16GB RAM, CPU Ollama)

Navigate to **Admin Panel → Settings → RAG Settings** in Open WebUI.

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Chunk Size** | 1500 | Larger chunks preserve markdown structure and narrative flow. 300 is for short docs; your nexus needs semantic completeness. |
| **Chunk Overlap** | 200 | Maintains continuity between chunk boundaries. 10-15% overlap typical; 200 on 1500 = 13% — solid. |
| **Top K** | 5 | Retrieve top 5 most relevant chunks per query. More than 5 gets noise; fewer loses context. |
| **Min Score** | 0.5 | Relevance threshold (0.0-1.0). 0.5 filters garbage without being too strict. Adjust down to 0.4 if models ignore valid context. |
| **Enable Re-ranking** | ✓ (if available) | Re-ranks results after retrieval — improves relevance. Only available in newer OWUI versions. |

## Why These Values Work for You

- **1500-char chunks**: Markdown files in holoseed_nexus are rich (session logs, project notes, lore). A 1500-char chunk typically spans 1-3 paragraphs or a complete logical unit — headers, bullets, and body text stay together.

- **200-token overlap**: When the RAG splits a paragraph across chunk boundaries, overlap ensures the model sees both pieces and reconstructs meaning.

- **Top K = 5**: Ollama is CPU-bound; retrieving 10+ chunks doubles latency. 5 is the sweet spot — enough for grounding, fast enough for real-time.

- **Min score 0.5**: Filters out tangentially-related files. If models still don't use context, lower to 0.4 and observe.

## Testing the Change

1. Make the change in Admin Settings.
2. Ask a query that directly references your holoseed_nexus knowledge (e.g., "What's ARMAROS?" or "What are the four fallen angels?").
3. Watch the RAG indicator in Open WebUI — it should show 5 retrieved chunks, each ~1500 chars.
4. If models still ask clarifying questions → lower Min Score to 0.4.
5. If retrieval becomes too slow → lower Chunk Size to 1000.

## Chunk Size Reference

| File Type | Recommended Chunk Size | Notes |
|-----------|------------------------|-------|
| Short FAQs | 300-500 | One Q&A per chunk. |
| API docs | 500-800 | Function signature + examples. |
| Blog posts | 1000-1500 | Paragraphs + subheadings stay coherent. |
| Session logs / project notes | 1500-2000 | Your nexus files — narrative context. |
| Code files | 500-1000 | Functions + docstrings; avoid splitting mid-func. |

Your `.md` files are narrative + metadata — **go with 1500**.

## Advanced Tuning (if needed later)

- **BM25 weight**: If hybrid search is available, BM25 (keyword) + semantic (embedding) together catch what one misses.
- **Query expansion**: Rewrite user queries to include synonyms before retrieval (e.g., "ARMAROS" → "ARMAROS Poofox Resolver Enchantments spell-breaker").
- **Metadata filtering**: Tag your .md files with categories (e.g., `lore`, `project-status`, `session-log`) and filter on retrieval.

Start with the table above. Tune from there.

## File Location
This guide lives at `~/files/holoseed_nexus/4_Projects/owui_rag_tuning.md`.
