#!/usr/bin/env bash
# -------------------------------
# Author: Chirag Khanna
# Date: 14-11-2026
# -------------------------------
# Run a FreeCAD script in a fresh GUI instance, print its traceback (if any), then quit.
# Usage: tools/fc_run.sh tools/make_parts_library.py
# Why: CROSS needs the GUI, and GUI mode hides script errors, so a small wrapper
# writes the traceback to a log and force-quits FreeCAD afterwards.
# Uses `freecad` from PATH (tested with the FreeCAD 1.1 AppImage).
# Override with FREECAD=/path/to/freecad. Close any open FreeCAD window first:
# a single-instance FreeCAD would swallow the script.
set -euo pipefail
FREECAD="${FREECAD:-$(command -v freecad || echo "$HOME/Applications/FreeCAD/AppRun")}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/fc_run.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
LOG="$WORK/fc_run.log"
cat > "$WORK/fc_run_wrapper.py" <<PY
import os, traceback, runpy
with open("$LOG", "w") as f:
    try:
        runpy.run_path(os.environ["SCRIPT"], run_name="__main__")
        f.write("OK\n")
    except SystemExit:
        f.write("OK\n")
    except BaseException:
        f.write(traceback.format_exc())
os._exit(0)
PY
SCRIPT="$(realpath "$1")" timeout "${FC_TIMEOUT:-300}" "$FREECAD" "$WORK/fc_run_wrapper.py" >/dev/null 2>&1 || true
cat "$LOG" 2>/dev/null || { echo "no log: FreeCAD did not run the script (another --single-instance FreeCAD open?)"; exit 1; }
grep -q '^OK$' "$LOG"
