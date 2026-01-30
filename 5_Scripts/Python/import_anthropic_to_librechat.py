#!/usr/bin/env python3
"""
Import Anthropic Claude Desktop export into LibreChat MongoDB
Usage: python import_anthropic_to_librechat.py
"""

import json
import subprocess
from datetime import datetime
import uuid
import sys
import os

# Config
ANTHROPIC_EXPORT = r"C:\Users\foxAsteria\files\holoseed_nexus\Archive\AnthropicExport\conversations.json"
LIBRECHAT_USER_ID = "697b1aa736b3384927ec9782"
MONGO_CONTAINER = "chat-mongodb"
MONGO_DB = "LibreChat"

def generate_object_id():
    """Generate a UUID for document ID"""
    return str(uuid.uuid4())

def parse_iso_date(date_str):
    """Convert ISO date string to MongoDB ISODate format"""
    if not date_str:
        return datetime.utcnow().isoformat() + "Z"
    # Already in ISO format, just ensure Z suffix
    if not date_str.endswith("Z"):
        date_str = date_str + "Z"
    return date_str

def convert_conversation(conv, user_id):
    """Convert Anthropic conversation to LibreChat format"""
    conv_id = conv.get("uuid", generate_object_id())
    created_at = parse_iso_date(conv.get("created_at"))
    updated_at = parse_iso_date(conv.get("updated_at"))

    # Convert messages
    messages = []
    message_ids = []
    parent_id = "00000000-0000-0000-0000-000000000000"

    for msg in conv.get("chat_messages", []):
        msg_id = msg.get("uuid", generate_object_id())
        message_ids.append(msg_id)

        # Extract text - prefer 'text' field, fall back to content
        text = msg.get("text", "")
        if not text and msg.get("content"):
            content = msg.get("content", [])
            if content and isinstance(content, list) and len(content) > 0:
                text = content[0].get("text", "")

        is_human = msg.get("sender") == "human"

        message_doc = {
            "messageId": msg_id,
            "user": user_id,
            "conversationId": conv_id,
            "text": text,
            "sender": "User" if is_human else "Claude (Imported)",
            "isCreatedByUser": is_human,
            "parentMessageId": parent_id,
            "endpoint": "anthropic",
            "model": "claude-desktop-import",
            "error": False,
            "unfinished": False,
            "tokenCount": len(text.split()),  # rough estimate
            "createdAt": parse_iso_date(msg.get("created_at")),
            "updatedAt": parse_iso_date(msg.get("updated_at")),
            "_meiliIndex": True,
            "__v": 0
        }
        messages.append(message_doc)
        parent_id = msg_id

    # Create conversation document
    conversation_doc = {
        "conversationId": conv_id,
        "user": user_id,
        "title": conv.get("name", "Imported Conversation")[:100],
        "endpoint": "anthropic",
        "endpointType": "anthropic",
        "model": "claude-desktop-import",
        "messages": message_ids,
        "files": [],
        "tags": ["imported", "claude-desktop"],
        "isArchived": False,
        "createdAt": created_at,
        "updatedAt": updated_at,
        "_meiliIndex": True,
        "__v": 0
    }

    return conversation_doc, messages

def mongo_insert(collection, doc):
    """Insert document into MongoDB via docker exec"""
    # Escape the JSON for shell
    doc_json = json.dumps(doc).replace("'", "\\'").replace('"', '\\"')

    cmd = f'''docker.exe exec {MONGO_CONTAINER} mongosh {MONGO_DB} --eval "db.{collection}.insertOne({json.dumps(doc)})"'''

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error inserting into {collection}: {result.stderr}")
        return False
    return True

def bulk_import():
    """Main import function"""
    print(f"Loading Anthropic export from: {ANTHROPIC_EXPORT}")

    with open(ANTHROPIC_EXPORT, 'r', encoding='utf-8') as f:
        convos = json.load(f)

    print(f"Found {len(convos)} conversations to import")

    # Prepare bulk insert documents
    all_convos = []
    all_messages = []

    for i, conv in enumerate(convos):
        conv_doc, msg_docs = convert_conversation(conv, LIBRECHAT_USER_ID)
        all_convos.append(conv_doc)
        all_messages.extend(msg_docs)

        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(convos)} conversations...")

    print(f"\nTotal: {len(all_convos)} conversations, {len(all_messages)} messages")

    # Write to temp files for bulk import
    convos_file = "/tmp/import_convos.json"
    msgs_file = "/tmp/import_msgs.json"

    # Save to Windows temp that Docker can access
    import tempfile
    import os

    temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), 'librechat_import')
    os.makedirs(temp_dir, exist_ok=True)

    convos_file = os.path.join(temp_dir, 'convos.json')
    msgs_file = os.path.join(temp_dir, 'msgs.json')

    with open(convos_file, 'w', encoding='utf-8') as f:
        json.dump(all_convos, f)

    with open(msgs_file, 'w', encoding='utf-8') as f:
        json.dump(all_messages, f)

    print(f"\nSaved to:\n  {convos_file}\n  {msgs_file}")
    print("\nNow inserting into MongoDB...")

    # Copy files to container and import
    # First copy to container
    subprocess.run(f'docker.exe cp "{convos_file}" {MONGO_CONTAINER}:/tmp/convos.json', shell=True)
    subprocess.run(f'docker.exe cp "{msgs_file}" {MONGO_CONTAINER}:/tmp/msgs.json', shell=True)

    # Import using mongoimport
    print("Importing conversations...")
    result = subprocess.run(
        f'docker.exe exec {MONGO_CONTAINER} mongoimport --db {MONGO_DB} --collection conversations --file /tmp/convos.json --jsonArray',
        shell=True, capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("Importing messages...")
    result = subprocess.run(
        f'docker.exe exec {MONGO_CONTAINER} mongoimport --db {MONGO_DB} --collection messages --file /tmp/msgs.json --jsonArray',
        shell=True, capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("\nDone! Refresh LibreChat to see imported conversations.")

if __name__ == "__main__":
    bulk_import()
