---
name: home-assistant-token-and-401-troubleshooting
description: "Home Assistant long-lived token setup + 401 root-cause checks and HA-side fixes."
version: 1.0.0
metadata:
  hermes:
    tags: [smart-home, home-assistant, auth, http]
---

# Home Assistant Token and 401 Troubleshooting

Use this when:
- You have a known-working HA host/port but all auth attempts return 401,
- You need to set or persist a long-lived access token,
- The HA `ban` integration is active or suspected.

## Token requirements
- Must be a **long-lived access token** from HA (Profile → Security → Long-Lived Access Tokens).
- Must be the latest active token printed here; do not use partial or older placeholders.
- If this session’s token comes back as a memory entry, treat that truncated string as a reference, not as a verified live token.

## Response checks
Run these from the same source IP used by Hermes, then share the exact output:

```
curl -s -o /tmp/ha_body.bin -w '%{http_code}\\n' -H 'Authorization: Bearer <TOKEN>' <HA_URL>/api/ && tail -c 400 /tmp/ha_body.bin

curl -si <HA_URL>/ | head -n 10
```

## 401 diagnosis order
1. Token is wrong/expired/profile-mismatched → generate a new long-lived token from HA UI.
2. IP is banned by `homeassistant.components.http.ban` in HA logs → restart HA or temporarily disable the `ban` integration.
3. Wrong URL/port/proxy or IPv6 vs IPv4 mismatch → verify HA is reachable from the Hermes host at the same address used in tokens/config.
4. Authorization config changed (HA >2025 often defaults to OAuth-style enforcement) → ensure legacy long-lived tokens are still enabled in HA and the given token matches the current user.

## Persisting the token
After verifying a working token, save it once and avoid duplicates:
1. Store a single compact memory entry for the current token.
2. Ensure `HASS_TOKEN` is available to Hermes before making HA calls.

## Pitfalls
- **Never overwrite a valid token with a placeholder or truncated value.** A failed write, interrupted here-doc, or accidental replacement with `...` can corrupt the stored token. Always verify the on-disk token matches the exact verified full string, and prefer append-only or reload-from-source flows when refreshing credentials.

## Escalation or full reset
If a confirmed-bad token cannot be replaced, take action:
1. Remove or redact active token entries from `fact_store` and memory stores.
2. Remove the `HASS_TOKEN` entry from `~/.hermes/.env`.
3. Prompt user to paste a fresh long-lived access token.

## HA secret hygiene
- After a confirmed-bad token, scrub these stores of HA token and entity data:
  - `fact_store` entries containing `Home Assistant` / token
  - `~/.hermes/memories/MEMORY.md` and `USER.md`
  - `~/.hermes/.env` `HASS_TOKEN` and optional `HASS_URL`
  - For backup mirrors such as `~/Hermes/.../backup/memories/MEMORY.md`, remove any HA token or entity secrets the user explicitly wants purged.
- Preserve only non-sensitive notes (for example, restore guide references) when possible.
