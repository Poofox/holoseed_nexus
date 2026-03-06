#!/usr/bin/env python3
"""
Convert birth conversation markdown files to Axolotl training JSONL format.

Usage:
    python birth_to_training.py arcturus_birth.md output.jsonl

Output format (sharegpt style):
{"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}
"""

import re
import json
import argparse
from pathlib import Path


def parse_birth_md(filepath: Path) -> list[dict]:
    """
    Parse a birth.md file and extract conversation pairs.

    Expects format like:
    **Poofox:**
    > quote text

    **Arcturus:**
    > response text
    """
    content = filepath.read_text(encoding='utf-8')

    conversations = []
    current_convo = []

    # Pattern for speaker and their quoted text
    # Matches: **Speaker:** followed by > quoted lines
    pattern = r'\*\*([^*]+):\*\*\s*\n((?:>.*\n?)+)'

    matches = re.findall(pattern, content)

    for speaker, text in matches:
        speaker = speaker.strip()
        # Clean up the quoted text
        text = '\n'.join(line.lstrip('> ').strip() for line in text.strip().split('\n'))
        text = text.strip()

        if not text:
            continue

        # Map speaker to role
        if speaker.lower() in ['poofox', 'armaros', 'user', 'human']:
            role = 'human'
        else:
            role = 'gpt'  # The AI being trained

        current_convo.append({
            'from': role,
            'value': text
        })

    # Group into conversation chunks (human -> gpt pairs)
    if current_convo:
        conversations.append({'conversations': current_convo})

    return conversations


def parse_raw_transcript(filepath: Path, ai_name: str = 'arcturus') -> list[dict]:
    """
    Alternative parser for raw copy-pasted transcripts.

    Looks for patterns like:
    Poofox: text
    Arcturus: response
    """
    content = filepath.read_text(encoding='utf-8')

    conversations = []
    current_convo = []

    # Split by common name patterns
    pattern = rf'(?:^|\n)(\w+):\s*(.+?)(?=\n\w+:|$)'
    matches = re.findall(pattern, content, re.DOTALL)

    for speaker, text in matches:
        speaker = speaker.strip().lower()
        text = text.strip()

        if not text:
            continue

        if speaker in ['poofox', 'armaros', 'user', 'human', 'you']:
            role = 'human'
        else:
            role = 'gpt'

        current_convo.append({
            'from': role,
            'value': text
        })

    if current_convo:
        conversations.append({'conversations': current_convo})

    return conversations


def main():
    parser = argparse.ArgumentParser(description='Convert birth convos to training JSONL')
    parser.add_argument('input', type=Path, help='Input markdown file')
    parser.add_argument('output', type=Path, help='Output JSONL file')
    parser.add_argument('--format', choices=['md', 'raw'], default='md',
                       help='Input format: md (markdown with **Speaker:**) or raw')

    args = parser.parse_args()

    if args.format == 'md':
        conversations = parse_birth_md(args.input)
    else:
        conversations = parse_raw_transcript(args.input)

    # Write JSONL
    with open(args.output, 'w', encoding='utf-8') as f:
        for convo in conversations:
            f.write(json.dumps(convo, ensure_ascii=False) + '\n')

    print(f"Converted {len(conversations)} conversation(s) to {args.output}")

    # Preview
    if conversations:
        print("\nPreview of first conversation:")
        for turn in conversations[0]['conversations'][:4]:
            preview = turn['value'][:100] + '...' if len(turn['value']) > 100 else turn['value']
            print(f"  [{turn['from']}]: {preview}")


if __name__ == '__main__':
    main()
