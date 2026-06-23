---
name: gateway-troubleshooting
description: Diagnose and fix Hermes gateway message delivery issues — flood control, message truncation, streaming failures, and platform-specific quirks.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [gateway, telegram, troubleshooting, delivery, flood-control, streaming]
---

# Gateway Troubleshooting

When messages are truncated, partially delivered, or silently dropped on any
messaging platform, use this diagnostic methodology. Start with log inspection,
then trace the platform adapter's send path to find the exact failure point.

## Trigger Conditions

- User reports incomplete/truncated messages ("the response cuts off mid-sentence")
- Messages display partially then stop (streaming died halfway)
- Gateway logs show delivery errors: flood control, rate limiting, timeouts
- Content that should be visible (tables, long code blocks) is missing

## Diagnostic Methodology

### 1. Inspect Gateway Logs

```bash
# Check for flood control / rate limiting
grep -i "flood\|rate limit\|retry after" ~/.hermes/logs/gateway.log | tail -20

# Check for message delivery failures
grep -i "failed to send\|delivery failed\|message_too_long\|error" ~/.hermes/logs/gateway.log | tail -20

# Check response sizes and delivery confirmation
grep "response ready.*telegram" ~/.hermes/logs/gateway.log | tail -10

# Check for streaming suppression (edit failures)
grep -i "suppressing normal final send\|flood.*backing off\|edit.*disabled" ~/.hermes/logs/gateway.log | tail -10
```

### 2. Classify the Failure

| Pattern in logs | Likely cause | See reference |
|-----------------|-------------|---------------|
| `Flood control exceeded. Retry in N seconds` | Telegram rate limiting → cascading delivery failure | `references/telegram-flood-control.md` |
| `message_too_long` or `too long` | Content exceeds platform limit (Telegram: 4096 UTF-16 units legacy, 32768 chars rich) | Check `MAX_MESSAGE_LENGTH` / `RICH_MESSAGE_MAX_CHARS` in platform adapter |
| `suppressing normal final send` + `streamed=True` | Streaming delivered content but final confirmation was skipped — often normal, not a bug | Verify `content_delivered=True` |
| `Failed to deliver after N retries` | Network or platform outage; all retry attempts exhausted | Check network, platform API status |

### 3. Trace the Platform Send Path

Key files to inspect (Telegram example):

| File | What to look for |
|------|-----------------|
| `gateway/platforms/telegram.py` | `send()` method (~line 2216), `MAX_MESSAGE_LENGTH`, `_SPLIT_THRESHOLD`, rich message path |
| `gateway/stream_consumer.py` | `_MAX_FLOOD_STRIKES` (line 96), edit backoff logic (~line 1483) |
| `gateway/config.py` | `DEFAULT_STREAMING_EDIT_INTERVAL` (line 386), streaming config |
| `gateway/run.py` | Progress edit interval `_PROGRESS_EDIT_INTERVAL` (~line 13736), final delivery logic |
| `gateway/platforms/base.py` | `truncate_message()` (line 4803), `_send_with_retry()` (line 3416) |

### 4. Apply Fix Based on Classification

**Flood control (most common cause of truncation):**

1. Increase `DEFAULT_STREAMING_EDIT_INTERVAL` in `gateway/config.py` — default 0.8s is right at Telegram's ~1 edit/s limit; 1.5s gives breathing room
2. Raise `_MAX_FLOOD_STRIKES` in `gateway/stream_consumer.py` — default 3 disables edits too quickly; 6 tolerates temporary rate limit bursts
3. Consider disabling streaming entirely for the platform in `config.yaml` under `display.platforms.<platform>.streaming: false` as a last resort

**Message too long:**
- The platform adapter's `truncate_message()` splits content into chunks with `(1/2)` suffixes
- If flood control is active, later chunks may not be delivered
- Fix the flood control first, then verify chunk delivery

**Silent drops:**
- Check `_send_with_retry()` retry logic — flood errors may not be in `_RETRYABLE_ERROR_PATTERNS` and get treated as permanent failures
- Look for `retryable=False` in the platform's `send()` error handling

### 5. Verify the Fix

After applying changes and restarting the gateway:
```bash
# Monitor for flood errors (should be zero or rare)
tail -f ~/.hermes/logs/gateway.log | grep -i flood

# Verify complete delivery
grep "response ready.*platform=telegram" ~/.hermes/logs/gateway.log | tail -5
```

## Gateway Restart

Code changes to the gateway require a restart. **The restart must be done from
outside the gateway process** — Hermes blocks self-restart at the process-ancestry
level. From a separate terminal (SSH, TTY, or another shell):
```bash
hermes gateway restart
```

## Platform-Specific References

- **Telegram flood control**: `references/telegram-flood-control.md` — error patterns, exact code locations, fix parameters, and the cascade failure mechanism
- **Telegram duplicate messages**: `references/telegram-streaming-duplication.md` — when streaming + rich_messages cause messages to appear twice; fix is `hermes config set display.platforms.telegram.streaming false` + gateway restart
