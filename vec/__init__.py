"""
vec — Python Vector (Phasor) Library
=====================================

Public API
----------
Vec    : The vector class.
RECT   : Constant for rectangular form selection in ``asString()``.
POLAR  : Constant for polar form selection in ``asString()``.

Quick start
-----------
>>> from vec import Vec, RECT, POLAR
>>> V1 = Vec("3 +j4")
>>> V2 = Vec("5 -A36.87")
>>> V3 = V1 + V2
>>> print(V3.asString(RECT, fmt1=".4f", fmt2=".4f"))
"""

from vec.core import Vec, VecError

# Form-selector constants used with Vec.asString()
RECT  = 0   # Rectangular form
POLAR = 1   # Polar form

__all__ = ["Vec", "VecError", "RECT", "POLAR"]
__version__ = "1.0.0"
