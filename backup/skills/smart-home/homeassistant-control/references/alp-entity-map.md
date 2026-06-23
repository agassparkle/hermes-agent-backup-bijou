# Alp's Home Assistant Entity Map

HA instance: `http://192.168.1.52:8123`

## Lights

| Friendly name | entity_id | Notes |
|---|---|---|
| Bird light / Kus Isik | `light.kus_isik` | Bedside/bird area light |
| RGB light | `light.rgb_light` | Full RGB; use `rgb_color` param |

## Automations (related)

| Friendly name | entity_id |
|---|---|
| Turn Off RGB | `automation.turn_off_rgb` |

## Input Booleans (RGB helpers)

| Friendly name | entity_id |
|---|---|
| rgb | `input_boolean.rgb` |
| RGB_ON | `input_boolean.rgb_on` |
| Rgb_random_Color | `input_boolean.rgb_random_color` |

## Notes

- RGB light supports `rgb_color: [R, G, B]` (0-255 each) in `light/turn_on` service call.
- Common colors: red `[255,0,0]`, green `[0,255,0]`, blue `[0,0,255]`, white `[255,255,255]`.
- Discovered via `/api/states` grep on `rgb` in entity_id or friendly_name.
