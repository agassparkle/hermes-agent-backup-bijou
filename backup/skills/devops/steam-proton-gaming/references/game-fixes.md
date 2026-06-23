# Per-Game Working Configurations

## TBH: Task Bar Hero (Steam App 3678970)

**Status:** Working with caveats
**Engine:** Unity (Xalia.Sdl windowing)
**Tested on:** Ubuntu 20.04, Intel Haswell iGPU (Xeon E3-1200 v3/4th Gen)

### Working Config
- **Proton:** GE-Proton10-34
- **Launch Option:** `PROTON_USE_WINED3D=1 %command%`
- **Installed Path:** `~/.local/share/Steam/compatibilitytools.d/GE-Proton10-34`

### Known Issues
| Issue | Workaround |
|-------|------------|
| Transparent areas render black (covers ⅔ screen) | In-game: toggle "Always on Top" setting |
| Proton Experimental: clicks pass through to underlying windows | Must use GE-Proton10-34 |
| **Synthetic mouse clicks (xdotool, python-xlib XTest) don't reach Unity UI popups** | Real user mouse works; for automation, use Proton-LayeredOverlay + WINE_LAYERED_OVERLAY_ALPHA=1 (see below) |

### Click-Through Bug (Synthetic Input) — IMPORTANT
**Symptom:** Real user clicks on TBH UI work fine, but automated clicks via `xdotool`, `python-xlib` `XTestFakeInput`, or `warp_pointer + send_event` **do not register on Unity UI popups** (e.g., the OFFLINE REWARDS dialog's Close button). They may register on the underlying game world (a click "passes through" the popup and hits a chest below), but the popup stays open.

**Confirmed in this session (June 2026):**
- `X server query_pointer` confirms synthetic pointer is at the correct screen coords, inside the TBH window (`child=0x6e00001`)
- `xtest.fake_input(d, X.MotionNotify, x=..., y=...)` followed by `ButtonPress`/`ButtonRelease` delivers events to the right window but Unity's UI layer ignores them
- The cursor on the actual screen (visible to a real user via remote viewer) does NOT visibly move with `warp_pointer` — Wine tracks its own cursor state separately from the X server cursor
- A human user can click the Close button manually without issue

**Root cause:** WineD3D + Unity's UI input system has a known bug where the layered window's hit-testing rejects synthetic events. Real human mouse events come through a different code path that doesn't have this issue.

**Fixes (none are perfect):**
1. **Proton-LayeredOverlay** custom Proton build (`thaylorz/proton-ge-custom` releases, `proton-layered-overlay-v1`) — fix at the Proton layer, the only known proper fix
2. Have a real user click the button (defeats automation)
3. Force-close the game process (`pkill -f TaskBarHero.exe` or `kill` the wine process) — Steam reopens and popup may re-trigger, requires save state

**Lesson for automation:** Don't assume synthetic mouse input works for Unity games under Wine. Test with a real human first; if the user can interact fine, only then is automation worth pursuing.

### Root Cause Analysis
- Game uses **layered windows** (WS_EX_LAYERED | WS_EX_TRANSPARENT) for taskbar overlay
- Xalia.Sdl windowing requires Vulkan for hardware acceleration
- Haswell iGPU has incomplete Vulkan support (MESA-INTEL warning)
- `PROTON_USE_WINED3D=1` forces WineD3D (OpenGL) fallback → works but loses DXVK performance
- Proton-LayeredOverlay (custom Proton build) fixes transparency properly but not tested on this hardware

### Launch Commands
```bash
# Step 1: Start Steam (sets up runtime env, env vars) — wait for UI to fully load
DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 XAUTHORITY=*** \
  ~/.local/share/Steam/steam.sh -applaunch 3678970

# Step 2: Once Steam UI is ready (library visible), trigger the actual launch
# (cold -applaunch often gets swallowed before UI is ready)
DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 XAUTHORITY=*** \
  steam steam://rungameid/3678970

# If Steam is already running, step 2 alone is enough.

# Direct (requires GE-Proton10-34 + PROTON_USE_WINED3D=1)
PROTON_USE_WINED3D=1 \
STEAM_COMPAT_CLIENT_INSTALL_PATH=~/.steam/steam \
STEAM_COMPAT_DATA_PATH=~/.steam/steam/steamapps/compatdata/3678970 \
~/.local/share/Steam/compatibilitytools.d/GE-Proton10-34/proton run \
  ~/.steam/steam/steamapps/common/TaskbarHero/TaskBarHero.exe
```

### ProtonDB Reference
- Rating: Gold (22 reports)
- Best reports: GE-Proton10-34 + PROTON_USE_WINED3D=1
- Proton-LayeredOverlay + WINE_LAYERED_OVERLAY_ALPHA=1 works for transparency on newer GPUs