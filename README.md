<!--
-------------------------------
Author: Chirag Khanna
Date: 15-11-2026
-------------------------------
-->

# Biped Robot

A small, open-source, **Cassie-style bipedal robot** (legs and pelvis only), built
to learn underactuated control and **reinforcement learning (RL)**: train a walking
policy in **MuJoCo** and run it on a **Jetson Nano**.

The leg design is based on Cassie by Agility Robotics, adapted to serial-bus servos, a Jetson Nano.

> **Status: early development.** Leg kinematics and the parts library are done.
> CAD, the MuJoCo model, controllers and RL training are being added.

---

## Contents

1. [The robot at a glance](#the-robot-at-a-glance)
2. [How the leg works](#how-the-leg-works)
3. [Hardware (bill of materials)](#hardware-bill-of-materials)
4. [Repository layout](#repository-layout)
5. [Setup on your computer](#setup-on-your-computer)
6. [Build your own: what to change](#build-your-own-what-to-change)
7. [Credits and licences](#credits-and-licences)

---

## The robot at a glance

| | |
|---|---|
| Legs | 2, Cassie-style ("bird" legs: the backward bend is the ankle) |
| Servos | 10 = 5 per leg: hip roll, hip yaw, hip pitch, knee, toe |
| Servo models | 8 × Feetech **ST3215** (30 kg·cm, 12 V) · 2 × Feetech **STS3250** (50 kg·cm, 12 V) at the knees |
| Passive joints | 1 per leg: the **tarsus** (ankle) joint, set by a rod |
| Brain | **NVIDIA Jetson Nano** (runs the RL policy) |
| IMU | **ST LSM6DSV16X** (6-axis, on-chip sensor fusion) on the pelvis |
| Power | 3S LiPo (11.1 V) + 5 V buck converter for the Jetson |
| Mass (bought parts) | ≈ 1.16 kg, before printed parts |

Leg lengths (mm): thigh **80** · shin **211.5** · tarsus **169.2** · foot **52**.
Standing (HOME) pose: hip pitch 32.3°, knee 95°, toe servo 54° → toe joint straight
under the hip, 251 mm below it, foot level.

## How the leg works

Side view, facing right:

```
                     ■ HIP PITCH  (ST3215)
                      \
                thigh  \  80 mm
                        ■ KNEE  (STS3250)
                       /
            shin      /  211.5 mm
                     /
   TARSUS joint ●   /      ← bends backward; NO motor (passive)
   (passive)     \          rod 1 (179 mm, from the thigh) sets its angle
                  \  tarsus  169.2 mm
                   \
                    ● TOE joint  ← ST3215 on the tarsus pushes it via rod 2 (115 mm)
                     ▬▬▬▶ foot 52 mm
```

- **Hip pitch** swings the whole leg.
- **Knee** sets the leg length: with rod 1 riding on the thigh, the tarsus follows
  the knee only, and the toe joint stays almost straight under the hip.
- **Rod loops:** each rod is pinned at both ends, so its free end must lie on two
  circles at once. `circle_intersection()` finds that point; if the circles don't
  meet, the pose is impossible (the knee works between about 69° and 128°).

## Hardware (bill of materials)

Source of truth: [`src/biped/parts.py`](src/biped/parts.py) (sizes, masses, quantities).
Print the list with `python -m biped.parts`. Entries marked *estimate* still need
to be weighed or measured.

| Part | Qty | Notes |
|---|---|---|
| Feetech ST3215 (STS3215-C018), 12 V 30 kg·cm | 8 | hip roll, yaw, pitch, toe |
| Feetech STS3250, 12 V 50 kg·cm | 2 | knees |
| NVIDIA Jetson Nano dev kit | 1 | policy runtime |
| ST LSM6DSV16X IMU breakout | 1 | rigid mount near the pelvis centre of mass |
| Waveshare Bus Servo Adapter (A) | 2 | one serial bus per leg |
| 12 V → 5 V ≥ 4 A buck converter | 1 | powers the Jetson |
| 3S LiPo ≈ 2200 mAh | 1 | |
| 624ZZ bearings (4 × 13 × 5) | 12 | every idle pivot |
| M4 ball-joint rod ends + M4 threaded rod | 8 + 4 | rods 1 and 2 |
| M3 and M4 screws | ~76 | |
| PETG filament | ~0.5 kg | printed parts |

## Repository layout

```
src/biped/                Python package (pure Python, also importable by FreeCAD)
  leg_kinematics.py         leg kinematics + rod-loop closure
  parts.py                  bought parts: size, mass, quantity
tests/
  test_leg_kinematics.py    checks for the leg kinematics
tools/
  make_parts_library.py     builds cad/parts_library.FCStd from src/biped/parts.py
  fc_run.sh                 runs a FreeCAD script in a fresh GUI and prints errors
cad/vendor/               third-party CAD (servo STEP), see cad/vendor/README.md
environment.yml           conda environment (sim, control, RL tools)
pyproject.toml            makes `biped` installable: pip install -e .
```

## Setup on your computer

Tested on **Ubuntu 22.04**.

**1. Clone**
```bash
git clone https://github.com/CK-chirag/biped_robot.git
cd biped_robot
```

**2. Python environment** (needs [Miniconda](https://docs.conda.io/en/latest/miniconda.html))
```bash
conda env create -f environment.yml
conda activate bipedrobot
pip install -e ".[test]"        # installs the `biped` package from src/ (editable) + pytest
```
> Using ROS 2 too? Its setup script adds ROS Python packages to `PYTHONPATH`, which
> breaks `pytest`. The conda env clears `PYTHONPATH` on activate; in other shells
> run `unset PYTHONPATH` first.

**3. Run the tests**
```bash
python -m pytest                         # or: python tests/test_leg_kinematics.py
```
You should see 10 `ok` lines.

**4. Print the parts list and mass budget**
```bash
python -m biped.parts
```

**5. (Optional) CAD with FreeCAD**
- Install **FreeCAD 1.1** (the AppImage works) so that `freecad` is on your PATH.
- Build the parts library:
  ```bash
  tools/fc_run.sh tools/make_parts_library.py     # writes cad/parts_library.FCStd
  ```
- For URDF export (coming next), install the
  [CROSS workbench](https://github.com/galou/freecad.cross): clone it into
  FreeCAD's `Mod` folder (`~/.local/share/FreeCAD/v1-1/Mod/` for FreeCAD 1.1) and
  install its Python dependencies `urdf-parser-py` and `xacro` into FreeCAD's Python.

## Build your own: what to change

- **Different leg lengths or rods:** edit the constants at the top of
  [`src/biped/leg_kinematics.py`](src/biped/leg_kinematics.py), then run the tests. If
  `leg_points()` returns `None` at your poses, a rod can't reach: change the rod
  length or lever arm.
- **Different parts:** edit [`src/biped/parts.py`](src/biped/parts.py) (size, mass,
  quantity) and rebuild the parts library.
- **Standing pose:** `HOME` in `src/biped/leg_kinematics.py`. Keep the knee well inside its
  reachable range so the rod loop never gets close to its limit.

## Credits and licences

- **Legolas** by daviddoo02: robot design ([MIT](https://github.com/daviddoo02/Legolas-an-open-source-biped)).
  Leg geometry from **Legolas_Controller** by Daniel Kutch
  ([MIT](https://github.com/daviddoo02/Legolas_Controller)), re-written in
  `src/biped/leg_kinematics.py`.
- **Cassie** by Agility Robotics, and Z. Xie et al., *Feedback Control for Cassie
  with Deep Reinforcement Learning*, IROS 2018: the leg concept.
- **STS3215 STEP model** from [SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100)
  by The Robot Studio (Apache-2.0), see `cad/vendor/README.md`.
- **CROSS** FreeCAD workbench by galou (LGPL-2.1), used as a tool, not included.
- **MuJoCo** by Google DeepMind.

Licence for this repository: to be added.
