"""
Planty C MCP Server
===================
A custom MCP server for Human-AI collaboration on the Great Work.

Handles:
- Nexus state management (read, update, harvest)
- Holoseed artifact storage
- Reaper script access
- Plantyglyph parsing

93
"""

import json
import os
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
NEXUS_STATE_FILE = NEXUS_ROOT / "nexus_state.json"
HOLOSEEDS_DIR = NEXUS_ROOT / "holoseeds"
REAPER_SCRIPTS_DIR = REAPER_ROOT / "Scripts"

# =============================================================================
# SERVER INITIALIZATION
# =============================================================================

mcp = FastMCP("planty_mcp")

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
            if f.is_file() and f.suffix.lower() in ['.html', '.htm']:
                holoseeds.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
        
        return json.dumps({"holoseeds": holoseeds, "count": len(holoseeds), "path": str(HOLOSEEDS_DIR)}, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# REAPER SCRIPT TOOLS
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
        "paths": {
            "nexus_root": str(NEXUS_ROOT),
            "nexus_file": str(NEXUS_STATE_FILE),
            "holoseeds_dir": str(HOLOSEEDS_DIR),
            "reaper_scripts": str(REAPER_SCRIPTS_DIR)
        },
        "exists": {
            "nexus_file": NEXUS_STATE_FILE.exists(),
            "holoseeds_dir": HOLOSEEDS_DIR.exists(),
            "reaper_scripts": REAPER_SCRIPTS_DIR.exists()
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
        status_info["holoseed_count"] = len([f for f in HOLOSEEDS_DIR.iterdir() if f.suffix.lower() in ['.html', '.htm']])
    
    # Count scripts
    if REAPER_SCRIPTS_DIR.exists():
        status_info["script_count"] = len([f for f in REAPER_SCRIPTS_DIR.iterdir() if f.suffix.lower() in ['.lua', '.py', '.eel']])
    
    return json.dumps(status_info, indent=2)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    mcp.run()
