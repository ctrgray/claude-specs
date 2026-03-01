#!/usr/bin/env python3
import json
import re
import subprocess
import sys

MATCH_PHRASES = re.compile(
    r"notify me"
    r"|notify me when (done|finished|complete)"
    r"|notify when (done|finished|complete)"
    r"|let me know when (done|finished|complete)"
    r"|send (me )?(a )?notification",
    re.IGNORECASE,
)

data = json.load(sys.stdin)
transcript_path = data.get("transcript_path", "")

try:
    with open(transcript_path) as f:
        lines = f.readlines()
except (OSError, TypeError):
    sys.exit(0)

matched = False
last_assistant_text = ""

for line in lines:
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        continue

    if entry.get("type") == "user":
        content = entry.get("message", {}).get("content", "")
        if isinstance(content, list):
            # Skip messages that are purely tool results
            if all(block.get("type") == "tool_result" for block in content if isinstance(block, dict)):
                continue
            content = " ".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            )
        if isinstance(content, str) and content.strip():
            matched = bool(MATCH_PHRASES.search(content))

    elif entry.get("type") == "assistant":
        content = entry.get("message", {}).get("content", "")
        if isinstance(content, list):
            texts = [
                block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
            ]
            content = " ".join(texts)
        if content.strip():
            last_assistant_text = content.strip()

if not matched:
    sys.exit(0)

# Generate a 3-5 word summary using Claude
try:
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=20,
        messages=[{
            "role": "user",
            "content": f"Summarize what was accomplished in 3-5 words (no punctuation, just the words):\n\n{last_assistant_text[:500]}"
        }]
    )
    summary = response.content[0].text.strip()
except Exception:
    words = re.sub(r"[^a-zA-Z0-9 ]", " ", last_assistant_text).split()
    summary = " ".join(words[:3]) if words else "Done"

subprocess.run([
    "osascript", "-e",
    f'display notification "{summary}" with title "Claude Code" sound name "default"',
])
