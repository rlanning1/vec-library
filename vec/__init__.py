"""
pyVectors — Python Vector (Phasor) Library
==========================================

Public API
----------
Vector : The vector class.
Vec    : Backward-compatible alias for Vector.
RECT   : Constant for rectangular form selection in ``asString()``.
POLAR  : Constant for polar form selection in ``asString()``.
RADIANS: Global flag — set to ``True`` to default all angle I/O to radians.

Quick start
-----------
>>> from vec import Vector, RECT, POLAR
>>> V1 = Vector("3 +j4")
>>> V2 = Vector("5 -A36.87")
>>> V3 = V1 + V2
>>> print(V3.asString(RECT, fmt1=".4f", fmt2=".4f"))

Radians mode
------------
>>> import vec
>>> vec.RADIANS = True          # all new vectors default to radians I/O
>>> V = Vector("5 +A1.5708")   # angle parsed as radians (~90 deg)
>>> print(V.ang())              # returns angle in radians
>>> vec.RADIANS = False         # restore default degrees mode
"""

from vec.core import Vector, VecError

# Backward-compatible alias — existing Vec code continues to work unchanged.
Vec = Vector

# Form-selector constants used with Vector.asString()
RECT  = 0   # Rectangular form
POLAR = 1   # Polar form

# Global angle-unit flag.
# When False (default): angles are in degrees unless \rad is present on the vector.
# When True           : all newly created vectors automatically receive \rad,
#                       unless the \deg attribute is present in the init string.
RADIANS: bool = False

__all__ = ["Vector", "Vec", "VecError", "RECT", "POLAR", "RADIANS"]
__version__ = "1.1.0"
