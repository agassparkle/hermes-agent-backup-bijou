# Remote server discovery checklist

Use this when inventorying a remote Linux host over SSH.

## Minimal evidence chain
- Connect with the provided key and user.
- Confirm identity:
  - `hostname`
  - `whoami`
  - `uptime -p`
- Check system services:
  - `systemctl list-units --type=service --state=running --no-pager --no-legend`
- Check user/app managers:
  - `pm2 list`
  - `systemctl --user list-units --state=running`
- Check containers:
  - `docker ps`
  - if denied, retry with `sudo docker ps`
- Inspect interesting processes:
  - `ps -eo pid,ppid,comm,args --forest`
  - `ps -u <user> -o pid,ppid,comm,args --forest`

## How to report results
- Separate confirmed facts from likely inference.
- Mention the command source when it matters:
  - "PM2 shows ..."
  - "systemd shows ..."
  - "sudo docker ps shows ..."
- If a subsystem is inaccessible, say what blocked it and what fallback you used.

## Good inventory pattern
- Host identity
- Uptime
- User-facing apps
- Proxy / ingress
- Containers
- Other noteworthy services

## Common interpretation rules
- Empty `docker ps` means no running containers, not that Docker is unused.
- PM2 app names are often the most user-facing label for Node apps.
- Reverse proxies like Caddy or Nginx can be running even when the app itself is a separate process.
- A generic service name is not enough; use process args or paths to identify the real app.
