#!/usr/bin/env python3
import json
import re
import subprocess
import sys

MATCH_PHRASES = re.compile(
    r"notify me"
    r"|notify( me)? when (done|finished|complete)"
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

last_user_text = ""
last_assistant_text = ""

for line in lines:
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        continue

    if entry.get("type") == "user":
        content = entry.get("message", {}).get("content", "")
        if isinstance(content, list):
            if content and all(block.get("type") == "tool_result" for block in content if isinstance(block, dict)):
                continue
            content = " ".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            )
        if content and content.strip():
            last_user_text = content.strip()

    elif entry.get("type") == "assistant":
        content = entry.get("message", {}).get("content", "")
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
            )
        stripped = content.strip()
        if stripped:
            last_assistant_text = stripped

if not MATCH_PHRASES.search(last_user_text):
    sys.exit(0)

if "message" in data:
    # Notification hook: message provided directly
    summary = data["message"]
elif "tool_name" in data:
    # PermissionRequest hook: Claude needs approval for a tool
    summary = f"Permission needed: {data['tool_name']}"
else:
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=30,
            messages=[{
                "role": "user",
                "content": f"Summarize what was accomplished in 5-10 words (no punctuation, just the words):\n\n{last_assistant_text[:500]}"
            }]
        )
        summary = response.content[0].text.strip()
    except Exception:
        words = re.findall(r"[a-zA-Z0-9]+", last_assistant_text)
        summary = " ".join(words[:3]) if words else "Done"

safe_summary = summary.replace("\\", "\\\\").replace('"', '\\"')
subprocess.run([
    "osascript", "-e",
    f'display notification "{safe_summary}" with title "Claude Code" sound name "default"',
])
