"""
-------------------------------
Author: Chirag Khanna
Date: 14-11-2026
-------------------------------

Planar (side-view) kinematics of one leg of our Legolas-style biped.

What this file does: given the servo angles of one leg, it works out where
every joint, rod and lever of that leg is in the side view. Two of the leg's
links are moved through rods, so each rod forms a closed loop; each loop is
solved by intersecting two circles (circle_intersection). If a loop can't close,
the pose is physically impossible and leg_points() returns None.

Geometry from Legolas_Controller `kinematics.py` (Daniel Kutch 2023, MIT
licence, github.com/daviddoo02/Legolas_Controller), re-written here with two
changes:
  1. Rod 1 is mounted on the THIGH (like Cassie's achilles rod), not on the hip
     housing. So the tarsus angle follows the knee only; hip pitch just swings
     the whole leg. The pin sits where Legolas had it at its default pose.
  2. Our frame and Cassie's names (see below).

Leg, top to bottom (Cassie names, Legolas names in brackets):
  thigh   (thigh, 80)     hip-pitch servo, ST3215
  shin    (foreleg, 211.5) knee servo, STS3250
  tarsus  (shin, 169.2)   PASSIVE: angle set by rod 1 (179) pulling a 45.71 lever
  foot    (foot, 52)      toe servo (ST3215) on the tarsus: 32 crank + rod 2 (115)

Frame (side view): origin at the hip-pitch axis, x forward, z up, mm.
Servo angles (rad):
  hip_pitch : thigh angle from straight down, + swings the thigh forward
  knee      : shin relative to thigh, + folds the shin backward (bird knee)
  toe       : toe-servo crank angle relative to the tarsus (Legolas convention)
Internally the maths runs in Legolas's own frame (x backward, y up) and points
are mirrored to ours at the end.
"""
from math import atan2, cos, sin, radians, hypot, sqrt, pi

THIGH = 80.0
SHIN = 211.5
TARSUS = 169.2
FOOT = 52.0

# Rod 1 (passive): thigh pin -> lever on the tarsus, near the shin's lower end
ROD1_LENGTH = 179.0
ROD1_NUB_RADIUS = 45.71
ROD1_ANGLE_OFFSET = radians(-17.39)

# Rod 2 (toe drive): servo crank on the tarsus -> lever on the foot
TOE_SERVO_OFFSET = (30.83, 19.25)   # servo shaft position in the tarsus frame
TOE_CRANK = 32.0
ROD2_LENGTH = 115.0
ROD2_NUB_RADIUS = 49.4
ROD2_ANGLE_OFFSET = radians(53.75)

# Legolas default pose, in our convention: (hip_pitch, knee, toe)
#   Legolas thigh angle -120 deg (its frame) = 30 deg forward of straight down
DEFAULT = (radians(30), radians(115), radians(115))

# Standing pose: knee mid-range (reachable ~69..128 deg), toe joint
# straight under the hip (x = 0), foot level, toe joint 251 mm below the hip.
HOME = (radians(32.3), radians(95), radians(54))

# Rod 1 pin in the THIGH frame (Legolas frame axes, along-thigh = +x).
# Chosen so that at DEFAULT it sits at Legolas's hip-fixed point (37.5, -16).
_LEGOLAS_PIN = (37.5, -16.0)
_A_THIGH_DEFAULT = radians(-120)


def circle_intersection(c1, r1, c2, r2):
    """Point P with |P - c1| = r1 and |P - c2| = r2.

    Two circles usually meet at two points; return the one on the LEFT of the
    line going from c1 to c2 (counter-clockwise side). Return None when the
    circles don't meet (rod too short / too long for that pose).
    """
    x1, y1 = c1
    x2, y2 = c2
    dx = x2 - x1
    dy = y2 - y1
    d = hypot(dx, dy)
    if d == 0 or d > r1 + r2 or d < abs(r1 - r2):
        return None
    a = (r1**2 - r2**2 + d**2) / (2*d)
    h = sqrt(max(r1**2 - a**2, 0.0))
    ux = dx / d
    uy = dy / d
    x = x1 + a * ux + h * (-uy)
    y = y1 + a * uy + h * ux 
    return (x,y)

def _along(start, angle, length):
    return (start[0] + length * cos(angle), start[1] + length * sin(angle))


def _rot(angle, v):
    c, s = cos(angle), sin(angle)
    return (c * v[0] - s * v[1], s * v[0] + c * v[1])


def _add(p, v):
    return (p[0] + v[0], p[1] + v[1])


ROD1_PIN_THIGH = _rot(-_A_THIGH_DEFAULT, _LEGOLAS_PIN)


def _ours(p):
    """Legolas frame (x back, y up) -> our frame (x forward, z up)."""
    return (-p[0], p[1])


def leg_points(hip_pitch, knee, toe):
    """Side-view positions for the given servo angles, or None if a rod loop
    can't close (the pose is physically impossible).

    Returns a dict:
      points (x, z) mm, our frame: hip, knee, ankle (tarsus joint), toe_joint,
        toe_tip, rod1_pin, rod1_nub, toe_servo, crank_end, rod2_nub
      passive / derived joint angles (rad):
        tarsus = tarsus angle relative to the shin (the passive joint)
        foot   = foot angle relative to the tarsus (the toe joint)
    """
    a_thigh = -pi / 2 - hip_pitch                 # our hip_pitch -> Legolas angle
    knee_pt = _along((0.0, 0.0), a_thigh, THIGH)
    pin = _rot(a_thigh, ROD1_PIN_THIGH)           # rod 1 pin rides on the thigh

    a_shin = a_thigh + knee
    ankle = _along(knee_pt, a_shin, SHIN)

    # Loop 1: rod 1 from the thigh pin to a lever circling the ankle joint
    nub1 = circle_intersection(pin, ROD1_LENGTH, ankle, ROD1_NUB_RADIUS)
    if nub1 is None:
        return None
    a_tarsus = atan2(ankle[1] - nub1[1], ankle[0] - nub1[0]) + ROD1_ANGLE_OFFSET
    toe_joint = _along(ankle, a_tarsus, TARSUS)

    # Loop 2: toe servo crank on the tarsus -> rod 2 -> lever circling the toe joint
    servo = _add(ankle, _rot(a_tarsus, TOE_SERVO_OFFSET))
    crank_end = _along(servo, a_tarsus + toe, TOE_CRANK)
    nub2 = circle_intersection(crank_end, ROD2_LENGTH, toe_joint, ROD2_NUB_RADIUS)
    if nub2 is None:
        return None
    a_foot = atan2(toe_joint[1] - nub2[1], toe_joint[0] - nub2[0]) + ROD2_ANGLE_OFFSET
    toe_tip = _along(toe_joint, a_foot, FOOT)

    pts = {"hip": (0.0, 0.0), "knee": knee_pt, "ankle": ankle, "toe_joint": toe_joint,
           "toe_tip": toe_tip, "rod1_pin": pin, "rod1_nub": nub1, "toe_servo": servo,
           "crank_end": crank_end, "rod2_nub": nub2}
    out = {k: _ours(v) for k, v in pts.items()}
    out["tarsus"] = a_tarsus - a_shin
    out["foot"] = a_foot - a_tarsus
    return out


def rod_lengths(p):
    """Measured rod lengths for a solved pose (should equal the design values)."""
    return (hypot(p["rod1_nub"][0] - p["rod1_pin"][0], p["rod1_nub"][1] - p["rod1_pin"][1]),
            hypot(p["rod2_nub"][0] - p["crank_end"][0], p["rod2_nub"][1] - p["crank_end"][1]))
