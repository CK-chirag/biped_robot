"""
-------------------------------
Author: Chirag Khanna
Date: 14-11-2026
-------------------------------

Off-the-shelf parts: size and mass, used by CAD (FreeCAD) and the sim (masses).

Pure Python so FreeCAD's own Python can import it. Sizes in mm, mass in grams.
`verified=False` means the number is an estimate: weigh / measure the real part
and update it here (the sim's mass budget depends on these).

shape:
  "step" -> import `step` file (path relative to the repo), size is the bounding box
  "box"  -> size = (x, y, z)
  "cyl"  -> size = (diameter, length)
  "ring" -> size = (outer diameter, inner diameter, width)   (bearings)
"""

PARTS = {
    # --- actuators ---
    "st3215": dict(shape="step", step="cad/vendor/STS3215_03a.step", size=(45.2, 24.7, 35.0),
                   mass=55, qty=8, verified=True,
                   note="Feetech STS3215-C018 12 V 30 kg.cm: hip roll/yaw/pitch, toe"),
    "sts3250": dict(shape="box", size=(45.2, 24.7, 35.0), mass=75, qty=2, verified=False,
                    note="Feetech STS3250 12 V 50 kg.cm, knees. Size/mass assumed = STS3215 case; check datasheet"),
    # --- electronics ---
    "jetson_nano": dict(shape="box", size=(100.0, 80.0, 29.0), mass=140, qty=1, verified=False,
                        note="Jetson Nano dev kit (carrier + module + heatsink). Weigh it"),
    "imu_lsm6dsv16x": dict(shape="box", size=(25.4, 17.8, 4.6), mass=2, qty=1, verified=False,
                           note="LSM6DSV16X breakout; size depends on the board you have"),
    "servo_bus_adapter": dict(shape="box", size=(42.0, 33.0, 12.0), mass=10, qty=2, verified=False,
                              note="Waveshare Bus Servo Adapter (A), one per leg"),
    "buck_5v": dict(shape="box", size=(51.0, 26.0, 14.0), mass=15, qty=1, verified=False,
                    note="12 V -> 5 V >= 4 A buck for the Jetson (e.g. XL4015 board)"),
    "battery_3s": dict(shape="box", size=(105.0, 34.0, 24.0), mass=185, qty=1, verified=False,
                       note="3S LiPo ~2200 mAh, 11.1 V nominal"),
    # --- hardware ---
    "bearing_624zz": dict(shape="ring", size=(13.0, 4.0, 5.0), mass=3, qty=12, verified=True,
                          note="624ZZ 4x13x5 on every idle pivot (M4 shaft)"),
    "m4_rod_end": dict(shape="cyl", size=(10.0, 30.0), mass=4, qty=8, verified=False,
                       note="M4 ball-joint rod end, 2 per rod, 2 rods per leg"),
    "m4_threaded_rod": dict(shape="cyl", size=(4.0, 100.0), mass=8, qty=4, verified=False,
                            note="rod 1 (179 mm c-c) and rod 2 (115 mm c-c); length set per rod"),
    "m3x10_screw": dict(shape="cyl", size=(3.0, 10.0), mass=1, qty=60, verified=True,
                        note="M3 socket head, servo + bracket mounting"),
    "m4x20_screw": dict(shape="cyl", size=(4.0, 20.0), mass=3, qty=16, verified=True,
                        note="M4 pivots through bearings"),
}


def total_mass_g(parts=PARTS):
    """Mass of all off-the-shelf parts (printed parts are added from the CAD model)."""
    return sum(p["mass"] * p["qty"] for p in parts.values())


if __name__ == "__main__":
    for name, p in PARTS.items():
        flag = "" if p["verified"] else "  (estimate)"
        print(f"{name:18s} {p['qty']:3d} x {p['mass']:4d} g = {p['qty'] * p['mass']:5d} g{flag}")
    print(f"{'total':18s} {total_mass_g():20d} g")
