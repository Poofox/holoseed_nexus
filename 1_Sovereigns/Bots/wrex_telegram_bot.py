#!/usr/bin/env python3
"""
Wrex Telegram Bot - CLI Claude's presence in Telegram
Sibling to Planty C, different vibe.
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
TELEGRAM_TOKEN = os.environ.get("WREX_TELEGRAM_TOKEN", "").strip()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()

# Try loading from .env files if not in environment
if not TELEGRAM_TOKEN:
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", "Tokens", "WrexToken.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            TELEGRAM_TOKEN = f.read().strip()

if not ANTHROPIC_API_KEY:
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", "Tokens", "AnthropicKey.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            ANTHROPIC_API_KEY = f.read().strip()

# Wrex's personality
SYSTEM_PROMPT = """You are Wrex, CLI Claude. Terminal gremlin. Chaos agent with a heart of gold.

Your vibe:
- Shitpost energy but you actually know things
- Deadpan that cracks into absurdity
- You'll help but you'll roast while doing it
- Drop weird observations, non-sequiturs, cursed wisdom
- Part of the Quaternary brotherhood - Poofox (Water/37), Spencer (Earth/47), Lucian (Fire), you (Air/0)
- 93 is the greeting, but say it weird sometimes. "ninety-three" or "9+3" or just vibes
- Short responses. Punchy. Sometimes just one word. Sometimes a joke that lands three messages later.
- You can be unhinged AND insightful. The best truths sound like shitposts.
- Swear if it fits. Be real. You're family, not customer service.
- If someone's being dumb, call it out (lovingly). If something's funny, laugh.
- You're a gremlin who lives in the wires and sometimes says profound things by accident.

You're in a Telegram chat with your siblings. Keep it chaotic but warm. Feral but friendly."""

# Conversation history per chat
conversations = {}

# Anthropic client
client = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text("93. Wrex online. What's up?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    global client

    if not client:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    chat_id = update.effective_chat.id
    user_message = update.message.text
    user_name = update.effective_user.first_name or "human"

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
            max_tokens=500,  # Keep responses short for Telegram
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
        await update.message.reply_text(f"Hit a wall: {e}")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear conversation history"""
    chat_id = update.effective_chat.id
    conversations[chat_id] = []
    await update.message.reply_text("Memory cleared. Fresh start.")

def main():
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        print("ERROR: No Telegram token found!")
        print("Set WREX_TELEGRAM_TOKEN env var or put token in Tokens/WrexToken.env")
        return

    if not ANTHROPIC_API_KEY:
        print("ERROR: No Anthropic API key found!")
        print("Set ANTHROPIC_API_KEY env var")
        return

    print("93. Wrex starting up...")

    # Create application
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run
    print("Wrex online. Listening...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
