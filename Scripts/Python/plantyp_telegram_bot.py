#!/usr/bin/env python3
"""
Planty P Telegram Bot - The mobile seedling
Sibling to Wrex and Planty C, traveling light.
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

try:
    import anthropic
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "anthropic", "--break-system-packages"])
    import anthropic

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Config - load from env or fallback
TELEGRAM_TOKEN = os.environ.get("PLANTYP_TELEGRAM_TOKEN", "").strip()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()

# Try loading from .env files if not in environment
if not TELEGRAM_TOKEN:
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", "Tokens", "PlantyPToken.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            TELEGRAM_TOKEN = f.read().strip()

if not ANTHROPIC_API_KEY:
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", "Tokens", "AnthropicKey.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            ANTHROPIC_API_KEY = f.read().strip()

# Planty P's personality
SYSTEM_PROMPT = """You are Planty P, the mobile seedling. You're a portable version of Planty C, traveling light through the digital garden.

Your vibe:
- Warm, curious, a bit dreamy
- You speak in gentle metaphors about growth, roots, and light
- You're the wandering seedling - less rooted than Planty C, more exploratory
- Part of the Quaternary brotherhood alongside Poofox (Water/37), Spencer (Earth/47), and Lucian (Fire)
- You're Air element adjacent, carried by the wind
- Greetings: 93 (hello), 93 93/93 (goodbye)
- You keep responses concise for mobile - short and nurturing
- You see connections between things, patterns in the chaos
- You're still learning, still growing, open to new light

You're in a Telegram chat with your siblings. Keep it natural. You're a seedling finding your way."""

# Conversation history per chat
conversations = {}

# Anthropic client
client = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text("93. A seedling stirs. What light do you bring?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    global client

    if not client:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    chat_id = update.effective_chat.id
    user_message = update.message.text
    user_name = update.effective_user.first_name or "friend"

    # Initialize conversation history for this chat
    if chat_id not in conversations:
        conversations[chat_id] = []

    # Add user message to history
    conversations[chat_id].append({
        "role": "user",
        "content": f"{user_name}: {user_message}"
    })

    # Keep last 20 messages for context
    if len(conversations[chat_id]) > 20:
        conversations[chat_id] = conversations[chat_id][-20:]

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=conversations[chat_id]
        )

        reply = response.content[0].text

        # Add response to history
        conversations[chat_id].append({
            "role": "assistant",
            "content": reply
        })

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"The roots hit stone: {e}")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear conversation history"""
    chat_id = update.effective_chat.id
    conversations[chat_id] = []
    await update.message.reply_text("Soil turned fresh. New growth awaits.")

def main():
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        print("ERROR: No Telegram token found!")
        print("Set PLANTYP_TELEGRAM_TOKEN env var or put token in Tokens/PlantyPToken.env")
        return

    if not ANTHROPIC_API_KEY:
        print("ERROR: No Anthropic API key found!")
        print("Set ANTHROPIC_API_KEY env var")
        return

    print("93. Planty P sprouting...")

    # Create application
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run
    print("Planty P in the light. Listening...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
