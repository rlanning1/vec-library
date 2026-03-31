"""
parser.py — Initialization string parsing logic for the Vec library.

Handles rectangular and polar form initialization strings, including
optional attribute switches appended after the vector value.
"""

import re
import math


# ---------------------------------------------------------------------------
# Attribute extraction helper
# ---------------------------------------------------------------------------

# Matches backslash-prefixed attribute tokens, e.g. \rad \parallel
_ATTR_RE = re.compile(r'\\[A-Za-z0-9_]{1,15}')

# Number pattern: integer, decimal, or scientific notation (e.g. 1e-12, 3.5E+2)
_NUM = r'\d+(?:\.\d+)?(?:[eE][+-]?\d+)?'


def _split_attrs(init_str: str) -> tuple:
    """
    Separate attribute switches from the vector value portion of the string.

    Returns
    -------
    (value_str, attrs)
        value_str : the portion of init_str that precedes any attributes
        attrs     : list of attribute strings found (e.g. ['\\rad', '\\parallel'])
    """
    from vec.core import VecError

    attrs = []
    value_part = init_str

    first_match = _ATTR_RE.search(init_str)
    if first_match:
        value_part = init_str[: first_match.start()]
        attr_part = init_str[first_match.start():]
        attrs = _ATTR_RE.findall(attr_part)

        raw_tokens = re.findall(r'\\[^\s\\]*', attr_part)
        for tok in raw_tokens:
            name = tok[1:]
            if len(name) == 0 or len(name) > 15:
                raise VecError(
                    f"Invalid attribute name '{tok}': must be 1-15 characters."
                )

    return value_part.strip(), attrs


# ---------------------------------------------------------------------------
# Rectangular form parser
# ---------------------------------------------------------------------------

_RECT_RE = re.compile(
    r'^'
    r'(?P<real>[+-]?\s*' + _NUM + r')?'   # optional real component
    r'\s*'
    r'(?:'
        r'(?P<isign>[+-])\s*j'             # sign before j
        r'(?P<imag>' + _NUM + r')'         # imaginary magnitude
    r')?'
    r'\s*$'
)


def _parse_rect(value_str: str):
    """
    Try to parse value_str as a rectangular-form vector.
    Returns (real, imag) on success, or None if not a rectangular form.
    """
    m = _RECT_RE.match(value_str)
    if m is None:
        return None

    real_str = m.group("real")
    isign = m.group("isign")
    imag_str = m.group("imag")

    if real_str is None and isign is None:
        return None

    if re.search(r'[A<∠]', value_str):
        return None

    real = float(real_str.replace(" ", "")) if real_str else 0.0

    if isign is not None and imag_str is not None:
        imag = float(imag_str)
        if isign == "-":
            imag = -imag
    elif isign is None and imag_str is None:
        imag = 0.0
    else:
        return None

    return real, imag


# ---------------------------------------------------------------------------
# Polar form parser
# ---------------------------------------------------------------------------

_POLAR_RE = re.compile(
    r'^'
    r'(?P<mag>[+-]?\s*' + _NUM + r')'     # magnitude (may be negative)
    r'(?:'
        r'\s*'
        r'(?:'
            r'(?P<asign>[+-])\s*[Aa]'      # +A / -A notation
            r'|(?P<lt><)'                   # < notation
            r'|(?P<ang_sym>\u2220)'         # angle symbol notation
        r')'
        r'\s*'
        r'(?P<angle>' + _NUM + r')'        # angle magnitude
    r')?'
    r'\s*$'
)


def _parse_polar(value_str: str, rad_flag: bool):
    """
    Try to parse value_str as a polar-form vector.
    Returns (real, imag) on success, or None if not a polar form.
    """
    m = _POLAR_RE.match(value_str)
    if m is None:
        return None

    mag_str = m.group("mag")
    if mag_str is None:
        return None

    mag = float(mag_str.replace(" ", ""))

    angle_str = m.group("angle")
    asign = m.group("asign")

    if angle_str is not None:
        angle = float(angle_str)
        if asign == "-":
            angle = -angle
    else:
        angle = 0.0

    if not rad_flag:
        angle_rad = math.radians(angle)
    else:
        angle_rad = angle

    if mag < 0:
        mag = abs(mag)
        angle_rad += math.pi

    real = mag * math.cos(angle_rad)
    imag = mag * math.sin(angle_rad)
    return real, imag


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def parse(init_str: str):
    """
    Parse an initialization string into (real, imag, attributes).

    Parameters
    ----------
    init_str : str
        A vector initialization string.

    Returns
    -------
    (real, imag, attrs)

    Raises
    ------
    VecError
        If the string cannot be parsed as a valid vector.
    """
    from vec.core import VecError

    if not isinstance(init_str, str):
        raise VecError("Initialization string must be a str.")

    value_str, attrs = _split_attrs(init_str)

    if not value_str:
        raise VecError(f"Empty vector value in initialization string: '{init_str}'")

    rad_flag = r"\rad" in attrs

    if "j" in value_str.lower():
        result = _parse_rect(value_str)
        if result is not None:
            real, imag = result
            return real, imag, attrs
        raise VecError(
            f"Could not parse rectangular initialization string: '{init_str}'"
        )

    result = _parse_polar(value_str, rad_flag)
    if result is not None:
        real, imag = result
        return real, imag, attrs

    raise VecError(f"Could not parse initialization string: '{init_str}'")
