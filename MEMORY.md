# Project Memory

## Project Purpose
This repo (`claude-specs`) stores Claude Code configuration, hooks, and agents.

## Key Files
- `CLAUDE.md` — auto-loaded project instructions (imports this file)
- `.claude/hooks/notify.py` — notification hook (Stop, Notification, PermissionRequest)
- `.claude/settings.local.json` — registers hooks and permissions
- `.claude/agents/simplifier.md` — simplifier subagent definition

## Notification Hook (`notify.py`)
Handles three Claude Code hook events and sends macOS notifications when triggered.

**Hook events handled:**
- `Stop` — fires when a session ends cleanly (NOT on user interrupts)
- `Notification` — fires when Claude sends a notification; payload has `message`
- `PermissionRequest` — fires when Claude needs tool approval; payload has `tool_name`

**Behavior:**
- Reads the session transcript (`.jsonl`) from `transcript_path` in hook input
- Checks **only the most recent user message** for notification-intent phrases
- Exits silently if no match phrase found (never accumulates across the session)
- Match phrases: "notify me", "notify (me) when done/finished/complete", "let me know when done/finished/complete", "send (me) (a) notification"
- For Notification hook: uses `data["message"]` as summary directly
- For PermissionRequest: summary is `f"Permission needed: {data['tool_name']}"`
- For Stop: calls `claude-haiku-4-5-20251001` to generate a 5-10 word summary; falls back to first 3 words of last assistant message
- Sends notification via `osascript` with title "Claude Code"

**Branch:** `add_notifications_hook` — all commits pushed

## Agents
- `simplifier.md` — strengthened to emphasize NEVER changing behavior, only how code is written

## Patterns / Decisions
- Hook fires only when match phrase is in the most recent user message — avoids firing on old "notify me" messages from earlier in a transcript
- Tool-result-only user messages are skipped when scanning for the last user text
- Summary uses Haiku for speed/cost; falls back gracefully without crashing
- Stop hook does NOT fire on user interrupts — only clean session ends
- PermissionRequest hook covers the "Claude needs attention" case mid-task
