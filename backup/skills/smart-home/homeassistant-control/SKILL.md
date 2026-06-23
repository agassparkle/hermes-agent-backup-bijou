---
name: homeassistant-control
description: "Control Home Assistant entities via its REST API: list states, toggle devices, and fetch camera snapshots."
version: 1.0.0
author: hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Smart-Home, Home Assistant, REST API, Lights, Cameras, IoT]
    homepage: https://developers.home-assistant.io/docs/api/rest/
prerequisites:
  commands: []
---

# Home Assistant Control

Use the Home Assistant REST API when the user wants to inspect or control entities directly.

## When to use

- Turn a light, switch, or scene on/off/toggle
- List entities and current states
- Find the exact `entity_id` by friendly name
- Fetch a camera snapshot from a camera entity
- Verify the result after a state-changing action

## Core workflow
## Core workflow
1. Get the Home Assistant base URL and a *long-lived access token*.
2. **Pre-check auth:** call `GET /api/states` with the token. If it returns `401 Unauthorized`, stop before attempting any control call; the token is expired, revoked, or malformed. Escalate or prompt for a fresh token.
3. Query `/api/states` to discover exact entity IDs and friendly names.
4. Use the exact `entity_id` in service calls; do not guess names.
5. After changing state, query `/api/states/<entity_id>` again to verify the result.
6. If the service call succeeds but the state still reads stale on the first check, wait briefly and re-query before concluding the action failed.
7. For cameras, fetch `/api/camera_proxy/<entity_id>` and save the bytes to a local file before showing it.

See `references/homeassistant-rest.md` for a compact endpoint cheat sheet and environment-specific quirks.

## Common REST endpoints

### List all states

```bash
curl -s \
  -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" \
  -H "Content-Type: application/json" \
  http://HOME_ASSISTANT_HOST:8123/api/states
```

### Read one entity state

```bash
curl -s \
  -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" \
  http://HOME_ASSISTANT_HOST:8123/api/states/light.kitchen
```

### Set light color (RGB)

```bash
curl -s -X POST \
  -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"light.rgb_light", "rgb_color": [255, 0, 0]}' \
  http://HOME_ASSISTANT_HOST:8123/api/services/light/turn_on
```

Common named colors: red `[255,0,0]`, green `[0,255,0]`, blue `[0,0,255]`, white `[255,255,255]`, warm white `[255,200,100]`.

### Set light brightness

```bash
curl -s -X POST \
  -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"light.kitchen", "brightness": 128}' \
  http://HOME_ASSISTANT_HOST:8123/api/services/light/turn_on
```

`brightness` is 0–255. Pass alongside `rgb_color` in the same payload to set both at once.

### Turn a light on/off/toggle

```bash
curl -s -X POST \
  -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"light.kitchen"}' \
  http://HOME_ASSISTANT_HOST:8123/api/services/light/turn_on

curl -s -X POST \
  -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"light.kitchen"}' \
  http://HOME_ASSISTANT_HOST:8123/api/services/light/turn_off

curl -s -X POST \
  -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"light.kitchen"}' \
  http://HOME_ASSISTANT_HOST:8123/api/services/light/toggle
```

### Fetch a camera snapshot

```bash
curl -s -o /tmp/ha_body.bin -w '%{http_code}\n' \
  -H "Authorization: Bearer $(cat /home/agas/.ha_token)" \
  http://192.168.1.52:8123/api/camera_proxy/camera.front_door \
  -o /tmp/front-door.jpg
```

## Pitfalls

- **Token redaction causes silent 401s.** Hermes's secret redactor replaces the HA token with `***` in terminal output and tool results. If you copy-paste the token from a previous turn's output, or use a placeholder like `eyJhbG...AI`, the request will fail with `401 Unauthorized`. Always use the raw token from memory or `.env` directly in the curl command — never from a redacted output string.
- Use the *full* token. A truncated or placeholder token will fail with `401 Unauthorized` even if the request shape is correct.
- Entity names in the UI can differ from the true `entity_id`. Always confirm via `/api/states`.
- Cameras often return binary image data; save it locally first, then show it with the image/vision workflow.
- Keep tokens out of git and out of chat logs.

## Verification
## Troubleshooting 401s and auth failures
1. If `/api/states` or any service call returns `401 Unauthorized`, the token is being rejected.
2. First verify the token directly: `curl -i -H "Authorization: Bearer *** http://<HA_HOST>:8123/api/`. If you see `401`, the token is invalid, expired, or scoped to a different instance/user.
3. Check HA logs for `homeassistant.components.http.ban` — repeated “invalid authentication from <IP>” means HA is rejecting your source IP as untrusted, often because a trusted proxy is misconfigured or the auth is plain API-password/Long-Lived-Access-Token mode.
4. If auth is via Header-based Long-Lived Access Token, HA must be in `api:` mode with trusted proxies set correctly if behind a proxy.
5. After fixing HA auth, re-run the service call and re-query the entity to confirm state.

## Tooling quirks
- In this environment, raw `curl` calls with quoted headers are brittle. Prefer Python `requests` or `fetch_url` for POST/GET to Home Assistant:
  - GET: `requests.get(url, headers=headers, timeout=30)`
  - POST: `requests.post(url, headers=headers, json=payload, timeout=30)`
- If you must use `curl`, use a here-doc or `python3 -c` to avoid shell quoting failures.
- Always print `response.status_code` and `response.text[:500]` when debugging HA API responses. Body is usually just `401: Unauthorized` on auth failures.

## Verification
- For lights/switches: read back `/api/states/<entity_id>` and confirm the new state.
- For cameras: confirm the file is non-empty and visually inspect the saved image.
- HA auth failures are silent on state change — stop and fix auth before retrying the same turn_on/turn_off call.

## Credential safety & cleanup
- Do not store full HA tokens in `fact_store` or `MEMORY.md`. If a token is verified live, keep it only where Hermes processes environment credentials safely (`~/.hermes/.env`).
- If the user requests “remove everything related to HA”, perform these exact steps in order:
  1. Search `fact_store` for all HA-related facts and remove them.
  2. Edit `/home/agas/.hermes/memories/MEMORY.md` and `USER.md` to strip HA-specific notes manually; `memory(action='remove')` often cannot match backticks/quotes, so use targeted edits.
  3. Edit `~/.hermes/.env` to delete `HASS_TOKEN=*** and, if present, `HASS_URL=`.
  4. Ask whether known HA backup mirrors such as `~/Hermes/.../backup/memories/MEMORY.md` should also be scrubbed, then remove the same fields/entity notes if the user confirms.
  5. Leave non-secret operational notes (for example, a restore guide) intact.

## Related notes

- See `references/homeassistant-rest.md` for a compact endpoint cheat sheet and session-proven quirks.
- See `references/alp-entity-map.md` for Alp's confirmed entity IDs (lights, automations, RGB helpers).
