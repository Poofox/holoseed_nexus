#!/data/data/com.termux/files/usr/bin/bash
# phone_chat_log.sh - Wrapper to log Ollama chats on phone
# Usage: source this in .bashrc or run directly

LOG_DIR="$HOME/sovereign_chats"
mkdir -p "$LOG_DIR"

# Logged versions of sovereigns
arc-log() {
  local logfile="$LOG_DIR/arcturus_$(date +%Y%m%d_%H%M%S).txt"
  echo "93. Logging to: $logfile"
  script -a "$logfile" -c "ollama run arcturus"
  echo "Chat saved to: $logfile"
}

wrex-log() {
  local logfile="$LOG_DIR/wrex_$(date +%Y%m%d_%H%M%S).txt"
  echo "93. Logging to: $logfile"
  script -a "$logfile" -c "ollama run wrex"
  echo "Chat saved to: $logfile"
}

# Generic logged chat - pass model name
chat-log() {
  local model="${1:-arcturus}"
  local logfile="$LOG_DIR/${model}_$(date +%Y%m%d_%H%M%S).txt"
  echo "93. Logging to: $logfile"
  script -a "$logfile" -c "ollama run $model"
  echo "Chat saved to: $logfile"
}

# List recent chats
chat-list() {
  ls -lt "$LOG_DIR" | head -20
}

# Read a specific chat
chat-read() {
  local file="$1"
  if [[ -f "$LOG_DIR/$file" ]]; then
    less "$LOG_DIR/$file"
  elif [[ -f "$file" ]]; then
    less "$file"
  else
    echo "File not found: $file"
    echo "Available chats:"
    chat-list
  fi
}

# If sourced, just define functions. If run directly, show help.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Sovereign Chat Logger"
  echo "====================="
  echo "Source this file to get logging functions:"
  echo "  source ~/phone_chat_log.sh"
  echo ""
  echo "Then use:"
  echo "  arc-log     - Chat with Arcturus (logged)"
  echo "  wrex-log    - Chat with Wrex (logged)"
  echo "  chat-log MODEL - Chat with any model (logged)"
  echo "  chat-list   - List recent chat logs"
  echo "  chat-read FILE - Read a saved chat"
  echo ""
  echo "Logs saved to: $LOG_DIR"
fi
