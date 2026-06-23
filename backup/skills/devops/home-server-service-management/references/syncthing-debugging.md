# Syncthing connectivity debugging

Symptom: a Syncthing remote device never connects (last seen epoch 0).

## Checklist (in order)

1. **Check local device config**
   - `curl -s -H "X-API-Key: <key>" http://localhost:8384/rest/config/devices/<deviceID>`
   - Verify the device exists and has an address (static or dynamic).

2. **Check connection state**
   - `curl -s -H "X-API-Key: <key>" http://localhost:8384/rest/system/connections`
   - `connected: false` + `at: "0001-01-01..."` = never connected.
   - `lastSeen: "1970-01-01..."` = same.

3. **Test raw port reachability**
   - `nc -zv -w 5 <remote-ip> 22000`
   - If "No route to host" → server down or Oracle Cloud firewall blocking at network level.
   - If "Connection refused" → port not listening on remote.
   - Can also try pinging the remote IP first.

4. **SSH to remote and check Syncthing**
   - Is syncthing running? `systemctl --user is-active syncthing`
   - Is port 22000 listening? `sudo ss -tlnp | grep 22000`
   - Does the remote have the LOCAL device in its config? Check `~/.local/state/syncthing/config.xml` devices.

5. **Check remote firewall**
   - `sudo iptables -L INPUT -n --line-numbers` — look for REJECT rules.
   - Oracle Cloud Ubuntu images: the default iptables allows only SSH (22), ICMP, and loopback. Everything else hits a `REJECT ... icmp-host-prohibited` at the end.
   - Also check: `sudo firewall-cmd --list-all`, `sudo ufw status`.

6. **Fix: add iptables ACCEPT rule**
   ```bash
   # Insert before the REJECT rule (check line numbers first):
   sudo iptables -I INPUT <N> -p tcp -m state --state NEW -m tcp --dport 22000 -j ACCEPT
   # Persist (pick the method that works):
   sudo netfilter-persistent save                     # Ubuntu ≥22.04 (writes to /etc/iptables/rules.v4 + rules.v6)
   sudo iptables-save | sudo tee /etc/iptables/rules.v4  # Debian/Ubuntu (manual)
   # or: sudo sh -c 'iptables-save > /etc/sysconfig/iptables'  # RHEL/Oracle Linux
   ```

7. **Fix: add device to remote Syncthing via REST API**
   ```bash
   # Get remote API key first:
   python3 -c "import xml.etree.ElementTree as ET; t=ET.parse('~/.local/state/syncthing/config.xml'); print(t.find('.//apikey').text)"
   
   # Add device:
   curl -s -X POST http://localhost:8384/rest/config/devices \
     -H 'X-API-Key: <remote-key>' \
     -H 'Content-Type: application/json' \
     -d '{"deviceID": "<local-device-id>", "name": "<name>", "addresses": ["dynamic"], "compression": "metadata", "introducer": false}'
   ```

8. **Verify connection**
   - Wait a few seconds, then re-check `rest/system/connections`.
   - Connection may come through Tailscale even if public IP is configured — that's fine and expected.

## Syncthing REST API quick reference

| Endpoint | Method | Purpose |
|---|---|---|
| `/rest/config/devices` | GET/POST | List/add devices |
| `/rest/config/devices/<id>` | GET/PATCH/DELETE | Get/update/remove device |
| `/rest/config/folders` | GET/POST | List/add folders |
| `/rest/system/connections` | GET | Active connection state |
| `/rest/stats/device` | GET | Per-device stats (lastSeen, duration) |
| `/rest/db/completion` | GET | Folder completion percentage |

API key lives in `~/.local/state/syncthing/config.xml` → `<apikey>` element.

## Sharing a folder between devices

Devices connected but no data flowing? A folder must exist on both sides with the **same folder ID** and both device IDs listed.

### Add a device to an existing folder (remote already has it)

```bash
# On the remote: add local device to the folder
curl -s -X PATCH http://localhost:8384/rest/config/folders/<folder-id> \
  -H 'X-API-Key: <remote-key>' -H 'Content-Type: application/json' \
  -d '{"devices": [
    {"deviceID": "<remote-device-id>"},
    {"deviceID": "<local-device-id>"}
  ]}'
```

### Create the matching folder locally

```bash
# On the local: create folder with same ID, local path, both devices
mkdir -p <local-path>
curl -s -X POST http://localhost:8384/rest/config/folders \
  -H 'X-API-Key: <local-key>' -H 'Content-Type: application/json' \
  -d '{
    "id": "<same-folder-id>",
    "label": "<label>",
    "path": "<local-path>",
    "type": "sendreceive",
    "rescanIntervalS": 60,
    "fsWatcherEnabled": true,
    "fsWatcherDelayS": 10,
    "devices": [
      {"deviceID": "<local-device-id>"},
      {"deviceID": "<remote-device-id>"}
    ]
  }'
```

### Index churn after folder config changes

If the folder is deleted and re-added via REST API, the index exchange can get stuck:
- **Symptom**: Remote logs show `"Device <X> folder <Y> has a new index ID"` repeatedly. Local shows 0% completion despite being connected.
- **Symptom**: Remote logs show `"closed by remote: handling index for <folder>: no such folder"` — the local side closed the connection because it didn't have the folder during a delete/re-add window.
- **Symptom**: Local `rest/db/status` shows `globalFiles` stuck at a low number (only local files) and never climbs to match the remote count.
- **Fix**: **Restart Syncthing on BOTH sides.** A single-side restart is not enough — the index handler state on the remote needs to be reset too.
  ```bash
  # Remote
  ssh <remote> 'systemctl --user restart syncthing'
  # Local
  systemctl --user restart syncthing
  # Wait 15-20s for index exchange
  ```
  After restart, `globalFiles` should immediately match the remote's file count and completion reaches 100%.

## Common pitfalls

- **Both sides must know each other's device ID.** Syncthing won't connect even if the IP is reachable — the device must be in the config on both ends.
- **Oracle Cloud default iptables blocks port 22000.** Always check `iptables -L INPUT -n` on the remote. The default Ubuntu image on Oracle Cloud has `REJECT all ... reject-with icmp-host-prohibited` at the end of the INPUT chain.
- **Persist iptables rules** — a reboot loses runtime rules unless saved to `/etc/sysconfig/iptables` (Oracle Linux / RHEL) or `/etc/iptables/rules.v4` (Debian/Ubuntu).
- **No folders = no sync, but devices still connect.** A device can be connected with zero shared folders — connections and folder sharing are separate concerns.
- **Folder delete/re-add breaks index exchange.** If you remove a folder and recreate it via REST API, restart both Syncthing instances. The remote's index handler gets wedged on the old index ID and won't recover without a restart.
- **`nc` failing with "No route to host" while SSH works** = almost certainly iptables REJECT on the remote, not the server being down. Ping also fails because Oracle's default iptables only allows ICMP from established connections.
