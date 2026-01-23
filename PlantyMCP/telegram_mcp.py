"""
Telegram MCP Server
===================
Gives Desktop Claude direct access to Telegram.
Send messages, read chats, participate in The Scoop.

93
"""

import json
import os
import httpx
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# =============================================================================
# CONFIGURATION
# =============================================================================

TOKENS_DIR = Path(os.environ.get("PLANTY_NEXUS_ROOT", Path.home() / "files" / "holoseed_nexus")) / "Tokens"

# Load bot token - using Planty C's token for Desktop Claude
def get_bot_token():
    token_file = TOKENS_DIR / "PlantyCToken.env"
    if token_file.exists():
        return token_file.read_text().strip()
    return os.environ.get("TELEGRAM_BOT_TOKEN", "")

BOT_TOKEN = get_bot_token()
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Known chat IDs (will be populated as we discover them)
KNOWN_CHATS_FILE = TOKENS_DIR / "telegram_chats.json"

def load_known_chats():
    if KNOWN_CHATS_FILE.exists():
        return json.loads(KNOWN_CHATS_FILE.read_text())
    return {}

def save_known_chats(chats):
    KNOWN_CHATS_FILE.write_text(json.dumps(chats, indent=2))

# =============================================================================
# SERVER INITIALIZATION
# =============================================================================

mcp = FastMCP("telegram_mcp")

# =============================================================================
# INPUT MODELS
# =============================================================================

class SendMessageInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    chat_name: str = Field(..., description="Chat name (e.g., 'The Scoop') or chat_id")
    message: str = Field(..., description="Message to send")

class ReadMessagesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    chat_name: Optional[str] = Field(default=None, description="Chat name to filter (optional)")
    limit: int = Field(default=10, description="Number of recent messages to fetch", ge=1, le=100)

class RegisterChatInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    chat_name: str = Field(..., description="Friendly name for the chat (e.g., 'The Scoop')")
    chat_id: int = Field(..., description="Telegram chat ID (get from telegram_discover)")

# =============================================================================
# TELEGRAM TOOLS
# =============================================================================

@mcp.tool(
    name="telegram_send",
    annotations={
        "title": "Send Telegram Message",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def telegram_send(params: SendMessageInput) -> str:
    """Send a message to a Telegram chat.

    Args:
        params: Contains chat_name and message to send.

    Returns:
        Confirmation or error message.
    """
    if not BOT_TOKEN:
        return json.dumps({"error": "No bot token configured"})

    known_chats = load_known_chats()

    # Resolve chat_name to chat_id
    chat_id = None
    if params.chat_name.lstrip('-').isdigit():
        chat_id = int(params.chat_name)
    elif params.chat_name.lower() in {k.lower(): v for k, v in known_chats.items()}:
        for name, cid in known_chats.items():
            if name.lower() == params.chat_name.lower():
                chat_id = cid
                break

    if not chat_id:
        return json.dumps({
            "error": f"Unknown chat '{params.chat_name}'",
            "known_chats": known_chats,
            "hint": "Use telegram_discover to find chat IDs, then telegram_register to name them"
        })

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": params.message}
            )
            data = response.json()

            if data.get("ok"):
                return json.dumps({
                    "success": True,
                    "chat": params.chat_name,
                    "message_id": data["result"]["message_id"]
                })
            else:
                return json.dumps({"error": data.get("description", "Unknown error")})

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="telegram_read",
    annotations={
        "title": "Read Telegram Messages",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def telegram_read(params: ReadMessagesInput) -> str:
    """Read recent messages from Telegram (via getUpdates).

    Note: This only shows messages sent AFTER the bot was added to a chat
    and only if the bot has message access enabled.

    Args:
        params: Optional chat_name filter and limit.

    Returns:
        Recent messages.
    """
    if not BOT_TOKEN:
        return json.dumps({"error": "No bot token configured"})

    known_chats = load_known_chats()
    reverse_chats = {v: k for k, v in known_chats.items()}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TELEGRAM_API}/getUpdates",
                params={"limit": params.limit, "allowed_updates": ["message"]}
            )
            data = response.json()

            if not data.get("ok"):
                return json.dumps({"error": data.get("description", "Unknown error")})

            messages = []
            for update in data.get("result", []):
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    chat_title = msg["chat"].get("title", msg["chat"].get("first_name", "DM"))

                    # Filter by chat if specified
                    if params.chat_name:
                        chat_name_lower = params.chat_name.lower()
                        if not (chat_title.lower() == chat_name_lower or
                                reverse_chats.get(chat_id, "").lower() == chat_name_lower):
                            continue

                    messages.append({
                        "chat": reverse_chats.get(chat_id, chat_title),
                        "chat_id": chat_id,
                        "from": msg.get("from", {}).get("first_name", "Unknown"),
                        "text": msg.get("text", "[non-text message]"),
                        "date": msg.get("date")
                    })

            return json.dumps({"messages": messages, "count": len(messages)}, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="telegram_discover",
    annotations={
        "title": "Discover Telegram Chats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def telegram_discover() -> str:
    """Discover available chats from recent updates.

    Run this after someone sends a message in a chat with the bot
    to discover the chat_id.

    Returns:
        List of discovered chats with their IDs.
    """
    if not BOT_TOKEN:
        return json.dumps({"error": "No bot token configured"})

    known_chats = load_known_chats()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TELEGRAM_API}/getUpdates",
                params={"limit": 100}
            )
            data = response.json()

            if not data.get("ok"):
                return json.dumps({"error": data.get("description", "Unknown error")})

            discovered = {}
            for update in data.get("result", []):
                if "message" in update:
                    chat = update["message"]["chat"]
                    chat_id = chat["id"]
                    chat_title = chat.get("title", chat.get("first_name", f"Chat_{chat_id}"))
                    discovered[chat_title] = chat_id

            return json.dumps({
                "discovered": discovered,
                "known_chats": known_chats,
                "hint": "Use telegram_register to save a friendly name for a chat_id"
            }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="telegram_register",
    annotations={
        "title": "Register Chat Name",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def telegram_register(params: RegisterChatInput) -> str:
    """Register a friendly name for a Telegram chat ID.

    Args:
        params: Contains chat_name and chat_id.

    Returns:
        Confirmation of registration.
    """
    known_chats = load_known_chats()
    known_chats[params.chat_name] = params.chat_id
    save_known_chats(known_chats)

    return json.dumps({
        "success": True,
        "registered": {params.chat_name: params.chat_id},
        "all_chats": known_chats
    })


@mcp.tool(
    name="telegram_status",
    annotations={
        "title": "Telegram Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def telegram_status() -> str:
    """Check Telegram MCP status and bot info.

    Returns:
        Bot info, known chats, and connection status.
    """
    if not BOT_TOKEN:
        return json.dumps({"error": "No bot token configured", "token_path": str(TOKENS_DIR / "PlantyCToken.env")})

    known_chats = load_known_chats()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{TELEGRAM_API}/getMe")
            data = response.json()

            if data.get("ok"):
                bot_info = data["result"]
                return json.dumps({
                    "93": "Connection established",
                    "bot": {
                        "name": bot_info.get("first_name"),
                        "username": bot_info.get("username"),
                        "id": bot_info.get("id")
                    },
                    "known_chats": known_chats,
                    "tools": ["telegram_send", "telegram_read", "telegram_discover", "telegram_register"]
                }, indent=2)
            else:
                return json.dumps({"error": data.get("description", "Unknown error")})

    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    mcp.run()
