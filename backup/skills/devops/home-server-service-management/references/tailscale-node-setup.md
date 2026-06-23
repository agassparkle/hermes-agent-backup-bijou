# Tailscale Node Setup — Class-Level Reference

Reproducible recipe and gotchas for installing Tailscale on a fresh Linux node (Ubuntu 22.04 / 24.04 verified, headless OK) and bringing it into the user's existing tailnet.

This is class-level — applies to any new Tailscale node (cloud VPS, home server, dev box), not a specific server.

## Install (verified Ubuntu 24.04 noble, 2026-06-19)

```bash
# Install via official script — sets up the apt repo, keyring, and unit file
curl -fsSL https://tailscale.com/install.sh | sh

# Enable IP forwarding (required for exit nodes and subnet routing)
# MUST do both v4 and v6 — exit nodes need both
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-tailscale.conf > /dev/null
echo "net.ipv6.conf.all.forwarding=1" | sudo tee /etc/sysctl.d/99-tailscale-ipv6.conf > /dev/null
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale-ipv6.conf

# tailscaled is auto-enabled and started by install.sh
sudo systemctl is-active tailscaled   # expect: active
tailscale version                       # was 1.98.4 on Ubuntu 24.04 arm64
```

Install typically takes 30-60 seconds (downloads ~34 MB tailscale + small keyring).

## Auth

Two paths. Pick based on whether you can interact with a browser from the SSH session:

### A. Headless / non-interactive (preferred for agents)

Generate a reusable, tagged auth key at https://login.tailscale.com/admin/settings/keys, then:

```bash
sudo tailscale up \
  --authkey=tskey-auth-XXXXXXXXXXXXXXXX \
  --ssh=false \
  --accept-routes \
  --advertise-exit-node \
  --hostname=<desired-tailnet-name>
```

### B. Interactive (user clicks URL)

```bash
sudo tailscale up --ssh=false --accept-routes --advertise-exit-node
```

The daemon blocks and prints a URL like:

```
To authenticate, visit:

    https://login.tailscale.com/a/xxxxxxxxxxxx
```

The user opens it in a browser, approves, and the daemon finishes. **Wrap with `timeout 25 ssh ...` if you need to detect "URL printed, waiting for click" instead of letting the agent's 120s timeout fire.**

## Flags — what to set on first `tailscale up`

| Flag | Why |
|---|---|
| `--ssh=false` | Tailscale SSH replaces OpenSSH on port 22. Most users want their existing sshd untouched. |
| `--accept-routes` | Lets this node use routes advertised by other tailnet nodes (subnet routes from foundry, homeassistant-1, etc.). |
| `--advertise-exit-node` | Offer this node as an internet exit for other nodes. **Requires admin-side approval to actually take effect** — see below. |
| `--hostname=<name>` | Override the OS hostname in MagicDNS. Useful when the OS hostname (`Hermes`) collides with default MagicDNS naming. **Watch out:** `tailscale up` resets the registered hostname to the OS default (often lowercase); check `tailscale status --json | jq '.Self.HostName'` afterwards. |
| `--authkey=tskey-...` | Headless auth — see path A above. |

## Exit Node + Key Expiry — admin-side approval required

Both of these **cannot** be enabled via CLI alone. The CLI reports success but the control plane ignores the request until an admin approves it in the web UI:

### Exit-node approval

After `tailscale up --advertise-exit-node` succeeds:
1. `tailscale status --json | jq '.Self.ExitNodeOption'` returns `false` even though the CLI claimed success.
2. User must go to https://login.tailscale.com/admin/machines
3. Find the node → "..." menu → **Edit route settings** → toggle **Use as exit node** → Save
4. `sudo systemctl restart tailscaled` on the node
5. Re-run `tailscale up` with the FULL flag list (the daemon rejects partial flags):

```bash
sudo tailscale up --ssh=false --accept-routes --advertise-exit-node
```

The "full flag list" requirement is enforced — the error message reads:
> Error: changing settings via 'tailscale up' requires mentioning all non-default flags. To proceed, either re-run your command with --reset or use the command below to explicitly mention the current value of all non-default settings.

### Key-expiry disable

The CLI cannot clear this. User must go to https://login.tailscale.com/admin/settings/preferences → "Key expiry" → **None**.

Verify per-node:
```bash
sudo tailscale status --json | jq '.Self.KeyExpiry'
# null = no expiry (good)
# "2026-12-16T22:02:27Z" = expires that date (override in admin UI)
```

## Verification

```bash
# Health summary
sudo tailscale status

# Detailed per-node state
sudo tailscale status --json | jq '{
  hostname: .Self.HostName,
  tailscale_ips: .Self.TailscaleIPs,
  online: .Self.Online,
  exit_node_offered: .Self.ExitNodeOption,
  key_expiry: .Self.KeyExpiry,
  advertised_routes: .Self.AllowedIPs,
  ip_forwarding_v4: (.Health | map(select(.[0] | contains("wantrunning"))) | length)
}'

# IP forwarding persistence
cat /proc/sys/net/ipv4/ip_forward       # expect 1
cat /proc/sys/net/ipv6/conf/all/forwarding   # expect 1

# End-to-end — ping another node by Tailscale IP
tailscale ping <peer-tailscale-ip>
```

## Common Gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `Warning: IPv6 forwarding is disabled. Subnet routes and exit nodes may not work correctly.` | Only v4 forwarding was enabled | Add v6 to sysctl.d and re-apply |
| `Tailscale is stopped.` after admin action in web UI | Admin toggled "Disable" / paused the node | `sudo systemctl restart tailscaled` + re-`tailscale up` with full flag list |
| `tailscale status --json | jq '.Self.ExitNodeOption'` returns `false` after `tailscale up --advertise-exit-node` | CLI doesn't propagate the flag in 1.98.x; admin approval missing | See "Exit Node + Key Expiry" section above |
| Hostname dropped from `Hermes` to `hermes` after re-running `tailscale up` | `tailscale up` resets registered hostname to lowercase OS default | Re-add `--hostname=<custom>` and re-`tailscale up` |
| `Error: changing settings via 'tailscale up' requires mentioning all non-default flags.` | Partial flag list after a previous successful `tailscale up` | Include every flag from the original auth, or pass `--reset` (loses registration) |
| `tailscale up` times out at 120s with no output | Daemon is blocking on browser auth URL | Hand back to the user with the printed URL, or use `--authkey=tskey-...` for headless |
| Node appears in tailnet but offline / `Last seen` keeps growing | tailscaled service stopped or paused | `sudo systemctl restart tailscaled`, then re-run `tailscale up` |
