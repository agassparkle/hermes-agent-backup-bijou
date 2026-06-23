---
name: linux-headless-gui-apps
description: Run Qt/GTK GUI applications on headless Linux servers using virtual framebuffers or offscreen platforms.
---

# Running GUI Applications on Headless Linux Servers

Use this skill when you need to run a graphical application (Qt, GTK, Electron, etc.) on a server without a display.

## Core Techniques

### 1. Qt Applications — `QT_QPA_PLATFORM=offscreen`

Set the `QT_QPA_PLATFORM` environment variable to `offscreen` before launching the app. This tells Qt to use its offscreen platform plugin instead of X11/Wayland.

```bash
QT_QPA_PLATFORM=offscreen qbittorrent --webui-port=8080 --no-splash
```

**Works for:** qBittorrent, VLC, any Qt5/Qt6 application with Web UI or CLI control.

**Caveats:**
- Requires the `qt6-qpa-plugins` or `qt5-qpa-plugins` package (usually installed with the app)
- Some apps may still need `XDG_RUNTIME_DIR` set: `XDG_RUNTIME_DIR=/tmp/runtime-$USER`

### 2. Xvfb (X Virtual Framebuffer)

For apps that don't support offscreen rendering or need a full X server:

```bash
# Install
sudo apt install -y xvfb

# Run with virtual display :99
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
your-gui-app
```

**Works for:** Almost any X11 application (GTK, Electron, older Qt, etc.)

**Caveats:** Higher memory/CPU overhead than `offscreen`.

### 3. Wayland — `WAYLAND_DISPLAY` with `weston` or `kwin_wayland`

Less common for servers; prefer Xvfb or offscreen.

## Common Applications & Flags

| Application | Offscreen Flag | Web UI Port Flag |
|-------------|----------------|------------------|
| qBittorrent | `QT_QPA_PLATFORM=offscreen` | `--webui-port=8080` |
| VLC | `QT_QPA_PLATFORM=offscreen` | `--extraintf=http --http-port=8080` |
| Calibre | `QT_QPA_PLATFORM=offscreen` | `--port=8080` |

## Verification Checklist

After starting the app:
1. `pgrep -f <app-name>` — process is running
2. `ss -tlnp | grep :<port>` — web UI port is listening
3. `curl http://localhost:<port>` — HTTP response received

## Pitfalls

- **Don't use `nohup` or `&` in foreground terminal commands** — use `terminal(background=true)` so Hermes can track the process.
- **GUI apps often write to stderr** — capture logs with `2>&1 | tee /tmp/app.log` or check the background process log via `process(action='log')`.
- **First run may create config directories** — specify `--profile` or `--config` to control where.
- **Permission issues on config dirs** — run as the correct user, not root.

## Reference Files

- `references/qbittorrent-headless.md` — qBittorrent-specific flags, config paths, and troubleshooting.