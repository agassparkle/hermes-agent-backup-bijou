# Foundry Virtual Tabletop notes

Foundry Virtual Tabletop (Foundry VTT) is a self-hosted online TTRPG platform. Players connect through a browser to join a hosted world/campaign.

## Recognition hints on a server
- PM2 app names may be `foundry`, `foundry_11`, or similar variants.
- The process command often points to a Foundry app directory, for example:
  - `/home/<user>/foundry/resources/app/main.js`
  - `/home/<user>/foundry11/resources/app/main.js`
- A reverse proxy such as Caddy may sit in front of it.
- The app may store user data in a separate `dataPath` directory.

## What to verify next when you find it
- Version/build in the app UI or startup logs
- World/system/module setup
- Public URL / proxy route
- Data directory location

## Session-specific note
On the user's server named `foundry` at `141.144.205.247`, PM2 showed two Foundry-related apps:
- `foundry`
- `foundry_11`

See also `references/foundry-oracle-caddy.md` for the current Oracle Cloud + Caddy layout, versions, ports, and proxy mapping.
