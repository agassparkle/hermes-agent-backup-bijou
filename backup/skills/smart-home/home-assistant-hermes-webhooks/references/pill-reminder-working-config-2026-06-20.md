# Pill Reminder — Working Config (2026-06-20)

This is the definitive working config validated end-to-end.
Previous attempts using `notify` REST platform failed because Hermes webhooks always require HMAC.

## Hermes side

```bash
hermes webhook subscribe pill-reminder2 \
  --prompt "Send this exact pill reminder to Telegram: 💊 Pill reminder: time to take your pill." \
  --deliver telegram \
  --deliver-chat-id 7018493241 \
  --secret "pill-secret-123" \
  --deliver-only
```

Result:
- URL: `http://localhost:8644/webhooks/pill-reminder2`
- Secret: `pill-secret-123`
- Header: `X-Webhook-Signature`

## HA Python script

Place at `/config/python_scripts/pill_reminder.py`:

```python
import hmac, hashlib, json, sys, urllib.request

URL = "http://100.81.31.58:8644/webhooks/pill-reminder2"
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

## HA configuration.yaml (inline automations — does NOT touch automations.yaml)

```yaml
input_boolean:
  pill_reminder_sent_today:
    name: "Pill Reminder Sent Today"
    initial: false
    icon: "mdi:pill"

shell_command:
  pill_reminder_webhook: "python3 /config/python_scripts/pill_reminder.py"

automation:
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

## Key decisions

- **Inline automations in `configuration.yaml`** (not `automations.yaml`) — isolates errors. A syntax mistake in `automations.yaml` prevents HA from loading ALL automations (`unavailable` + `restored: true`), requiring backup restore.
- **`state` condition** instead of `template` for the dedupe flag — simpler, more reliable.
- **`id:` on every automation** — survives reordering, easy to identify in logs/UI.
- **`mode: single`** — prevents duplicate notifications if Shield flips between `playing`/`on` rapidly.
- **Tailscale IP** (`100.81.31.58`) because HA and Hermes are on different networks (HA on LAN, Hermes on Oracle Cloud).

## Verification

From Hermes host:
```bash
python3 -c "
import hmac, hashlib, urllib.request
url = 'http://localhost:8644/webhooks/pill-reminder2'
secret = b'pill-secret-123'
sig = hmac.new(secret, b'{}', hashlib.sha256).hexdigest()
req = urllib.request.Request(url, data=b'{}',
    headers={'Content-Type': 'application/json', 'X-Webhook-Signature': sig}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    print(r.read().decode())
"
```

Expected: `{"status": "delivered", "route": "pill-reminder2", ...}`
