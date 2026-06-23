---
name: hermes-cron-jobs
description: Patterns, pitfalls, and debugging workflows for Hermes cron jobs. Covers LLM-driven vs no_agent modes, toolset requirements for state persistence, delivery mechanisms, and scheduler quirks.
category: devops
---

# Hermes Cron Jobs — Patterns & Pitfalls

## Two Execution Modes

| Mode | `no_agent` | Use when |
|------|------------|----------|
| **LLM-driven** (default) | `false` | Need reasoning, conditional logic, formatting, multi-step decisions |
| **Script-only** | `true` | Deterministic probes, watchdogs, fixed-output tasks, reliable scheduling |

### LLM-driven (`no_agent: false`)
- Loads an LLM each tick with the prompt + enabled toolsets
- **Delivers stdout to chat** (works reliably)
- **Scheduler quirk**: Jobs with extra toolsets beyond the default (e.g., `terminal` + `homeassistant`) may fail to run on schedule — observed in testing
- State **does not persist** between runs unless written to disk (file, DB, HA entity)

### Script-only (`no_agent: true`)
- Runs a Python/Shell script directly — no LLM tokens
- **Reliably runs on schedule** (every minute if `* * * * *`)
- **Delivery bug**: `stdout` from `no_agent=true` scripts does **not** deliver to chat (`origin` or `telegram`) — observed in testing, status shows `ok` but no message appears
- Can import `hermes_tools` (HA, terminal, etc.) in the cron runtime environment
- Script **must** emit output for delivery; empty stdout = silent (watchdog pattern)

## State Persistence — The Critical Pattern

**LLM-driven jobs cannot remember anything between runs.** Each tick is a fresh prompt.

To achieve "once per day" or "once per condition":
1. **Write a marker file to disk** (e.g., `/tmp/job-name-$(date +%F).marker`)
2. **Check it at start** — if exists, exit silently
3. **Require `terminal` toolset** to run `test -f` / `touch`

Without `terminal` toolset, an LLM-driven job **will spam every minute** when its condition is true.

## Toolset Requirements

| Need | Toolset |
|------|---------|
| Read HA entity state | `homeassistant` |
| Create/check marker files on disk | `terminal` |
| Run shell commands | `terminal` |
| Web search/API calls | `web` |
| File read/write | `file` |

## Delivery Targets

| `deliver` value | Behavior |
|-----------------|----------|
| `origin` (default) | Current chat/topic — works for LLM-driven |
| `telegram` | Explicit Telegram — works for LLM-driven |
| `local` | Save only, no delivery |
| `platform:chat_id:thread_id` | Specific destination |

**Observed**: `no_agent=true` + `deliver: telegram` shows `last_status: ok` but **no message arrives**.

## Debugging Workflow

1. **Check job list** — `cronjob list` to see `last_run_at`, `last_status`, `next_run_at`
2. **Manual run** — `cronjob run <job_id>` (may not update `last_run_at` for LLM-driven)
3. **Wait for scheduled tick** — `last_run_at` only updates on scheduler tick
4. **Add explicit logging** — output timestamp + state for verification
5. **Test marker logic manually** — `test -f /path && echo exists`

## Common Pitfalls

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Spams every minute | Missing `terminal` toolset + no marker persistence | Add `terminal`, write marker file |
| Job never runs on schedule | LLM-driven + extra toolsets (`terminal` + `homeassistant`) | Use `no_agent=true` script or minimal toolsets |
| `no_agent=true` runs but no output | Delivery bug for script mode | Use LLM-driven for user-facing output |
| `last_run_at` stuck | Manual `run` doesn't count; only scheduler ticks | Wait for next cron minute |

## Working Patterns

### Once-per-day LLM-driven (requires `terminal`)
```yaml
enabled_toolsets: ["homeassistant", "terminal"]
prompt: |
  1. terminal: test -f /tmp/job-$(date +%F).marker → if exit 0, exit silently
  2. homeassistant: get entity state
  3. if condition met: terminal: touch /tmp/job-$(date +%F).marker, output notification
```

### Reliable scheduled probe (`no_agent=true`)
```yaml
no_agent: true
script: probe.py
# probe.py uses hermes_tools, prints only when action needed
deliver: local  # or handle notification inside script via webhook
```

### HA Automation → Webhook (Recommended for User Notifications)
The user's **actual pill reminder** works via:
- HA automation triggers on Shield `playing`/`on` 09:00-11:59
- Calls Hermes webhook (`shell_command` → python script)
- Uses `input_boolean.pill_reminder_sent_today` as daily guard (resets at midnight)
- **This is more reliable than cron** for state-change notifications

## References
- `references/cron-debugging-session.md` — Full session transcript: test pill reminder spam, mode comparison, delivery bugs
- `references/scheduler-quirks.md` — Observed scheduler behaviors (LLM-driven + terminal toolset not scheduling, no_agent delivery bug)

## Templates
- `templates/once-per-day-llm-driven.yaml` — Cron job config for LLM-driven daily marker pattern (requires `terminal` toolset)
- `templates/reliable-probe-no-agent.py` — Python script template for `no_agent=true` probes (uses `hermes_tools`, emits only on trigger)

## Scripts
- `scripts/verify-cron-marker.sh` — Quick marker file check: `./verify-cron-marker.sh job-name`