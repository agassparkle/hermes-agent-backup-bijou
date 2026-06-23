# Pill Reminder — Current Setup (2026-06-20)

## Architecture

```
HA automations.yaml (2 automations)
  pill_reminder_reset_daily — midnight reset of input_boolean
  pill_reminder_shield_active_09_12 — Shield playing/on 09:00-12:00
    → shell_command.pill_reminder_webhook
    → /config/python_scripts/pill_reminder.py
    → Hermes webhook pill-reminder2 (HMAC-SHA256, X-Webhook-Signature)
    → Telegram 💊
```

## HA configuration.yaml additions

```yaml
input_boolean:
  pill_reminder_sent_today:
    name: "Pill Reminder Sent Today"
    initial: false
    icon: "mdi:pill"

shell_command:
  pill_reminder_webhook: "python3 /config/python_scripts/pill_reminder.py"
```

## HA automations.yaml additions

```yaml
- alias: "Pill Reminder - Reset Daily Flag"
  id: pill_reminder_reset_daily
  trigger:
    - platform: time
      at: "00:00:00"
  action:
    - service: input_boolean.turn_off
      target:
        entity_id: input_boolean.pill_reminder_sent_today
  mode: single

- alias: "Pill Reminder - Shield Active (09-12)"
  id: pill_reminder_shield_active
  trigger:
    - platform: state
      entity_id: media_player.android_tv_192_168_1_62
      to: "playing"
      id: "shield_playing"
    - platform: state
      entity_id: media_player.android_tv_192_168_1_62
      to: "on"
      id: "shield_on"
  condition:
    - condition: time
      after: "09:00:00"
      before: "12:00:00"
    - condition: state
      entity_id: input_boolean.pill_reminder_sent_today
      state: "off"
  action:
    - service: input_boolean.turn_on
      target:
        entity_id: input_boolean.pill_reminder_sent_today
    - service: shell_command.pill_reminder_webhook
  mode: single
```

## Python script: /config/python_scripts/pill_reminder.py

```python
import hmac, hashlib, json, sys, urllib.request

URL = "http://192.168.1.51:8644/webhooks/pill-reminder2"
SECRET = b"pill-secret-123"
PAYLOAD = b"{}"

sig = hmac.new(SECRET, PAYLOAD, hashlib.sha256).hexdigest()

req = urllib.request.Request(
    URL, data=PAYLOAD,
    headers={
        "Content-Type": "application/json",
        "X-Webhook-Signature": sig,
    }, method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print(r.read().decode())
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
```

## Hermes webhook

```bash
hermes webhook subscribe pill-reminder2 \
  --prompt "Send this exact pill reminder: 💊 Pill reminder: time to take your pill." \
  --deliver telegram \
  --deliver-chat-id 7018493241 \
  --secret "pill-secret-123" \
  --deliver-only
```

## Key gotchas

1. **Duplicate `automation:` keys**: If `configuration.yaml` has `automation: !include automations.yaml`, adding inline `automation:` entries creates a duplicate key that overwrites the include — all automations go unavailable. Fix: put new automations in `automations.yaml`.
2. **`shell_command:` restart**: New shell commands require a full HA restart — YAML reload is not sufficient.
3. **Header name**: Must be `X-Webhook-Signature` (not `X-Hermes-Signature`).
4. **HMAC required**: Hermes webhooks always require HMAC-SHA256. The `notify` REST platform approach does NOT work because it can't compute dynamic HMAC headers.
5. **Network**: HA at 192.168.1.52, Hermes at 192.168.1.51 (same LAN). Script uses LAN IP, not Tailscale IP (100.81.31.58 may not be reachable from the Hermes host itself).
6. **Body bytes**: `payload = b"{}"` (bytes) — string `"{}"` produces different HMAC.
