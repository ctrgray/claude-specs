# Project Memory

## Project Purpose
This repo (`claude-specs`) stores Claude Code configuration, hooks, and instructions.

## Key Files
- `CLAUDE.md` — auto-loaded project instructions (imports this file)
- `instructions.md` — early draft of notify hook (superseded)
- `.claude/hooks/notify.py` — the active Stop hook
- `.claude/settings.local.json` — registers the Stop hook and permissions

## Notification Hook (`notify.py`)
A Claude Code `Stop` hook that sends a macOS notification when a session ends.

**Behavior:**
- Reads the session transcript (`.jsonl`) from `transcript_path` in hook input
- Scans user messages for notification-intent phrases ("notify me", "let me know when done", etc.)
- Only fires if a matching phrase was found in the current session
- Calls `claude-haiku-4-5-20251001` to generate a 3-5 word summary of the last assistant message
- Falls back to first 3 words of last assistant message if the API call fails
- Sends notification via `osascript` with title "Claude Code"

**Branch:** `add_notifications_hook` (not yet merged to master)

## Patterns / Decisions
- Hook reads transcript to detect user intent rather than always notifying — avoids noise
- Tool-result-only user messages are skipped when checking for notification phrases
- Summary uses Haiku for speed/cost; falls back gracefully without crashing the hook
