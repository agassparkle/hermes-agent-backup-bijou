# qBittorrent Headless Reference

## Installation

```bash
# Preferred: dedicated nox package (no GUI deps)
sudo apt install -y qbittorrent-nox

# Fallback: GUI version + offscreen (this session's workaround)
# qbittorrent package already installed
```

## Running with Offscreen Platform

```bash
# Basic
QT_QPA_PLATFORM=offscreen qbittorrent --webui-port=8080 --no-splash

# With custom profile directory
QT_QPA_PLATFORM=offscreen qbittorrent --webui-port=8080 --profile=/home/user/.config/qbittorrent-headless --no-splash

# Background via Hermes (tracked process)
# terminal(background=true, command="QT_QPA_PLATFORM=offscreen qbittorrent --webui-port=8080 --no-splash")
```

## Flags Used This Session

| Flag | Purpose |
|------|---------|
| `--webui-port=8080` | Web UI listens on port 8080 |
| `--no-splash` | Disable splash screen (cleaner logs) |
| `QT_QPA_PLATFORM=offscreen` | Run without X11/Wayland display |

## Default Credentials

- **Username:** `admin`
- **Password:** `adminadmin` (first run) or blank — Web UI prompts to set on first access

## Config Location

- Default: `~/.config/qBittorrent/qBittorrent.conf`
- With `--profile`: `<profile-dir>/qBittorrent.conf`

## Troubleshooting

**"could not connect to display" / "could not load Qt platform plugin 'xcb'"**
→ You're running the GUI version without `QT_QPA_PLATFORM=offscreen` or Xvfb.

**Web UI not accessible**
→ Check `ss -tlnp | grep :8080` — if not listening, check process logs via `process(action='log')`.

**Config permission errors**
→ Ensure the config directory is owned by the running user.

## Process Management

```bash
# Check if running
pgrep -f qbittorrent

# Kill existing
pkill -f qbittorrent

# Verify port
ss -tlnp | grep :8080
```