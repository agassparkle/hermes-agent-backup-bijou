#!/usr/bin/env python3
"""
Hermes Cron Job — Reliable No-Agent Probe Template

Runs on schedule, checks condition, emits output ONLY when action needed.
Use with: no_agent: true, script: reliable-probe.py

Delivery note: no_agent stdout has delivery bug — use webhook/API call
inside script for user notifications, or deliver: local + separate notifier.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# hermes_tools available in cron runtime
from hermes_tools import ha_get_state, terminal, web_search

MARKER_DIR = Path("/tmp")
JOB_NAME = "reliable-probe"  # Change per job

def main():
    marker = MARKER_DIR / f"{JOB_NAME}-{datetime.now().strftime('%F')}.marker"

    # Already ran today?
    if marker.exists():
        return 0  # Silent success

    # --- YOUR LOGIC HERE ---
    # Example: Check HA entity
    result = ha_get_state(entity_id="media_player.example")
    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        return 1

    state = result.get("state", "unknown")

    # Condition: trigger on "playing" or "on"
    if state not in ("playing", "on"):
        return 0  # Silent, will retry next tick

    # Condition met — create marker
    term_result = terminal(command=f"touch {marker}")
    if term_result.get("exit_code", 1) != 0:
        print(f"ERROR: Failed to create marker: {term_result}", file=sys.stderr)
        return 1

    # --- NOTIFICATION ---
    # Option A: Print for delivery (buggy in no_agent)
    # print(f"🔔 Alert: Entity is {state}")

    # Option B: Call webhook directly (reliable)
    # import requests
    # requests.post("https://your-hermes/webhooks/alert", json={"state": state})

    # Option C: Write to file for external pickup
    # Path("/tmp/alert-pending").write_text(json.dumps({"state": state, "time": datetime.now().isoformat()}))

    return 0

if __name__ == "__main__":
    sys.exit(main())