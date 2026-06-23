# Telegram Streaming + Rich Messages Duplication

## Symptom

Every agent response appears twice in the Telegram chat — two identical, fully-rendered
message bubbles (with tables, code formatting, etc.) sent back-to-back with the same timestamp.

## Root Cause

When both `streaming: true` and `rich_messages: true` are enabled for the Telegram platform,
the streaming edit messages and the final rich-rendered message can land as separate
Telegram messages rather than one message with inline edits.

Gateway logs show `Suppressing normal final send... final delivery already confirmed
(streamed=True... content_delivered=True)` — the gateway believes it suppressed the
duplicate, but the rich message rendering layer creates a new message anyway.

## Fix

```bash
hermes config set display.platforms.telegram.streaming false
```

Then restart the gateway (must be from outside the gateway process):
```bash
hermes gateway restart
```

Note: `config.yaml` cannot be edited directly by the agent — must use `hermes config`.

## Verification

After restart, check that responses no longer duplicate. The gateway log should still
show `response ready` entries with a single chat ID per response.

## Session Reference

2026-06-20: Alp reported duplicate messages in Telegram group "Agas and wacu" (topic 19).
Messages appeared twice at 4:36 PM and 4:41 PM. Fix applied same session, confirmed working.
