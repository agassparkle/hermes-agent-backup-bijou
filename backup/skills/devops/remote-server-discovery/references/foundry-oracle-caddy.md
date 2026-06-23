# Foundry + Oracle/Caddy notes

Session-specific notes for the user's Oracle Cloud Foundry host.

## Host summary
- Hostname: `foundry`
- Public IP: `141.144.205.247`
- SSH user used successfully: `ubuntu`
- One SSH key path used: `/mnt/sda2/UBuntu_Backup/Oracle Cloud  Keys/agassparkle.key`

## Foundry instances observed
Two Foundry Virtual Tabletop instances were running under PM2:
- `foundry` -> `/home/ubuntu/foundry/resources/app/main.js --dataPath=/home/ubuntu/foundryuserdata`
- `foundry_11` -> `/home/ubuntu/foundry11/resources/app/main.js --dataPath=/home/ubuntu/foundryuserdata11`

## Versions
- `/home/ubuntu/foundry/resources/app/package.json` -> Foundry VTT `12.331.0`
- `/home/ubuntu/foundry11/resources/app/package.json` -> Foundry VTT `11.315.0`

## Data directories
- `/home/ubuntu/foundryuserdata`
  - world: `forbidden-lands`
  - system: `forbidden-lands`
- `/home/ubuntu/foundryuserdata11`
  - world: `hasanfinder`
  - system: `pf1`

## Ports and proxying
- Foundry app ports: `30000` and `30001`
- Caddy listens on `80` and `443`
- Caddyfile routes `agassparkle.ddns.net` and `https://` to `localhost:30001`
- Public traffic therefore lands on the `foundry_11` instance unless the proxy config changes

## Useful inspection locations
- `Data/Config/options.json` for port, hostname, proxy, and update-channel settings
- `Data/worlds/<world>/world.json` for world title/system/version compatibility
- `Data/systems/<system>/system.json` for system metadata
- `Data/modules/<module>/module.json` for module metadata
