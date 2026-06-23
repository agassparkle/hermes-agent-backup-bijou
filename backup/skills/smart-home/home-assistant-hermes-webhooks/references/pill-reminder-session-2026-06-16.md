# Pill Reminder — Session Artifacts (2026-06-16)

## Actual config used in this session

### Hermes config.yaml (platforms section)

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8644
      secret: "hermes-webhook-secret"
  telegram:
    streaming: true
  discord:
    streaming: false
```

### Webhook subscription

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

### HA python script

**File:** `/config/python_scripts/pill_reminder.py`

```python
import hmac, hashlib, json, urllib.request, sys

url = "http://192.168.1.51:8644/webhooks/pill-reminder2"
secret = b"pill-secret-123"
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

### HA configuration.yaml additions

```yaml
input_boolean:
  pill_reminder_sent_today:
    name: "Pill reminder sent today"
    initial: false

shell_command:
  pill_reminder_webhook: "python3 /config/python_scripts/pill_reminder.py"

automation:
  - alias: "Reset pill reminder daily flag"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.pill_reminder_sent_today
    mode: single
```

### HA automations.yaml addition

```yaml
- alias: "Pill reminder - Shield activity"
  description: "Triggers pill reminder when Shield starts playing between 09:00-11:59"
  trigger:
    - platform: state
      entity_id: media_player.android_tv_192_168_1_62
      to: ["playing", "on"]
  condition:
    - condition: time
      after: "09:00:00"
      before: "11:59:59"
    - condition: template
      value_template: "{{ not states('input_boolean.pill_reminder_sent_today') | bool }}"
  action:
    - service: shell_command.pill_reminder_webhook
    - service: input_boolean.turn_on
      target:
        entity_id: input_boolean.pill_reminder_sent_today
  mode: single
```

## Key gotchas encountered

1. **Wrong header**: Used `X-Hermes-Signature` initially → 401. Correct is `X-Webhook-Signature`.
2. **Multi-line python in shell_command**: Fails with syntax/indentation errors. Must use external script file.
3. **Network**: HA at 192.168.1.52, Hermes at 192.168.1.51 (same LAN). Script uses LAN IP.
4. **Body bytes**: `payload = b"{}"` (bytes) — string `"{}"` produces different HMAC.
5. **Secret format**: Raw string `pill-secret-123`, not base64 or `whsec_` prefixed.

## Test commands

From HA Developer Tools → Actions:
- Service: `shell_command.pill_reminder_webhook` → Call Service

From Hermes host:
```bash
hermes webhook test pill-reminder2
# or
python3 -c "
import hmac, hashlib, urllib.request
url = 'http://192.168.1.51:8644/webhooks/pill-reminder2'
secret = b'pill-secret-123'
payload = b'{}'
sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()
req = urllib.request.Request(url, data=payload,
    headers={'Content-Type': 'application/json', 'X-Webhook-Signature': sig}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    print(r.read().decode())
"
```

## Backup cron (expires 2026-06-23)

Hermes cron job `1ec54427a168` — "Pill reminder (first detection, expires 7d)"
- Schedule: `* 9-11 * * *` (every minute 09-11:59)
- Checks `media_player.android_tv_192_168_1_62` for `playing`/`on`
- Sends once per day via Telegram
- Auto-expires after 10,080 runs (7 days)