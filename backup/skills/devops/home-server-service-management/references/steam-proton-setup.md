# Steam / Proton Setup Reference

## Steam Installation (Ubuntu 20.04+)

```bash
# Official .deb from Steam (newer than repo version)
wget -qO /tmp/steam.deb https://cdn.cloudflare.steamstatic.com/client/installer/steam.deb
sudo apt update && sudo apt install -y /tmp/steam.deb
```

## Proton-GE Manual Installation

When `protonup` CLI fails (returns HTML "Not Found" page), use GitHub API directly:

```bash
# 1. Find latest GE-Proton tag
curl -sL https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases | jq -r '.[].tag_name' | head -1

# 2. Get download URL for specific version (e.g., GE-Proton10-34)
curl -sL https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/tags/GE-Proton10-34 \
  | jq -r '.assets[] | select(.name | test("tar.gz$")) | .browser_download_url'

# 3. Download and extract to Steam compatibilitytools.d
mkdir -p ~/.local/share/Steam/compatibilitytools.d
cd ~/.local/share/Steam/compatibilitytools.d
curl -L -o GE-Proton10-34.tar.gz https://github.com/GloriousEggroll/proton-ge-custom/releases/download/GE-Proton10-34/GE-Proton10-34.tar.gz
tar -xzf GE-Proton10-34.tar.gz
rm GE-Proton10-34.tar.gz
```

## Steam Configuration for Proton

1. Launch Steam, log in
2. **Settings → Compatibility**:
   - ✅ Enable Steam Play for supported titles
   - ✅ Enable Steam Play for all other titles
   - Run other titles with: **GE-Proton10-34** (or latest installed)

## Game-Specific Launch Options

| Game (App ID) | Launch Options | Notes |
|---------------|----------------|-------|
| TBH: Task Bar Hero (3678970) | `PROTON_USE_WINED3D=1 %command%` | Fixes mouse input; black bg without Proton-LayeredOverlay |
| TBH: Task Bar Hero (3678970) | `WINE_LAYERED_OVERLAY_ALPHA=1 %command%` | Requires Proton-LayeredOverlay build for transparency |

## TBH: Task Bar Hero Specifics (from ProtonDB)

- **ProtonDB Rating:** Gold (22 reports)
- **Best:** Proton-LayeredOverlay (`proton-layered-overlay-v1`) + `WINE_LAYERED_OVERLAY_ALPHA=1 %command%` — full transparency
- **Common:** GE-Proton10-34 + `PROTON_USE_WINED3D=1 %command%` — playable, black background
- **Issues:** Transparent window renders black; mouse clicks pass through; window management problems
- **GPU:** Minimum GTX 750 Ti / RX 460 (2GB VRAM); Intel integrated (Xeon E3-1200 v3/4th Gen) may struggle

## Headless CLI Launch (after GUI config)

```bash
# Find appmanifest
grep -l '"appid"\t\t"3678970"' ~/.steam/steam/steamapps/appmanifest_*.acf

# Launch with specific Proton
STEAM_COMPAT_CLIENT_INSTALL_PATH=~/.steam/steam \
STEAM_COMPAT_DATA_PATH=~/.steam/steam/steamapps/compatdata/3678970 \
~/.local/share/Steam/compatibilitytools.d/GE-Proton10-34/proton run \
  ~/.steam/steam/steamapps/common/TBH\ Task\ Bar\ Hero/TBH_Task_Bar_Hero.exe
```

## Troubleshooting

- **Steam won't start on Wayland:** `GDK_BACKEND=x11 steam`
- **Proton not showing in dropdown:** Restart Steam after extracting to `compatibilitytools.d/`
- **Game crashes on launch:** Check `~/.steam/steam/steamapps/compatdata/<appid>/pfx/drive_c/users/steamuser/Temp/` for logs
- **Missing 32-bit libs:** `sudo apt install -y lib32gcc-s1 libc6-i386 libstdc++6:i386`