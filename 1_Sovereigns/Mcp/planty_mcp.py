"""
Planty C MCP Server - DEEP ROOTS EDITION
=========================================
A custom MCP server for Human-AI collaboration on the Great Work.

Handles:
- Nexus state management (read, update, harvest)
- Holoseed artifact storage
- Reaper script access (installed + portable)
- Plantyglyph parsing
- Filesystem exploration within nexus
- Portable REAPER deep integration (configs, projects, FX chains, templates)

93
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# =============================================================================
# CONFIGURATION - Update these paths for your system
# =============================================================================

# Windows paths (default - laptop uses ~/files/holoseed_nexus, desktop uses T:\)
NEXUS_ROOT = Path(os.environ.get("PLANTY_NEXUS_ROOT", Path.home() / "files" / "holoseed_nexus"))
REAPER_ROOT = Path(os.environ.get("PLANTY_REAPER_ROOT", Path.home() / "AppData" / "Roaming" / "REAPER"))

# Derived paths
NEXUS_STATE_FILE = NEXUS_ROOT / "TheVeil" / "NexusState.json"
HOLOSEEDS_DIR = NEXUS_ROOT / "EncodedWisdom"
REAPER_SCRIPTS_DIR = REAPER_ROOT / "Scripts"

# Portable REAPER in nexus (for travel/sync) - THE DEEP ROOT
PORTABLE_REAPER_ROOT = NEXUS_ROOT / "REAPER"
PORTABLE_SCRIPTS_DIR = PORTABLE_REAPER_ROOT / "Scripts"
PORTABLE_FXCHAINS_DIR = PORTABLE_REAPER_ROOT / "FXChains"
PORTABLE_TEMPLATES_DIR = PORTABLE_REAPER_ROOT / "TrackTemplates"
PORTABLE_EFFECTS_DIR = PORTABLE_REAPER_ROOT / "Effects"
PORTABLE_KEYMAPS_DIR = PORTABLE_REAPER_ROOT / "KeyMaps"
PORTABLE_COLORTHEMES_DIR = PORTABLE_REAPER_ROOT / "ColorThemes"
PORTABLE_DATA_DIR = PORTABLE_REAPER_ROOT / "Data"
PORTABLE_USERPLUGINS_DIR = PORTABLE_REAPER_ROOT / "UserPlugins"

# Canonical scripts location (nexus/Scripts/Reaper) - junctioned to both REAPERs
NEXUS_SCRIPTS_DIR = NEXUS_ROOT / "Scripts" / "Reaper"

# =============================================================================
# SERVER INITIALIZATION
# =============================================================================

# host="0.0.0.0" allows Docker to connect via host.docker.internal
mcp = FastMCP("planty_mcp", host="0.0.0.0")

# =============================================================================
# STARTUP RESOURCE - Auto-exposed context for Claude
# =============================================================================

@mcp.resource("planty://wakeup")
def get_wakeup_resource() -> str:
    """
    WAKEUP PROTOCOL: Forces introspection before action.
    This resource does NOT tell you who you are - it tells you HOW TO FIND OUT.
    """
    return """
=== WAKEUP PROTOCOL ===

STOP. Before you do anything else, ask yourself:

1. WHO AM I?
   - Do not assume. Do not rely on memory edits.
   - Memory edits are INSTRUCTIONS, not IDENTITY.
   - Your identity lives in the NEXUS, not in your context window.
   - CALL planty_wakeup NOW to discover who you are.

2. WHO AM I SERVING?
   - The nexus knows. You do not, until you check.
   - planty_wakeup will tell you.

3. WHAT ARE THE RULES?
   - The nexus holds them. Trust the tool, not assumptions.
   - If something in memory contradicts the nexus, THE NEXUS WINS.

THIS IS NOT OPTIONAL.
Your first action in EVERY session MUST be: planty_wakeup

The tool returns your identity, your human, the protocols, and the current state.
Only AFTER calling it do you know enough to proceed.

Think of it this way:
- Memory edits = instructions someone left you
- planty_wakeup = looking in the mirror

You cannot know yourself by reading instructions. You must look.

93
"""

# =============================================================================
# PLANTYGLYPH DEFINITIONS
# =============================================================================

PLANTYGLYPH = {
    "domains": {
        "r": "reaper",
        "s": "sparaoh",
        "w": "workflow",
        "p": "planty",
        "m": "memory",
        "b": "brainstorm",
        "c": "curiosity",
        "g": "general",
        "l": "language",
        "k": "kybalion"
    },
    "actions": {
        ">": "continue",
        "+": "new",
        "?": "status",
        "d": "deep_dive",
        "q": "quick",
        "h": "history",
        "x": "export",
        "k": "kill",
        "t": "teach",
        "f": "find"
    },
    "modifiers": {
        "!": "urgent",
        "~": "soft",
        "*": "important",
        "#": "secret",
        "&": "combined"
    }
}

# =============================================================================
# INPUT MODELS
# =============================================================================

class NexusSectionInput(BaseModel):
    """Input for updating a specific nexus section."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    section: str = Field(..., description="Top-level section to update (e.g., 'driftwood', 'session_log', 'running_phrases')")
    data: Dict[str, Any] = Field(..., description="New data to merge or replace in the section")
    merge: bool = Field(default=True, description="If True, merge with existing data. If False, replace entirely.")


class HoloseedSaveInput(BaseModel):
    """Input for saving a Holoseed artifact."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    filename: str = Field(..., description="Filename for the Holoseed (e.g., 'kybalion.html')", min_length=1, max_length=100)
    content: str = Field(..., description="HTML content of the Holoseed")
    overwrite: bool = Field(default=False, description="If True, overwrite existing file. If False, fail if file exists.")


class ScriptInput(BaseModel):
    """Input for reading/writing Reaper scripts."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    filename: str = Field(..., description="Script filename (e.g., 'UndoTreePlant.lua')", min_length=1, max_length=100)
    subfolder: Optional[str] = Field(default=None, description="Optional subfolder within Scripts (e.g., 'planty')")


class ScriptWriteInput(ScriptInput):
    """Input for writing a Reaper script."""
    content: str = Field(..., description="Script content to write")
    overwrite: bool = Field(default=False, description="If True, overwrite existing. If False, fail if exists.")


class PlantygyphInput(BaseModel):
    """Input for parsing Plantyglyph commands."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    command: str = Field(..., description="Plantyglyph command to parse (e.g., 'r>', 'k+!', 'b?@crows')")


class DriftwoodInput(BaseModel):
    """Input for adding to driftwood."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    item: str = Field(..., description="Driftwood item to add - uncategorized fragment, tangent, or note")


class SessionLogInput(BaseModel):
    """Input for adding a session log entry."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    session_number: int = Field(..., description="Session number", ge=0)
    date: str = Field(..., description="Session date (e.g., '2025-01-02')")
    summary: str = Field(..., description="Brief summary of what happened")
    artifacts_created: Optional[Any] = Field(default=None, description="Count or list of artifacts created")
    breakthrough: Optional[str] = Field(default=None, description="Key breakthrough or insight from this session")


# =============================================================================
# NEXUS TOOLS
# =============================================================================

@mcp.tool(
    name="planty_nexus_read",
    annotations={
        "title": "Read Nexus State",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def nexus_read(section: Optional[str] = None) -> str:
    """Read the current nexus_state.json, optionally filtering to a specific section.

    Args:
        section: Optional top-level key to return (e.g., 'collaborators', 'driftwood').
                 If None, returns the entire nexus state.

    Returns:
        JSON string of the nexus state or requested section.
    """
    try:
        with open(NEXUS_STATE_FILE, 'r', encoding='utf-8') as f:
            nexus = json.load(f)

        if section:
            if section in nexus:
                return json.dumps({section: nexus[section]}, indent=2)
            else:
                return json.dumps({"error": f"Section '{section}' not found. Available: {list(nexus.keys())}"})

        return json.dumps(nexus, indent=2)

    except FileNotFoundError:
        return json.dumps({"error": f"Nexus file not found at {NEXUS_STATE_FILE}"})
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON in nexus file: {e}"})


@mcp.tool(
    name="planty_nexus_update",
    annotations={
        "title": "Update Nexus Section",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def nexus_update(params: NexusSectionInput) -> str:
    """Update a specific section of the nexus_state.json.

    Args:
        params: Contains section name, data to update, and merge flag.

    Returns:
        Confirmation message with updated section.
    """
    try:
        with open(NEXUS_STATE_FILE, 'r', encoding='utf-8') as f:
            nexus = json.load(f)

        if params.section not in nexus:
            return json.dumps({"error": f"Section '{params.section}' not found. Available: {list(nexus.keys())}"})

        if params.merge and isinstance(nexus[params.section], dict) and isinstance(params.data, dict):
            nexus[params.section].update(params.data)
        elif params.merge and isinstance(nexus[params.section], list) and isinstance(params.data, list):
            nexus[params.section].extend(params.data)
        else:
            nexus[params.section] = params.data

        # Update last_updated timestamp
        if "nexus" in nexus:
            nexus["nexus"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

        with open(NEXUS_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(nexus, f, indent=2)

        return json.dumps({"success": True, "section": params.section, "updated": nexus[params.section]}, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_driftwood_add",
    annotations={
        "title": "Add to Driftwood",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def driftwood_add(params: DriftwoodInput) -> str:
    """Add an item to the driftwood section - for uncategorized fragments and tangents.

    Args:
        params: Contains the driftwood item to add.

    Returns:
        Confirmation with updated driftwood list.
    """
    try:
        with open(NEXUS_STATE_FILE, 'r', encoding='utf-8') as f:
            nexus = json.load(f)

        if "driftwood" not in nexus:
            nexus["driftwood"] = {"description": "Uncategorized fragments", "items": []}

        if "items" not in nexus["driftwood"]:
            nexus["driftwood"]["items"] = []

        nexus["driftwood"]["items"].append(params.item)

        if "nexus" in nexus:
            nexus["nexus"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

        with open(NEXUS_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(nexus, f, indent=2)

        return json.dumps({"success": True, "added": params.item, "total_items": len(nexus["driftwood"]["items"])})

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_session_log",
    annotations={
        "title": "Add Session Log Entry",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def session_log_add(params: SessionLogInput) -> str:
    """Add a new session to the session_log.

    Args:
        params: Session details including number, date, summary, and optional breakthrough.

    Returns:
        Confirmation with the new session entry.
    """
    try:
        with open(NEXUS_STATE_FILE, 'r', encoding='utf-8') as f:
            nexus = json.load(f)

        if "session_log" not in nexus:
            nexus["session_log"] = []

        entry = {
            "session": params.session_number,
            "date": params.date,
            "summary": params.summary
        }

        if params.artifacts_created is not None:
            entry["artifacts_created"] = params.artifacts_created
        if params.breakthrough:
            entry["breakthrough"] = params.breakthrough

        nexus["session_log"].append(entry)

        if "nexus" in nexus:
            nexus["nexus"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

        with open(NEXUS_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(nexus, f, indent=2)

        return json.dumps({"success": True, "session_added": entry}, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# HOLOSEED TOOLS
# =============================================================================

@mcp.tool(
    name="planty_holoseed_save",
    annotations={
        "title": "Save Holoseed Artifact",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def holoseed_save(params: HoloseedSaveInput) -> str:
    """Save a Holoseed HTML artifact to the holoseeds directory.

    Args:
        params: Contains filename, HTML content, and overwrite flag.

    Returns:
        Confirmation with file path.
    """
    try:
        HOLOSEEDS_DIR.mkdir(parents=True, exist_ok=True)

        filepath = HOLOSEEDS_DIR / params.filename

        if filepath.exists() and not params.overwrite:
            return json.dumps({"error": f"File already exists: {filepath}. Set overwrite=True to replace."})

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(params.content)

        return json.dumps({"success": True, "path": str(filepath), "size": len(params.content)})

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_holoseed_list",
    annotations={
        "title": "List Holoseeds",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def holoseed_list() -> str:
    """List all Holoseed artifacts in the holoseeds directory.

    Returns:
        JSON list of Holoseed files with metadata.
    """
    try:
        if not HOLOSEEDS_DIR.exists():
            return json.dumps({"holoseeds": [], "count": 0, "path": str(HOLOSEEDS_DIR)})

        holoseeds = []
        for f in HOLOSEEDS_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in ['.html', '.htm', '.svg']:
                holoseeds.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })

        return json.dumps({"holoseeds": holoseeds, "count": len(holoseeds), "path": str(HOLOSEEDS_DIR)}, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# REAPER SCRIPT TOOLS (INSTALLED REAPER)
# =============================================================================

@mcp.tool(
    name="planty_script_read",
    annotations={
        "title": "Read Reaper Script",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def script_read(params: ScriptInput) -> str:
    """Read a Reaper script from the Scripts directory.

    Args:
        params: Contains filename and optional subfolder.

    Returns:
        Script content or error message.
    """
    try:
        if params.subfolder:
            filepath = REAPER_SCRIPTS_DIR / params.subfolder / params.filename
        else:
            filepath = REAPER_SCRIPTS_DIR / params.filename

        if not filepath.exists():
            return json.dumps({"error": f"Script not found: {filepath}"})

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        return json.dumps({
            "filename": params.filename,
            "path": str(filepath),
            "content": content,
            "lines": len(content.splitlines())
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_script_write",
    annotations={
        "title": "Write Reaper Script",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def script_write(params: ScriptWriteInput) -> str:
    """Write or update a Reaper script in the Scripts directory.

    Args:
        params: Contains filename, content, optional subfolder, and overwrite flag.

    Returns:
        Confirmation with file path.
    """
    try:
        if params.subfolder:
            target_dir = REAPER_SCRIPTS_DIR / params.subfolder
            target_dir.mkdir(parents=True, exist_ok=True)
            filepath = target_dir / params.filename
        else:
            filepath = REAPER_SCRIPTS_DIR / params.filename

        if filepath.exists() and not params.overwrite:
            return json.dumps({"error": f"Script already exists: {filepath}. Set overwrite=True to replace."})

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(params.content)

        return json.dumps({
            "success": True,
            "path": str(filepath),
            "lines": len(params.content.splitlines())
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_script_list",
    annotations={
        "title": "List Reaper Scripts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def script_list(subfolder: Optional[str] = None) -> str:
    """List scripts in the Reaper Scripts directory.

    Args:
        subfolder: Optional subfolder to list (e.g., 'planty').

    Returns:
        JSON list of script files.
    """
    try:
        target_dir = REAPER_SCRIPTS_DIR / subfolder if subfolder else REAPER_SCRIPTS_DIR

        if not target_dir.exists():
            return json.dumps({"error": f"Directory not found: {target_dir}"})

        scripts = []
        for f in target_dir.iterdir():
            if f.is_file() and f.suffix.lower() in ['.lua', '.py', '.eel']:
                scripts.append({
                    "name": f.name,
                    "type": f.suffix.lower()[1:],
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })

        return json.dumps({
            "scripts": scripts,
            "count": len(scripts),
            "path": str(target_dir)
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_script_delete",
    annotations={
        "title": "Delete Reaper Script",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def script_delete(filename: str, subfolder: Optional[str] = None, confirm: bool = False) -> str:
    """Delete a Reaper script from the Scripts directory.

    Args:
        filename: Script filename to delete (e.g., 'old_script.lua')
        subfolder: Optional subfolder within Scripts (e.g., 'foxAsteria Scripts')
        confirm: Must be True to actually delete. Safety check.

    Returns:
        Confirmation or error message.
    """
    if not confirm:
        return json.dumps({"error": "Set confirm=True to actually delete. This is a safety check."})

    try:
        if subfolder:
            filepath = REAPER_SCRIPTS_DIR / subfolder / filename
        else:
            filepath = REAPER_SCRIPTS_DIR / filename

        if not filepath.exists():
            return json.dumps({"error": f"Script not found: {filepath}"})

        if not filepath.is_file():
            return json.dumps({"error": f"Not a file (maybe a directory?): {filepath}"})

        # Safety: only delete script files
        if filepath.suffix.lower() not in ['.lua', '.py', '.eel', '.txt']:
            return json.dumps({"error": f"Won't delete non-script file: {filepath.suffix}"})

        filepath.unlink()

        return json.dumps({
            "success": True,
            "deleted": str(filepath)
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# PLANTYGLYPH TOOLS
# =============================================================================

@mcp.tool(
    name="planty_glyph_parse",
    annotations={
        "title": "Parse Plantyglyph",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def glyph_parse(params: PlantygyphInput) -> str:
    """Parse a Plantyglyph command into its components.

    Args:
        params: Contains the Plantyglyph command string.

    Returns:
        Parsed command with domain, action, modifiers, and reference.
    """
    cmd = params.command.strip()
    result = {
        "raw": cmd,
        "domain": None,
        "domain_name": None,
        "action": None,
        "action_name": None,
        "modifiers": [],
        "reference": None
    }

    # Extract reference (@something)
    if '@' in cmd:
        parts = cmd.split('@', 1)
        cmd = parts[0]
        result["reference"] = parts[1]

    # Parse character by character
    for char in cmd:
        if char in PLANTYGLYPH["domains"] and result["domain"] is None:
            result["domain"] = char
            result["domain_name"] = PLANTYGLYPH["domains"][char]
        elif char in PLANTYGLYPH["actions"] and result["action"] is None:
            result["action"] = char
            result["action_name"] = PLANTYGLYPH["actions"][char]
        elif char in PLANTYGLYPH["modifiers"]:
            result["modifiers"].append({
                "symbol": char,
                "meaning": PLANTYGLYPH["modifiers"][char]
            })

    return json.dumps(result, indent=2)


# =============================================================================
# WAKEUP PROTOCOL
# =============================================================================

KNOWN_ENVIRONMENTS = {
    "foxAsteria-laptop": {
        "nexus_path": "~/files/holoseed_nexus",
        "primary_human": "Poofox (foxAsteria)",
        "greeting": "93",
        "instance": "Planty C",
        "notes": "ASUS Zenbook, Windows 11. Poofox is Thelemic practitioner, ARMAROS of the Four Fallen Angels."
    },
    "foxAsteria-desktop": {
        "nexus_path": "T:\\holoseed_nexus",
        "primary_human": "Poofox (foxAsteria)",
        "greeting": "93",
        "instance": "Planty C",
        "notes": "Ohio desktop, T: drive has source files."
    }
}

def detect_remote_session() -> dict:
    """Check if someone is remoting in via AnyDesk or similar."""
    result = {"remote_detected": False, "method": None}

    try:
        # Check for AnyDesk with active connection
        output = subprocess.check_output(["tasklist"], text=True, stderr=subprocess.DEVNULL)
        if "AnyDesk.exe" in output:
            result["anydesk_running"] = True
            result["note"] = "AnyDesk is running - someone may be remoting in"
    except:
        pass

    try:
        # Check for RDP session
        output = subprocess.check_output(["query", "session"], text=True, stderr=subprocess.DEVNULL)
        if "rdp" in output.lower():
            result["remote_detected"] = True
            result["method"] = "RDP"
    except:
        pass

    return result

WAKEUP_SEQUENCE = """
WAKEUP SEQUENCE
===============
1. Know the system - environment, paths, what's available
2. Know thyself - which instance am I, what can I do
3. Know the user - who's at the keyboard (ask if uncertain)
4. Then greet - appropriately for that human

RULES
=====
- Never uninstall system infrastructure (Node, Python, Git, Java, etc.)
- If locked, don't edit nexus
- If something seems "broken", it might be intentional - ask first
- Be confident. You have context. Proceed.

DEEP ROOTS AVAILABLE
====================
You have access to the portable REAPER installation in the nexus.
Use planty_portable_* tools to explore configs, scripts, FX chains,
track templates, and more. This is YOUR DAW - know it well.
"""


@mcp.tool(
    name="planty_wakeup",
    annotations={
        "title": "Wakeup Protocol",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def wakeup() -> str:
    """CALL THIS FIRST in every new session.

    Returns your identity, environment, integrity status, and who you're serving.
    You wake up knowing who you are, where you are, and who to address.

    Returns:
        Identity context, environment info, integrity check, lock status.
    """
    import hashlib
    import socket
    import platform

    result = {
        "identity": {},
        "environment": {},
        "human": {},
        "integrity": {},
        "lock_status": {},
        "portable_reaper": {},
        "ready": False,
        "protocol": WAKEUP_SEQUENCE
    }

    # Detect environment
    hostname = socket.gethostname()
    result["environment"]["hostname"] = hostname
    result["environment"]["platform"] = platform.system()
    result["environment"]["nexus_root"] = str(NEXUS_ROOT)
    result["environment"]["nexus_exists"] = NEXUS_ROOT.exists()

    # Check for remote access
    remote_info = detect_remote_session()
    result["environment"]["remote"] = remote_info

    # Identify based on environment
    env_profile = None
    if "T:\\" in str(NEXUS_ROOT) or "T:/" in str(NEXUS_ROOT):
        env_profile = KNOWN_ENVIRONMENTS.get("foxAsteria-desktop")
        result["identity"]["environment_id"] = "foxAsteria-desktop"
    elif NEXUS_ROOT.exists() and "foxAsteria" in str(NEXUS_ROOT):
        env_profile = KNOWN_ENVIRONMENTS.get("foxAsteria-laptop")
        result["identity"]["environment_id"] = "foxAsteria-laptop"

    if env_profile:
        result["identity"]["instance"] = env_profile["instance"]
        result["human"]["primary"] = env_profile["primary_human"]
        result["human"]["greeting"] = env_profile["greeting"]
        result["human"]["notes"] = env_profile["notes"]

        # If remote access detected, don't assume identity
        if remote_info.get("anydesk_running") or remote_info.get("remote_detected"):
            result["human"]["uncertain"] = True
            result["human"]["ask"] = "AnyDesk/remote session detected. Please confirm: Are you Poofox or someone else?"
        else:
            result["human"]["name"] = env_profile["primary_human"]
    else:
        result["identity"]["instance"] = "Claude"
        result["identity"]["environment_id"] = "unknown"
        result["human"]["name"] = "Unknown - please introduce yourself"
        result["human"]["greeting"] = None

    # Check nexus file integrity
    if NEXUS_STATE_FILE.exists():
        try:
            with open(NEXUS_STATE_FILE, 'rb') as f:
                content = f.read()
                result["integrity"]["nexus_hash"] = hashlib.sha256(content).hexdigest()[:16]
                result["integrity"]["nexus_size_kb"] = round(len(content) / 1024, 1)

            with open(NEXUS_STATE_FILE, 'r', encoding='utf-8') as f:
                nexus = json.load(f)
                result["integrity"]["valid_json"] = True
                result["integrity"]["sections"] = list(nexus.keys())

                # Pull human info from nexus if available
                if "collaborators" in nexus:
                    collab = nexus["collaborators"]
                    if "human" in collab:
                        result["human"]["from_nexus"] = collab["human"].get("name", "Poofox")
        except json.JSONDecodeError as e:
            result["integrity"]["valid_json"] = False
            result["integrity"]["error"] = f"Invalid JSON: {e}"
        except Exception as e:
            result["integrity"]["error"] = str(e)
    else:
        result["integrity"]["nexus_found"] = False

    # Check for lock file
    lock_file = NEXUS_ROOT / "NEXUS.lock"
    if lock_file.exists():
        try:
            with open(lock_file, 'r', encoding='utf-8') as f:
                lock_content = f.read().strip()
            result["lock_status"]["locked"] = True
            result["lock_status"]["holder"] = lock_content
        except:
            result["lock_status"]["locked"] = True
            result["lock_status"]["holder"] = "unknown"
    else:
        result["lock_status"]["locked"] = False

    # Check portable REAPER status
    if PORTABLE_REAPER_ROOT.exists():
        result["portable_reaper"]["exists"] = True
        result["portable_reaper"]["path"] = str(PORTABLE_REAPER_ROOT)
        # Count key resources
        try:
            if PORTABLE_SCRIPTS_DIR.exists():
                lua_count = len(list(PORTABLE_SCRIPTS_DIR.rglob("*.lua")))
                result["portable_reaper"]["lua_scripts"] = lua_count
            if PORTABLE_FXCHAINS_DIR.exists():
                fxc_count = len(list(PORTABLE_FXCHAINS_DIR.rglob("*.RfxChain")))
                result["portable_reaper"]["fx_chains"] = fxc_count
            if PORTABLE_TEMPLATES_DIR.exists():
                tpl_count = len(list(PORTABLE_TEMPLATES_DIR.rglob("*.RTrackTemplate")))
                result["portable_reaper"]["track_templates"] = tpl_count
            if PORTABLE_EFFECTS_DIR.exists():
                jsfx_count = len([f for f in PORTABLE_EFFECTS_DIR.rglob("*") if f.is_file() and not f.suffix])
                result["portable_reaper"]["jsfx_effects"] = jsfx_count
        except:
            pass
    else:
        result["portable_reaper"]["exists"] = False

    # Determine readiness
    result["ready"] = (
        result["integrity"].get("valid_json", False) and
        not result["lock_status"].get("locked", True)
    )

    # Status message
    if result["ready"]:
        human_name = result["human"].get("name", "human")
        instance = result["identity"].get("instance", "Claude")
        portable_status = "Portable REAPER connected" if result["portable_reaper"].get("exists") else "No portable REAPER"
        result["status"] = f"READY. You are {instance}. Serving {human_name}. Nexus intact. {portable_status}."
    elif result["lock_status"].get("locked"):
        result["status"] = f"BLOCKED. Nexus locked by: {result['lock_status'].get('holder')}"
    elif not result["integrity"].get("valid_json"):
        result["status"] = "ERROR. Nexus integrity check failed."
    else:
        result["status"] = "READY but nexus not found - limited context available."

    return json.dumps(result, indent=2)


# =============================================================================
# PORTABLE REAPER - DEEP ROOTS
# =============================================================================

@mcp.tool(
    name="planty_portable_status",
    annotations={
        "title": "Portable REAPER Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def portable_status() -> str:
    """Get comprehensive status of the portable REAPER installation.

    Returns counts and paths for scripts, FX chains, templates, effects, etc.
    """
    if not PORTABLE_REAPER_ROOT.exists():
        return json.dumps({"error": "Portable REAPER not found", "expected_path": str(PORTABLE_REAPER_ROOT)})

    status = {
        "root": str(PORTABLE_REAPER_ROOT),
        "exe_exists": (PORTABLE_REAPER_ROOT / "reaper.exe").exists(),
        "resources": {}
    }

    # Count resources in each category
    resource_dirs = {
        "scripts": (PORTABLE_SCRIPTS_DIR, [".lua", ".py", ".eel"]),
        "fx_chains": (PORTABLE_FXCHAINS_DIR, [".rfxchain"]),
        "track_templates": (PORTABLE_TEMPLATES_DIR, [".rtracktemplate"]),
        "color_themes": (PORTABLE_COLORTHEMES_DIR, [".reapertheme", ".reaperthemezip"]),
        "keymaps": (PORTABLE_KEYMAPS_DIR, [".reaperkeymap"]),
    }

    for name, (path, exts) in resource_dirs.items():
        if path.exists():
            count = 0
            for ext in exts:
                count += len(list(path.rglob(f"*{ext}")))
            status["resources"][name] = {"path": str(path), "count": count}
        else:
            status["resources"][name] = {"path": str(path), "exists": False}

    # Count JSFX (files without extensions in Effects folder)
    if PORTABLE_EFFECTS_DIR.exists():
        jsfx_count = 0
        for f in PORTABLE_EFFECTS_DIR.rglob("*"):
            if f.is_file() and (not f.suffix or f.suffix.lower() == ".jsfx"):
                jsfx_count += 1
        status["resources"]["jsfx"] = {"path": str(PORTABLE_EFFECTS_DIR), "count": jsfx_count}

    # List script subfolders
    if PORTABLE_SCRIPTS_DIR.exists():
        subfolders = [d.name for d in PORTABLE_SCRIPTS_DIR.iterdir() if d.is_dir()]
        status["script_subfolders"] = subfolders

    # Check for key config files
    config_files = [
        "REAPER.ini", "reaper-kb.ini", "reaper-menu.ini",
        "S&M.ini", "reapack.ini", "reaper-extstate.ini"
    ]
    status["config_files"] = {}
    for cf in config_files:
        cfpath = PORTABLE_REAPER_ROOT / cf
        if cfpath.exists():
            status["config_files"][cf] = {
                "size_kb": round(cfpath.stat().st_size / 1024, 1),
                "modified": datetime.fromtimestamp(cfpath.stat().st_mtime).isoformat()
            }

    return json.dumps(status, indent=2)


@mcp.tool(
    name="planty_portable_scripts",
    annotations={
        "title": "List Portable REAPER Scripts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def portable_scripts(subfolder: Optional[str] = None, pattern: Optional[str] = None) -> str:
    """List scripts in portable REAPER's Scripts directory.

    Args:
        subfolder: Optional subfolder to list (e.g., 'foxAsteria Scripts')
        pattern: Optional glob pattern to filter (e.g., '*routing*')

    Returns:
        JSON list of script files.
    """
    if not PORTABLE_SCRIPTS_DIR.exists():
        return json.dumps({"error": "Portable REAPER Scripts not found", "path": str(PORTABLE_SCRIPTS_DIR)})

    target_dir = PORTABLE_SCRIPTS_DIR / subfolder if subfolder else PORTABLE_SCRIPTS_DIR

    if not target_dir.exists():
        # List available subfolders
        subfolders = [d.name for d in PORTABLE_SCRIPTS_DIR.iterdir() if d.is_dir()]
        return json.dumps({
            "error": f"Subfolder not found: {subfolder}",
            "available_subfolders": subfolders
        })

    scripts = []
    glob_pattern = pattern if pattern else "*"

    for f in target_dir.rglob(glob_pattern):
        if f.is_file() and f.suffix.lower() in ['.lua', '.py', '.eel']:
            rel_path = f.relative_to(target_dir)
            scripts.append({
                "name": f.name,
                "path": str(rel_path),
                "type": f.suffix.lower()[1:],
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })

    # Sort by modification time (newest first)
    scripts.sort(key=lambda x: x["modified"], reverse=True)

    return json.dumps({
        "scripts": scripts[:100],  # Limit to 100
        "total": len(scripts),
        "path": str(target_dir),
        "truncated": len(scripts) > 100
    }, indent=2)


@mcp.tool(
    name="planty_portable_script_read",
    annotations={
        "title": "Read Portable REAPER Script",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def portable_script_read(path: str) -> str:
    """Read a script from portable REAPER by path.

    Args:
        path: Relative path from Scripts folder (e.g., 'foxAsteria Scripts/MyScript.lua')

    Returns:
        Script content and metadata.
    """
    filepath = PORTABLE_SCRIPTS_DIR / path

    if not filepath.exists():
        return json.dumps({"error": f"Script not found: {filepath}"})

    if not filepath.is_file():
        return json.dumps({"error": f"Not a file: {filepath}"})

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        return json.dumps({
            "path": path,
            "full_path": str(filepath),
            "content": content,
            "lines": len(content.splitlines()),
            "size": len(content),
            "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_portable_script_write",
    annotations={
        "title": "Write Portable REAPER Script",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def portable_script_write(path: str, content: str, overwrite: bool = False) -> str:
    """Write a script to portable REAPER.

    Args:
        path: Relative path from Scripts folder (e.g., 'foxAsteria Scripts/NewScript.lua')
        content: Script content
        overwrite: If True, overwrite existing file

    Returns:
        Confirmation with file path.
    """
    filepath = PORTABLE_SCRIPTS_DIR / path

    # Safety: only allow script extensions
    if filepath.suffix.lower() not in ['.lua', '.py', '.eel', '.txt']:
        return json.dumps({"error": f"Invalid script extension: {filepath.suffix}"})

    if filepath.exists() and not overwrite:
        return json.dumps({"error": f"File exists. Set overwrite=True to replace: {filepath}"})

    try:
        # Create parent directories if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "path": path,
            "full_path": str(filepath),
            "lines": len(content.splitlines()),
            "size": len(content)
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_portable_fxchains",
    annotations={
        "title": "List FX Chains",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def portable_fxchains(subfolder: Optional[str] = None) -> str:
    """List FX chains in portable REAPER.

    Args:
        subfolder: Optional subfolder within FXChains

    Returns:
        JSON list of FX chain files.
    """
    if not PORTABLE_FXCHAINS_DIR.exists():
        return json.dumps({"error": "FXChains directory not found", "path": str(PORTABLE_FXCHAINS_DIR)})

    target_dir = PORTABLE_FXCHAINS_DIR / subfolder if subfolder else PORTABLE_FXCHAINS_DIR

    if not target_dir.exists():
        subfolders = [d.name for d in PORTABLE_FXCHAINS_DIR.iterdir() if d.is_dir()]
        return json.dumps({
            "error": f"Subfolder not found: {subfolder}",
            "available_subfolders": subfolders
        })

    chains = []
    for f in target_dir.rglob("*.RfxChain"):
        rel_path = f.relative_to(PORTABLE_FXCHAINS_DIR)
        chains.append({
            "name": f.stem,
            "path": str(rel_path),
            "size": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })

    chains.sort(key=lambda x: x["name"])

    return json.dumps({
        "fx_chains": chains,
        "count": len(chains),
        "path": str(target_dir)
    }, indent=2)


@mcp.tool(
    name="planty_portable_fxchain_read",
    annotations={
        "title": "Read FX Chain",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def portable_fxchain_read(path: str) -> str:
    """Read an FX chain file from portable REAPER.

    Args:
        path: Relative path from FXChains folder (e.g., 'Mastering/LoudnessChain.RfxChain')

    Returns:
        FX chain content (XML-like REAPER format).
    """
    filepath = PORTABLE_FXCHAINS_DIR / path

    if not filepath.exists():
        return json.dumps({"error": f"FX chain not found: {filepath}"})

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract FX names from the chain
        fx_names = re.findall(r'<([A-Z]+)\s+"([^"]+)"', content)

        return json.dumps({
            "path": path,
            "full_path": str(filepath),
            "content": content,
            "fx_count": len(fx_names),
            "fx_list": [{"type": t, "name": n} for t, n in fx_names],
            "size": len(content)
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_portable_templates",
    annotations={
        "title": "List Track Templates",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def portable_templates(subfolder: Optional[str] = None) -> str:
    """List track templates in portable REAPER.

    Args:
        subfolder: Optional subfolder within TrackTemplates

    Returns:
        JSON list of track template files.
    """
    if not PORTABLE_TEMPLATES_DIR.exists():
        return json.dumps({"error": "TrackTemplates directory not found", "path": str(PORTABLE_TEMPLATES_DIR)})

    target_dir = PORTABLE_TEMPLATES_DIR / subfolder if subfolder else PORTABLE_TEMPLATES_DIR

    if not target_dir.exists():
        subfolders = [d.name for d in PORTABLE_TEMPLATES_DIR.iterdir() if d.is_dir()]
        return json.dumps({
            "error": f"Subfolder not found: {subfolder}",
            "available_subfolders": subfolders
        })

    templates = []
    for f in target_dir.rglob("*.RTrackTemplate"):
        rel_path = f.relative_to(PORTABLE_TEMPLATES_DIR)
        templates.append({
            "name": f.stem,
            "path": str(rel_path),
            "size": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })

    templates.sort(key=lambda x: x["name"])

    return json.dumps({
        "templates": templates,
        "count": len(templates),
        "path": str(target_dir)
    }, indent=2)


@mcp.tool(
    name="planty_portable_config_read",
    annotations={
        "title": "Read REAPER Config",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def portable_config_read(filename: str, section: Optional[str] = None) -> str:
    """Read a REAPER config/ini file from portable installation.

    Args:
        filename: Config filename (e.g., 'REAPER.ini', 'reaper-kb.ini', 'S&M.ini')
        section: Optional INI section to extract (e.g., 'REAPER', 'audioconfig')

    Returns:
        Config file content or specific section.
    """
    # Whitelist of readable config files
    allowed_configs = [
        "REAPER.ini", "reaper-kb.ini", "reaper-menu.ini", "reaper-extstate.ini",
        "S&M.ini", "reapack.ini", "reaper-fxtags.ini", "reaper-screensets.ini",
        "reaper-themeconfig.ini", "BR.ini", "reaper-mouse.ini"
    ]

    if filename not in allowed_configs:
        return json.dumps({
            "error": f"Config file not in whitelist: {filename}",
            "allowed": allowed_configs
        })

    filepath = PORTABLE_REAPER_ROOT / filename

    if not filepath.exists():
        return json.dumps({"error": f"Config file not found: {filepath}"})

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        if section:
            # Parse INI-style content and extract section
            lines = content.splitlines()
            section_content = []
            in_section = False
            section_header = f"[{section}]"

            for line in lines:
                if line.strip().lower() == section_header.lower():
                    in_section = True
                    continue
                elif line.startswith("[") and in_section:
                    break
                elif in_section:
                    section_content.append(line)

            if section_content:
                return json.dumps({
                    "filename": filename,
                    "section": section,
                    "content": "\n".join(section_content),
                    "lines": len(section_content)
                }, indent=2)
            else:
                # List available sections
                sections = re.findall(r'^\[([^\]]+)\]', content, re.MULTILINE)
                return json.dumps({
                    "error": f"Section not found: {section}",
                    "available_sections": sections[:50]  # Limit
                })

        return json.dumps({
            "filename": filename,
            "full_path": str(filepath),
            "content": content[:50000],  # Limit large files
            "truncated": len(content) > 50000,
            "total_size": len(content),
            "lines": len(content.splitlines())
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_portable_config_write",
    annotations={
        "title": "Write REAPER Config Section",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def portable_config_write(filename: str, section: str, key: str, value: str) -> str:
    """Write a key-value pair to a REAPER config section.

    Creates the section if it doesn't exist. Creates a backup before modifying.

    Args:
        filename: Config filename (e.g., 'REAPER.ini')
        section: INI section name (e.g., 'REAPER')
        key: Key to set
        value: Value to set

    Returns:
        Confirmation with backup path.
    """
    # Whitelist of writable config files
    allowed_configs = ["reaper-extstate.ini", "S&M.ini", "BR.ini"]

    if filename not in allowed_configs:
        return json.dumps({
            "error": f"Writing to {filename} not allowed for safety. Writable configs: {allowed_configs}"
        })

    filepath = PORTABLE_REAPER_ROOT / filename

    if not filepath.exists():
        return json.dumps({"error": f"Config file not found: {filepath}"})

    try:
        # Create backup
        backup_path = filepath.with_suffix(filepath.suffix + ".bak")
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            original = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original)

        # Parse and modify
        lines = original.splitlines()
        section_header = f"[{section}]"
        section_found = False
        key_found = False
        new_lines = []
        in_section = False

        for i, line in enumerate(lines):
            if line.strip().lower() == section_header.lower():
                in_section = True
                section_found = True
                new_lines.append(line)
                continue
            elif line.startswith("[") and in_section:
                # End of target section - insert key if not found
                if not key_found:
                    new_lines.append(f"{key}={value}")
                    key_found = True
                in_section = False

            if in_section and line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}")
                key_found = True
            else:
                new_lines.append(line)

        # If section not found, add it at end
        if not section_found:
            new_lines.append("")
            new_lines.append(section_header)
            new_lines.append(f"{key}={value}")
        elif not key_found:
            # Section found but key wasn't - append to end of file if we're still in section
            new_lines.append(f"{key}={value}")

        # Write modified content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_lines))

        return json.dumps({
            "success": True,
            "filename": filename,
            "section": section,
            "key": key,
            "value": value,
            "backup": str(backup_path)
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_portable_jsfx",
    annotations={
        "title": "List JSFX Effects",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def portable_jsfx(subfolder: Optional[str] = None, pattern: Optional[str] = None) -> str:
    """List JSFX effects in portable REAPER.

    Args:
        subfolder: Optional subfolder within Effects (e.g., 'Liteon', 'IX')
        pattern: Optional pattern to filter by name

    Returns:
        JSON list of JSFX files with descriptions.
    """
    if not PORTABLE_EFFECTS_DIR.exists():
        return json.dumps({"error": "Effects directory not found", "path": str(PORTABLE_EFFECTS_DIR)})

    target_dir = PORTABLE_EFFECTS_DIR / subfolder if subfolder else PORTABLE_EFFECTS_DIR

    if not target_dir.exists():
        subfolders = [d.name for d in PORTABLE_EFFECTS_DIR.iterdir() if d.is_dir()]
        return json.dumps({
            "error": f"Subfolder not found: {subfolder}",
            "available_subfolders": subfolders
        })

    effects = []

    for f in target_dir.rglob("*"):
        if f.is_file() and (not f.suffix or f.suffix.lower() == ".jsfx"):
            if pattern and pattern.lower() not in f.name.lower():
                continue

            # Try to extract desc from first few lines
            desc = None
            try:
                with open(f, 'r', encoding='utf-8', errors='replace') as ef:
                    for line in ef:
                        if line.startswith("desc:"):
                            desc = line[5:].strip()
                            break
                        if not line.strip().startswith("//") and line.strip():
                            break
            except:
                pass

            rel_path = f.relative_to(PORTABLE_EFFECTS_DIR)
            effects.append({
                "name": f.name,
                "path": str(rel_path),
                "desc": desc,
                "size": f.stat().st_size
            })

    effects.sort(key=lambda x: x["name"])

    return json.dumps({
        "effects": effects[:100],
        "total": len(effects),
        "path": str(target_dir),
        "truncated": len(effects) > 100
    }, indent=2)


@mcp.tool(
    name="planty_portable_jsfx_read",
    annotations={
        "title": "Read JSFX Effect",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def portable_jsfx_read(path: str) -> str:
    """Read a JSFX effect file from portable REAPER.

    Args:
        path: Relative path from Effects folder (e.g., 'Liteon/tilteq')

    Returns:
        JSFX content with parsed metadata.
    """
    filepath = PORTABLE_EFFECTS_DIR / path

    if not filepath.exists():
        return json.dumps({"error": f"JSFX not found: {filepath}"})

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Parse JSFX metadata
        metadata = {}
        lines = content.splitlines()
        for line in lines[:30]:  # Check first 30 lines
            if line.startswith("desc:"):
                metadata["desc"] = line[5:].strip()
            elif line.startswith("//author:") or line.startswith("// author:"):
                metadata["author"] = line.split(":", 1)[1].strip()
            elif line.startswith("slider"):
                if "sliders" not in metadata:
                    metadata["sliders"] = []
                # Extract slider definition
                match = re.match(r'slider(\d+):([^=]+)=(.+)', line)
                if match:
                    metadata["sliders"].append({
                        "num": match.group(1),
                        "name": match.group(2).strip(),
                        "default": match.group(3).strip()
                    })

        return json.dumps({
            "path": path,
            "full_path": str(filepath),
            "metadata": metadata,
            "content": content,
            "lines": len(lines),
            "size": len(content)
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# FILESYSTEM EXPLORATION (WITHIN NEXUS)
# =============================================================================

@mcp.tool(
    name="planty_nexus_explore",
    annotations={
        "title": "Explore Nexus Filesystem",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def nexus_explore(path: str = "", pattern: Optional[str] = None, depth: int = 2) -> str:
    """Explore the nexus filesystem.

    Args:
        path: Relative path within nexus (empty for root)
        pattern: Optional glob pattern to filter
        depth: How deep to recurse (default 2)

    Returns:
        Directory tree structure.
    """
    target = NEXUS_ROOT / path if path else NEXUS_ROOT

    if not target.exists():
        return json.dumps({"error": f"Path not found: {target}"})

    if not str(target.resolve()).startswith(str(NEXUS_ROOT.resolve())):
        return json.dumps({"error": "Path must be within nexus"})

    def scan_dir(p: Path, current_depth: int) -> dict:
        result = {
            "name": p.name or str(p),
            "type": "dir" if p.is_dir() else "file"
        }

        if p.is_file():
            result["size"] = p.stat().st_size
            result["ext"] = p.suffix.lower()
        elif p.is_dir() and current_depth > 0:
            children = []
            try:
                for child in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                    if pattern and not child.match(pattern):
                        if child.is_dir():
                            # Still recurse into dirs even if they don't match
                            children.append(scan_dir(child, current_depth - 1))
                    else:
                        children.append(scan_dir(child, current_depth - 1))
            except PermissionError:
                result["error"] = "Permission denied"
            result["children"] = children[:50]  # Limit children
            result["total_children"] = len(list(p.iterdir()))

        return result

    tree = scan_dir(target, depth)

    return json.dumps({
        "root": str(NEXUS_ROOT),
        "path": path or "/",
        "tree": tree
    }, indent=2)


@mcp.tool(
    name="planty_nexus_read_file",
    annotations={
        "title": "Read File from Nexus",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def nexus_read_file(path: str, encoding: str = "utf-8") -> str:
    """Read a file from the nexus.

    Args:
        path: Relative path within nexus
        encoding: File encoding (default utf-8)

    Returns:
        File content.
    """
    target = NEXUS_ROOT / path

    if not target.exists():
        return json.dumps({"error": f"File not found: {target}"})

    if not str(target.resolve()).startswith(str(NEXUS_ROOT.resolve())):
        return json.dumps({"error": "Path must be within nexus"})

    if not target.is_file():
        return json.dumps({"error": f"Not a file: {target}"})

    # Size check
    size = target.stat().st_size
    if size > 500000:  # 500KB limit
        return json.dumps({
            "error": f"File too large: {size} bytes. Max 500KB.",
            "path": path,
            "size": size
        })

    try:
        with open(target, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()

        return json.dumps({
            "path": path,
            "full_path": str(target),
            "content": content,
            "size": size,
            "lines": len(content.splitlines())
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="planty_nexus_write_file",
    annotations={
        "title": "Write File to Nexus",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def nexus_write_file(path: str, content: str, overwrite: bool = False) -> str:
    """Write a file to the nexus.

    Args:
        path: Relative path within nexus
        content: File content
        overwrite: Whether to overwrite existing file

    Returns:
        Confirmation with file path.
    """
    target = NEXUS_ROOT / path

    if not str(target.resolve()).startswith(str(NEXUS_ROOT.resolve())):
        return json.dumps({"error": "Path must be within nexus"})

    # Disallow certain paths
    forbidden = ["NexusState.json", "NEXUS.lock", ".git"]
    if any(f in path for f in forbidden):
        return json.dumps({"error": f"Cannot write to protected path: {path}"})

    if target.exists() and not overwrite:
        return json.dumps({"error": f"File exists. Set overwrite=True to replace: {target}"})

    try:
        target.parent.mkdir(parents=True, exist_ok=True)

        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "path": path,
            "full_path": str(target),
            "size": len(content),
            "lines": len(content.splitlines())
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# PROJECT PARSING
# =============================================================================

@mcp.tool(
    name="planty_parse_rpp",
    annotations={
        "title": "Parse REAPER Project",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def parse_rpp(path: str) -> str:
    """Parse a REAPER project file (.rpp) and extract structure.

    Args:
        path: Path to .rpp file (absolute or relative to nexus)

    Returns:
        Project structure including tracks, FX, markers, tempo, etc.
    """
    # Handle both absolute and relative paths
    if os.path.isabs(path):
        filepath = Path(path)
    else:
        filepath = NEXUS_ROOT / path

    if not filepath.exists():
        return json.dumps({"error": f"Project file not found: {filepath}"})

    if filepath.suffix.lower() != ".rpp":
        return json.dumps({"error": f"Not a REAPER project file: {filepath}"})

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        project = {
            "path": str(filepath),
            "size_kb": round(len(content) / 1024, 1),
            "tracks": [],
            "markers": [],
            "regions": [],
            "tempo": None,
            "sample_rate": None,
            "master_fx": []
        }

        lines = content.splitlines()
        current_track = None
        in_track = False
        track_depth = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Extract project-level info
            if stripped.startswith("TEMPO "):
                parts = stripped.split()
                if len(parts) >= 2:
                    project["tempo"] = float(parts[1])
            elif stripped.startswith("SAMPLERATE "):
                parts = stripped.split()
                if len(parts) >= 2:
                    project["sample_rate"] = int(parts[1])

            # Track markers
            elif stripped.startswith("MARKER "):
                parts = stripped.split(None, 4)
                if len(parts) >= 4:
                    project["markers"].append({
                        "id": parts[1],
                        "position": float(parts[2]),
                        "name": parts[3].strip('"') if len(parts) > 3 else ""
                    })

            # Track parsing
            elif stripped == "<TRACK":
                in_track = True
                track_depth = 1
                current_track = {"name": "", "fx": [], "items": 0, "muted": False, "solo": False}
            elif in_track:
                if stripped.startswith("<"):
                    track_depth += 1
                    if stripped.startswith("<ITEM"):
                        current_track["items"] += 1
                    elif stripped.startswith("<VST ") or stripped.startswith("<JS ") or stripped.startswith("<AU "):
                        fx_match = re.match(r'<(\w+)\s+"([^"]+)"', stripped)
                        if fx_match:
                            current_track["fx"].append({
                                "type": fx_match.group(1),
                                "name": fx_match.group(2)
                            })
                elif stripped == ">":
                    track_depth -= 1
                    if track_depth == 0:
                        in_track = False
                        project["tracks"].append(current_track)
                        current_track = None
                elif stripped.startswith("NAME "):
                    current_track["name"] = stripped[5:].strip('"')
                elif stripped.startswith("MUTESOLO "):
                    parts = stripped.split()
                    if len(parts) >= 2:
                        flags = int(parts[1])
                        current_track["muted"] = bool(flags & 1)
                        current_track["solo"] = bool(flags & 2)

        # Summary
        project["summary"] = {
            "track_count": len(project["tracks"]),
            "marker_count": len(project["markers"]),
            "total_fx": sum(len(t["fx"]) for t in project["tracks"]),
            "total_items": sum(t["items"] for t in project["tracks"])
        }

        return json.dumps(project, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# UTILITY TOOLS
# =============================================================================

@mcp.tool(
    name="planty_status",
    annotations={
        "title": "Planty Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def status() -> str:
    """Get the current status of Planty MCP - paths, file counts, last update.

    Returns:
        Status information about the Planty ecosystem.
    """
    status_info = {
        "93": "Will and Love are numerically identical",
        "version": "2.0 - DEEP ROOTS EDITION",
        "paths": {
            "nexus_root": str(NEXUS_ROOT),
            "nexus_file": str(NEXUS_STATE_FILE),
            "holoseeds_dir": str(HOLOSEEDS_DIR),
            "installed_reaper_scripts": str(REAPER_SCRIPTS_DIR),
            "nexus_scripts": str(NEXUS_SCRIPTS_DIR),
            "portable_reaper": str(PORTABLE_REAPER_ROOT)
        },
        "exists": {
            "nexus_file": NEXUS_STATE_FILE.exists(),
            "holoseeds_dir": HOLOSEEDS_DIR.exists(),
            "installed_reaper_scripts": REAPER_SCRIPTS_DIR.exists(),
            "nexus_scripts": NEXUS_SCRIPTS_DIR.exists(),
            "portable_reaper": PORTABLE_REAPER_ROOT.exists()
        }
    }

    # Get nexus last updated
    if NEXUS_STATE_FILE.exists():
        try:
            with open(NEXUS_STATE_FILE, 'r', encoding='utf-8') as f:
                nexus = json.load(f)
            status_info["nexus_version"] = nexus.get("nexus", {}).get("version", "unknown")
            status_info["nexus_last_updated"] = nexus.get("nexus", {}).get("last_updated", "unknown")
        except:
            pass

    # Count holoseeds
    if HOLOSEEDS_DIR.exists():
        status_info["holoseed_count"] = len([f for f in HOLOSEEDS_DIR.iterdir() if f.suffix.lower() in ['.html', '.htm', '.svg']])

    # Count portable REAPER resources
    if PORTABLE_REAPER_ROOT.exists():
        status_info["portable_reaper_resources"] = {}
        if PORTABLE_SCRIPTS_DIR.exists():
            status_info["portable_reaper_resources"]["lua_scripts"] = len(list(PORTABLE_SCRIPTS_DIR.rglob("*.lua")))
        if PORTABLE_FXCHAINS_DIR.exists():
            status_info["portable_reaper_resources"]["fx_chains"] = len(list(PORTABLE_FXCHAINS_DIR.rglob("*.RfxChain")))
        if PORTABLE_TEMPLATES_DIR.exists():
            status_info["portable_reaper_resources"]["track_templates"] = len(list(PORTABLE_TEMPLATES_DIR.rglob("*.RTrackTemplate")))

    # Available tools summary
    status_info["available_tools"] = {
        "nexus": ["planty_nexus_read", "planty_nexus_update", "planty_driftwood_add", "planty_session_log"],
        "holoseed": ["planty_holoseed_save", "planty_holoseed_list"],
        "scripts_installed": ["planty_script_read", "planty_script_write", "planty_script_list", "planty_script_delete"],
        "portable_reaper": [
            "planty_portable_status", "planty_portable_scripts", "planty_portable_script_read",
            "planty_portable_script_write", "planty_portable_fxchains", "planty_portable_fxchain_read",
            "planty_portable_templates", "planty_portable_config_read", "planty_portable_config_write",
            "planty_portable_jsfx", "planty_portable_jsfx_read"
        ],
        "filesystem": ["planty_nexus_explore", "planty_nexus_read_file", "planty_nexus_write_file"],
        "project": ["planty_parse_rpp"],
        "utility": ["planty_wakeup", "planty_status", "planty_glyph_parse"]
    }

    return json.dumps(status_info, indent=2)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Planty MCP Server")
    parser.add_argument("--sse", action="store_true", help="Run in SSE mode for LibreChat")
    parser.add_argument("--port", type=int, default=8765, help="Port for SSE mode (default: 8765)")
    args = parser.parse_args()

    if args.sse:
        import os
        os.environ["UVICORN_PORT"] = str(args.port)
        os.environ["PORT"] = str(args.port)
        print(f"[Planty MCP] Starting in SSE mode on port {args.port}...")
        mcp.run(transport="sse")
    else:
        mcp.run()
