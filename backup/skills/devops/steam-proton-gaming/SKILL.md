---
name: steam-proton-gaming
description: Install Steam, manage GE-Proton, run Windows games on Ubuntu/Debian (local display or headless)
category: devops
tags: [steam, proton, gaming, wine, ubuntu, linux]
---

# Steam + Proton Gaming on Linux

Class-level skill for installing Steam, managing Proton/GE-Proton, and running Windows games on Ubuntu/Debian servers (headless or with display).

## When to Use

- User wants to run a Windows game on Linux via Steam/Proton
- Setting up a gaming-capable Linux server (local display or remote/headless)
- Troubleshooting Proton-specific game issues (click-through, transparency, Vulkan, etc.)
- Installing GE-Proton custom builds for better compatibility

## Prerequisites

- Ubuntu 20.04+ / Debian 11+ (or derivatives)
- `sudo` access for `apt` installs
- X11 display (`:0`) or Wayland session for game rendering
- For headless: Sunshine/Moonlight, VNC, or Steam Remote Play

## Installation Steps

### 1. Install Steam (official `.deb`, not repo — newer)

```bash
wget -qO /tmp/steam.deb https://cdn.cloudflare.steamstatic.com/client/installer/steam.deb
sudo apt update && sudo apt install -y /tmp/steam.deb
```

### 2. Install GE-Proton (manual, reliable)

ProtonUp-Qt is GUI-only; the `protonup` CLI from VHSgunzo has no Linux releases. Download directly from GloriousEggroll:

```bash
mkdir -p ~/.local/share/Steam/compatibilitytools.d
cd ~/.local/share/Steam/compatibilitytools.d
curl -L -o GE-Proton10-34.tar.gz \
  https://github.com/GloriousEggroll/proton-ge-custom/releases/download/GE-Proton10-34/GE-Proton10-34.tar.gz
tar -xzf GE-Proton10-34.tar.gz && rm GE-Proton10-34.tar.gz
```

Verify: `ls ~/.local/share/Steam/compatibilitytools.d/GE-Proton10-34`

### 3. Configure Steam

Launch Steam once (`steam`) → Settings → Compatibility:
- ✅ Enable Steam Play for supported titles
- ✅ Enable Steam Play for all other titles
- **Run other titles with:** → **GE-Proton10-34** (or your installed version)

### 4. Per-Game Launch Options

Right-click game → Properties → General → Launch Options:

| Issue | Launch Option |
|-------|---------------|
| Mouse clicks pass through / not detected | `PROTON_USE_WINED3D=1 %command%` |
| Transparency broken (black background) | `WINE_LAYERED_OVERLAY_ALPHA=1 %command%` (requires Proton-LayeredOverlay) |
| Both | `PROTON_USE_WINED3D=1 WINE_LAYERED_OVERLAY_ALPHA=1 %command%` |

## Running Games from CLI (Remote/SSH)

**First, check if Steam is already running** — `pgrep -af "steam.sh -srt-logger-opened" | head -1`. If yes, **skip the two-step dance entirely** and go straight to:

```bash
DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 XAUTHORITY=/run/u...rity \
  steam steam://rungameid/<APP_ID>
```

The URL handler dispatches the launch through the running Steam client, which already has the GE-Proton compatibility tool selected and your per-game launch options (`PROTON_USE_WINED3D=1 %command%`) configured.

**Cold start (Steam not running) — two steps required:**

```bash
# 1. Start Steam with -applaunch (sets up runtime env)
DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 XAUTHORITY=/run/u...rity \
  ~/.local/share/Steam/steam.sh -applaunch <APP_ID>
# 2. Wait for Steam UI to fully load (Next Fest banner, library visible), THEN:
DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 XAUTHORITY=/run/u...rity \
  steam steam://rungameid/<APP_ID>
```

> **Pitfall:** Cold `-applaunch` alone often leaves Steam running but the game never spawns — Steam UI swallows the launch arg before the library is ready. If you see Steam on the Store page with no game, Steam is up but the app launch was dropped. Fix: trigger `steam steam://rungameid/<APP_ID>` after the UI loads.
>
> **Pitfall:** Don't blindly run the two-step dance every time — if Steam is already up, step 1 is wasted and step 2 still works. Always `pgrep steam` first. (Verified: TBH launched cleanly via single `steam steam://rungameid/3678970` when Steam was already running, June 2026.)

**Direct Proton (advanced — must replicate Steam's pressure-vessel env):**

```bash
export XDG_RUNTIME_DIR=/run/user/1000
export DISPLAY=:0
export XAUTHORITY=/run/u...team \
STEAM_COMPAT_DATA_PATH=~/.steam/steam/steamapps/compatdata/<APP_ID> \
~/.local/share/Steam/compatibilitytools.d/GE-Proton10-34/proton run \
  ~/.steam/steam/steamapps/common/<GameFolder>/<GameExe>.exe
```

> **Pitfall:** Direct `proton run` often fails with "Video driver not supported" on older iGPUs (Haswell, etc.) because Steam's SteamLinuxRuntime provides WineD3D/OpenGL fallback. Use `steam.sh -applaunch` instead.

## Known Game Fixes (Reference: `references/game-fixes.md`)

See `references/game-fixes.md` for per-game working configurations.

### TBH: Task Bar Hero (App 3678970)

- **Working:** GE-Proton10-34 + `PROTON_USE_WINED3D=1 %command%`
- **Broken:** Proton Experimental (clicks pass through)
- **Issue:** Transparent areas render black → workaround: in-game "Always on Top" toggle
- **Root cause:** Unity game using Xalia.Sdl windowing; needs Vulkan (Haswell iGPU incomplete) → `PROTON_USE_WINED3D=1` forces WineD3D/OpenGL path
- **Click-through on Unity UI popups:** With `PROTON_USE_WINED3D=1`, **synthetic** mouse clicks (XTest fake_input from Hermes) pass through Unity UI elements (e.g. OFFLINE REWARDS popup Close button) and land on underlying game objects. Confirmed live: XTest click on the popup's Close button at (1045, 705) spawned a chest in the gameplay scene underneath — the click reached the game world, not the UI. **Real human clicks DO register on the UI** (user verified: "I can click the Close. So it is working"). This is *not* a wine/Proton input bug — it's a WineD3D + Unity-UI + XTest interaction: gameplay input still works, but Unity's UI input layer ignores synthetic input. Fix: switch to Proton-LayeredOverlay custom Proton build (full transparency + clicks). Workaround for unattended play: send `Esc` key via XTest (popups often dismiss on Esc) or kill `TaskBarHero.exe` and rely on Steam Cloud save.

## Troubleshooting Checklist

| Symptom | Check |
|---------|-------|
| "Video driver not supported" / Vulkan errors | Force WineD3D: `PROTON_USE_WINED3D=1` |
| Mouse clicks don't register / pass through | Use GE-Proton (not Proton Experimental) + `PROTON_USE_WINED3D=1` |
| **Synthetic clicks (xdotool/python-xlib) don't reach Unity UI** | See `references/game-fixes.md` → TBH click-through bug. Real human works, automation doesn't. Use Proton-LayeredOverlay to fix. |
| Black background where transparency expected | Proton-LayeredOverlay + `WINE_LAYERED_OVERLAY_ALPHA=1` |
| Game won't launch from SSH | Missing `DISPLAY`, `XDG_RUNTIME_DIR`, `XAUTHORITY` |
| Steam not detecting GE-Proton | Restart Steam after extracting to `compatibilitytools.d/` |
| Cold `-applaunch` Steam UI shows Store page, no game spawns | Use `steam steam://rungameid/<APP_ID>` after Steam UI is ready (Steam swallowed the launch arg) |
| UI popup won't dismiss on click (TBH with WineD3D) | Clicks pass through Unity UI to game world. Try `Esc` key, or switch to Proton-LayeredOverlay. See `scripts/x11_click.py`. |
| Steam running but game never spawns | Cold `-applaunch` got swallowed — wait for UI, then `steam steam://rungameid/<APP_ID>` |
| Steam already running, want to launch a game | **Skip the two-step dance.** Just run `steam steam://rungameid/<APP_ID>` — single command, works directly. |
| Unity game crashes with `Xalia.Sdl.WindowingSystem` / `PlatformNotSupportedException` | Old iGPU (Haswell/Ivy Bridge) — `PROTON_USE_WINED3D=1` to skip Vulkan |
| Steam exits cleanly, no error, no game | Check `~/.steam/steam/logs/console-linux.txt` for the actual app-launch dispatch line |

### Diagnosing Silent Launch Failures

When Steam exits or hangs without a visible error, the diagnostic log is here:

```bash
tail -100 ~/.steam/steam/logs/console-linux.txt
```

Key lines to look for:
- `Adding process <pid> for gameID <APP_ID>` — Steam dispatched the launch
- `MESA-INTEL: warning: Haswell Vulkan support is incomplete` — old iGPU, force WineD3D
- `System.PlatformNotSupportedException: Video driver not supported` — Xalia/Unity can't find a usable GL/Vulkan driver
- `XOpenIM() failed` — usually harmless (locale issue)
- Missing `Adding process` lines after `-applaunch` — Steam UI wasn't ready, launch was dropped

## Remote Access (Headless Servers)

| Method | Best For |
|--------|----------|
| **Sunshine + Moonlight** | Gaming — low latency, hardware encoding |
| **Steam Remote Play** | Easiest — built into Steam, works over internet |
| **VNC (TigerVNC/x11vnc)** | Desktop access — higher latency |
| **RDP (xrdp)** | Windows clients — decent performance |

Install Sunshine:
```bash
curl -sL https://github.com/LizardByte/Sunshine/releases/latest/download/sunshine-ubuntu22.04-amd64.deb -o /tmp/sunshine.deb
sudo apt install -y /tmp/sunshine.deb
sudo systemctl enable --now sunshine
# Configure at http://<server>:47990
```

## Updating GE-Proton

Check latest at: https://github.com/GloriousEggroll/proton-ge-custom/releases

```bash
# Replace version in URL
VERSION=GE-Proton10-XX
curl -L -o $VERSION.tar.gz https://github.com/GloriousEggroll/proton-ge-custom/releases/download/$VERSION/$VERSION.tar.gz
tar -xzf $VERSION.tar.gz -C ~/.local/share/Steam/compatibilitytools.d/
rm $VERSION.tar.gz
# Restart Steam
```

## References

- `references/game-fixes.md` — per-game working configs (includes TBH click-through bug, June 2026)
- `references/protondb-queries.md` — how to check ProtonDB for a game
- `scripts/x11_click.py` — env-var-driven X11 click/key automation (X11_TARGET/X11_CLICK_X/Y/X11_KEY). Minimal API, good for one-off scripted use.
- `scripts/wine-click.py` — argparse-driven X11 click with window-name matching, motion-event support, optional keypress. Same XTest backend as x11_click.py but better for interactive use and supports `--list` to discover windows.

## Unattended X11 Input

For automation on a headless server (clicking popups, pressing keys while a game runs):

```bash
# Click a coordinate inside a target window (matches by wm_name)
XAUTHORITY=/run/u...rity X11_TARGET=TaskBarHero \
  X11_CLICK_X=1045 X11_CLICK_Y=705 \
  python3 ~/.hermes/skills/devops/steam-proton-gaming/scripts/x11_click.py

# Send a key (X11 keycode; 36=Return, 9=Esc)
XAUTHORITY=/run/u...rity X11_TARGET=TaskBarHero X11_KEY=9 \
  python3 ~/.hermes/skills/devops/steam-proton-gaming/scripts/x11_click.py
```

Requires `pip install python-xlib`. Uses XTest `fake_input` so clicks bypass GrabActive/focus-stealing apps. Sets input focus and raises the target window by `wm_name` match before clicking.

### Calibrating Click Coordinates: The Cursor Trap

`scrot` (and most X11 screenshot tools) **do not capture the hardware mouse cursor** — it's drawn as a GPU sprite on top of the framebuffer, not part of any window's pixels. This means:

- Hermes cannot see where the cursor is from its own `scrot` screenshot
- Visual estimation of button positions from screenshots is unreliable
- The user must **manually move the cursor, take their own screenshot, and paste it back** to provide ground-truth cursor coordinates

**Pattern that works:**
1. Hermes warps pointer to an estimated position
2. User moves cursor (or leaves it) and takes a screenshot showing both the cursor AND the target button
3. User pastes the image
4. Hermes reads the *cursor's* position from the user-supplied screenshot — that IS the true screen coordinate
5. Hermes warps to the *button's* position (read from the same screenshot) and asks for verification before clicking

Do not iterate blindly: "warp → scrot → guess" wastes 3+ rounds because the cursor is invisible in Hermes-side screenshots.

### When XTest Clicks Land in the Wrong Place

If a click via `x11_click.py` lands on an *underlying* game object instead of the target UI element (e.g., a Unity popup Close button), the click coordinates were right but the Wine/Proton/Unity stack is dropping UI input. Confirm with the user — they can usually click it manually, which proves the button is functional. The fix is a different Proton version (Proton-LayeredOverlay), not better coordinates.