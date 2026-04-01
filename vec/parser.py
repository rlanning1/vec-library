"""
parser.py — Initialization string parsing logic for the pyVectors library.

Handles rectangular and polar form initialization strings, including
optional attribute switches appended after the vector value.
"""

import re
import math


# ---------------------------------------------------------------------------
# Attribute extraction helper
# ---------------------------------------------------------------------------

# Matches backslash-prefixed attribute tokens, e.g. \rad \deg \parallel
_ATTR_RE = re.compile(r'\\[A-Za-z0-9_]{1,15}')

# ---------------------------------------------------------------------------
# Variable substitution pre-parser
# ---------------------------------------------------------------------------

# Matches a standard Python identifier (letters/underscore start, then
# letters/digits/underscore).  The negative lookbehind (?<!\\) prevents
# matching inside attribute tokens such as \rad or \parallel.
_IDENT_RE = re.compile(r'(?<!\\)\b([A-Za-z_][A-Za-z0-9_]*)\b')

# Structural tokens that must never be treated as variable names.
# 'j' is the rectangular imaginary separator; 'A' is the polar angle separator.
_PROTECTED = frozenset({'j', 'A'})

# Numeric literal pattern used to recognise already-substituted components.
_NUM_LITERAL_RE = re.compile(
    r'^[+-]?\s*\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$'
)


def _substitute_vars(init_str: str, caller_locals: dict) -> str:
    """
    Scan *init_str* for Python identifier tokens and replace each one with
    the numeric value found in *caller_locals*.

    Tokens are matched by :data:`_IDENT_RE` (standard Python identifier
    syntax).  The following tokens are **never** substituted:

    * Tokens in :data:`_PROTECTED` (``'j'`` and ``'A'``).
    * Tokens that already look like numeric literals.
    * Tokens that appear after a backslash (attribute switches such as
      ``\\rad``).

    Parameters
    ----------
    init_str : str
        Raw initialization string as supplied by the caller.
    caller_locals : dict
        ``f_locals`` dict from the caller's stack frame.

    Returns
    -------
    str
        A copy of *init_str* with every recognised variable name replaced by
        ``str(float(value))``.

    Raises
    ------
    VecError
        * If an identifier token is not found in *caller_locals*.
        * If the value found in *caller_locals* is not ``int`` or ``float``.
    """
    from vec.core import VecError

    def _replace(match: re.Match) -> str:
        name = match.group(1)

        # Never substitute structural keywords.
        # Also protect tokens of the form j<digits> or A<digits> — these are
        # the compact "operator fused with number" forms (e.g. "+j4", "+A90")
        # that the init-string syntax permits.  They are not variable names.
        if name in _PROTECTED:
            return name
        if len(name) > 1 and name[0] in _PROTECTED and name[1:].replace('.','',1).isdigit():
            return name

        # Already a plain number — nothing to do.
        if _NUM_LITERAL_RE.match(name):
            return name

        # Look up the identifier in the caller's locals.
        if name not in caller_locals:
            raise VecError(
                f"Variable '{name}' not found in caller's local scope."
            )

        value = caller_locals[name]
        if not isinstance(value, (int, float)):
            raise VecError(
                f"Variable '{name}' has type '{type(value).__name__}'; "
                f"only int and float values may be used in initialization strings."
            )

        return str(float(value))

    return _IDENT_RE.sub(_replace, init_str)

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
        attr_part  = init_str[first_match.start():]
        attrs      = _ATTR_RE.findall(attr_part)

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
        r'\s*'                             # optional space between j and magnitude
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
    isign    = m.group("isign")
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
    asign     = m.group("asign")

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
        mag       = abs(mag)
        angle_rad += math.pi

    real = mag * math.cos(angle_rad)
    imag = mag * math.sin(angle_rad)
    return real, imag


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def parse(init_str: str, global_radians: bool = False,
          caller_locals: dict = None):
    """
    Parse an initialization string into (real, imag, attributes).

    Before any parsing occurs, *init_str* is passed through the variable
    substitution pre-parser (:func:`_substitute_vars`) when *caller_locals*
    is supplied.  Any Python identifier tokens found in the string (other
    than the protected tokens ``j`` and ``A``) are looked up in
    *caller_locals* and replaced with their numeric values.

    Parameters
    ----------
    init_str : str
        A vector initialization string.  May contain Python variable names
        in place of numeric literals (e.g. ``"R11 +j Xc"`` or ``"m < a"``).
    global_radians : bool, optional
        The current value of the module-level ``RADIANS`` flag.  When
        ``True``, polar angles are interpreted as radians unless ``\\deg``
        is present in the init string (which forces degree parsing).
    caller_locals : dict or None, optional
        ``f_locals`` dict from the caller's stack frame, used for variable
        substitution.  When ``None`` no substitution is attempted.

    Returns
    -------
    (real, imag, attrs)

    Raises
    ------
    VecError
        If the string cannot be parsed as a valid vector, if a variable
        name is not found in *caller_locals*, or if a variable's value is
        not numeric.

    Notes
    -----
    ``\\rad`` in the init string always forces radian parsing regardless of
    ``global_radians``.  ``\\deg`` in the init string forces degree parsing
    regardless of ``global_radians``.  When neither is present,
    ``global_radians`` determines the default.
    """
    from vec.core import VecError

    if not isinstance(init_str, str):
        raise VecError("Initialization string must be a str.")

    # Run variable substitution before any other processing.
    if caller_locals is not None:
        init_str = _substitute_vars(init_str, caller_locals)

    value_str, attrs = _split_attrs(init_str)

    if not value_str:
        raise VecError(f"Empty vector value in initialization string: '{init_str}'")

    # Determine whether to parse the polar angle as radians:
    #   \rad present           -> radians  (explicit per-vector override)
    #   \deg present           -> degrees  (explicit per-vector override)
    #   neither present        -> follow global_radians flag
    if r"\rad" in attrs:
        rad_flag = True
    elif r"\deg" in attrs:
        rad_flag = False
    else:
        rad_flag = global_radians

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
