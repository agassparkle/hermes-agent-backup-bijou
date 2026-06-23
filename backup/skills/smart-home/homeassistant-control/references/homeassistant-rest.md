# Home Assistant REST notes

## Endpoint reminders

- Base URL pattern: `http://HOST:8123`
- Read states: `GET /api/states`
- Read one entity: `GET /api/states/<entity_id>`
- Light services: `POST /api/services/light/turn_on`, `turn_off`, `toggle`
- Body shape: `{"entity_id":"light.example"}`

## Environment-specific examples seen here

- Example host: `http://192.168.1.52:8123`
- Known alias in this environment: `bird light` → `light.kus_isik`
- Known alias in this environment: `RGB light` → `light.rgb_light` (supports `rgb_color` and `brightness`)

## Verification quirk

- A successful light service call can still be followed by a briefly stale `/api/states/<entity_id>` response.
- If the first readback does not match the requested state, wait about 1 second and query again before deciding the action failed.

## Practical pattern

1. Call the service.
2. Read back the entity state.
3. If stale, retry the read once or twice with a short delay.
4. Only report success after the verified state changes.
