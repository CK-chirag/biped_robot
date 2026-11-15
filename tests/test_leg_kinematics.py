"""
-------------------------------
Author: Chirag Khanna
Date: 14-11-2026
-------------------------------

Tests for biped/leg_kinematics.py.

What is checked:
  * circle_intersection(): known answers (unit circles, 3-4-5 triangle), the
    "left side" rule, and None when two circles don't meet
  * leg_points(): both rod loops close at the default pose with the exact rod
    lengths, the pose matches the original Legolas geometry, the leg has the
    bird ("digitigrade") shape, hip pitch does not change the passive tarsus
    angle (rod 1 rides on the thigh), the knee range 70-125 deg is reachable,
    and the HOME pose stands level with the toe joint under the hip

Run (after `pip install -e .`):  python -m pytest tests/
      or:  python tests/test_leg_kinematics.py"""
from math import isclose, sqrt, radians

from biped import leg_kinematics as L


def close(p, q, tol=1e-6):
    return isclose(p[0], q[0], abs_tol=tol) and isclose(p[1], q[1], abs_tol=tol)


def test_two_unit_circles_left_point():
    # centres 1 apart, both radius 1 -> meet at (0.5, ±0.866); left of (0,0)->(1,0) is +y
    assert close(L.circle_intersection((0, 0), 1, (1, 0), 1), (0.5, sqrt(3) / 2))


def test_left_side_flips_with_direction():
    # going from (1,0) to (0,0) the left side is -y
    assert close(L.circle_intersection((1, 0), 1, (0, 0), 1), (0.5, -sqrt(3) / 2))


def test_3_4_5_triangle():
    # rod of 3 from origin, nub radius 4 around (5,0): right angle at P
    assert close(L.circle_intersection((0, 0), 3, (5, 0), 4), (1.8, 2.4))


def test_no_intersection_returns_none():
    assert L.circle_intersection((0, 0), 1, (5, 0), 1) is None      # too far apart
    assert L.circle_intersection((0, 0), 5, (1, 0), 1) is None      # one inside the other


def test_default_pose_closes_both_loops():
    p = L.leg_points(*L.DEFAULT)
    assert p is not None
    r1, r2 = L.rod_lengths(p)
    assert isclose(r1, L.ROD1_LENGTH, abs_tol=1e-6)
    assert isclose(r2, L.ROD2_LENGTH, abs_tol=1e-6)


def test_default_pose_matches_legolas():
    # same pose as Legolas_Controller, mirrored to x-forward (values from the original geometry)
    p = L.leg_points(*L.DEFAULT)
    assert close(p["knee"], (40.0, -69.3), tol=0.1)
    assert close(p["ankle"], (-170.7, -87.7), tol=0.1)
    assert close(p["toe_joint"], (-6.2, -127.4), tol=0.1)


def test_bird_leg_shape():
    # knee in front of the hip, ankle (tarsus joint) behind it, foot pointing forward
    p = L.leg_points(*L.DEFAULT)
    assert p["knee"][0] > 0 and p["ankle"][0] < 0
    assert p["toe_tip"][0] > p["toe_joint"][0]


def test_hip_swing_does_not_change_tarsus():
    # rod 1 rides on the thigh -> passive tarsus angle depends on the knee only
    _, knee, toe = L.DEFAULT
    t0 = L.leg_points(radians(30), knee, toe)["tarsus"]
    for hip in (0, 15, 45, 60):
        assert isclose(L.leg_points(radians(hip), knee, toe)["tarsus"], t0, abs_tol=1e-9)


def test_knee_sweep_stays_solvable():
    hip, _, toe = L.DEFAULT
    for deg in range(70, 126, 5):
        assert L.leg_points(hip, radians(deg), toe) is not None, deg


def test_home_pose_stands_level_under_hip():
    p = L.leg_points(*L.HOME)
    assert abs(p["toe_joint"][0]) < 0.5                      # toe joint under the hip
    assert abs(p["toe_tip"][1] - p["toe_joint"][1]) < 0.5    # foot level
    assert isclose(-p["toe_joint"][1], 251.4, abs_tol=0.5)    # leg height


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
