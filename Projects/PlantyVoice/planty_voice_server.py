#!/usr/bin/env python3
"""
Planty Voice Server - Voice interface for Arcturus
Receives text from web frontend, queries Ollama, returns response.
"""

import os
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Planty Voice")

# Allow CORS for phone access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama config
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("PLANTY_MODEL", "arcturus-cloud")

# Conversation history (simple in-memory for prototype)
conversation_history = []

class ChatRequest(BaseModel):
    message: str
    clear_history: bool = False

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send message to Arcturus, get response."""
    global conversation_history

    if request.clear_history:
        conversation_history = []

    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": request.message
    })

    # Build prompt with history (keep last 10 exchanges for context)
    messages = conversation_history[-20:]  # 10 exchanges = 20 messages

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": 256,  # Keep responses conversational length
                    "temperature": 0.7
                }
            },
            timeout=120  # 2 min timeout for slower responses
        )
        response.raise_for_status()

        result = response.json()
        assistant_message = result.get("message", {}).get("content", "")

        if not assistant_message:
            raise HTTPException(status_code=500, detail="Empty response from model")

        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return ChatResponse(response=assistant_message)

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Model took too long to respond")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
async def clear_history():
    """Clear conversation history."""
    global conversation_history
    conversation_history = []
    return {"status": "cleared"}

@app.get("/health")
async def health():
    """Health check."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        ollama_ok = r.status_code == 200
    except:
        ollama_ok = False

    return {
        "status": "ok",
        "ollama": ollama_ok,
        "model": MODEL
    }

# Serve static files (frontend)
static_dir = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    print("Planty Voice Server starting...")
    print(f"   Model: {MODEL}")
    print(f"   Ollama: {OLLAMA_URL}")
    print(f"   Open http://localhost:8093 in browser")
    uvicorn.run(app, host="0.0.0.0", port=8093)
