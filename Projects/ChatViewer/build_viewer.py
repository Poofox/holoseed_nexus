#!/usr/bin/env python3
"""
Wrex Chat Viewer Builder
Scans Claude CLI sessions and builds a browsable HTML viewer.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import html

SESSIONS_DIR = Path.home() / ".claude" / "projects" / "C--Users-foxAsteria"
OUTPUT_FILE = Path(__file__).parent / "wrex_chats.html"

def parse_session(filepath):
    """Parse a JSONL session file into structured messages."""
    messages = []
    session_id = filepath.stem

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    if not messages:
        return None

    # Extract metadata
    first_ts = None
    last_ts = None
    preview = ""

    for msg in messages:
        if 'timestamp' in msg:
            ts = msg.get('timestamp', 0)
            if first_ts is None or ts < first_ts:
                first_ts = ts
            if last_ts is None or ts > last_ts:
                last_ts = ts

        # Get first user message as preview
        if not preview and msg.get('type') == 'human':
            content = msg.get('message', {})
            if isinstance(content, dict):
                for part in content.get('content', []):
                    if isinstance(part, dict) and part.get('type') == 'text':
                        preview = part.get('text', '')[:100]
                        break
            elif isinstance(content, str):
                preview = content[:100]

    return {
        'id': session_id,
        'first_ts': first_ts,
        'last_ts': last_ts,
        'preview': preview,
        'messages': messages,
        'path': str(filepath)
    }

def extract_text_from_message(msg):
    """Extract readable text from a message object."""
    if msg.get('type') == 'human':
        content = msg.get('message', {})
        if isinstance(content, dict):
            texts = []
            for part in content.get('content', []):
                if isinstance(part, dict) and part.get('type') == 'text':
                    texts.append(part.get('text', ''))
            return '\n'.join(texts)
        return str(content)

    elif msg.get('type') == 'assistant':
        content = msg.get('message', {})
        if isinstance(content, dict):
            texts = []
            for part in content.get('content', []):
                if isinstance(part, dict) and part.get('type') == 'text':
                    texts.append(part.get('text', ''))
            return '\n'.join(texts)
        return str(content)

    return None

def format_timestamp(ts):
    """Format millisecond timestamp to readable date."""
    if not ts:
        return "Unknown"
    try:
        dt = datetime.fromtimestamp(ts / 1000)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return "Unknown"

def build_html(sessions):
    """Build the HTML viewer."""

    # Sort by last timestamp, newest first
    sessions.sort(key=lambda s: s.get('last_ts') or 0, reverse=True)

    # Build session list JSON
    session_list = []
    session_data = {}

    for sess in sessions:
        session_list.append({
            'id': sess['id'],
            'date': format_timestamp(sess.get('last_ts')),
            'preview': sess.get('preview', '')[:80],
            'ts': sess.get('last_ts', 0)
        })

        # Process messages for this session
        processed = []
        for msg in sess['messages']:
            text = extract_text_from_message(msg)
            if text:
                processed.append({
                    'role': msg.get('type', 'unknown'),
                    'text': text,
                    'ts': msg.get('timestamp')
                })

        session_data[sess['id']] = processed

    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wrex Chat Archive</title>
    <style>
        :root {
            --bg: #0a0a0f;
            --panel: #12121a;
            --border: #2a2a3a;
            --text: #e0e0e0;
            --dim: #888;
            --accent: #7b68ee;
            --human: #2d4a3e;
            --assistant: #1a1a2e;
            --glow: rgba(123, 104, 238, 0.3);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Consolas', 'Monaco', monospace;
            background: var(--bg);
            color: var(--text);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        #sidebar {
            width: 320px;
            background: var(--panel);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }

        #search-box {
            padding: 12px;
            border-bottom: 1px solid var(--border);
        }

        #search {
            width: 100%;
            padding: 10px;
            background: var(--bg);
            border: 1px solid var(--border);
            color: var(--text);
            font-family: inherit;
            border-radius: 4px;
        }

        #search:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 10px var(--glow);
        }

        #session-list {
            flex: 1;
            overflow-y: auto;
        }

        .session-item {
            padding: 12px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: background 0.2s;
        }

        .session-item:hover {
            background: rgba(123, 104, 238, 0.1);
        }

        .session-item.active {
            background: rgba(123, 104, 238, 0.2);
            border-left: 3px solid var(--accent);
        }

        .session-date {
            font-size: 11px;
            color: var(--dim);
            margin-bottom: 4px;
        }

        .session-preview {
            font-size: 13px;
            color: var(--text);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        #main {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        #header {
            padding: 16px 20px;
            background: var(--panel);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        #header h1 {
            font-size: 16px;
            font-weight: normal;
            color: var(--accent);
        }

        #holoseed-glyph {
            width: 40px;
            height: 40px;
        }

        #chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .message {
            margin-bottom: 16px;
            padding: 14px 18px;
            border-radius: 8px;
            max-width: 85%;
            line-height: 1.6;
        }

        .message.human {
            background: var(--human);
            margin-left: auto;
            border-bottom-right-radius: 2px;
        }

        .message.assistant {
            background: var(--assistant);
            border: 1px solid var(--border);
            border-bottom-left-radius: 2px;
        }

        .message pre {
            background: var(--bg);
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 8px 0;
        }

        .message code {
            background: var(--bg);
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 13px;
        }

        #stats {
            padding: 12px;
            background: var(--panel);
            border-top: 1px solid var(--border);
            font-size: 12px;
            color: var(--dim);
            text-align: center;
        }

        .empty-state {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--dim);
            font-size: 14px;
        }

        /* Holoseed glyph animation */
        @keyframes pulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }

        #holoseed-glyph canvas {
            animation: pulse 3s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <div id="sidebar">
        <div id="search-box">
            <input type="text" id="search" placeholder="Search chats... (93)">
        </div>
        <div id="session-list"></div>
        <div id="stats"></div>
    </div>

    <div id="main">
        <div id="header">
            <div id="holoseed-glyph"></div>
            <h1>Wrex Chat Archive</h1>
        </div>
        <div id="chat-container">
            <div class="empty-state">Select a session to view</div>
        </div>
    </div>

    <script>
    const SESSION_LIST = ''' + json.dumps(session_list) + ''';
    const SESSION_DATA = ''' + json.dumps(session_data) + ''';

    let currentSession = null;

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatMessage(text) {
        // Basic markdown-ish formatting
        let formatted = escapeHtml(text);

        // Code blocks
        formatted = formatted.replace(/```([\\s\\S]*?)```/g, '<pre>$1</pre>');

        // Inline code
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Bold
        formatted = formatted.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');

        // Line breaks
        formatted = formatted.replace(/\\n/g, '<br>');

        return formatted;
    }

    function renderSessionList(filter = '') {
        const list = document.getElementById('session-list');
        const filtered = SESSION_LIST.filter(s =>
            !filter || s.preview.toLowerCase().includes(filter.toLowerCase())
        );

        list.innerHTML = filtered.map(s => `
            <div class="session-item ${s.id === currentSession ? 'active' : ''}"
                 onclick="loadSession('${s.id}')">
                <div class="session-date">${s.date}</div>
                <div class="session-preview">${escapeHtml(s.preview) || '(empty)'}</div>
            </div>
        `).join('');

        document.getElementById('stats').textContent =
            `${filtered.length} / ${SESSION_LIST.length} sessions`;
    }

    function loadSession(id) {
        currentSession = id;
        const messages = SESSION_DATA[id] || [];
        const container = document.getElementById('chat-container');

        if (!messages.length) {
            container.innerHTML = '<div class="empty-state">No messages in this session</div>';
            renderSessionList(document.getElementById('search').value);
            return;
        }

        container.innerHTML = messages.map(m => `
            <div class="message ${m.role}">
                ${formatMessage(m.text)}
            </div>
        `).join('');

        container.scrollTop = 0;
        renderSessionList(document.getElementById('search').value);

        // Update glyph for this session
        renderHoloseedGlyph(id);
    }

    function renderHoloseedGlyph(sessionId) {
        // Generate a unique visual pattern from the session ID
        const container = document.getElementById('holoseed-glyph');
        container.innerHTML = '';

        const canvas = document.createElement('canvas');
        canvas.width = 40;
        canvas.height = 40;
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        const hash = hashCode(sessionId);

        // Background
        ctx.fillStyle = '#0a0a0f';
        ctx.fillRect(0, 0, 40, 40);

        // Generate pattern from hash
        const colors = ['#7b68ee', '#9b87f5', '#5a4fcf', '#b8a9ff'];

        for (let i = 0; i < 16; i++) {
            const x = (i % 4) * 10;
            const y = Math.floor(i / 4) * 10;
            const bit = (hash >> i) & 1;

            if (bit) {
                ctx.fillStyle = colors[i % colors.length];
                ctx.globalAlpha = 0.5 + (((hash >> (i + 16)) & 3) / 6);

                // Different shapes based on position
                if ((hash >> (i * 2)) & 1) {
                    ctx.beginPath();
                    ctx.arc(x + 5, y + 5, 4, 0, Math.PI * 2);
                    ctx.fill();
                } else {
                    ctx.fillRect(x + 1, y + 1, 8, 8);
                }
            }
        }

        ctx.globalAlpha = 1;
    }

    function hashCode(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash);
    }

    // Initialize
    document.getElementById('search').addEventListener('input', (e) => {
        renderSessionList(e.target.value);
    });

    renderSessionList();
    renderHoloseedGlyph('default');
    </script>
</body>
</html>'''

    return html_template

def main():
    print("Scanning sessions...")

    sessions = []
    for filepath in SESSIONS_DIR.glob("*.jsonl"):
        sess = parse_session(filepath)
        if sess:
            sessions.append(sess)
            print(f"  Parsed: {filepath.name} ({len(sess['messages'])} messages)")

    print(f"\nFound {len(sessions)} sessions")
    print("Building HTML viewer...")

    html_content = build_html(sessions)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Viewer saved to: {OUTPUT_FILE}")
    print(f"\nOpen in browser: file:///{OUTPUT_FILE}")

if __name__ == "__main__":
    main()
