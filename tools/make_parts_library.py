"""
-------------------------------
Author: Chirag Khanna
Date: 14-11-2026
-------------------------------

Build cad/parts_library.FCStd from biped/parts.py (one object per part).

Run:  tools/fc_run.sh tools/make_parts_library.py
STEP parts are imported as-is; the others are dimensioned placeholder solids,
good enough for layout and clearance checks while designing the robot. Each object gets Mass_g,
Qty, Verified and Note properties so the assembly can read masses later.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))   # FreeCAD's Python can't see pip installs

import FreeCAD as fc  # noqa: E402
import Part  # noqa: E402
from biped.parts import PARTS  # noqa: E402

doc = fc.newDocument("parts_library")
x = 0.0
for name, p in PARTS.items():
    if p["shape"] == "step":
        shape = Part.read(str(ROOT / p["step"]))
    elif p["shape"] == "box":
        shape = Part.makeBox(*p["size"])
    elif p["shape"] == "cyl":
        d, length = p["size"]
        shape = Part.makeCylinder(d / 2, length)
    elif p["shape"] == "ring":
        od, id_, w = p["size"]
        shape = Part.makeCylinder(od / 2, w).cut(Part.makeCylinder(id_ / 2, w))
    else:
        raise ValueError(f"{name}: unknown shape {p['shape']}")

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    bb = shape.BoundBox
    obj.Placement.Base = fc.Vector(x - bb.XMin, -bb.YMin, -bb.ZMin)   # lay parts out in a row
    x += bb.XLength + 15.0
    for prop, kind, val in (("Mass_g", "App::PropertyFloat", float(p["mass"])),
                            ("Qty", "App::PropertyInteger", int(p["qty"])),
                            ("Verified", "App::PropertyBool", bool(p["verified"])),
                            ("Note", "App::PropertyString", p["note"])):
        obj.addProperty(kind, prop, "Part data")
        setattr(obj, prop, val)
    print(f"{name:18s} bbox {bb.XLength:6.1f} x {bb.YLength:6.1f} x {bb.ZLength:6.1f} mm")

doc.recompute()
out = ROOT / "cad" / "parts_library.FCStd"
doc.saveAs(str(out))
print("saved", out)
