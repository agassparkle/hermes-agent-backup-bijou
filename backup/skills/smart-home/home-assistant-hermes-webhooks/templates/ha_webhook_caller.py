#!/usr/bin/env python3
"""
HA shell_command script to call a Hermes webhook.
Place at /config/python_scripts/<name>.py on the HA host.
"""

import hmac, hashlib, json, urllib.request, sys

# ==== CONFIGURE THESE ====
URL = "http://<HERMES_HOST_IP>:8644/webhooks/<route-name>"
SECRET = b"<route-secret>"  # exact secret from `hermes webhook subscribe`
PAYLOAD = b"{}"             # raw bytes; must match signature computation
# ===========================

def main():
    sig = hmac.new(SECRET, PAYLOAD, hashlib.sha256).hexdigest()
    req = urllib.request.Request(
        URL, data=PAYLOAD,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": sig  # NOT X-Hermes-Signature
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(resp.read().decode())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()