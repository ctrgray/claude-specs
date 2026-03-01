#!/usr/bin/env python3
import json
import re
import subprocess
import sys

MATCH_PHRASES = re.compile(
    r"notify me when (done|finished|complete)"
    r"notify when (done|finished|complete)"
    re.IGNORECASE,
)

data = json.load(sys.stdin)
transcript_path = data.get("transcript_path", "")

try:
    with open(transcript_path) as f:
        lines = f.readlines()
except (OSError, TypeError):
    sys.exit(0)

for line in lines:
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        continue
    # Only check user messages
    if entry.get("type") != "user":
        continue
    content = entry.get("message", {}).get("content", "")
    if isinstance(content, list):
        content = " ".join(
            block.get("text", "") for block in content if isinstance(block, dict)
        )
    if MATCH_PHRASES.search(content):
        subprocess.run([
            "osascript", "-e",
            'display notification "Claude is done" with title "Claude Code" sound name "default"',
        ])
        sys.exit(0)
