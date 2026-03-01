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
            content = " ".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            )
        if MATCH_PHRASES.search(content):
            matched = True

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

# Extract 1-3 word summary from the last assistant message
words = re.sub(r"[^a-zA-Z0-9 ]", " ", last_assistant_text).split()
summary = " ".join(words[:3]) if words else "Done"

subprocess.run([
    "osascript", "-e",
    f'display notification "{summary}" with title "Claude Code" sound name "default"',
])
