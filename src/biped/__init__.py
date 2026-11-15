"""
-------------------------------
Author: Chirag Khanna
Date: 14-11-2026
-------------------------------

biped: Python package for a small Cassie-style (Legolas-based) bipedal robot.

Modules:
  leg_kinematics  side-view leg kinematics: closes the two push-rod loops of each
               leg and returns joint and linkage positions for given servo angles
  parts        sizes and masses of the bought parts (servos, Jetson Nano, IMU,
               battery, bearings, screws), shared by the CAD scripts and the sim

Everything here is plain Python + math, so FreeCAD's own Python can import it.
"""
