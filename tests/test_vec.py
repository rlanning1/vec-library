# tests/test_vec.py
# Comprehensive test suite for the Vec library.
# Run from the vec-library/ directory with:  python3 -m pytest tests/ -v

import math
import pytest
from vec import Vec, VecError, RECT, POLAR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def approx(a, b, tol=1e-6):
    """Return True if a and b are within tol of each other."""
    return abs(a - b) < tol


# ===========================================================================
# 1. INITIALIZATION — RECTANGULAR FORM
# ===========================================================================

class TestInitRect:

    def test_real_and_imag_positive(self):
        V = Vec("3.2 +j1.5")
        assert approx(V.real(), 3.2)
        assert approx(V.img(), 1.5)

    def test_real_positive_explicit_sign(self):
        V = Vec("+3.2 +j1.5")
        assert approx(V.real(), 3.2)
        assert approx(V.img(), 1.5)

    def test_real_positive_imag_negative(self):
        V = Vec("3.3 -j1.5")
        assert approx(V.real(), 3.3)
        assert approx(V.img(), -1.5)

    def test_real_negative_imag_negative(self):
        V = Vec("-1 -j6.1")
        assert approx(V.real(), -1.0)
        assert approx(V.img(), -6.1)

    def test_imaginary_only(self):
        """Omitted real component defaults to zero."""
        V = Vec("-j4.1")
        assert approx(V.real(), 0.0)
        assert approx(V.img(), -4.1)

    def test_space_before_j(self):
        """Space between sign and j is permitted."""
        V = Vec("3.2 + j1.5")
        assert approx(V.real(), 3.2)
        assert approx(V.img(), 1.5)

    def test_integer_components(self):
        V = Vec("3 +j4")
        assert approx(V.real(), 3.0)
        assert approx(V.img(), 4.0)

    def test_magnitude_and_angle_from_rect(self):
        """3 +j4 → magnitude 5, angle ~53.13°"""
        V = Vec("3 +j4")
        assert approx(V.mag(), 5.0)
        assert approx(V.ang(), 53.13010235415598)

    def test_pure_real_via_rect(self):
        """A pure real expressed with +j0."""
        V = Vec("5 +j0")
        assert approx(V.real(), 5.0)
        assert approx(V.img(), 0.0)
        assert approx(V.mag(), 5.0)
        assert approx(V.ang(), 0.0)


# ===========================================================================
# 2. INITIALIZATION — POLAR FORM
# ===========================================================================

class TestInitPolar:

    def test_A_notation_positive_angle(self):
        V = Vec("10.41 +A15.2")
        assert approx(V.mag(), 10.41)
        assert approx(V.ang(), 15.2)

    def test_A_notation_negative_angle(self):
        V = Vec(r"5.0 -A1.33 \rad")
        assert approx(V.mag(), 5.0)
        assert approx(V.ang(), -1.33)

    def test_angle_zero_default(self):
        """Omitted angle defaults to zero."""
        V = Vec("3.3")
        assert approx(V.mag(), 3.3)
        assert approx(V.ang(), 0.0)

    def test_lt_notation(self):
        V = Vec("10 <45")
        assert approx(V.mag(), 10.0)
        assert approx(V.ang(), 45.0)

    def test_unicode_angle_notation(self):
        V = Vec("10 ∠45")
        assert approx(V.mag(), 10.0)
        assert approx(V.ang(), 45.0)

    def test_lt_and_unicode_equivalent(self):
        V1 = Vec("10 <45")
        V2 = Vec("10 ∠45")
        assert V1 == V2

    def test_negative_magnitude(self):
        """Negative magnitude → same mag, angle + 180°."""
        V = Vec("-3.3")
        assert approx(V.mag(), 3.3)
        assert approx(V.ang(), 180.0)

    def test_negative_magnitude_rect_components(self):
        V = Vec("-5 <0")
        assert approx(V.real(), -5.0)
        assert approx(V.img(), 0.0, tol=1e-9)

    def test_polar_rect_components(self):
        """10∠45° → real = 10·cos(45°), imag = 10·sin(45°)"""
        V = Vec("10 <45")
        expected_real = 10 * math.cos(math.radians(45))
        expected_imag = 10 * math.sin(math.radians(45))
        assert approx(V.real(), expected_real)
        assert approx(V.img(), expected_imag)

    def test_radians_flag_input(self):
        """Angle in the init string interpreted as radians when \\rad is set."""
        V = Vec(r"5.0 +A1.5708 \rad")
        # 1.5708 rad ≈ 90°
        assert approx(V.real(), 0.0, tol=1e-4)
        assert approx(V.img(), 5.0, tol=1e-4)

    def test_radians_flag_output(self):
        """ang() returns radians when \\rad attribute is set."""
        V = Vec(r"1 +A1.0 \rad")
        assert approx(V.ang(), 1.0)

    def test_degrees_output_default(self):
        """ang() returns degrees when \\rad is not set."""
        V = Vec("1 +A90")
        assert approx(V.ang(), 90.0)


# ===========================================================================
# 3. DEFERRED INITIALIZATION
# ===========================================================================

class TestDeferredInit:

    def test_none_creates_uninitialized(self):
        V = Vec(None)
        with pytest.raises(VecError):
            V.real()

    def test_initialize_method(self):
        V = Vec(None)
        V.initialize("3 +j4")
        assert approx(V.real(), 3.0)
        assert approx(V.img(), 4.0)

    def test_reinitialize_clears_attrs(self):
        V = Vec(None)
        V.initialize(r"5 +j10 \parallel")
        assert V.hasAttrib(r"\parallel")
        V.initialize("2 -j3")
        assert not V.hasAttrib(r"\parallel")

    def test_reinitialize_new_value(self):
        V = Vec("1 +j1")
        V.initialize("3 +j4")
        assert approx(V.real(), 3.0)
        assert approx(V.img(), 4.0)

    def test_uninitialized_blocks_all_value_methods(self):
        V = Vec(None)
        for method in [V.real, V.img, V.mag, V.ang, V.rect, V.polar]:
            with pytest.raises(VecError):
                method()

    def test_uninitialized_blocks_arithmetic(self):
        V = Vec(None)
        with pytest.raises(VecError):
            _ = V + Vec("1 +j0")


# ===========================================================================
# 4. VALUE EXTRACTION METHODS
# ===========================================================================

class TestValueExtraction:

    def setup_method(self):
        self.V = Vec("3 +j4")

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
        V = Vec(r"3 +j4 \rad")
        m, a = V.polar()
        assert approx(m, 5.0)
        assert approx(a, math.atan2(4, 3))

    def test_ang_radians_when_rad_set(self):
        V = Vec(r"3 +j4 \rad")
        assert approx(V.ang(), math.atan2(4, 3))


# ===========================================================================
# 5. ARITHMETIC OPERATORS
# ===========================================================================

class TestArithmetic:

    def test_add_two_vecs(self):
        V1 = Vec("3 +j4")
        V2 = Vec("1 -j2")
        V3 = V1 + V2
        assert approx(V3.real(), 4.0)
        assert approx(V3.img(), 2.0)

    def test_sub_two_vecs(self):
        V1 = Vec("3 +j4")
        V2 = Vec("1 -j2")
        V3 = V1 - V2
        assert approx(V3.real(), 2.0)
        assert approx(V3.img(), 6.0)

    def test_mul_two_vecs(self):
        """(3+j4)(1-j2) = 3 -j6 +j4 -j²8 = 11 -j2"""
        V1 = Vec("3 +j4")
        V2 = Vec("1 -j2")
        V3 = V1 * V2
        assert approx(V3.real(), 11.0)
        assert approx(V3.img(), -2.0)

    def test_div_two_vecs(self):
        """(3+j4)/(1-j2): denom=5; real=(3-8)/5=-1, imag=(4+6)/5=2"""
        V1 = Vec("3 +j4")
        V2 = Vec("1 -j2")
        V3 = V1 / V2
        assert approx(V3.real(), -1.0)
        assert approx(V3.img(), 2.0)

    def test_neg(self):
        V = Vec("3 +j4")
        Vn = -V
        assert approx(Vn.real(), -3.0)
        assert approx(Vn.img(), -4.0)

    def test_abs_returns_magnitude(self):
        V = Vec("3 +j4")
        assert approx(abs(V), 5.0)

    def test_abs_returns_float(self):
        V = Vec("3 +j4")
        assert isinstance(abs(V), float)

    def test_scalar_radd(self):
        V = Vec("3 +j4")
        result = 2 + V
        assert approx(result.real(), 5.0)
        assert approx(result.img(), 4.0)

    def test_scalar_add(self):
        V = Vec("3 +j4")
        result = V + 2
        assert approx(result.real(), 5.0)
        assert approx(result.img(), 4.0)

    def test_scalar_rsub(self):
        V = Vec("3 +j4")
        result = 10 - V
        assert approx(result.real(), 7.0)
        assert approx(result.img(), -4.0)

    def test_scalar_rmul(self):
        V = Vec("3 +j4")
        result = 5 * V
        assert approx(result.real(), 15.0)
        assert approx(result.img(), 20.0)

    def test_scalar_mul(self):
        V = Vec("3 +j4")
        result = V * 5
        assert approx(result.real(), 15.0)
        assert approx(result.img(), 20.0)

    def test_scalar_rtruediv(self):
        """scalar / V: 1 / (1+j0) = 1"""
        V = Vec("2 +j0")
        result = 10 / V
        assert approx(result.real(), 5.0)
        assert approx(result.img(), 0.0)

    def test_operands_not_modified(self):
        """Arithmetic never modifies the operand vectors."""
        V1 = Vec("3 +j4")
        V2 = Vec("1 -j2")
        _ = V1 + V2
        assert approx(V1.real(), 3.0) and approx(V1.img(), 4.0)
        assert approx(V2.real(), 1.0) and approx(V2.img(), -2.0)

    def test_chained_operations(self):
        """5 * V1 / V2 should not raise and should return a Vec."""
        V1 = Vec(r"5 +j10 \parallel")
        V2 = Vec(r"3 +A22 \parallel")
        result = 5 * V1 / V2
        assert isinstance(result, Vec)

    def test_division_by_zero_raises(self):
        V = Vec("3 +j4")
        Vz = Vec("0 +j0")
        with pytest.raises(VecError):
            _ = V / Vz

    def test_div_by_zero_scalar(self):
        V = Vec("3 +j4")
        with pytest.raises(VecError):
            _ = V / 0


# ===========================================================================
# 6. EQUALITY
# ===========================================================================

class TestEquality:

    def test_equal_vecs(self):
        V1 = Vec("3 +j4")
        V2 = Vec("3 +j4")
        assert V1 == V2

    def test_unequal_vecs(self):
        V1 = Vec("3 +j4")
        V2 = Vec("1 -j2")
        assert not (V1 == V2)

    def test_epsilon_tolerance(self):
        """Vectors within floating-point noise should compare equal."""
        V1 = Vec("3 +j4")
        V2 = Vec("3 +j4")
        tiny = Vec("1e-12 +j0")
        V3 = V1 + tiny
        assert V3 == V2

    def test_rect_and_polar_same_vector(self):
        """3+j4 and 5∠53.13° represent the same vector."""
        V1 = Vec("3 +j4")
        V2 = Vec("5 +A53.13010235415598")
        assert V1 == V2

    def test_not_equal_to_non_vec(self):
        # __eq__ returns NotImplemented for non-Vec types (called directly),
        # which Python then converts to False via the == operator.
        V = Vec("3 +j4")
        assert V.__eq__("not a vec") is NotImplemented
        assert not (V == "not a vec")  # Python converts NotImplemented -> False


# ===========================================================================
# 7. CONJUGATE AND COPY
# ===========================================================================

class TestConjugateAndCopy:

    def test_conjugate_negates_imag(self):
        V = Vec("3 +j4")
        Vc = V.conjugate()
        assert approx(Vc.real(), 3.0)
        assert approx(Vc.img(), -4.0)

    def test_conjugate_preserves_real(self):
        V = Vec("-2 +j5")
        Vc = V.conjugate()
        assert approx(Vc.real(), -2.0)

    def test_conjugate_preserves_attrs(self):
        V = Vec(r"3 +j4 \parallel")
        Vc = V.conjugate()
        assert Vc.hasAttrib(r"\parallel")

    def test_conjugate_original_unchanged(self):
        V = Vec("3 +j4")
        _ = V.conjugate()
        assert approx(V.img(), 4.0)

    def test_double_conjugate_identity(self):
        V = Vec("3 +j4")
        assert V == V.conjugate().conjugate()

    def test_copy_same_value(self):
        V = Vec("3 +j4")
        Vc = V.copy()
        assert V == Vc

    def test_copy_is_independent(self):
        """Modifying the copy's attributes should not affect the original."""
        V = Vec(r"3 +j4 \parallel")
        Vc = V.copy()
        Vc.delAttrib(r"\parallel")
        assert V.hasAttrib(r"\parallel")
        assert not Vc.hasAttrib(r"\parallel")

    def test_copy_preserves_attrs(self):
        V = Vec(r"3 +j4 \parallel \admittance")
        Vc = V.copy()
        assert Vc.hasAttrib(r"\parallel")
        assert Vc.hasAttrib(r"\admittance")


# ===========================================================================
# 8. ATTRIBUTE SWITCHES
# ===========================================================================

class TestAttributes:

    def test_attr_from_init_string(self):
        V = Vec(r"5 +j10 \parallel \admittance")
        assert V.hasAttrib(r"\parallel")
        assert V.hasAttrib(r"\admittance")

    def test_add_attrib(self):
        V = Vec("3 +j4")
        V.addAttrib(r"\source")
        assert V.hasAttrib(r"\source")

    def test_del_attrib(self):
        V = Vec(r"3 +j4 \source")
        V.delAttrib(r"\source")
        assert not V.hasAttrib(r"\source")

    def test_del_nonexistent_no_error(self):
        V = Vec("3 +j4")
        V.delAttrib(r"\nonexistent")  # should not raise

    def test_has_attrib_false(self):
        V = Vec("3 +j4")
        assert not V.hasAttrib(r"\missing")

    def test_add_duplicate_attr(self):
        """Adding a duplicate attribute should not create duplicates."""
        V = Vec("3 +j4")
        V.addAttrib(r"\parallel")
        V.addAttrib(r"\parallel")
        assert V._attrs.count(r"\parallel") == 1

    def test_invalid_attr_empty_raises(self):
        V = Vec("3 +j4")
        with pytest.raises(VecError):
            V.addAttrib("\\")  # backslash + empty name

    def test_invalid_attr_too_long_raises(self):
        V = Vec("3 +j4")
        with pytest.raises(VecError):
            V.addAttrib("\\" + "a" * 16)  # 16 chars — exceeds 15

    def test_attr_max_length_ok(self):
        V = Vec("3 +j4")
        V.addAttrib("\\" + "a" * 15)  # exactly 15 — should be fine

    def test_result_attr_union(self):
        V1 = Vec(r"5 +j10 \parallel")
        V2 = Vec(r"3 +j4 \admittance")
        V3 = V1 + V2
        assert V3.hasAttrib(r"\parallel")
        assert V3.hasAttrib(r"\admittance")

    def test_result_attr_no_duplicates(self):
        V1 = Vec(r"5 +j10 \parallel")
        V2 = Vec(r"3 +j4 \parallel")
        V3 = V1 + V2
        assert V3._attrs.count(r"\parallel") == 1

    def test_rad_attr_propagates_to_result(self):
        V1 = Vec(r"1 +A1.0 \rad")
        V2 = Vec("0 +j1")
        V3 = V1 + V2
        assert V3.hasAttrib(r"\rad")


# ===========================================================================
# 9. STRING REPRESENTATION
# ===========================================================================

class TestStringRepresentation:

    def test_asString_rect_default_format(self):
        V = Vec("3 +j4")
        s = V.asString(RECT)
        assert "3.0" in s
        assert "4.0" in s
        assert "j" in s

    def test_asString_rect_with_format(self):
        V = Vec("3 +j4")
        s = V.asString(RECT, fmt1=".2f", fmt2=".2f")
        assert s == "3.00 +j4.00"

    def test_asString_rect_negative_imag(self):
        V = Vec("3 -j4")
        s = V.asString(RECT, fmt1=".1f", fmt2=".1f")
        assert s == "3.0 -j4.0"

    def test_asString_polar_default_format(self):
        V = Vec("3 +j4")
        s = V.asString(POLAR)
        assert "∠" in s
        assert "5.0" in s

    def test_asString_polar_with_format(self):
        V = Vec("3 +j4")
        s = V.asString(POLAR, fmt1=".3f", fmt2=".1f")
        assert "5.000" in s
        assert "∠" in s

    def test_asString_polar_radians_mode(self):
        V = Vec(r"3 +j4 \rad")
        s = V.asString(POLAR)
        angle_rad = math.atan2(4, 3)
        assert str(angle_rad) in s or f"{angle_rad:.4f}" in s.replace(" ", "")

    def test_asString_invalid_form_raises(self):
        V = Vec("3 +j4")
        with pytest.raises(VecError):
            V.asString(99)

    def test_repr_initialized(self):
        V = Vec("3 +j4")
        r = repr(V)
        assert r.startswith("Vec('")
        assert "j" in r

    def test_repr_uninitialized(self):
        V = Vec(None)
        assert repr(V) == "Vec(None)"


# ===========================================================================
# 10. ERROR HANDLING
# ===========================================================================

class TestErrorHandling:

    def test_invalid_init_string_raises(self):
        with pytest.raises(VecError):
            Vec("not a vector")

    def test_empty_init_string_raises(self):
        with pytest.raises(VecError):
            Vec("")

    def test_non_string_init_raises(self):
        with pytest.raises(VecError):
            Vec(42)

    def test_vecerror_is_exception(self):
        assert issubclass(VecError, Exception)

    def test_division_by_zero_raises_vecerror(self):
        V = Vec("3 +j4")
        with pytest.raises(VecError, match="zero"):
            V / Vec("0 +j0")


# ===========================================================================
# 11. ROUND-TRIP CONSISTENCY
# ===========================================================================

class TestRoundTrip:

    def test_rect_to_polar_and_back(self):
        """Converting 3+j4 to polar and back should recover original values."""
        V = Vec("3 +j4")
        mag, ang = V.polar()
        V2 = Vec(f"{mag} +A{ang}")
        assert V == V2

    def test_polar_to_rect_and_back(self):
        V = Vec("10 <45")
        r, i = V.rect()
        V2 = Vec(f"{r} +j{i}")
        assert V == V2

    def test_add_subtract_identity(self):
        """V1 + V2 - V2 should equal V1."""
        V1 = Vec("3 +j4")
        V2 = Vec("1 -j2")
        assert (V1 + V2) - V2 == V1

    def test_mul_div_identity(self):
        """V1 * V2 / V2 should equal V1."""
        V1 = Vec("3 +j4")
        V2 = Vec("1 -j2")
        assert (V1 * V2) / V2 == V1

    def test_neg_neg_identity(self):
        V = Vec("3 +j4")
        assert -(-V) == V

    def test_conjugate_mul_is_mag_squared(self):
        """V * conj(V) should be a real vector with magnitude = |V|²."""
        V = Vec("3 +j4")
        result = V * V.conjugate()
        assert approx(result.real(), 25.0)   # 3²+4²
        assert approx(result.img(), 0.0, tol=1e-9)
