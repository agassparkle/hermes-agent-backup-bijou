# Home Assistant Automation Troubleshooting

Quick reference for diagnosing bulk automation failures.

## Symptom: Many automations `unavailable` with `"restored": true`

```json
{
  "entity_id": "automation.mount_pictures",
  "state": "unavailable",
  "attributes": {
    "restored": true,
    "friendly_name": "Mount Pictures"
  }
}
```

**Meaning:** HA attempted to restore automation state from previous run but **failed to load the automation config** (usually `automations.yaml`).

## Likely causes (check in order)

| Cause | How to verify |
|-------|---------------|
| YAML syntax error in `automations.yaml` | `python3 -c "import yaml; yaml.safe_load(open('/config/automations.yaml'))"` |
| File missing / empty | `ls -la /config/automations.yaml` |
| Invalid schema (missing trigger/action) | Same YAML validation — HA logs show exact line |
| Include conflict | Check `configuration.yaml` for multiple `automation:` keys |
| HA version upgrade breaking change | Check HA release notes for automation schema changes |

## Diagnostic commands (run on HA host)

```bash
# 1. Check file exists and has content
cat /config/automations.yaml | head -50

# 2. Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('/config/automations.yaml'))" && echo "OK"

# 3. Check HA logs for automation parse errors
grep -i "automation" /config/home-assistant.log | grep -iE "error|fail|parse|invalid" | tail -20

# 4. Verify automations not loaded via API
curl -H "Authorization: Bearer $TOKEN" http://localhost:8123/api/config/automation/config
# Returns 404 if config failed to load
```

## Remote diagnostic commands (when HA is on another host, e.g. 192.168.1.52)

```bash
# Get token from local Hermes env
TOKEN=$(grep HASS_TOKEN ~/.hermes/.env | cut -d= -f2)

# 1. List all automations and their states
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  http://192.168.1.52:8123/api/states | \
  jq -r '.[] | select(.entity_id | startswith("automation.")) | "\(.entity_id) \(.state) \(.attributes.friendly_name // "")"'

# 2. Inspect a single "unavailable" automation for "restored": true
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  http://192.168.1.52:8123/api/states/automation.mount_pictures | jq .

# 3. Verify automation config not loaded (expects 404)
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  http://192.168.1.52:8123/api/config/automation/config

# 4. If config is fixed, reload remotely
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  http://192.168.1.52:8123/api/services/automation/reload
```

## Recovery

1. Fix the YAML / restore from backup
2. Reload without full restart:
   ```bash
   curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:8123/api/services/automation/reload
   ```
3. Verify: `GET /api/states` — automations should show `on`/`off`, not `unavailable`

## API endpoints for automation state

- `GET /api/states` — filter `entity_id` starting with `automation.`
- `GET /api/states/automation.<name>` — inspect one
- `POST /api/services/automation/reload` — reload config
- `GET /api/config/automation/config` — returns loaded config (404 if not loaded)

## Key insight

**"unavailable" + "restored": true = config load failure, NOT entity communication failure.**

The automations themselves are fine. Do NOT delete/recreate them. Fix the source YAML and reload.