# Foundry Cloud Server — Session Notes

Last verified: 2026-06-22.

## Verified SSH command

```bash
ssh -i "/mnt/sda2/UBuntu_Backup/Oracle Cloud  Keys/agassparkle.key" \
    -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
    ubuntu@141.144.205.247
```

ICMP (ping) is blocked by Oracle's network-level firewall, but SSH on port 22 is reachable. The `agassparkle.key` is the only key that works — `Hermes.key` returns `Permission denied (publickey)`.

## Server Identity

| Field | Value |
|---|---|
| IP | `141.144.205.247` |
| Hostname | `foundry` |
| User | `ubuntu` |
| OS | Ubuntu 22.04 LTS (jammy), aarch64 (ARM64) |
| Uptime (2026-06-22) | 36 days |
| Disk | 194 GB, 22 GB used (11%) |
| Sudo | passwordless |

## Tailscale (2026-06-22)

| Field | Value |
|---|---|
| `tailscaled` | active |
| Tailscale IP | `100.77.126.105` |
| Exit node | offered |

## Services Running

| Service | Detail |
|---|---|
| **Foundry VTT** | 2 instances via PM2: `foundry` (port 30000), `foundry_11` (port 30001). Both online 36 days. |
| **Caddy** | Reverse proxy: `agassparkle.ddns.net` → localhost:30001. Also serves catch-all HTTPS → localhost:30001. Admin on 127.0.0.1:2019. |
| **Docker** | Installed but no containers running |
| **Syncthing** | Not installed |

## Foundry VTT Modules

Located in `~/FoundryModules/` — Free League Forbidden Lands full pack:

| Module | File |
|---|---|
| Core Game v6.0.0 | `fbl-core-game-v6.0.0.7z` |
| Bitter Reach v6.0 | `fbl-bitter-reach_V6-0-0_FVTT11_CLEAN.7z` |
| Bloodmarch v1.0.1 | `fbl-bloodmarch_V1.0.1_FVTT11_CLEAN.7z` |
| Book of Beasts v1.0.1 | `fbl-book-of-beasts_V1.0.1_FVTT11_CLEAN.7z` |
| Raven's Purge v5.1.1 | `fbl-ravens-purge-V5-1-1_FVTT11_CLEAN.7z` |
| TheRipper93 Compilation | `TheRipper93 - FoundryVTT Compilation.7z` |

Also present: `~/.fex-emu/` — FEX emulator for x86-on-ARM compatibility.

## Caddy Config (`/etc/caddy/Caddyfile`)

```
agassparkle.ddns.net {
    reverse_proxy localhost:30001
    encode zstd gzip
}

https:// {
    tls internal { on_demand }
    reverse_proxy localhost:30001
    encode zstd gzip
}
```

## PM2

Two named processes in fork mode: `foundry` (port 30000) and `foundry_11` (port 30001). Both `watching: disabled`. Restart with `pm2 restart foundry` or `pm2 restart foundry_11`.

## Health Notes

- **ARM64 architecture** — uses FEX emulator for x86 binaries. Some Foundry modules may need compatibility checks.
- **No Syncthing** — if the user wants vault syncing to this server, Syncthing would need to be installed fresh.
