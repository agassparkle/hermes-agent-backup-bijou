---
name: home-assistant-hermes-webhooks
description: "Create HA automations that trigger Hermes webhooks for event-driven notifications (Telegram, Discord, etc.) — covers webhook platform setup, signature validation, shell_command scripting, and network connectivity patterns."
version: 1.0.0
author: Hermes
tags: [Smart-Home, Home-Assistant, Hermes, Webhooks, Telegram, Automation, Integration]
---

# Home Assistant + Hermes Webhooks Integration

Use this skill when the user wants **event-driven notifications from Home Assistant to Telegram (or other Hermes platforms) without polling**. This covers the full stack: HA automation → Hermes webhook → platform delivery.

## When to use

- User wants real-time alerts (e.g., "notify me when Shield starts playing between 9-12")
- Polling cron jobs are too slow, spammy, or wasteful
- Notification must go through Hermes (not HA's native notify services)
- Need once-per-day deduplication, time windows, or complex conditions

## Architecture

```
HA Automation (state trigger + time condition + template dedupe)
    → shell_command (Python script)
    → Hermes webhook endpoint (port 8644)
    → Hermes gateway platform (telegram/direct delivery)
    → Telegram chat
```

## Core components

### 1. Hermes webhook platform enablement

Add to `~/.hermes/config.yaml` under top-level `platforms:` (alongside `telegram:`, `discord:`):

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8644
      secret: "your-global-hmac-secret"
```

Then restart gateway: `pkill -f "hermes_cli.*gateway run" && hermes gateway run &`

### 2. Create webhook subscription

```bash
hermes webhook subscribe <name> \
  --prompt "Exact message template to deliver" \
  --deliver telegram \
  --deliver-chat-id <chat_id> \
  --secret <route-secret> \
  --deliver-only
```

- `--deliver-only` = zero LLM cost, direct template rendering
- Returns `URL: http://localhost:8644/webhooks/<name>` and HMAC secret
- **Every webhook ALWAYS has a secret.** If you omit `--secret`, one is auto-generated. There is no unsigned mode — all webhooks require HMAC signatures.

### 3. Signature validation (CRITICAL)

Hermes expects **`X-Webhook-Signature`** header (NOT `X-Hermes-Signature`).

```python
# Correct header name
headers = {
    "Content-Type": "application/json",
    "X-Webhook-Signature": sig  # hex HMAC-SHA256 of body with route secret
}
```

Secrets are raw strings (not `whsec_` base64). HMAC-SHA256 of raw body bytes.

### 4. HA shell_command script

Create `/config/python_scripts/<name>.py`:

```python
import hmac, hashlib, json, urllib.request, sys

url = "http://<HERMES_HOST>:8644/webhooks/<route-name>"
secret = b"<route-secret>"
payload = b"{}"
sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()
req = urllib.request.Request(url, data=payload,
    headers={"Content-Type": "application/json", "X-Webhook-Signature": sig}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print(r.read().decode())
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
```

In `configuration.yaml`:

```yaml
shell_command:
  <name>: "python3 /config/python_scripts/<name>.py"
```

Use **LAN IP** (`192.168.1.x`) if HA and Hermes on same network. Tailscale IP (`100.x.x.x`) if across tailscale.

### 5. HA automation YAML

**IMPORTANT:** If `configuration.yaml` already has `automation: !include automations.yaml`, add new automations to `automations.yaml` — never add a second `automation:` key to `configuration.yaml`. A second key overwrites the first, making all automations unavailable.

**`shell_command:` reload requirement:** After adding a new `shell_command:` to `configuration.yaml`, you must fully restart Home Assistant. YAML reload (Developer Tools → Reload) does NOT pick up new shell commands.

```yaml
- alias: "<friendly name>"
  trigger:
    - platform: state
      entity_id: <target_entity>
      to: ["playing", "on"]  # or from/to as needed
  condition:
    - condition: time
      after: "09:00:00"
      before: "11:59:59"
    - condition: template
      value_template: "{{ not states('input_boolean.<dedupe_flag>') | bool }}"
  action:
    - service: shell_command.<name>
    - service: input_boolean.turn_on
      target:
        entity_id: input_boolean.<dedupe_flag>
  mode: single
```

Add dedupe flag:

```yaml
input_boolean:
  <dedupe_flag>:
    name: "<description>"
    initial: false
```

Reset at midnight:

```yaml
automation:
  - alias: "Reset <dedupe_flag> daily"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.<dedupe_flag>
    mode: single
```

## Network connectivity patterns

| Scenario | Hermes host IP to use in script |
|----------|--------------------------------|
| HA + Hermes on same LAN | `192.168.1.x` (or `br0` bridge IP) |
| HA on Tailscale, Hermes on Tailscale | `100.x.x.x` (from `tailscale ip -4`) |
| HA on LAN, Hermes on different network | Public IP or VPN endpoint |

Test from HA host: `curl -X POST http://<IP>:8644/webhook/<name> ...`

## Troubleshooting

### 401 Unauthorized from webhook
- Header must be `X-Webhook-Signature` (not `X-Hermes-Signature`)
- Secret must match exactly the route secret from `hermes webhook subscribe`
- Body must be identical bytes (empty `b"{}"` vs `{}` matters)
- Check gateway logs: `grep webhook ~/.hermes/logs/gateway.log`

### 401 from HA `notify` REST platform
- **This will never work** — the HA REST notify platform cannot compute HMAC-SHA256 signatures. You MUST use `shell_command` + Python script instead. Do not waste time debugging REST platform headers.

### Shell command timeout / empty stdout
- Script must be in `/config/python_scripts/` (HA only allows this path for python)
- Use `python3 /config/python_scripts/script.py` in shell_command
- Add `import sys; print(..., file=sys.stderr)` for error visibility

### "Invalid signature" but secret looks right
- Verify HMAC is SHA256 hex of **raw body bytes**, not JSON string
- `payload = b"{}"` (Python bytes), not `"{}"` (string)
- `secret.encode()` for string secrets, raw bytes if already bytes

### `hermes webhook test` works but HA gets 401
- The CLI test command uses **GitHub-style** validation (`X-Hub-Signature-256: sha256=<hex>`)
- HA scripts must use **Generic** validation (`X-Webhook-Signature: <raw hex>`)
- Both use the **same route secret**, but different header formats
- See `references/webhook-test-vs-manual.md` for details

### HA can't reach Hermes
- Check `ss -tlnp | grep 8644` on Hermes host — must listen on `0.0.0.0:8644`
- Test from HA host: `curl http://<HERMES_IP>:8644/`
- Firewall/UFW may block port 8644

## Pitfalls

- **Duplicate `automation:` keys** — If `configuration.yaml` has `automation: !include automations.yaml` and you add another `automation:` block with inline entries, the second overwrites the first. Result: ALL automations from `automations.yaml` go `unavailable` with `restored: true`. Fix: put new automations IN `automations.yaml`, not inline in `configuration.yaml`. User hit this twice — always check for existing `automation:` keys before adding inline YAML.
- **`shell_command:` requires full HA restart** — YAML reload is NOT sufficient. After adding a `shell_command:` entry, restart HA completely. The Developer Tools → YAML → Reload won't pick it up.
- **Header name is `X-Webhook-Signature`** — this is the #1 cause of 401s
- **(DO NOT USE) HA `notify` REST platform:** Hermes webhooks **always** require HMAC signature validation. Even if you omit `--secret` from `hermes webhook subscribe`, it auto-generates one — there is no unsigned mode. The HA `notify` REST platform only supports static headers and cannot compute HMAC-SHA256 dynamically. **The `shell_command` + Python script approach is the ONLY method that works.** Any HA config using `notify:` with `platform: rest` targeting a Hermes webhook will silently fail with `401 Invalid signature`.
- **Never add inline YAML to `automations.yaml`:** A single syntax error in `automations.yaml` prevents Home Assistant from loading **all** automations — every one becomes `unavailable` with `restored: true`, requiring a restore from backup. Instead, place new automations inline under `automation:` in `configuration.yaml` with unique `id:` fields, or use a separate `!include` file. This isolates errors to the new config only.
- Shell commands in HA **cannot use multi-line python** easily — use external script file
- HA shell_command only executes scripts under `/config/python_scripts/` or `/config/shell_scripts/`
- `deliver: telegram` in webhook subscription requires Hermes Telegram platform connected
- Once-per-day dedupe needs `input_boolean` + midnight reset automation
- Webhook URL in HA script must be reachable from HA's network perspective
- Global webhook secret in config.yaml is for Svix-style validation; per-route secret is used for `X-Webhook-Signature`
- **Duplicate `automation:` key destroys all automations**: If `configuration.yaml` already has `automation: !include automations.yaml`, adding a second `automation:` block silently overwrites the first — all automations from `automations.yaml` go `unavailable` with `restored: true`. Always add new automations to `automations.yaml` directly, never inline a second `automation:` key in `configuration.yaml`.
- **`shell_command` needs full HA restart**: Unlike automations and input_booleans (which work with YAML reload), `shell_command:` entries only take effect after a full Home Assistant restart. If the action doesn't appear in Developer Tools → Actions, restart HA.
- **`notify` REST platform can't do HMAC signatures**: The `notify` REST platform only supports static headers. For HMAC-signed webhooks, use `shell_command` + Python script instead.

## Related skills

- `home-assistant-rest-control` — for direct entity control via REST API
- `homeassistant-control` — for light/camera/entity operations
- `hermes-agent` — for Hermes gateway, webhook, cron, platform config

## Reference files

- `references/pill-reminder-working-config-2026-06-20.md` — definitive end-to-end working pill reminder config (Python script + HA YAML + verification)
- `references/webhook-test-vs-manual.md` — explains why `hermes webhook test` uses different header format than manual POSTs
- `references/pill-reminder-session-2026-06-16.md` — original session artifacts from first implementation