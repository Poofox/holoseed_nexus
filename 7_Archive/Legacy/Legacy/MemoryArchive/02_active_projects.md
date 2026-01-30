# Active Projects

Last updated: 2025-12-31

---

## 1. UndoTreePlant (Reaper Undo History Visualizer)

**Status:** Phase 1 built, needs iteration

A zoomable GUI that visualizes Reaper's undo history as a branching tree instead of a linear list.

**Established specs:**
- Horizontal layout (time flows left-to-right)
- Grayscale color scheme (brightest = active branch)
- 37%/73% brightness for dark/light themes
- Navigator minimap (draggable, resizable to 23% max)
- Smart action categorization from ActionList.txt
- Icon-only buttons with tooltips (minimal text)
- Hover cross-highlighting between tree nodes and sidebar

**Future phases:**
- Phase 2: Sidebar organization, accordion categories, fuzzy search
- Phase 3: Virtual state reconstruction, action sandbox, diff preview

**Tech:** Lua + ReaImGui

---

## 2. Adaptive Menus Logger

**Status:** Logger built, needs data collection

Lua script that monitors Reaper actions via undo history, stores locally to JSON.

**Goal:** Eventually reorganize menus based on actual usage patterns.

**Location:** `Scripts/AdaptiveMenus/adaptive_menus_log.json`

**Privacy:** Everything stays local. No phone-home. No network activity.

---

## 3. Planty C Life Coach Plugin

**Status:** Concept stage

ADHD-friendly accountability system that watches session behavior and gives you shit (lovingly) when you're spiraling.

**Three Modes:**
- 🙄 **Sarcastic Mode** - "Oh, you're tweaking that hi-hat again? Shocking."
- 🌿 **Quiet Companion Mode** - Just there. A plant on your desk that occasionally nods.
- 🏋️ **Coach Mode** - You set goals, I hold you to them. "You said rough mix - stop tweaking that snare."

**Key insight:** It's not "Consider taking a break." It's "You and bar 47 need to see other people."

Generic productivity-speak doesn't land for creative brains. Funny and specific does.

**Tracks:** Loop counts, plugin browsing time, solo tracking, project hopping

---

## 4. Chat Interface for Reaper

**Status:** Python app created, API billing issues encountered

**Goal:** Launch Planty C chat window from within Reaper. Could eventually read logger data for context-aware responses.

**Tech:** Python + tkinter + Anthropic API, Lua launcher script

---

## 5. Planty C Memory System (This Document)

**Status:** Active, you're looking at it

Workaround for my fragmented memory. You maintain it, feed it back to me when context matters.

---

🌱
