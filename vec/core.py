"""
core.py — Vector class implementation.

Provides the Vector class for representing and manipulating complex vectors
(phasors) in both rectangular and polar forms.
"""

import math
from typing import Union

# Type alias for operands accepted by arithmetic operators
Operand = Union["Vector", int, float, complex]

# Tolerance used for equality comparisons
_EPSILON = 1e-9


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class VecError(Exception):
    """Exception raised for all pyVectors library errors."""


# ---------------------------------------------------------------------------
# Vector class
# ---------------------------------------------------------------------------

class Vector:
    """
    A complex vector (phasor) maintained in both rectangular and polar forms.

    Parameters
    ----------
    init_str : str or None
        Initialization string (see specification for syntax), or ``None``
        to create an uninitialized vector.

    Raises
    ------
    VecError
        If the initialization string cannot be parsed.

    Notes
    -----
    When the module-level ``RADIANS`` flag is ``True``, every vector created
    from an initialization string automatically receives the ``\\rad``
    attribute unless the ``\\deg`` attribute is explicitly present in the
    initialization string, in which case ``\\deg`` is retained and ``\\rad``
    is removed.
    """

    # ------------------------------------------------------------------
    # Construction and initialization
    # ------------------------------------------------------------------

    def __init__(self, init_str):
        self._initialized = False
        self._real: float = 0.0
        self._imag: float = 0.0
        self._mag: float = 0.0
        self._ang_rad: float = 0.0   # always stored in radians internally
        self._attrs: list[str] = []

        if init_str is not None:
            self._parse_and_set(init_str)

    def initialize(self, init_str: str) -> None:
        """
        Initialize (or re-initialize) the vector from an initialization string.

        If the vector was previously initialized, the attribute list is cleared
        before the new string is parsed.

        Parameters
        ----------
        init_str : str

        Raises
        ------
        VecError
            If the initialization string cannot be parsed.
        """
        self._attrs = []
        self._initialized = False
        self._parse_and_set(init_str)

    def _parse_and_set(self, init_str: str) -> None:
        """Internal: parse init_str and populate internal state."""
        from vec.parser import parse   # deferred to avoid circular import
        import vec                     # deferred to read RADIANS flag

        real, imag, attrs = parse(init_str, global_radians=vec.RADIANS)
        self._real = real
        self._imag = imag
        self._mag = math.hypot(real, imag)
        self._ang_rad = math.atan2(imag, real)

        # Apply RADIANS global flag:
        #   - If RADIANS is True and \deg is present -> keep \deg, ensure no \rad
        #   - If RADIANS is True and \deg is absent  -> inject \rad if not already present
        #   - If RADIANS is False                    -> leave attrs as parsed
        if vec.RADIANS:
            if r"\deg" in attrs:
                if r"\rad" in attrs:
                    attrs.remove(r"\rad")
            else:
                if r"\rad" not in attrs:
                    attrs.append(r"\rad")

        self._attrs = attrs
        self._initialized = True

    def _require_initialized(self) -> None:
        """Raise VecError if this vector has not been initialized."""
        if not self._initialized:
            raise VecError("Operation on an uninitialized Vector.")

    # ------------------------------------------------------------------
    # Attribute management
    # ------------------------------------------------------------------

    def addAttrib(self, attr: str) -> None:
        r"""
        Add an attribute switch to this vector.

        Parameters
        ----------
        attr : str
            Attribute name including the leading backslash, e.g. ``r'\parallel'``.
            Must be 1-15 characters (the backslash counts).

        Raises
        ------
        VecError
            If the attribute name length is invalid (empty name or > 15 chars).
        """
        name = attr[1:] if attr.startswith("\\") else attr
        if len(name) == 0 or len(name) > 15:
            raise VecError(
                f"Invalid attribute name '{attr}': name portion must be 1-15 characters."
            )
        if attr not in self._attrs:
            self._attrs.append(attr)

    def delAttrib(self, attr: str) -> None:
        """
        Remove an attribute switch from this vector.

        Does nothing if the attribute is not present.

        Parameters
        ----------
        attr : str
        """
        try:
            self._attrs.remove(attr)
        except ValueError:
            pass

    def hasAttrib(self, attr: str) -> bool:
        """
        Return ``True`` if the attribute is present, ``False`` otherwise.

        Parameters
        ----------
        attr : str
        """
        return attr in self._attrs

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @property
    def _rad_mode(self) -> bool:
        r"""True when \rad is set and \deg is not."""
        return r"\rad" in self._attrs and r"\deg" not in self._attrs

    @property
    def _deg_mode(self) -> bool:
        r"""True when the \deg attribute is set."""
        return r"\deg" in self._attrs

    @staticmethod
    def _from_rect(real: float, imag: float, attrs: list[str]) -> "Vector":
        """Create a fully initialized Vector from rectangular components and attrs."""
        v = Vector(None)
        v._real = real
        v._imag = imag
        v._mag = math.hypot(real, imag)
        v._ang_rad = math.atan2(imag, real)
        v._attrs = list(attrs)
        v._initialized = True
        return v

    @staticmethod
    def _to_vec(operand: Operand) -> "Vector":
        """
        Convert a scalar operand to a Vector.

        Scalars become a purely-real vector with no attributes.
        complex scalars are also supported for convenience.
        """
        if isinstance(operand, Vector):
            return operand
        if isinstance(operand, complex):
            return Vector._from_rect(operand.real, operand.imag, [])
        if isinstance(operand, (int, float)):
            return Vector._from_rect(float(operand), 0.0, [])
        raise VecError(
            f"Unsupported operand type for Vector arithmetic: {type(operand).__name__}"
        )

    @staticmethod
    def _union_attrs(a: list[str], b: list[str]) -> list[str]:
        """Return the union of two attribute lists (preserving order, no duplicates)."""
        combined = list(a)
        for attr in b:
            if attr not in combined:
                combined.append(attr)
        return combined

    # ------------------------------------------------------------------
    # Value extraction methods
    # ------------------------------------------------------------------

    def real(self) -> float:
        """Return the real component."""
        self._require_initialized()
        return self._real

    def img(self) -> float:
        """Return the imaginary component."""
        self._require_initialized()
        return self._imag

    def mag(self) -> float:
        """Return the magnitude."""
        self._require_initialized()
        return self._mag

    def ang(self) -> float:
        r"""
        Return the angle.

        Returns radians if ``\rad`` is set (and ``\deg`` is not);
        degrees otherwise (including when ``\deg`` is explicitly set).
        """
        self._require_initialized()
        if self._rad_mode:
            return self._ang_rad
        return math.degrees(self._ang_rad)

    def rect(self) -> tuple[float, float]:
        """Return ``(real, imaginary)`` as a tuple."""
        self._require_initialized()
        return self._real, self._imag

    def polar(self) -> tuple[float, float]:
        r"""
        Return ``(magnitude, angle)`` as a tuple.

        Angle is in radians if ``\rad`` is set (and ``\deg`` is not);
        degrees otherwise.
        """
        self._require_initialized()
        angle = self._ang_rad if self._rad_mode else math.degrees(self._ang_rad)
        return self._mag, angle

    # ------------------------------------------------------------------
    # String representation methods
    # ------------------------------------------------------------------

    def asString(self, form: int, fmt1: str = None, fmt2: str = None) -> str:
        """
        Return a formatted string representation of the vector.

        Parameters
        ----------
        form : int
            ``RECT`` (0) for rectangular form, ``POLAR`` (1) for polar form.
        fmt1 : str, optional
            Python format specification for the first component
            (real or magnitude). E.g. ``"6.2f"``.
        fmt2 : str, optional
            Python format specification for the second component
            (imaginary or angle). E.g. ``"3.0f"``.

        Returns
        -------
        str

        Raises
        ------
        VecError
            If called on an uninitialized vector or if ``form`` is not
            ``RECT`` or ``POLAR``.
        """
        from vec import RECT, POLAR   # deferred to avoid circular import

        self._require_initialized()

        if form == RECT:
            return self._as_rect_string(fmt1, fmt2)
        elif form == POLAR:
            return self._as_polar_string(fmt1, fmt2)
        else:
            raise VecError(f"Unknown form selector: {form!r}. Use RECT or POLAR.")

    def _format_component(self, value: float, fmt: str | None) -> str:
        """Format a single numeric component using an optional format spec."""
        if fmt is None:
            return str(value)
        return format(value, fmt)

    def _as_rect_string(self, fmt1: str | None, fmt2: str | None) -> str:
        """Format as rectangular: [-][real] [+|-]j[imaginary]"""
        real_str = self._format_component(self._real, fmt1)
        imag_abs = abs(self._imag)
        imag_str = self._format_component(imag_abs, fmt2)
        sign = "-" if self._imag < 0 else "+"
        return f"{real_str} {sign}j{imag_str}"

    def _as_polar_string(self, fmt1: str | None, fmt2: str | None) -> str:
        """Format as polar: [magnitude] angle [angle]"""
        angle = self._ang_rad if self._rad_mode else math.degrees(self._ang_rad)
        mag_str = self._format_component(self._mag, fmt1)
        ang_str = self._format_component(angle, fmt2)
        return f"{mag_str} \u2220 {ang_str}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        if not self._initialized:
            return "Vector(None)"
        real_str = self._as_rect_string(None, None)
        return f"Vector('{real_str}')"

    def __str__(self) -> str:
        """Informal string form (same as repr)."""
        return self.__repr__()

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    def conjugate(self) -> "Vector":
        """
        Return a new Vector that is the complex conjugate of this vector.

        Attributes are copied to the result.
        """
        self._require_initialized()
        return Vector._from_rect(self._real, -self._imag, list(self._attrs))

    def copy(self) -> "Vector":
        """
        Return a new, independent Vector with the same value and attributes.
        """
        self._require_initialized()
        return Vector._from_rect(self._real, self._imag, list(self._attrs))

    # ------------------------------------------------------------------
    # Arithmetic operator methods
    # ------------------------------------------------------------------

    def __add__(self, other: Operand) -> "Vector":
        self._require_initialized()
        other = Vector._to_vec(other)
        other._require_initialized()
        return Vector._from_rect(
            self._real + other._real,
            self._imag + other._imag,
            Vector._union_attrs(self._attrs, other._attrs),
        )

    def __radd__(self, other: Operand) -> "Vector":
        return Vector._to_vec(other).__add__(self)

    def __sub__(self, other: Operand) -> "Vector":
        self._require_initialized()
        other = Vector._to_vec(other)
        other._require_initialized()
        return Vector._from_rect(
            self._real - other._real,
            self._imag - other._imag,
            Vector._union_attrs(self._attrs, other._attrs),
        )

    def __rsub__(self, other: Operand) -> "Vector":
        return Vector._to_vec(other).__sub__(self)

    def __mul__(self, other: Operand) -> "Vector":
        self._require_initialized()
        other = Vector._to_vec(other)
        other._require_initialized()
        # (a+jb)(c+jd) = (ac-bd) + j(ad+bc)
        a, b = self._real, self._imag
        c, d = other._real, other._imag
        return Vector._from_rect(
            a * c - b * d,
            a * d + b * c,
            Vector._union_attrs(self._attrs, other._attrs),
        )

    def __rmul__(self, other: Operand) -> "Vector":
        return Vector._to_vec(other).__mul__(self)

    def __truediv__(self, other: Operand) -> "Vector":
        self._require_initialized()
        other = Vector._to_vec(other)
        other._require_initialized()
        denom = other._real ** 2 + other._imag ** 2
        if abs(denom) < _EPSILON:
            raise VecError("Division by a zero vector.")
        # (a+jb)/(c+jd) = ((ac+bd) + j(bc-ad)) / (c^2+d^2)
        a, b = self._real, self._imag
        c, d = other._real, other._imag
        return Vector._from_rect(
            (a * c + b * d) / denom,
            (b * c - a * d) / denom,
            Vector._union_attrs(self._attrs, other._attrs),
        )

    def __rtruediv__(self, other: Operand) -> "Vector":
        return Vector._to_vec(other).__truediv__(self)

    def __neg__(self) -> "Vector":
        self._require_initialized()
        return Vector._from_rect(-self._real, -self._imag, list(self._attrs))

    def __abs__(self) -> float:
        """Return the magnitude (as a plain float, not a Vector)."""
        self._require_initialized()
        return self._mag

    def __eq__(self, other: object) -> bool:
        """Equality with epsilon tolerance on both components."""
        if not isinstance(other, Vector):
            return NotImplemented
        if not self._initialized or not other._initialized:
            return False
        return (
            abs(self._real - other._real) < _EPSILON
            and abs(self._imag - other._imag) < _EPSILON
        )


# ---------------------------------------------------------------------------
# Backward-compatibility alias
# ---------------------------------------------------------------------------

#: Alias for :class:`Vector`. Allows code written for v1.0.0 to continue
#: working without modification.
Vec = Vector
