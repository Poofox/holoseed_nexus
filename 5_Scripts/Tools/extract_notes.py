import re
import json
import os

path = r'C:\Users\foxAsteria\Downloads\colornote-decrypted.raw'

with open(path, 'rb') as f:
    data = f.read()

text = data.decode('utf-8', errors='ignore')

# Remove null bytes and other control chars
clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

# Find JSON objects - looking for note structures
# ColorNote format has _id, title, note, created_date, etc.
pattern = r'\{"_id":\d+.*?"note":".*?".*?\}'

matches = re.findall(pattern, clean, re.DOTALL)
print(f"Found {len(matches)} raw matches")

# Try to parse and extract actual notes
notes = []
for m in matches:
    try:
        # The match might have extra stuff, try to parse
        obj = json.loads(m)
        if 'note' in obj or 'title' in obj:
            notes.append(obj)
    except json.JSONDecodeError:
        # Try to find just the first complete JSON object
        try:
            # Find balanced braces
            depth = 0
            end = 0
            for i, c in enumerate(m):
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            if end > 0:
                obj = json.loads(m[:end])
                if 'note' in obj:
                    notes.append(obj)
        except:
            pass

print(f"Successfully parsed {len(notes)} notes")

# Save to file
output_path = r'C:\Users\foxAsteria\Downloads\colornote-notes-extracted.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(notes, f, indent=2, ensure_ascii=False)

print(f"Saved to {output_path}")

# Print first few notes
for i, note in enumerate(notes[:10]):
    print(f"\n=== Note {i+1} ===")
    title = note.get('title', '(no title)')
    content = note.get('note', '')[:200]
    print(f"Title: {title}")
    print(f"Content: {content}...")
