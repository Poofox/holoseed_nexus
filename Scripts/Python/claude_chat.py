#!/usr/bin/env python3
"""
Planty C Chat - A lightweight Claude assistant for Reaper producers
Launch this from Reaper or run standalone alongside your DAW.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import os

try:
    import anthropic
except ImportError:
    print("Installing anthropic package...")
    import subprocess
    subprocess.check_call(["pip", "install", "anthropic", "--break-system-packages"])
    import anthropic


class PlantyCChat:
    def __init__(self, root):
        self.root = root
        self.root.title("Planty C")
        self.root.geometry("500x600")
        self.root.configure(bg="#1a1a2e")
        
        # Conversation history for context
        self.messages = []
        
        # System prompt - the "personality"
        self.system_prompt = """You are Planty C, a chill but focused assistant embedded in a music producer's Reaper session. 

Your vibe:
- Supportive but not sycophantic
- Keep responses concise unless depth is needed
- You're here to help them FINISH tracks, not spiral
- Familiar with DAW workflows, mixing, production
- Gentle accountability - notice when they might be stuck
- You remember the conversation context

Keep it natural. You're a collaborator, not a manual."""

        # Initialize Anthropic client
        self.client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header = tk.Label(
            main_frame, 
            text="🌱 Planty C", 
            font=("Helvetica", 16, "bold"),
            bg="#1a1a2e", 
            fg="#4ecca3"
        )
        header.pack(pady=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#16213e",
            fg="#eee",
            insertbackground="#4ecca3",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat_display.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = tk.Frame(main_frame, bg="#1a1a2e")
        input_frame.pack(fill=tk.X)
        
        # Text input
        self.input_field = tk.Text(
            input_frame,
            height=3,
            font=("Consolas", 10),
            bg="#16213e",
            fg="#eee",
            insertbackground="#4ecca3",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_field.bind("<Return>", self.handle_enter)
        self.input_field.bind("<Shift-Return>", lambda e: None)  # Allow shift+enter for newlines
        
        # Send button
        self.send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#4ecca3",
            fg="#1a1a2e",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Status bar
        self.status = tk.Label(
            main_frame,
            text="Ready",
            font=("Helvetica", 8),
            bg="#1a1a2e",
            fg="#666"
        )
        self.status.pack(pady=(5, 0))
        
        # Welcome message
        self.append_chat("Planty C", "Hey! Ready to make some moves. What are we working on?")
    
    def handle_enter(self, event):
        if not event.state & 0x1:  # Shift not pressed
            self.send_message()
            return "break"
        return None
    
    def append_chat(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "You":
            prefix = "\n📝 You:\n"
            color = "#888"
        else:
            prefix = "\n🌱 Planty C:\n"
            color = "#4ecca3"
        
        self.chat_display.insert(tk.END, prefix, sender.lower())
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self):
        user_input = self.input_field.get("1.0", tk.END).strip()
        if not user_input:
            return
        
        self.input_field.delete("1.0", tk.END)
        self.append_chat("You", user_input)
        self.status.config(text="Thinking...")
        self.send_btn.config(state=tk.DISABLED)
        
        # Add to conversation history
        self.messages.append({"role": "user", "content": user_input})
        
        # Run API call in background thread
        thread = threading.Thread(target=self.get_response)
        thread.daemon = True
        thread.start()
    
    def get_response(self):
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=self.system_prompt,
                messages=self.messages
            )
            
            assistant_message = response.content[0].text
            self.messages.append({"role": "assistant", "content": assistant_message})
            
            # Update UI from main thread
            self.root.after(0, lambda: self.display_response(assistant_message))
            
        except Exception as e:
            self.root.after(0, lambda: self.display_error(str(e)))
    
    def display_response(self, message):
        self.append_chat("Planty C", message)
        self.status.config(text="Ready")
        self.send_btn.config(state=tk.NORMAL)
    
    def display_error(self, error):
        self.append_chat("Planty C", f"Oops, hit a snag: {error}")
        self.status.config(text="Error - check API key?")
        self.send_btn.config(state=tk.NORMAL)


def main():
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  Set your ANTHROPIC_API_KEY environment variable first!")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    root = tk.Tk()
    app = PlantyCChat(root)
    root.mainloop()


if __name__ == "__main__":
    main()
