---
name: home-server-service-management
description: Manage services on a home Ubuntu server (qBittorrent, Foundry VTT, Home Assistant, etc.) — start/stop, configure, troubleshoot headless operation.
category: devops
---

# Home Server Service Management

Manage long-running services on the user's Ubuntu home server. The server runs multiple self-hosted applications (Foundry VTT, Home Assistant, qBittorrent, etc.) behind Caddy reverse proxy.

## Core Principles

1. **Check config first** — Always read the service's config file before overriding settings (ports, paths, auth). The config file is the source of truth.
2. **Check memory + fact_store before SSH** — Before running any SSH command on a named server (`foundry`, `hermes`, future VPSes), search both the `memory` block and `fact_store` for connection details. Don't try `ssh <name>` and wait for `Name or service not known` first. The user has flagged this slip explicitly.
3. **Don't install unless asked** — Never run `apt install` or similar unless the user explicitly requests it. Most services are already installed.
4. **Respect headless requirements** — Qt-based apps (qBittorrent, etc.) need `QT_QPA_PLATFORM=offscreen` to run without a display.
5. **Use existing process management** — Prefer systemd services when they exist. If not, background processes with `notify_on_complete=false` for daemons.

## qBittorrent Specifics

- Binary: `/usr/bin/qbittorrent` (GUI version, works headless with offscreen)
- Config: `~/.config/qBittorrent/qBittorrent.conf`
- WebUI port: read from `WebUI\Port` in config (default 8080)
- Headless launch: `QT_QPA_PLATFORM=offscreen qbittorrent --no-splash &`
- Do NOT pass `--webui-port` unless user explicitly wants to override config

## Foundry VTT Specifics (local home server)

- Two instances: localhost:30000 and localhost:30001
- Caddy reverse proxy in front
- Managed via systemd (check `systemctl status foundry*`)

## Cloud Servers (Oracle VPS)

The user has two Oracle Cloud VPSes. Both use `ubuntu` user and share the same keys directory `/mnt/sda2/UBuntu_Backup/Oracle Cloud  Keys/`. **Linux is case-sensitive on filenames — verify the exact casing before connecting.**

| Field | foundry | hermes |
|---|---|---|
| IP | `141.144.205.247` | `130.61.122.103` |
| Hostname | `foundry` | `Hermes` (collides with MagicDNS default — rename to `hermes-server` or similar when adding to tailnet) |
| SSH key (exact case) | `agassparkle.key` | **`Hermes.key`** (capital H — `hermes.key` will 404) |
| OS | Ubuntu 22.04 (jammy) ARM64 | Ubuntu 24.04 (noble) ARM64 |
| Tailscale | installed and active; IP `100.77.126.105`, account `alpozben@` | installed (1.98.4) and active; IP `100.76.208.31`, account `alpozben@` |
| Caddy | reverse proxy fronts two VTT instances — browser-facing `localhost:30001`, other `localhost:30000` | not configured yet |
| Timezone | UTC | (default UTC; no `timedatectl` change) |
| Purpose | Foundry VTT (2 instances, Caddy reverse proxy) | Syncthing hub, Jack vault |

Connect with:
```bash
# foundry
ssh -i "/mnt/sda2/UBuntu_Backup/Oracle Cloud  Keys/agassparkle.key" \
    -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
    ubuntu@141.144.205.247

# hermes
ssh -i "/mnt/sda2/UBuntu_Backup/Oracle Cloud  Keys/Hermes.key" \
    -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
    ubuntu@130.61.122.103
```

Or use the bundled helper script for foundry: `bash scripts/foundry-ssh.sh [command...]`.

See `references/foundry-cloud-server.md` for the foundry live-session snapshot, and `references/hermes-cloud-server.md` for the hermes server.

### Adding a new cloud server to this skill

When the user introduces a new Oracle Cloud VPS:
1. Get the IP, hostname, user, and exact-case SSH key filename before connecting.
2. Verify connectivity once with `BatchMode=yes` — never run commands blind.
3. Snapshot `tailscaled` status, OS release, sudo passwordless check, and any custom hostname collisions.
4. Add a row to the table above **and** create a `references/<server>-cloud-server.md` snapshot file.
5. Update both memory entries (consolidated `memory` entry + a `fact_store` fact) so the agent has the connection details in two places.

### Tailscale install on a fresh Ubuntu cloud server

Pattern verified on `hermes` (Ubuntu 24.04 noble, 2026-06-19). Detailed gotchas live in `references/tailscale-node-setup.md`.

```bash
# 1. Install via official apt repo (no manual key download)
curl -fsSL https://tailscale.com/install.sh | sh

# 2. Enable BOTH v4 and v6 IP forwarding NOW (exit-node warnings otherwise)
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-tailscale.conf > /dev/null
echo "net.ipv6.conf.all.forwarding=1" | sudo tee /etc/sysctl.d/99-tailscale-ipv6.conf > /dev/null
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale-ipv6.conf

# 3. tailscaled is auto-enabled and started by the install script
sudo systemctl is-active tailscaled   # verify active

# 4. Auth — use one-shot auth key for headless, or expect a URL to surface
sudo tailscale up --ssh=false --accept-routes --advertise-exit-node
```

**Flags to always set on first `tailscale up`:**
- `--ssh=false` unless explicitly wanted (Tailscale SSH replaces OpenSSH listening on port 22).
- `--accept-routes` to use routes advertised by other nodes in the tailnet.
- `--advertise-exit-node` if the node should offer itself as one — but see admin-approval pitfall below.
- `--hostname=<custom>` if the OS hostname collides with a MagicDNS name (e.g. `Hermes` hostname → use `hermes-server`). **Note:** `tailscale up` resets the registered hostname to lowercase; check `tailscale status --json | jq '.Self.HostName'` after.
- `--authkey=tskey-...` for headless auth when the user has created a reusable key at https://login.tailscale.com/admin/settings/keys.

**Time budget:** the install + `tailscale up` together can take 90-120 seconds. Set `timeout=120` on the SSH command or it will trip the agent's 120s default and look like a hang.

**Exit node + key-expiry both require admin-side approval** that the CLI cannot grant. After `tailscale up --advertise-exit-node`:
1. The CLI reports success but the control plane still shows `ExitNodeOption: False` in `tailscale status --json`.
2. The user must go to https://login.tailscale.com/admin/machines → node → "..." → **Edit route settings** → toggle **Use as exit node** → Save.
3. Key expiry defaults to ~180 days and is set in https://login.tailscale.com/admin/settings/preferences → "Key expiry" → **None**. CLI cannot clear this.
4. After admin approval, `sudo systemctl restart tailscaled` on the node, then re-run `tailscale up` with the **full** flag list (the daemon refuses partial flag lists with `--advertise-exit-node` and replies: "Error: changing settings via 'tailscale up' requires mentioning all non-default flags").

## Home Assistant Specifics

- Long-lived token for API access
- Entity IDs stored in memory (e.g., `media_player.android_tv_192_168_1_62` for Shield)
- REST API via `ha_*` tools

## Steam / Proton Specifics

- Steam installs to `~/.steam/steam` (compatibility tools in `~/.local/share/Steam/compatibilitytools.d/`)
- Proton-GE versions (GE-Proton10-34, etc.) must be manually extracted to `compatibilitytools.d/` — `protonup` CLI is unreliable
- Enable in Steam: **Settings → Compatibility → Enable Steam Play for all titles** → select Proton version
- Per-game launch options (right-click → Properties → General → Launch Options):
  - `PROTON_USE_WINED3D=1 %command%` — common fix for mouse/input issues
  - `WINE_LAYERED_OVERLAY_ALPHA=1 %command%` — enables layered window transparency (TBH: Task Bar Hero)
- Verify Proton installation: `ls ~/.local/share/Steam/compatibilitytools.d/`

## Syncthing Specifics

- Config: `~/.local/state/syncthing/config.xml` (API key in `<apikey>` element)
- REST API on `http://localhost:8384/rest/` — authenticate with `X-API-Key` header
- Device IDs: get with `syncthing --device-id`
- Connectivity debugging workflow: see `references/syncthing-debugging.md`

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Qt app fails with "could not connect to display" | Set `QT_QPA_PLATFORM=offscreen` |
| Port mismatch | Read config file first (`grep -i port ~/.config/qBittorrent/qBittorrent.conf`) |
| Killing wrong process | Use `pgrep -f` to verify PIDs, check listening ports with `ss -tlnp \| grep qbittorrent` |
| Assuming service isn't installed | Check `which <binary>` and `apt list --installed \| grep <name>` first |
| `protonup` CLI returns "Not Found" | Use GitHub API directly: `curl -sL https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/tags/GE-Proton10-34 \| jq -r '.assets[] \| select(.name \| test("tar.gz$")) \| .browser_download_url'` then download/extract manually |
| Steam fails to launch on Wayland | Try `GDK_BACKEND=x11 steam` or ensure XWayland is available |
| `ssh <name>` fails with `Name or service not known` | The agent jumped straight to the command without checking memory. Always check `~/.ssh/config`, memory, and `fact_store` for connection details (host, user, key path) **before** running the SSH command. The user has flagged this workflow slip explicitly. |
| SSH key path is the **wrong case** (`hermes.key` vs `Hermes.key`) and fails with `Permission denied (publickey)` | Linux filenames are case-sensitive. Always copy the key filename verbatim from the user / `ls` output — do not normalize capitalization. |
| `memory replace` returns "Replacement would put memory at X/2200 chars" even though only one entry is being swapped | The `replace` action calculates post-replace total against current state. If you need to consolidate multiple overlapping entries into one, you must `remove` the redundant entries **first** (in the same turn), then `replace` the survivor. Doing `replace` alone won't free space from sibling entries. |
| `hermes gateway restart` (or its long form `python -m hermes_cli.main gateway restart`) returns "Refusing to restart the gateway from inside the gateway process" — even when run via `terminal(background=true)` | The guard checks the process tree, not foreground/background status. `setsid -f` / `nohup` / `disown` are also blocked by Hermes (shell-level detach wrappers are forbidden). **There is no path from inside an active gateway session to restart it.** Tell the user to run `hermes gateway restart` themselves from a separate shell. Expect a brief disconnect (Telegram/HA/webhooks drop for ~5-15s) and warn the user before they confirm. |
| `patch` / `write_file` to `~/.hermes/config.yaml` returns "Refusing to write to Hermes config file: Agent cannot modify security-sensitive configuration" | Hermes blocks the agent from editing its own config directly. Tell the user to edit the file themselves (`nano ~/.hermes/config.yaml`) or use `hermes config set <key.path> <value>`. The change only takes effect after a gateway restart, which compounds the previous pitfall. |
| User asks to raise `memory_char_limit` (e.g., from 2200 → 4000) | Edit `~/.hermes/config.yaml` line ~391 (`memory.memory_char_limit`), save, then the user must run `hermes gateway restart` from a separate shell. **Note:** the in-turn memory tool may keep reporting the old cap until the *next* gateway session, even after a clean restart — if a `memory add` still fails with the old limit, the bump did not propagate and another restart is needed. |
| `sudo tailscale set --advertise-exit-node=true` returns silently with no error, but `tailscale status --json | jq '.Self.ExitNodeOption'` still shows `false` | In Tailscale 1.98.x, `tailscale set` does not propagate `--advertise-exit-node`. Use `tailscale up --advertise-exit-node` with the full flag list instead. Expect an auth URL or admin-side approval. |
| `tailscale up` hangs past the agent's 120s timeout with no output, then times out | The command is blocking on browser-based auth. Either: (a) hand control back to the user and ask them to click the auth URL, or (b) wait for the user to generate a reusable `tskey-...` auth key from https://login.tailscale.com/admin/settings/keys and re-run with `--authkey=tskey-...`. Wrap the call in `timeout 25 ssh ...` if you need to surface "URL printed, waiting for click" instead of hanging. |
| Syncthing device never connects (last seen epoch 0); `nc -zv <ip> 22000` returns "No route to host" even though SSH works | Oracle Cloud Ubuntu images have a default iptables that REJECTs everything except SSH (22), ICMP, and loopback. Add an ACCEPT rule before the REJECT line: `sudo iptables -I INPUT <N> -p tcp -m state --state NEW --dport 22000 -j ACCEPT`. Persist with `iptables-save > /etc/sysconfig/iptables`. See `references/syncthing-debugging.md` for full workflow. |

## Pill Reminder Test Workflow

Use this when the user wants to verify the HA pill-reminder path.

1. Confirm the Pill reminder schedule, then inspect the cron job:
   - Current cron info: job_id, provider/model, schedule, next run, scheduled toolsets.
2. Trigger the reminder entity outside the main window:
   - Default time gate is `* 9-11 * * *` (Europe/Helsinki / EEST).
   - If that blocks execution, temporarily set schedule to `* * * * *`.
   - Trigger Shield with `ha_call_service` turn_on if supported; otherwise use a readable state change like `media_play_pause`.
3. Verify execution:
   - Check `last_run_at` / `last_status`.
   - Wait ~1 minute after edit, then re-list.
4. Restore the original schedule after testing.

`cronjob` will surface next eligible runs; if `last_run_at` doesn't update after a minute, retry the trigger and then restore immediately.

## Pill Reminder Test Workflow

Use this when the user wants to verify the HA pill-reminder path end-to-end.

1. Inspect the job first:
   - Current cron info: job_id, provider/model, schedule, next run, scheduled toolsets.
   - The job is time-gated by `* 9-11 * * *` (Europe/Helsinki / EEST), so runs outside that window are silent no-ops.
2. Exercise the reminder entity:
   - Prefer `media_play_pause` for Shield unless `turn_on` is accepted.
   - For a forced test now, temporarily set schedule to `* * * * *`.
3. Verify execution:
   - Wait ~1 minute, then re-list and check `last_run_at` / `last_status`.
4. Always restore the original schedule after testing.

## Verification Steps

After starting any service:
1. `pgrep -f <service>` — confirm process running
2. `ss -tlnp \| grep <port>` — confirm port listening
3. Test endpoint if applicable (curl WebUI, etc.)