# How to Check ProtonDB for a Game

## Quick Lookup

1. **Web:** https://www.protondb.com/app/<APP_ID>
2. **Search:** https://www.protondb.com/search?q=<game name>
3. **SteamDB:** https://steamdb.info/app/<APP_ID>/info/ → click ProtonDB link

## Reading Reports

### Rating Scale
- **Platinum** — Works perfectly out of the box
- **Gold** — Works with minor tweaks (launch options, Proton version)
- **Silver** — Runs but with significant issues
- **Bronze** — Runs but barely playable
- **Borked** — Doesn't work

### Key Fields to Check
| Field | What It Tells You |
|-------|-------------------|
| **Proton Version** | Which GE-Proton / Proton-Experimental worked |
| **Launch Options** | Exact env vars needed |
| **GPU/Driver** | Match your hardware (NVIDIA/AMD/Intel, driver version) |
| **Distro** | Arch, Ubuntu, Fedora, SteamOS — config may differ |
| **Date** | Recent reports = current Proton versions |

### Filtering Tips
- Click **your GPU vendor** (NVIDIA/AMD/Intel) to filter
- Sort by **date** (newest first) — Proton changes fast
- Look for "**Medal**" users — experienced reporters

## Steam Deck Verified vs ProtonDB

| Source | Meaning |
|--------|---------|
| **Steam Deck Verified** | Valve tested on Steam Deck (fixed hardware, SteamOS) |
| **Playable** | Works on Deck but needs user tweaks |
| **Unsupported** | Valve says it won't work on Deck |
| **ProtonDB** | Community reports across all Linux hardware |

> **Rule:** ProtonDB > Steam Deck status for desktop Linux. Deck has fixed GPU (AMD VanGogh); your desktop may differ.

## Automating Checks

```bash
# Quick curl + jq (if game has reports)
APP_ID=3678970
curl -s "https://www.protondb.com/api/v1/reports/summaries/${APP_ID}.json" | jq '.trendingTier, .totalReports, .reports[0] | {protonVersion, rating, gpu, distro, date}'
```

## Recording Your Own Results

After testing, submit to ProtonDB:
1. Launch game via Steam
2. In Steam: **View → ProtonDB** (or visit protondb.com)
3. Click **Report** → fill form (Proton version, launch options, GPU, distro, rating)

Helps the next person with your hardware!