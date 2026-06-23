# Cron Debugging Session — Test Pill Reminder (2026-06-17)

## Goal
Create a test duplicate of the pill reminder cron job running 15:00–22:00 to verify behavior without affecting production.

## Original Job (Production)
- **ID**: `1ec54427a168`
- **Schedule**: `* 9-11 * * *` (every minute 9–11 AM)
- **Toolsets**: `homeassistant` only
- **Model**: `stepfun/step-3.7-flash:free` / `nous`
- **Delivery**: `telegram`
- **Flaw**: No `terminal` toolset → cannot persist daily marker → **spams every minute** when Shield is `playing`/`on`

## Test Attempts

| Attempt | Mode | Toolsets | Schedule | Result |
|---------|------|----------|----------|--------|
| 1 | LLM-driven | `homeassistant` | `* 15-22 * * *` | **Spammed every minute** (no marker persistence) |
| 2 | LLM-driven | `homeassistant` + `terminal` | `* 15-22 * * *` | **Never ran on schedule** (scheduler quirk) |
| 3 | `no_agent=true` | Python script | `* 15-22 * * *` | Ran every minute, status `ok`, **no delivery to chat** |
| 4 | LLM-driven | `homeassistant` + `terminal` (no model) | `* 15-22 * * *` | Never ran on schedule |

## Key Findings

### 1. LLM-driven + `terminal` toolset breaks scheduler
Jobs with `enabled_toolsets: ["homeassistant", "terminal"]` and no explicit model **do not run on schedule**. The first test job (only `homeassistant`) ran at 16:00. Adding `terminal` stopped scheduled execution.

### 2. `no_agent=true` delivery bug
Script runs (status `ok`, `last_run_at` updates every minute) but **stdout never delivers** to `origin` or `telegram`. Manual `send_message` works fine.

### 3. Manual `cronjob run` ≠ scheduled run
- Does not update `last_run_at` for LLM-driven jobs
- Does not trigger delivery for `no_agent=true`
- Only scheduler ticks produce real runs with delivery

### 4. Marker file pattern works — but needs `terminal`
```bash
# Check
test -f /tmp/pill-reminder-test-$(date +%F).marker
# Create
touch /tmp/pill-reminder-test-$(date +%F).marker
```
This pattern **works** when the LLM has `terminal` toolset and the job actually runs.

## Root Cause of Original Job Spam
The production cron job (`1ec54427a168`) has **only `homeassistant` toolset**. It cannot create/check marker files on disk. Each minute it runs, sees Shield is `playing`, sends notification, forgets. **It would spam every minute 9–11 AM when Shield is on.**

## Actual Working Pill Reminder
The user's **real** pill reminder uses **HA Automation → Hermes Webhook**:
- Trigger: Shield `playing`/`on` 09:00–11:59
- Action: `shell_command` → Python script → Hermes webhook `100.81.31.58:8644/webhooks/pill-reminder`
- Daily guard: `input_boolean.pill_reminder_sent_today` (resets at midnight)
- **This is the correct pattern** for state-change notifications

## Recommendation
- **Deprecate the cron job** — it's redundant and broken
- **Keep HA automation** as primary
- If cron backup needed: use `no_agent=true` script with explicit webhook call (bypass delivery bug)