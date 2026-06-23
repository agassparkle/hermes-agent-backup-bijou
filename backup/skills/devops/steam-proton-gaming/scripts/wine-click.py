#!/usr/bin/env python3
"""
wine-click.py — Move mouse and click inside a Wine/Proton game window.

Uses python-xlib XTest extension to send synthetic input to a target X11 window
identified by WM_NAME (substring match). This works for most Wine/Proton apps,
but Unity games under WineD3D may ignore synthetic clicks on UI popups — see
the TBH section in references/game-fixes.md for the known click-through bug.

Usage:
    python3 wine-click.py --name "TaskBarHero" --x 916 --y 590
    python3 wine-click.py --name "TaskBarHero" --x 916 --y 590 --button 3   # right click
    python3 wine-click.py --name "TaskBarHero" --x 916 --y 590 --key Return # press key after click
    python3 wine-click.py --list            # list all windows with WM_NAME

Requires: python-xlib (pip install python-xlib)
"""

import argparse
import os
import sys
import time

os.environ.setdefault("DISPLAY", ":0")

from Xlib import display, X
from Xlib.ext import xtest


def find_window(d, name_substr):
    """Find first top-level window whose WM_NAME contains name_substr."""
    root = d.screen().root
    for w in root.query_tree().children:
        try:
            n = w.get_wm_name()
            if n and name_substr.lower() in n.lower():
                return w
        except Exception:
            pass
    return None


def list_windows(d):
    root = d.screen().root
    for w in root.query_tree().children:
        try:
            n = w.get_wm_name()
            cls = w.get_wm_class()
            g = w.get_geometry()
            if n or (cls and cls != (None, None)):
                print(f"0x{w.id:08x}  name={n!r:40s}  class={cls!r:30s}  size={g.width}x{g.height}  pos=({g.x},{g.y})")
        except Exception:
            pass


def move_and_click(d, target_win, screen_x, screen_y, button=1, key=None, hold_ms=80, pre_motion=True):
    """Focus target window, move X pointer, send motion event, then click."""
    # Focus + raise
    target_win.set_input_focus(X.RevertToParent, X.CurrentTime)
    target_win.raise_window()
    d.sync()
    time.sleep(0.15)

    # Warp X server pointer
    root = d.screen().root
    root.warp_pointer(screen_x, screen_y)
    d.sync()
    time.sleep(0.05)

    # XTest MotionNotify (delivered to whatever window is at the cursor)
    if pre_motion:
        xtest.fake_input(d, X.MotionNotify, x=screen_x, y=screen_y, detail=0)
        d.sync()
        time.sleep(0.1)

    # Click
    xtest.fake_input(d, X.ButtonPress, x=screen_x, y=screen_y, detail=button)
    d.sync()
    time.sleep(hold_ms / 1000.0)
    xtest.fake_input(d, X.ButtonRelease, x=screen_x, y=screen_y, detail=button)
    d.sync()
    time.sleep(0.1)

    # Optional key
    if key:
        keysym = XK_string_to_keycode(d, key)
        xtest.fake_input(d, X.KeyPress, detail=keysym)
        d.sync()
        time.sleep(0.05)
        xtest.fake_input(d, X.KeyRelease, detail=keysym)
        d.sync()


def XK_string_to_keycode(d, s):
    """Convert key name like 'Return', 'Escape', 'space' to keycode."""
    from Xlib import XK
    sym = XK.string_to_keysym(s)
    return d.keysym_to_keycode(sym)


def main():
    ap = argparse.ArgumentParser(description="Click inside a Wine/Proton game window")
    ap.add_argument("--display", default=":0")
    ap.add_argument("--name", help="Substring of window WM_NAME to target")
    ap.add_argument("--x", type=int, help="Screen X coord")
    ap.add_argument("--y", type=int, help="Screen Y coord")
    ap.add_argument("--button", type=int, default=1, help="Mouse button (1=left, 2=middle, 3=right)")
    ap.add_argument("--key", help="Key to press after click (e.g., Return, Escape)")
    ap.add_argument("--hold-ms", type=int, default=80, help="Button hold duration in ms")
    ap.add_argument("--no-motion", action="store_true", help="Skip XTest MotionNotify (some apps prefer raw click)")
    ap.add_argument("--list", action="store_true", help="List all top-level windows and exit")
    args = ap.parse_args()

    if args.display:
        os.environ["DISPLAY"] = args.display

    d = display.Display()
    if args.list:
        list_windows(d)
        return

    if not (args.name and args.x is not None and args.y is not None):
        ap.error("--name, --x, --y are required (or use --list)")

    target = find_window(d, args.name)
    if not target:
        print(f"No window with name containing {args.name!r}", file=sys.stderr)
        sys.exit(1)

    g = target.get_geometry()
    if not (g.x <= args.x <= g.x + g.width and g.y <= args.y <= g.y + g.height):
        print(f"WARN: ({args.x},{args.y}) is outside window 0x{target.id:x} bounds ({g.x},{g.y})-({g.x+g.width},{g.y+g.height})", file=sys.stderr)

    move_and_click(
        d, target, args.x, args.y,
        button=args.button,
        key=args.key,
        hold_ms=args.hold_ms,
        pre_motion=not args.no_motion,
    )
    print(f"Clicked ({args.x}, {args.y}) on window 0x{target.id:x} ({target.get_wm_name()!r})")


if __name__ == "__main__":
    main()
