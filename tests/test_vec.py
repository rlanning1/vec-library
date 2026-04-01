# tests/test_vec.py
# Comprehensive test suite for the pyVectors library.
# Run from the pyVectors/ directory with:  python3 -m pytest tests/ -v

import math
import pytest
import vec
from vec import Vector, Vec, VecError, RECT, POLAR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def approx(a, b, tol=1e-6):
    """Return True if a and b are within tol of each other."""
    return abs(a - b) < tol


# ---------------------------------------------------------------------------
# Fixture: ensure RADIANS is reset to False before every test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_radians():
    """Reset the RADIANS global to False before and after every test."""
    vec.RADIANS = False
    yield
    vec.RADIANS = False


# ===========================================================================
# 1. INITIALIZATION — RECTANGULAR FORM
# ===========================================================================

class TestInitRect:

    def test_real_and_imag_positive(self):
        V = Vector("3.2 +j1.5")
        assert approx(V.real(), 3.2)
        assert approx(V.img(), 1.5)

    def test_real_positive_explicit_sign(self):
        V = Vector("+3.2 +j1.5")
        assert approx(V.real(), 3.2)
        assert approx(V.img(), 1.5)

    def test_real_positive_imag_negative(self):
        V = Vector("3.3 -j1.5")
        assert approx(V.real(), 3.3)
        assert approx(V.img(), -1.5)

    def test_real_negative_imag_negative(self):
        V = Vector("-1 -j6.1")
        assert approx(V.real(), -1.0)
        assert approx(V.img(), -6.1)

    def test_imaginary_only(self):
        """Omitted real component defaults to zero."""
        V = Vector("-j4.1")
        assert approx(V.real(), 0.0)
        assert approx(V.img(), -4.1)

    def test_space_before_j(self):
        """Space between sign and j is permitted."""
        V = Vector("3.2 + j1.5")
        assert approx(V.real(), 3.2)
        assert approx(V.img(), 1.5)

    def test_integer_components(self):
        V = Vector("3 +j4")
        assert approx(V.real(), 3.0)
        assert approx(V.img(), 4.0)

    def test_magnitude_and_angle_from_rect(self):
        """3 +j4 -> magnitude 5, angle ~53.13 deg"""
        V = Vector("3 +j4")
        assert approx(V.mag(), 5.0)
        assert approx(V.ang(), 53.13010235415598)

    def test_pure_real_via_rect(self):
        """A pure real expressed with +j0."""
        V = Vector("5 +j0")
        assert approx(V.real(), 5.0)
        assert approx(V.img(), 0.0)
        assert approx(V.mag(), 5.0)
        assert approx(V.ang(), 0.0)


# ===========================================================================
# 2. INITIALIZATION — POLAR FORM
# ===========================================================================

class TestInitPolar:

    def test_A_notation_positive_angle(self):
        V = Vector("10.41 +A15.2")
        assert approx(V.mag(), 10.41)
        assert approx(V.ang(), 15.2)

    def test_A_notation_negative_angle_radians(self):
        V = Vector(r"5.0 -A1.33 \rad")
        assert approx(V.mag(), 5.0)
        assert approx(V.ang(), -1.33)

    def test_angle_zero_default(self):
        """Omitted angle defaults to zero."""
        V = Vector("3.3")
        assert approx(V.mag(), 3.3)
        assert approx(V.ang(), 0.0)

    def test_lt_notation(self):
        V = Vector("10 <45")
        assert approx(V.mag(), 10.0)
        assert approx(V.ang(), 45.0)

    def test_unicode_angle_notation(self):
        V = Vector("10 ∠45")
        assert approx(V.mag(), 10.0)
        assert approx(V.ang(), 45.0)

    def test_lt_and_unicode_equivalent(self):
        V1 = Vector("10 <45")
        V2 = Vector("10 ∠45")
        assert V1 == V2

    def test_negative_magnitude(self):
        """Negative magnitude -> same mag, angle + 180 deg."""
        V = Vector("-3.3")
        assert approx(V.mag(), 3.3)
        assert approx(V.ang(), 180.0)

    def test_negative_magnitude_rect_components(self):
        V = Vector("-5 <0")
        assert approx(V.real(), -5.0)
        assert approx(V.img(), 0.0, tol=1e-9)

    def test_polar_rect_components(self):
        """10<45 deg -> real = 10*cos(45), imag = 10*sin(45)"""
        V = Vector("10 <45")
        expected_real = 10 * math.cos(math.radians(45))
        expected_imag = 10 * math.sin(math.radians(45))
        assert approx(V.real(), expected_real)
        assert approx(V.img(), expected_imag)

    def test_radians_flag_input(self):
        r"""Angle in the init string interpreted as radians when \rad is set."""
        V = Vector(r"5.0 +A1.5708 \rad")
        assert approx(V.real(), 0.0, tol=1e-4)
        assert approx(V.img(), 5.0, tol=1e-4)

    def test_radians_flag_output(self):
        r"""ang() returns radians when \rad attribute is set."""
        V = Vector(r"1 +A1.0 \rad")
        assert approx(V.ang(), 1.0)

    def test_degrees_output_default(self):
        r"""ang() returns degrees when \rad is not set."""
        V = Vector("1 +A90")
        assert approx(V.ang(), 90.0)


# ===========================================================================
# 3. DEFERRED INITIALIZATION
# ===========================================================================

class TestDeferredInit:

    def test_none_creates_uninitialized(self):
        V = Vector(None)
        with pytest.raises(VecError):
            V.real()

    def test_initialize_method(self):
        V = Vector(None)
        V.initialize("3 +j4")
        assert approx(V.real(), 3.0)
        assert approx(V.img(), 4.0)

    def test_reinitialize_clears_attrs(self):
        V = Vector(None)
        V.initialize(r"5 +j10 \parallel")
        assert V.hasAttrib(r"\parallel")
        V.initialize("2 -j3")
        assert not V.hasAttrib(r"\parallel")

    def test_reinitialize_new_value(self):
        V = Vector("1 +j1")
        V.initialize("3 +j4")
        assert approx(V.real(), 3.0)
        assert approx(V.img(), 4.0)

    def test_uninitialized_blocks_all_value_methods(self):
        V = Vector(None)
        for method in [V.real, V.img, V.mag, V.ang, V.rect, V.polar]:
            with pytest.raises(VecError):
                method()

    def test_uninitialized_blocks_arithmetic(self):
        V = Vector(None)
        with pytest.raises(VecError):
            _ = V + Vector("1 +j0")


# ===========================================================================
# 4. VALUE EXTRACTION METHODS
# ===========================================================================

class TestValueExtraction:

    def setup_method(self):
        self.V = Vector("3 +j4")

    def test_real(self):
        assert approx(self.V.real(), 3.0)

    def test_img(self):
        assert approx(self.V.img(), 4.0)

    def test_mag(self):
        assert approx(self.V.mag(), 5.0)

    def test_ang_degrees(self):
        assert approx(self.V.ang(), math.degrees(math.atan2(4, 3)))

    def test_rect_tuple(self):
        r, i = self.V.rect()
        assert approx(r, 3.0) and approx(i, 4.0)

    def test_polar_tuple_degrees(self):
        m, a = self.V.polar()
        assert approx(m, 5.0)
        assert approx(a, math.degrees(math.atan2(4, 3)))

    def test_polar_tuple_radians(self):
        V = Vector(r"3 +j4 \rad")
        m, a = V.polar()
        assert approx(m, 5.0)
        assert approx(a, math.atan2(4, 3))

    def test_ang_radians_when_rad_set(self):
        V = Vector(r"3 +j4 \rad")
        assert approx(V.ang(), math.atan2(4, 3))


# ===========================================================================
# 5. ARITHMETIC OPERATORS
# ===========================================================================

class TestArithmetic:

    def test_add_two_vecs(self):
        V1 = Vector("3 +j4")
        V2 = Vector("1 -j2")
        V3 = V1 + V2
        assert approx(V3.real(), 4.0)
        assert approx(V3.img(), 2.0)

    def test_sub_two_vecs(self):
        V1 = Vector("3 +j4")
        V2 = Vector("1 -j2")
        V3 = V1 - V2
        assert approx(V3.real(), 2.0)
        assert approx(V3.img(), 6.0)

    def test_mul_two_vecs(self):
        """(3+j4)(1-j2) = 3 -j6 +j4 -j^2*8 = 11 -j2"""
        V1 = Vector("3 +j4")
        V2 = Vector("1 -j2")
        V3 = V1 * V2
        assert approx(V3.real(), 11.0)
        assert approx(V3.img(), -2.0)

    def test_div_two_vecs(self):
        """(3+j4)/(1-j2): denom=5; real=(3-8)/5=-1, imag=(4+6)/5=2"""
        V1 = Vector("3 +j4")
        V2 = Vector("1 -j2")
        V3 = V1 / V2
        assert approx(V3.real(), -1.0)
        assert approx(V3.img(), 2.0)

    def test_neg(self):
        V  = Vector("3 +j4")
        Vn = -V
        assert approx(Vn.real(), -3.0)
        assert approx(Vn.img(), -4.0)

    def test_abs_returns_magnitude(self):
        V = Vector("3 +j4")
        assert approx(abs(V), 5.0)

    def test_abs_returns_float(self):
        V = Vector("3 +j4")
        assert isinstance(abs(V), float)

    def test_scalar_radd(self):
        V = Vector("3 +j4")
        result = 2 + V
        assert approx(result.real(), 5.0)
        assert approx(result.img(), 4.0)

    def test_scalar_add(self):
        V = Vector("3 +j4")
        result = V + 2
        assert approx(result.real(), 5.0)
        assert approx(result.img(), 4.0)

    def test_scalar_rsub(self):
        V = Vector("3 +j4")
        result = 10 - V
        assert approx(result.real(), 7.0)
        assert approx(result.img(), -4.0)

    def test_scalar_rmul(self):
        V = Vector("3 +j4")
        result = 5 * V
        assert approx(result.real(), 15.0)
        assert approx(result.img(), 20.0)

    def test_scalar_mul(self):
        V = Vector("3 +j4")
        result = V * 5
        assert approx(result.real(), 15.0)
        assert approx(result.img(), 20.0)

    def test_scalar_rtruediv(self):
        V = Vector("2 +j0")
        result = 10 / V
        assert approx(result.real(), 5.0)
        assert approx(result.img(), 0.0)

    def test_operands_not_modified(self):
        """Arithmetic never modifies the operand vectors."""
        V1 = Vector("3 +j4")
        V2 = Vector("1 -j2")
        _ = V1 + V2
        assert approx(V1.real(), 3.0) and approx(V1.img(), 4.0)
        assert approx(V2.real(), 1.0) and approx(V2.img(), -2.0)

    def test_chained_operations(self):
        """5 * V1 / V2 should not raise and should return a Vector."""
        V1 = Vector(r"5 +j10 \parallel")
        V2 = Vector(r"3 +A22 \parallel")
        result = 5 * V1 / V2
        assert isinstance(result, Vector)

    def test_division_by_zero_raises(self):
        V  = Vector("3 +j4")
        Vz = Vector("0 +j0")
        with pytest.raises(VecError):
            _ = V / Vz

    def test_div_by_zero_scalar(self):
        V = Vector("3 +j4")
        with pytest.raises(VecError):
            _ = V / 0


# ===========================================================================
# 6. EQUALITY
# ===========================================================================

class TestEquality:

    def test_equal_vecs(self):
        V1 = Vector("3 +j4")
        V2 = Vector("3 +j4")
        assert V1 == V2

    def test_unequal_vecs(self):
        V1 = Vector("3 +j4")
        V2 = Vector("1 -j2")
        assert not (V1 == V2)

    def test_epsilon_tolerance(self):
        """Vectors within floating-point noise should compare equal."""
        V1   = Vector("3 +j4")
        V2   = Vector("3 +j4")
        tiny = Vector("1e-12 +j0")
        V3   = V1 + tiny
        assert V3 == V2

    def test_rect_and_polar_same_vector(self):
        """3+j4 and 5<53.13 deg represent the same vector."""
        V1 = Vector("3 +j4")
        V2 = Vector("5 +A53.13010235415598")
        assert V1 == V2

    def test_not_equal_to_non_vec(self):
        V = Vector("3 +j4")
        assert V.__eq__("not a vec") is NotImplemented
        assert not (V == "not a vec")


# ===========================================================================
# 7. CONJUGATE AND COPY
# ===========================================================================

class TestConjugateAndCopy:

    def test_conjugate_negates_imag(self):
        V  = Vector("3 +j4")
        Vc = V.conjugate()
        assert approx(Vc.real(), 3.0)
        assert approx(Vc.img(), -4.0)

    def test_conjugate_preserves_real(self):
        V  = Vector("-2 +j5")
        Vc = V.conjugate()
        assert approx(Vc.real(), -2.0)

    def test_conjugate_preserves_attrs(self):
        V  = Vector(r"3 +j4 \parallel")
        Vc = V.conjugate()
        assert Vc.hasAttrib(r"\parallel")

    def test_conjugate_original_unchanged(self):
        V = Vector("3 +j4")
        _ = V.conjugate()
        assert approx(V.img(), 4.0)

    def test_double_conjugate_identity(self):
        V = Vector("3 +j4")
        assert V == V.conjugate().conjugate()

    def test_copy_same_value(self):
        V  = Vector("3 +j4")
        Vc = V.copy()
        assert V == Vc

    def test_copy_is_independent(self):
        """Modifying the copy's attributes should not affect the original."""
        V  = Vector(r"3 +j4 \parallel")
        Vc = V.copy()
        Vc.delAttrib(r"\parallel")
        assert V.hasAttrib(r"\parallel")
        assert not Vc.hasAttrib(r"\parallel")

    def test_copy_preserves_attrs(self):
        V  = Vector(r"3 +j4 \parallel \admittance")
        Vc = V.copy()
        assert Vc.hasAttrib(r"\parallel")
        assert Vc.hasAttrib(r"\admittance")


# ===========================================================================
# 8. ATTRIBUTE SWITCHES
# ===========================================================================

class TestAttributes:

    def test_attr_from_init_string(self):
        V = Vector(r"5 +j10 \parallel \admittance")
        assert V.hasAttrib(r"\parallel")
        assert V.hasAttrib(r"\admittance")

    def test_add_attrib(self):
        V = Vector("3 +j4")
        V.addAttrib(r"\source")
        assert V.hasAttrib(r"\source")

    def test_del_attrib(self):
        V = Vector(r"3 +j4 \source")
        V.delAttrib(r"\source")
        assert not V.hasAttrib(r"\source")

    def test_del_nonexistent_no_error(self):
        V = Vector("3 +j4")
        V.delAttrib(r"\nonexistent")   # should not raise

    def test_has_attrib_false(self):
        V = Vector("3 +j4")
        assert not V.hasAttrib(r"\missing")

    def test_add_duplicate_attr(self):
        """Adding a duplicate attribute should not create duplicates."""
        V = Vector("3 +j4")
        V.addAttrib(r"\parallel")
        V.addAttrib(r"\parallel")
        assert V._attrs.count(r"\parallel") == 1

    def test_invalid_attr_empty_raises(self):
        V = Vector("3 +j4")
        with pytest.raises(VecError):
            V.addAttrib("\\")   # backslash + empty name

    def test_invalid_attr_too_long_raises(self):
        V = Vector("3 +j4")
        with pytest.raises(VecError):
            V.addAttrib("\\" + "a" * 16)   # 16 chars -- exceeds 15

    def test_attr_max_length_ok(self):
        V = Vector("3 +j4")
        V.addAttrib("\\" + "a" * 15)   # exactly 15 -- should be fine

    def test_result_attr_union(self):
        V1 = Vector(r"5 +j10 \parallel")
        V2 = Vector(r"3 +j4 \admittance")
        V3 = V1 + V2
        assert V3.hasAttrib(r"\parallel")
        assert V3.hasAttrib(r"\admittance")

    def test_result_attr_no_duplicates(self):
        V1 = Vector(r"5 +j10 \parallel")
        V2 = Vector(r"3 +j4 \parallel")
        V3 = V1 + V2
        assert V3._attrs.count(r"\parallel") == 1

    def test_rad_attr_propagates_to_result(self):
        V1 = Vector(r"1 +A1.0 \rad")
        V2 = Vector("0 +j1")
        V3 = V1 + V2
        assert V3.hasAttrib(r"\rad")


# ===========================================================================
# 9. STRING REPRESENTATION
# ===========================================================================

class TestStringRepresentation:

    def test_asString_rect_default_format(self):
        V = Vector("3 +j4")
        s = V.asString(RECT)
        assert "3.0" in s
        assert "4.0" in s
        assert "j" in s

    def test_asString_rect_with_format(self):
        V = Vector("3 +j4")
        s = V.asString(RECT, fmt1=".2f", fmt2=".2f")
        assert s == "3.00 +j4.00"

    def test_asString_rect_negative_imag(self):
        V = Vector("3 -j4")
        s = V.asString(RECT, fmt1=".1f", fmt2=".1f")
        assert s == "3.0 -j4.0"

    def test_asString_polar_default_format(self):
        V = Vector("3 +j4")
        s = V.asString(POLAR)
        assert "\u2220" in s
        assert "5.0" in s

    def test_asString_polar_with_format(self):
        V = Vector("3 +j4")
        s = V.asString(POLAR, fmt1=".3f", fmt2=".1f")
        assert "5.000" in s
        assert "\u2220" in s

    def test_asString_polar_radians_mode(self):
        V = Vector(r"3 +j4 \rad")
        s = V.asString(POLAR)
        angle_rad = math.atan2(4, 3)
        assert str(angle_rad) in s or f"{angle_rad:.4f}" in s.replace(" ", "")

    def test_asString_invalid_form_raises(self):
        V = Vector("3 +j4")
        with pytest.raises(VecError):
            V.asString(99)

    def test_repr_initialized(self):
        V = Vector("3 +j4")
        r = repr(V)
        assert r.startswith("Vector('")
        assert "j" in r

    def test_repr_uninitialized(self):
        V = Vector(None)
        assert repr(V) == "Vector(None)"


# ===========================================================================
# 10. ERROR HANDLING
# ===========================================================================

class TestErrorHandling:

    def test_invalid_init_string_raises(self):
        with pytest.raises(VecError):
            Vector("not a vector")

    def test_empty_init_string_raises(self):
        with pytest.raises(VecError):
            Vector("")

    def test_non_string_init_raises(self):
        with pytest.raises(VecError):
            Vector(42)

    def test_vecerror_is_exception(self):
        assert issubclass(VecError, Exception)

    def test_division_by_zero_raises_vecerror(self):
        V = Vector("3 +j4")
        with pytest.raises(VecError, match="zero"):
            V / Vector("0 +j0")


# ===========================================================================
# 11. ROUND-TRIP CONSISTENCY
# ===========================================================================

class TestRoundTrip:

    def test_rect_to_polar_and_back(self):
        """Converting 3+j4 to polar and back should recover original values."""
        V       = Vector("3 +j4")
        mag, ang = V.polar()
        V2      = Vector(f"{mag} +A{ang}")
        assert V == V2

    def test_polar_to_rect_and_back(self):
        V      = Vector("10 <45")
        r, i   = V.rect()
        V2     = Vector(f"{r} +j{i}")
        assert V == V2

    def test_add_subtract_identity(self):
        """V1 + V2 - V2 should equal V1."""
        V1 = Vector("3 +j4")
        V2 = Vector("1 -j2")
        assert (V1 + V2) - V2 == V1

    def test_mul_div_identity(self):
        """V1 * V2 / V2 should equal V1."""
        V1 = Vector("3 +j4")
        V2 = Vector("1 -j2")
        assert (V1 * V2) / V2 == V1

    def test_neg_neg_identity(self):
        V = Vector("3 +j4")
        assert -(-V) == V

    def test_conjugate_mul_is_mag_squared(self):
        """V * conj(V) should be a real vector with magnitude = |V|^2."""
        V      = Vector("3 +j4")
        result = V * V.conjugate()
        assert approx(result.real(), 25.0)
        assert approx(result.img(), 0.0, tol=1e-9)


# ===========================================================================
# 12. BACKWARD COMPATIBILITY — Vec ALIAS
# ===========================================================================

class TestVecAlias:

    def test_vec_alias_creates_vector_instance(self):
        """Vec() should create a Vector instance."""
        V = Vec("3 +j4")
        assert isinstance(V, Vector)

    def test_vec_alias_arithmetic(self):
        """Vec instances should participate in arithmetic with Vector instances."""
        V1 = Vec("3 +j4")
        V2 = Vector("1 -j2")
        V3 = V1 + V2
        assert isinstance(V3, Vector)
        assert approx(V3.real(), 4.0)
        assert approx(V3.img(), 2.0)

    def test_vec_alias_is_vector_class(self):
        """Vec and Vector should be the same class object."""
        assert Vec is Vector


# ===========================================================================
# 13. RADIANS GLOBAL FLAG
# ===========================================================================

class TestRadiansGlobal:

    def test_radians_false_by_default(self):
        """RADIANS should be False at module level by default."""
        assert vec.RADIANS is False

    def test_radians_false_degrees_behavior_unchanged(self):
        """With RADIANS=False, angle I/O is in degrees as before."""
        vec.RADIANS = False
        V = Vector("1 +A90")
        assert approx(V.ang(), 90.0)
        assert not V.hasAttrib(r"\rad")

    def test_radians_true_auto_injects_rad_attr(self):
        r"""With RADIANS=True, new vectors automatically get \rad."""
        vec.RADIANS = True
        V = Vector("1 +A90")
        assert V.hasAttrib(r"\rad")

    def test_radians_true_angle_parsed_as_radians(self):
        """With RADIANS=True, angle in init string is interpreted as radians."""
        vec.RADIANS = True
        V = Vector("5 +A1.5708")   # ~pi/2 radians
        assert approx(V.real(), 0.0, tol=1e-4)
        assert approx(V.img(), 5.0, tol=1e-4)

    def test_radians_true_ang_returns_radians(self):
        """With RADIANS=True, ang() returns radians."""
        vec.RADIANS = True
        V = Vector("1 +A1.0")
        assert approx(V.ang(), 1.0)

    def test_radians_true_polar_returns_radians(self):
        """With RADIANS=True, polar() angle is in radians."""
        vec.RADIANS = True
        V  = Vector("5 +A1.0")
        m, a = V.polar()
        assert approx(a, 1.0)

    def test_radians_true_asString_polar_shows_radians(self):
        """With RADIANS=True, asString(POLAR) displays angle in radians."""
        vec.RADIANS = True
        V = Vector("1 +A1.0")
        s = V.asString(POLAR)
        assert approx(float(s.split("\u2220")[1].strip()), 1.0)

    def test_radians_true_rect_form_unaffected(self):
        """Rectangular form input is not affected by RADIANS flag."""
        vec.RADIANS = True
        V = Vector("3 +j4")
        assert approx(V.real(), 3.0)
        assert approx(V.img(), 4.0)
        assert approx(V.mag(), 5.0)

    def test_radians_true_result_inherits_via_union_only(self):
        r"""Arithmetic results get \rad via union, not auto-injection."""
        vec.RADIANS = True
        V1 = Vector("3 +j4")    # gets \rad auto-injected
        vec.RADIANS = False
        V2 = Vector("1 +j0")    # no auto-injection; no \rad
        # Result union: V1 has \rad, V2 does not -> result has \rad
        V3 = V1 + V2
        assert V3.hasAttrib(r"\rad")

    def test_radians_false_after_true_no_auto_injection(self):
        r"""After setting RADIANS back to False, new vectors do not get \rad."""
        vec.RADIANS = True
        _ = Vector("1 +A1.0")
        vec.RADIANS = False
        V = Vector("1 +A90")
        assert not V.hasAttrib(r"\rad")
        assert approx(V.ang(), 90.0)


# ===========================================================================
# 14. \deg ATTRIBUTE OVERRIDE
# ===========================================================================

class TestDegAttribute:

    def test_deg_attr_no_effect_when_radians_false(self):
        r"""When RADIANS=False, \deg has no effect (already in degrees mode)."""
        vec.RADIANS = False
        V = Vector(r"1 +A45 \deg")
        assert approx(V.ang(), 45.0)
        assert V.hasAttrib(r"\deg")
        assert not V.hasAttrib(r"\rad")

    def test_deg_overrides_radians_true_for_input(self):
        r"""When RADIANS=True, \deg causes angle to be parsed in degrees."""
        vec.RADIANS = True
        V = Vector(r"10 +A45 \deg")
        # 45 degrees
        assert approx(V.real(), 10 * math.cos(math.radians(45)))
        assert approx(V.img(), 10 * math.sin(math.radians(45)))

    def test_deg_removes_rad_when_radians_true(self):
        r"""When RADIANS=True and \deg is present, \rad must not be present."""
        vec.RADIANS = True
        V = Vector(r"1 +A45 \deg")
        assert V.hasAttrib(r"\deg")
        assert not V.hasAttrib(r"\rad")

    def test_deg_ang_returns_degrees(self):
        r"""ang() returns degrees when \deg is set, even if RADIANS=True."""
        vec.RADIANS = True
        V = Vector(r"1 +A45 \deg")
        assert approx(V.ang(), 45.0)

    def test_deg_polar_returns_degrees(self):
        r"""polar() returns angle in degrees when \deg is set."""
        vec.RADIANS = True
        V    = Vector(r"10 +A45 \deg")
        m, a = V.polar()
        assert approx(a, 45.0)

    def test_deg_asString_shows_degrees(self):
        r"""asString(POLAR) shows degrees when \deg is set."""
        vec.RADIANS = True
        V = Vector(r"10 +A45 \deg")
        s = V.asString(POLAR, fmt1=".2f", fmt2=".2f")
        assert "45.00" in s

    def test_deg_propagates_via_union(self):
        r"""Result of arithmetic inherits \deg through attribute union."""
        vec.RADIANS = False
        V1 = Vector(r"3 +j4 \deg")
        V2 = Vector("1 +j0")
        V3 = V1 + V2
        assert V3.hasAttrib(r"\deg")

    def test_rad_takes_precedence_over_deg_in_union(self):
        r"""If result union has both \rad and \deg, \deg wins (deg_mode check)."""
        vec.RADIANS = False
        V1 = Vector(r"3 +j4 \rad")
        V2 = Vector(r"1 +j0 \deg")
        V3 = V1 + V2
        # Both attrs present in union; _rad_mode is False when \deg present -> degrees output
        assert V3.hasAttrib(r"\rad")
        assert V3.hasAttrib(r"\deg")
        assert not V3._rad_mode   # \deg overrides \rad in output
        # V3 = (3+1) + j(4+0) = 4 +j4; angle in degrees = 45.0
        assert approx(V3.ang(), math.degrees(math.atan2(4, 4)))


# ===========================================================================
# 15. VARIABLE SUBSTITUTION PRE-PARSER
# ===========================================================================

class TestVariableSubstitution:
    """Tests for the v1.1.0 variable substitution pre-parser."""

    # --- Rectangular form ---------------------------------------------------

    def test_rect_both_vars(self):
        """Both components supplied as variables — rectangular form."""
        R11 = 10000.0
        Xc  = 452.0
        V = Vector("R11 +j Xc")
        assert approx(V.real(), 10000.0)
        assert approx(V.img(),  452.0)

    def test_rect_real_var_imag_literal(self):
        """Real component is a variable; imaginary is a literal."""
        resistance = 330.0
        V = Vector("resistance +j4.7")
        assert approx(V.real(), 330.0)
        assert approx(V.img(),  4.7)

    def test_rect_real_literal_imag_var(self):
        """Real component is a literal; imaginary is a variable."""
        reactance = 75.5
        V = Vector("3.0 +j reactance")
        assert approx(V.real(), 3.0)
        assert approx(V.img(), 75.5)

    def test_rect_negative_imag_var(self):
        """Negative imaginary component expressed as a variable."""
        Xc = 452.0
        V = Vector("100.0 -j Xc")
        assert approx(V.real(), 100.0)
        assert approx(V.img(), -452.0)

    def test_rect_both_literals_unchanged(self):
        """Pure-literal strings pass through substitution without change."""
        V = Vector("3.0 +j4.0")
        assert approx(V.real(), 3.0)
        assert approx(V.img(), 4.0)

    def test_rect_integer_var(self):
        """Integer variable values are accepted and converted to float."""
        n = 5
        V = Vector("n +j0")
        assert approx(V.real(), 5.0)
        assert approx(V.img(), 0.0)

    def test_rect_underscore_var(self):
        """Variable names with leading underscores are valid identifiers."""
        _r = 1.0
        _x = 2.0
        V = Vector("_r +j _x")
        assert approx(V.real(), 1.0)
        assert approx(V.img(), 2.0)

    def test_rect_alphanumeric_var(self):
        """Variable names that start with a letter then contain digits (R001)."""
        R001 = 47.0
        V = Vector("R001 +j0")
        assert approx(V.real(), 47.0)

    # --- Polar form ---------------------------------------------------------

    def test_polar_both_vars(self):
        """Both magnitude and angle supplied as variables — polar form."""
        m = 20.22
        a = 45.0
        V = Vector("m < a")
        assert approx(V.mag(), 20.22)
        assert approx(V.ang(), 45.0)

    def test_polar_mag_var_angle_literal(self):
        """Magnitude is a variable; angle is a literal."""
        magnitude = 10.0
        V = Vector("magnitude < 30")
        assert approx(V.mag(), 10.0)
        assert approx(V.ang(), 30.0)

    def test_polar_mag_literal_angle_var(self):
        """Magnitude is a literal; angle is a variable."""
        theta = 60.0
        V = Vector("5.0 < theta")
        assert approx(V.mag(), 5.0)
        assert approx(V.ang(), 60.0)

    def test_polar_unicode_angle_symbol_with_vars(self):
        """Variable substitution works with the ∠ angle separator."""
        mag = 7.0
        ang = 30.0
        V = Vector("mag ∠ ang")
        assert approx(V.mag(), 7.0)
        assert approx(V.ang(), 30.0)

    def test_polar_A_notation_with_vars(self):
        """Variable substitution works with +A angle notation."""
        mag = 5.0
        phi = 90.0
        V = Vector("mag +A phi")
        assert approx(V.mag(), 5.0)
        assert approx(V.ang(), 90.0)

    def test_polar_negative_A_notation_with_var(self):
        """Variable substitution works with -A angle notation."""
        mag = 5.0
        phi = 45.0
        V = Vector("mag -A phi")
        assert approx(V.ang(), -45.0)

    # --- Attributes alongside variables ------------------------------------

    def test_vars_with_rad_attr(self):
        r"""Variable substitution works alongside the \rad attribute."""
        mag   = 1.0
        angle = math.pi / 2
        V = Vector(r"mag +A angle \rad")
        assert approx(V.real(), 0.0, tol=1e-9)
        assert approx(V.img(), 1.0, tol=1e-9)

    def test_attr_name_not_substituted(self):
        r"""Tokens inside attribute switches (e.g. 'rad') are never substituted."""
        mag = 5.0
        ang = 45.0
        # 'rad' appears as part of \rad — must not be treated as a variable
        V = Vector(r"mag < ang \rad")
        # just verify it parses without error and uses radians
        assert approx(V.mag(), 5.0)

    # --- initialize() method ------------------------------------------------

    def test_initialize_with_vars(self):
        """initialize() resolves variables from its caller's local scope."""
        V = Vector(None)
        real_part = 6.0
        imag_part = 8.0
        V.initialize("real_part +j imag_part")
        assert approx(V.real(), 6.0)
        assert approx(V.img(), 8.0)

    # --- Error handling -----------------------------------------------------

    def test_undefined_var_raises_vecerror(self):
        """An identifier not found in local scope must raise VecError."""
        with pytest.raises(VecError, match="not found"):
            Vector("undefined_variable +j0")

    def test_wrong_type_var_raises_vecerror(self):
        """A variable whose value is not int or float must raise VecError."""
        bad_val = "hello"
        with pytest.raises(VecError, match="str"):
            Vector("bad_val +j0")

    def test_j_never_substituted(self):
        """'j' must never be treated as a variable name even if defined locally."""
        j = 99.0   # should be completely ignored by the pre-parser
        V = Vector("3.0 +j4.0")
        assert approx(V.real(), 3.0)
        assert approx(V.img(), 4.0)

    def test_A_never_substituted(self):
        """'A' must never be treated as a variable name even if defined locally."""
        A = 999.0   # should be completely ignored by the pre-parser
        V = Vector("10 +A45")
        assert approx(V.mag(), 10.0)
        assert approx(V.ang(), 45.0)
