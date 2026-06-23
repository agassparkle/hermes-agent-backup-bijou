# Hermes Cloud Server — Session Notes

Introduced 2026-06-19. Last verified: 2026-06-22.

## Verified SSH command

```bash
ssh -i "/mnt/sda2/UBuntu_Backup/Oracle Cloud  Keys/Hermes.key" \
    -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
    ubuntu@130.61.122.103
```

**Case-sensitive key filename:** `Hermes.key` (capital H). Linux will not find `hermes.key`. Always copy verbatim.

**Note:** The local key directory has a double space: `Oracle Cloud  Keys` (not `Oracle Cloud Keys`). Always use the exact path.

## Server identity

| Field | Value |
|---|---|
| IP | `130.61.122.103` |
| Hostname (OS) | `Hermes` |
| User | `ubuntu` |
| OS | Ubuntu 24.04.4 LTS (noble), arm64 |
| Sudo | passwordless (`sudo -n true` succeeds) |
| IP forwarding | v4=1, v6=1 (set during Tailscale install) |
| Locale | unset |

## Services running (2026-06-22)

| Service | Detail |
|---|---|
| **Syncthing** | v1.27.2, user systemd service, running since Jun 20 |
| **Tailscale** | v1.98.4, active |
| **iptables** | Port 22000 ACCEPT before REJECT rule, persisted via netfilter-persistent |

## Syncthing setup

| Field | Value |
|---|---|
| Device ID | `PE7IUSA-BHA3PXI-QVLICNW-J4RMA56-RGYNKKQ-55OXTV4-B7Y5EH3-NGU2DQH` |
| API Key | `MsxdhKYt7FY3b6aDhGsC77hZRtJFJzzy` |
| Peer | agas-ubuntu (`JHKL4B6-2PMEBID-...`) |
| Jack Vault folder | `hermes-vault` → `/home/ubuntu/jack-vault` (sendreceive) |
| Connected via | Tailscale (`100.76.208.31`) and public IP (`46.196.105.182`) |

## iptables (firewall)

Port 22000 was blocked by Oracle's default iptables (only SSH + ICMP allowed). Fixed 2026-06-22:

```bash
sudo iptables -I INPUT 4 -p tcp -m state --state NEW -m tcp --dport 22000 -j ACCEPT
sudo netfilter-persistent save
```

Rule is at position 4 (before the blanket REJECT). Persisted to `/etc/iptables/rules.v4` and `/etc/iptables/rules.v6`.

## Tailscale (2026-06-19)

| Field | Value |
|---|---|
| `tailscaled` service | active |
| Version | 1.98.4 |
| Account | `alpozben@gmail.com` (user ID 4558614140497612) |
| Tailscale IP | `100.76.208.31` (v4), `fd7a:115c:a1e0::9f39:d020` (v6) |
| Registered hostname | `hermes` (lowercase — `tailscale up` reset from OS `Hermes`) |
| `--accept-routes` | enabled |
| `--advertise-exit-node` | **approved on the server side, but admin-side toggle still pending in control plane** |
| Key expiry | **still set to 2026-12-16** — user must clear in https://login.tailscale.com/admin/settings/preferences |
| Health | No warnings about IP forwarding after the sysctl fix |

### Recipe used (this session)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-tailscale.conf > /dev/null
echo "net.ipv6.conf.all.forwarding=1" | sudo tee /etc/sysctl.d/99-tailscale-ipv6.conf > /dev/null
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale-ipv6.conf
sudo systemctl enable --now tailscaled
sudo tailscale up --ssh=false --accept-routes --advertise-exit-node
```

First `tailscale up` blocked on browser auth — user completed it from their end. The OS hostname `Hermes` was reset to `hermes` (lowercase) by `tailscale up`; if a specific name is needed, re-run with `--hostname=hermes-server`.

### Still outstanding (admin-side)

1. **Exit-node approval** — `tailscale status --json | jq '.Self.ExitNodeOption'` returns `false`. User must approve at https://login.tailscale.com/admin/machines → `hermes` → Edit route settings → toggle Use as exit node → Save.
2. **Key expiry disable** — `KeyExpiry: 2026-12-16T22:02:27Z`. User must set "Key expiry" to None at https://login.tailscale.com/admin/settings/preferences.

## Past-session reference

The server was first recorded in a session on 2026-06-19 as fact #50 in holographic memory:
> "Alp's second cloud server 'hermes' at 130.61.122.103, hostname 'Hermes', user ubuntu. SSH private key at /mnt/sda2/UBuntu_Backup/Oracle Cloud  Keys/Hermes.key (capital H — case-sensitive on Linux). Tailscale was not installed as of 2026-06-19."

**Fact #50 is now stale** (Tailscale IS installed and authed). A future cleanup pass should either update it or add a follow-up fact #51 noting the current state. The `memory` block was also updated to reflect the install.
