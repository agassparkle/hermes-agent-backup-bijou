#!/usr/bin/env python3
"""
X11 click + key automation for unattended game/screen control.

Uses XTest extension (fake_input) so clicks pass through any focus
grabbers that block warp+sende_event. Also sets input focus and raises
the target window by wm_name match before clicking.

Install: pip install python-xlib
Usage:
    X11_CLICK_X=1045 X11_CLICK_Y=705 X11_TARGET=TaskBarHero ./x11_click.py
    X11_KEY=36 X11_TARGET=TaskBarHero ./x11_click.py   # 36 = Return keycode
"""
import os, sys, time

# Read config from env (default to TBH popup Close coords)
TARGET = os.environ.get("X11_TARGET", "TaskBarHero")
CLICK_X = int(os.environ.get("X11_CLICK_X", "1045"))
CLICK_Y = int(os.environ.get("X11_CLICK_Y", "705"))
KEY = int(os.environ["X11_KEY"]) if "X11_KEY" in os.environ else None
HOLD_MS = int(os.environ.get("X11_HOLD_MS", "60"))

os.environ.setdefault("DISPLAY", ":0")
# XAUTHORITY is intentionally not set here — caller is expected to export it

from Xlib import display, X
from Xlib.ext import xtest


def find_window(root, wm_name):
    for w in root.query_tree().children:
        try:
            if w.get_wm_name() == wm_name:
                return w
        except Exception:
            pass
    return None


def main():
    d = display.Display()
    root = d.screen().root

    win = find_window(root, TARGET)
    if not win:
        sys.exit(f"Window with wm_name={TARGET!r} not found")

    try:
        win.set_input_focus(X.RevertToParent, X.CurrentTime)
        win.raise_window()
    except Exception as e:
        print(f"warn: focus/raise failed: {e}", file=sys.stderr)
    d.sync()
    time.sleep(0.15)

    if KEY is not None:
        xtest.fake_input(d, X.KeyPress, detail=KEY)
        d.sync()
        time.sleep(0.05)
        xtest.fake_input(d, X.KeyRelease, detail=KEY)
        d.sync()
        print(f"Sent key {KEY} to {TARGET}")
        return

    # Click
    root.warp_pointer(CLICK_X, CLICK_Y)
    d.sync()
    time.sleep(0.05)

    q = root.query_pointer()
    print(f"Pointer at ({q.root_x}, {q.root_y}), child=0x{q.child.id:x}")

    xtest.fake_input(d, X.ButtonPress, detail=1)
    d.sync()
    time.sleep(HOLD_MS / 1000)
    xtest.fake_input(d, X.ButtonRelease, detail=1)
    d.sync()
    print(f"Clicked at ({CLICK_X}, {CLICK_Y}) in {TARGET}")


if __name__ == "__main__":
    main()
