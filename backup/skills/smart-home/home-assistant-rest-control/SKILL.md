---
name: home-assistant-rest-control
description: "Control Home Assistant via its REST API: discover entities, call services, and verify state changes."
version: 1.0.0
author: Hermes
tags: [Smart-Home, Home-Assistant, REST, Automation, IoT]
---

# Home Assistant REST Control

Use this skill when the user wants you to interact with a Home Assistant instance directly: list entities, toggle devices, change scenes, inspect states, or verify automations.

## Core workflow

1. Identify the Home Assistant base URL and authentication method.
2. Discover the target entity by querying states when the exact entity_id is unknown.
3. Call the appropriate service endpoint.
4. Verify the result with a follow-up state query.

## Known Entities (Alp's HA at 192.168.1.52)

| Friendly name | entity_id | Notes |
|---|---|---|
| Bird light | `light.kus_isik` | On/off only; can accept 200 but state can remain stuck |
| RGB light | `light.rgb_light` | Supports `rgb_color` parameter |

---

## Common API patterns

- `GET /api/states` — list all entity states
- `GET /api/states/<entity_id>` — inspect one entity
- `POST /api/services/<domain>/<service>` — invoke a service

Typical light toggle example:

- `POST /api/services/light/toggle` with `{"entity_id": "light.kitchen"}`

## Entity discovery tips

When the user gives a nickname like "kus isik" or a rough label:

- Search `friendly_name` and `entity_id` from `/api/states`
- Prefer exact entity_id matches when available
- If multiple candidates match, ask which one only if the target still isn’t clear after inspection

## Verification

After a service call, read the entity state again and report the final state, not just that the API accepted the request.

## Secrets handling

- Keep Home Assistant tokens out of git and shared notes.
- The token must be stored as `HASS_TOKEN=<token>` in `~/.hermes/.env` so it persists across sessions.
- Never echo secrets back to the user.
- To set it: `echo 'HASS_TOKEN=<token>' >> ~/.hermes/.env`

## Token recovery

If `HASS_TOKEN` is missing from `~/.hermes/.env`, try these in order:
1. Search past sessions: `session_search(query="HASS_TOKEN home assistant token eyJ")` — session logs may contain the token verbatim if it was pasted in chat.
2. **Warning**: session DB stores text as-is but may truncate long values shown in snippets. The full token is preserved in the raw DB but snippet display may show `eyJhbG...Ud78`. Use `session_search` with `session_id` + `around_message_id` scroll to get the full user message.
3. If unrecoverable, ask the user to create a new long-lived token in HA: **Profile → Long-Lived Access Tokens → Create Token**.

## Token setup

The HA long-lived access token must be present as `HASS_TOKEN` in `~/.hermes/.env`.
To create one: HA UI → Profile (bottom-left avatar) → **Long-Lived Access Tokens** → Create token.
Then add to `~/.hermes/.env`:
```
HASS_URL=http://192.168.1.52:8123
HASS_TOKEN=<paste token here>
```

If a `401 Unauthorized` is returned, the token is missing, wrong, or not being forwarded. Check:
1. `grep HASS_TOKEN ~/.hermes/.env` — must be present and non-empty.
2. The env file is actually loaded by the running gateway (restart if you just added it).
3. Token hasn't been revoked in HA UI.

> **Caution:** Hermes may mask `HASS_TOKEN` values in terminal output, returning `***` instead of the real token. When reading the token in Python, do shell-parse `~/.hermes/.env` first, or pass it via the environment, so you do not accidentally reuse the masked string `***`. Calling `/api/` with a literal `***` returns `401`, not a 200.

Do NOT search codebase test files or config.yaml for the token — it lives only in `~/.hermes/.env`.

## Pitfalls

- Home Assistant can return `401 Unauthorized` if the token is wrong, expired, or not actually being sent as a Bearer token.
- **Service calls may return `200 OK` but the entity state does not change.** Always verify with a follow-up state readback. If state is unchanged, the device may be unreachable, unresponsive, or stuck — retrying or checking device status is needed. Do not assume the command executed wirelessly.
- Friendly names can be ambiguous; verify with entity_id before acting.
- `HASS_TOKEN` is NOT set by default in `~/.hermes/.env` — it must be explicitly added. Check with `grep HASS_TOKEN ~/.hermes/.env` before trying any API call; save the user a 401 roundtrip.
- Session snippets truncate long tokens (e.g. `eyJhbG...Ud78`) — scroll into the raw session message to get the full value before asking the user to re-paste.
- Do not waste time grepping test files or the hermes-agent source for the token — those are test fixtures, not real credentials.
- `curl`/terminal output may show `HASS_TOKEN=***`, which means the token was masked by Hermes, not that the env var is missing. Do not treat `***` as a valid token or paste it back into requests — it will cause 401s.
- `HTTP 200` from `/api/` in a previous turn does not guarantee the bearer token is still valid. Always pre-check `/api/` with the token in the same execution context; if it returns `401`, stop and recover the token before calling any service endpoint.

## Cron-backed reminder testing

This user validates Home Assistant driven reminders with Hermes cron jobs. When asked to test or verify events such as the pill reminder:

1. Confirm whether the trigger window is active.
2. If outside the window, temporarily create a one-shot or alternate test cron with a different schedule, then restore the original schedule when complete.
3. Manually trigger the underlying entity if needed (e.g. `media_player.android_tv_192_168_1_62`), but never treat a `200 OK` from a service call as success alone.
4. Read back the entity state after the trigger to confirm the event fired as expected.
5. Clean up both temporary config files and temporary test crons after verification.

## Shield reference reminder

This user says "shield" as a possible label reference. The underlying HA entity in this environment may be `media_player.android_tv_192_168_1_62` (friendly_name: Shield). When the user says "shield," check the known reference before guessing other entities.

## Automation Troubleshooting

### Bulk "unavailable" with `"restored": true`

When **multiple automations** show state `unavailable` and their attributes include `"restored": true`, this means **Home Assistant tried to restore them from saved state but failed to load the automation configuration** (usually `automations.yaml`).

**Root causes (in order of likelihood):**
1. **Duplicate `automation:` key in configuration.yaml** — e.g. `automation: !include automations.yaml` followed by a second `automation:` block with inline entries. The second overwrites the first; automations.yaml never loads. This is the #1 cause for this user.
2. **YAML syntax error** in `automations.yaml` — HA fails to parse, aborts loading all automations
2. **File missing or empty** — `automations.yaml` was deleted, moved, or truncated
3. **Invalid automation definition** — missing required fields (trigger, action), malformed condition, or use of removed/renamed integration
4. **Include/merge conflict** — if using `automation: !include automations.yaml` and another include overrides it
5. **HA version incompatibility** — upgrade introduced breaking changes to automation schema

**Diagnosis steps:**
1. Check a single unavailable automation via `GET /api/states/automation.<name>` — confirm `"restored": true`
2. Attempt to load automation config via `GET /api/config/automation/config` — returns `404` if config not loaded
3. **SSH to the HA host and inspect `automations.yaml` directly:**
   - Check file exists and has content
   - Run `yamllint automations.yaml` or `python3 -c "import yaml; yaml.safe_load(open('automations.yaml'))"` to validate syntax
   - Look for recent edits (timestamps, git history if tracked)
4. Check HA logs: `grep -i automation /config/home-assistant.log` — look for parse errors at startup

**Recovery:**
- Fix the YAML syntax error
- Restore from backup if file was corrupted
- Reload automations: `POST /api/services/automation/reload` (if config is now valid)
- Or restart HA completely

**Note:** This is a **config load failure**, not an entity communication issue. The automations themselves are fine — HA just can't read their definitions. Do NOT delete or recreate automations; fix the source file and reload.

## Reference files

- See `references/rest-api.md` for a compact API cheat sheet and the discovery/toggle pattern used in this session.
- See `references/automation-troubleshooting.md` for diagnosing bulk automation failures (unavailable + restored: true).
