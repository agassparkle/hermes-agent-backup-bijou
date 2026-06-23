# Memory → Vault Migration

When Hermes persistent memory fills up (80%+), migrate long entries into vault notes.

## When to Migrate

A memory entry is a candidate for vault migration when:
- **Long** (200+ chars) — config details, troubleshooting steps, reference material
- **Server/device/service** → `Directory/machines/`
- **Pitfall, bug, or fix** → `Wiki/`
- **Reference knowledge** (game rules, API specs, auth config) → `Resources/`
- **Automation or workflow** → `Areas/`

## What Stays in Memory

- Short behavioral preferences (1-2 lines)
- Pointers to vault notes: `[[path/to/note]]` format
- Operationally frequent facts (entity IDs, connection patterns)
- Cross-session guardrails ("don't override config defaults")

## Migration Pattern

For each candidate:
1. Create vault note with full detail under the right folder
2. Update folder's `index.md` with a link
3. Replace memory entry with short pointer
4. Commit + push

## Concrete Example (June 2026 — wacu vault)

**Migration stats:**
- Before: 92% full (3,763/4,000 chars), 13 entries
- After: 42% full (1,680/4,000 chars), 12 entries
- Freed: ~2,080 characters

**What moved:**

| Memory Entry | → | Vault Note |
|---|---|---|
| Cloud server IPs, ports, keys (2 servers) | → | `Directory/machines/oracle-foundry.md`, `oracle-hermes.md` |
| Pill reminder full HA config | → | `Areas/home-assistant/pill-reminder.md` |
| Forbidden Lands dice rules | → | `Resources/forbidden-lands-dice.md` |
| Google OAuth config | → | `Resources/google-workspace-oauth.md` |
| Gateway restart rules | → | `Wiki/hermes-gateway-restart.md` |
| HA pitfalls × 2 | → | `Wiki/home-assistant-pitfalls.md` |

**After migration — memory entry example (long → short):**

Before:
> Pill reminder (2026-06-20 rebuilt): HA automations pill_reminder_reset_daily + pill_reminder_shield_active_09_12 in automations.yaml. Shell_command pill_reminder_webhook → /config/python_scripts/pill_reminder.py → Hermes webhook pill-reminder2 (secret pill-secret-123, HMAC-SHA256 X-Webhook-Signature) at http://192.168.1.51:8644/webhooks/pill-reminder2. Once/day via input_boolean.pill_reminder_sent_today...

After:
> Pill reminder: [[Areas/home-assistant/pill-reminder]]. Webhook pill-reminder2, secret pill-secret-123. input_boolean ile günde 1 kere.

Full detail now in `Areas/home-assistant/pill-reminder.md` with architecture diagram, config files table, and pitfalls.

## Checklist

- [ ] Create vault note in correct folder
- [ ] Write full detail (architecture, config, troubleshooting)
- [ ] Update folder `index.md`
- [ ] Replace memory entry with short `[[path]]` pointer
- [ ] Call `memory` with `replace` (not add) to swap the entry
- [ ] Remove any now-redundant secondary entries (e.g., when one vault note covers two old memory entries)
- [ ] Commit + push
