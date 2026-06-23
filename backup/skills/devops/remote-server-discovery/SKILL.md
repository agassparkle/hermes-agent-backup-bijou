---
name: remote-server-discovery
description: Discover what is running on a remote Linux server over SSH, map service names to actual apps, and produce a grounded server inventory.
---

# Remote server discovery

Use this skill when the user asks what is running on a server, wants to identify apps on a host, or asks you to get familiar with a remote machine over SSH.

## Goal
Produce a grounded inventory of the server: host identity, uptime, exposed services, app processes, containerized workloads, and reverse proxy clues.

## Workflow
1. Connect with the provided SSH key and username.
2. Verify host identity immediately:
   - `hostname`
   - `whoami`
   - `uptime -p`
3. Check what is running at the OS level:
   - `systemctl list-units --type=service --state=running`
   - `systemctl --user list-units --state=running` when user services matter
4. Check app managers and common runtimes:
   - `pm2 list`
   - `docker ps` or `sudo docker ps` if the socket is restricted
   - `ps` for the target user and any interesting parent/child trees
5. Look for reverse proxies / ingress layers:
   - `caddy`, `nginx`, `traefik`, `cloudflared`, `tailscaled`, or similar services
6. Map names to actual software:
   - inspect command lines and paths
   - use process arguments, app directories, and service names to distinguish app names from generic processes
   - for Foundry VTT specifically, check the PM2 app names, the `resources/app/package.json` version, and the `--dataPath` directory
   - if Foundry is present, inspect `Data/Config/options.json`, `Data/worlds/*/world.json`, `Data/systems/*/system.json`, and `Data/modules/*/module.json`
7. Summarize only confirmed facts first, then add reasonable inferences separately.

## Output format
- Start with the host identity.
- List confirmed running apps/services in short bullets.
- Separate "confirmed" from "likely" when identification is inferred from process names or paths.
- If a key subsystem cannot be inspected, say what blocked it and whether a fallback was used.

## Pitfalls
- An empty `docker ps` means no running containers, not that Docker is unused.
- PM2 app names are often the clearest source of truth for Node-based app deployments.
- Docker socket permission errors are often resolved by re-running with `sudo`; do not treat them as a final conclusion.
- A reverse proxy service can make the externally visible app different from the local process name.
- Do not claim an app is present unless you have process, service, or configuration evidence.

## Notes
- A running systemd service is not necessarily the user-facing app; inspect process args when the service name is generic.
- For browser-based self-hosted apps, it is often useful to check whether they are served behind a proxy such as Caddy.

## Reference files
- references/remote-server-discovery.md: concise checklist, command patterns, and example evidence structure.
- references/foundry-vtt.md: Foundry VTT-specific identification notes and server mapping hints.
- references/foundry-oracle-caddy.md: the user's Oracle Cloud Foundry setup, versions, ports, and proxy mapping.
