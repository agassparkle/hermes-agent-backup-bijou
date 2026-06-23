# Home Assistant REST API cheat sheet

Compact workflow used for direct control.

## Base endpoints

- `GET /api/states` — list every entity and its current state
- `GET /api/states/<entity_id>` — inspect one entity
- `POST /api/services/<domain>/<service>` — call a service

## Auth

Use a long-lived bearer token in the `Authorization` header:

- `Authorization: Bearer <token>`

Keep the token local-only; do not store it in git.

## Discovery pattern

When the user says a casual name like "kus isik":

1. Fetch `/api/states`
2. Filter by `entity_id` and `attributes.friendly_name`
3. Choose the most likely entity
4. If needed, confirm ambiguity before acting

## Toggle pattern

Example for a light:

```json
POST /api/services/light/toggle
{"entity_id": "light.kus_isik"}
```

Then verify with:

```json
GET /api/states/light.kus_isik
```

## Notes from this session

- The user’s `kus isik` target resolved to `light.kus_isik`.
- A service call succeeded with `POST /api/services/light/toggle`.
- Verification should always read the entity back after the service call.
