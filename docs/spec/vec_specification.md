# Vec — Python Vector Library
## Finalized Specification

**Version:** 1.0  
**Date:** 2026-03-29  
**Status:** Approved

> **Note:** This is an internal design document intended for developers and maintainers. It records the design decisions, implementation rules, and rationale behind the `Vec` library. For installation and usage instructions, see `docs/vec_documentation.md` and `README.md`.

---

## Table of Contents

1. [Overview](#overview)
2. [Package Structure](#package-structure)
3. [Module-Level Constants](#module-level-constants)
4. [Class: Vec](#class-vec)
5. [Initialization Strings](#initialization-strings)
6. [Attribute Switches](#attribute-switches)
7. [Operator Methods](#operator-methods)
8. [Value Extraction Methods](#value-extraction-methods)
9. [String Representation Methods](#string-representation-methods)
10. [Utility Methods](#utility-methods)
11. [Internal Representation](#internal-representation)
12. [Scalar Conversion Rules](#scalar-conversion-rules)
13. [Result Vector Rules](#result-vector-rules)
14. [Error Handling](#error-handling)
15. [General Usage Examples](#general-usage-examples)

---

## 1. Overview

`Vec` is a Python library for representing and manipulating complex vectors (phasors). Each vector is maintained internally in both rectangular (`a + jb`) and polar (`c ∠ θ`) forms. Vectors can participate in standard Python arithmetic expressions via operator overloading. An attribute switch system allows user-defined metadata to be attached to vector objects.

---

## 2. Package Structure

```
vec-library/               # GitHub repository root
├── vec/                   # Installable Python package
│   ├── __init__.py        # Public API: exports Vec, RECT, POLAR
│   ├── core.py            # Vec class implementation
│   └── parser.py          # Initialization string parsing logic
├── tests/
│   └── test_vec.py        # Test suite
├── docs/
│   ├── vec_documentation.md       # User-facing: usage, methods, examples
│   └── spec/
│       └── vec_specification.md   # Internal: design decisions, rules, rationale
├── README.md
├── pyproject.toml         # pip-installable package configuration
└── LICENSE
```

The package can be installed globally via `pip`, or the `vec/` folder can be dropped directly into a project directory.

---

## 3. Module-Level Constants

Defined in `vec/__init__.py` and available upon import:

```python
RECT  = 0   # Rectangular form selector for asString()
POLAR = 1   # Polar form selector for asString()
```

**Usage:**
```python
from vec import Vec, RECT, POLAR
```

---

## 4. Class: Vec

### Constructor

```python
V = Vec(init_str | None)
```

- When a valid initialization string is provided, the vector is initialized immediately.
- When `None` is passed, the vector is created in an **uninitialized** state. Any operation attempted on an uninitialized vector raises a `VecError`.

**Examples:**
```python
V1 = Vec("-j4.1")
V2 = Vec(r"5.0 -A1.33 \rad")
V3 = Vec(None)                  # Uninitialized
V3.initialize("3 +j4")          # Initialized later
```

### `initialize(init_str)` Method

Initializes or **re-initializes** a vector from an initialization string.

- If the vector was previously initialized, the attribute list is **cleared** before parsing the new string.
- After re-initialization, the vector holds the new value and any attributes found in the new string.

```python
V = Vec(None)
V.initialize("10 +A45")              # Initialize
V.initialize(r"2 -j3 \parallel")     # Re-initialize; prior attributes cleared
```

---

## 5. Initialization Strings

The initialization string defines the vector's value and optional attribute switches. Parsing is handled by `parser.py`.

### 5.1 Rectangular Form

**Syntax:** `[real] [sign]j[imaginary] [\attr ...]`

- The real component is a signed floating-point number.
- The imaginary component is preceded by `+j` or `-j`.
- Whitespace between the sign character and `j` is permitted (e.g., `+ j1.5`).
- If the real component is omitted, it is assumed to be zero.

| Example String       | Interpretation            |
|----------------------|---------------------------|
| `"3.20 +j1.5"`       | 3.20 + j1.5               |
| `"+3.2 +j1.5"`       | 3.2 + j1.5                |
| `"3.3 -j1.5"`        | 3.3 − j1.5                |
| `"-1 -j6.1"`         | −1 − j6.1                 |
| `"-j4.1"`            | 0 − j4.1 (real = 0)       |
| `"3.2 + j1.5"`       | 3.2 + j1.5 (space before j allowed) |

### 5.2 Polar Form

**Syntax:** `[magnitude] [sign]A[angle] [\attr ...]`

- The magnitude is a non-negative floating-point number.
  - Exception: a negative magnitude (e.g., `-3.3`) is accepted and treated as the same magnitude at **angle + 180°**.
- The angle is preceded by `+A`, `-A`, `<`, or `∠` (Unicode U+2220).
- If the angle is omitted, it is assumed to be zero.
- By default, angles in the initialization string are interpreted as **degrees**.
- If the `\rad` attribute switch is present, the angle is interpreted as **radians**.

| Example String          | Interpretation                    |
|-------------------------|-----------------------------------|
| `"10.41 +A15.2"`        | Magnitude 10.41, angle +15.2°     |
| `r"5.0 -A1.33 \rad"`   | Magnitude 5.0, angle −1.33 rad    |
| `"3.3"`                 | Magnitude 3.3, angle 0°           |
| `"10 <45"`              | Magnitude 10, angle +45°          |
| `"10 ∠45"`              | Magnitude 10, angle +45°          |
| `"-3.3"`                | Magnitude 3.3, angle 180°         |

### 5.3 Accepted Angle Notations (Polar)

All three notations are equivalent and accepted interchangeably:

| Notation   | Example         |
|------------|-----------------|
| `+A` / `-A`| `"10 +A45"`     |
| `<`        | `"10 <45"`      |
| `∠`        | `"10 ∠45"`      |

### 5.4 Attribute Switches in the Initialization String

User-defined attribute switches may be appended to the initialization string after the vector value. Each attribute begins with `\` and is 1–15 characters long.

```python
V = Vec(r"5 +j10 \parallel \admittance")
V = Vec(r"10 +A45 \rad \source")
```

---

## 6. Attribute Switches

Every `Vec` object maintains an internal list of attribute strings. Attributes function as on/off switches — an attribute either exists in the list or it does not.

### 6.1 Format

An attribute is a string of 1–15 characters, conventionally prefixed with `\` in usage (though the backslash is part of the string itself).

### 6.2 Reserved Attribute: `\rad`

`\rad` is a reserved attribute name with special meaning:

- When set, the initialization string's angle is interpreted in **radians** (instead of the default degrees).
- When set, `ang()` returns the angle in **radians**.
- When set, `asString()` displays the angle in **radians**.
- Internally, all angles are always stored as **radians** regardless of this attribute.
- `\rad` follows the same union rule as all other attributes (see Section 13).

### 6.3 Attribute Methods

```python
V.addAttrib(r"\myattr")      # Add an attribute
V.delAttrib(r"\myattr")      # Remove an attribute (no error if not present)
V.hasAttrib(r"\myattr")      # Returns True if attribute exists, False otherwise
```

**Example:**
```python
V = Vec("0.3 +j0.10")
V.addAttrib(r"\parallel")
V.addAttrib(r"\admittance")

if V.hasAttrib(r"\parallel"):
    print("Vector components are in parallel.")
```

---

## 7. Operator Methods

The following operator methods are implemented. Each operator accepts either a `Vec` object or a scalar (numeric) value as the second operand. Scalars are automatically converted to a `Vec` internally before the operation is performed (see Section 12).

| Method        | Operation            |
|---------------|----------------------|
| `__add__`     | `V1 + V2`            |
| `__radd__`    | `scalar + V`         |
| `__sub__`     | `V1 - V2`            |
| `__rsub__`    | `scalar - V`         |
| `__mul__`     | `V1 * V2`            |
| `__rmul__`    | `scalar * V`         |
| `__truediv__` | `V1 / V2`            |
| `__rtruediv__`| `scalar / V`         |
| `__neg__`     | `-V` (negate)        |
| `__abs__`     | `abs(V)` (magnitude) |
| `__eq__`      | `V1 == V2` (equality with epsilon tolerance) |
| `__repr__`    | Developer-friendly representation |

Every arithmetic operation **always returns a new `Vec` object**. The operand vectors are never modified.

---

## 8. Value Extraction Methods

```python
V.real()          # Returns the real component (float)
V.img()           # Returns the imaginary component (float)
V.mag()           # Returns the magnitude (float)
V.ang()           # Returns the angle; radians if \rad is set, degrees otherwise (float)
a, b = V.rect()   # Returns (real, imaginary) as a tuple
mag, ang = V.polar()  # Returns (magnitude, angle) as a tuple
```

**Note:** `ang()` and `polar()` respect the `\rad` attribute for the returned angle unit.

---

## 9. String Representation Methods

### `asString(form, fmt1=None, fmt2=None)`

Returns a formatted string representation of the vector.

- `form`: `RECT` or `POLAR` (module-level constants).
- `fmt1`: Optional Python format string for the first component (real or magnitude).
- `fmt2`: Optional Python format string for the second component (imaginary or angle).

**Rectangular form output:** `[-][real] [+|-]j[imaginary]`

```python
V.asString(RECT)
# --> "-3.124479 -j4.5678987"

V.asString(RECT, fmt1="3.2f", fmt2="3.2f")
# --> "-3.12 -j4.57"
```

**Polar form output:** `[magnitude] ∠ [angle]`

- Angle is displayed in degrees or radians depending on the `\rad` attribute.

```python
V.asString(POLAR)
# --> "5.12345 ∠ 15.7654"

V.asString(POLAR, fmt1="6.2f", fmt2="3.0f")
# --> "  5.12 ∠  16"
```

### `__repr__`

Returns a developer-friendly string suitable for display in a Python REPL or debugger:

```python
repr(V)
# --> "Vec('3.2 +j1.5')"
```

---

## 10. Utility Methods

### `conjugate()`

Returns a new `Vec` object that is the complex conjugate of the vector (negates the imaginary component).

```python
V  = Vec("3 +j4")
Vc = V.conjugate()   # --> Vec representing 3 -j4
```

### `copy()`

Returns a new, independent `Vec` object with the same value and attributes as the original.

```python
V2 = V1.copy()
```

---

## 11. Internal Representation

- Vectors are stored internally in **both** rectangular (`a + jb`) and polar (`c ∠ θ`) forms at all times.
- Angles are **always stored internally in radians**, regardless of the `\rad` attribute setting.
- The `\rad` attribute affects only **input parsing** (initialization strings) and **output formatting** (`ang()`, `polar()`, `asString()`).

---

## 12. Scalar Conversion Rules

When an arithmetic operator receives a scalar (non-`Vec`) operand, the scalar is converted to a `Vec` internally as follows:

- The scalar value becomes the **real component**.
- The imaginary component is set to **+j0**.
- The resulting angle is **0** (pure real vector).
- The scalar-as-vector carries **no attributes**.

```python
result = 5 * V1     # 5 is converted to Vec("5 +j0") internally
result = V1 + 2.5   # 2.5 is converted to Vec("2.5 +j0") internally
```

---

## 13. Result Vector Rules

When an operation produces a result vector, the following rules govern its state:

### 13.1 Attribute List

The result vector's attribute list is the **union** of the attribute lists of both operands. If both operands carry the same attribute, it appears only once in the result.

```python
V1 = Vec(r"5 +j10 \parallel")
V2 = Vec(r"3 +j4 \admittance")
V3 = V1 + V2
# V3 has attributes: \parallel, \admittance
```

> **Note:** The `Vec` class performs the union mechanically and does not validate whether the combination of attributes is semantically meaningful. It is the responsibility of the calling application to ensure that attributes on operand vectors are compatible before performing operations.

### 13.2 The `\rad` Attribute on Results

Because `\rad` is simply a reserved attribute (not a special case), it follows the same union rule. If **either** operand has `\rad` set, the result will have `\rad` set.

> **Important:** If `V1` has `\rad` and `V2` does not, the result `V3 = V1 + V2` will display angles in radians, even if `V2`'s angle was originally expressed in degrees. This is expected behavior.

### 13.3 Initialization State

All result vectors are considered **fully initialized**.

---

## 14. Error Handling

The library defines a custom exception class `VecError` (inheriting from `Exception`) for all library-specific errors.

| Condition | Error Raised |
|---|---|
| Operation on an uninitialized vector | `VecError` |
| Invalid initialization string format | `VecError` |
| Division by a zero vector | `VecError` (division by zero) |
| Invalid attribute name (length 0 or > 15) | `VecError` |

---

## 15. General Usage Examples

### Basic Instantiation and Arithmetic

```python
from vec import Vec, RECT, POLAR

V1 = Vec(r"5 +j10 \parallel")
V2 = Vec(r"3 +A22 \parallel")
V3 = 5 * V1 / V2

print(V3.asString(RECT))
print(V3.asString(POLAR, fmt1="6.3f", fmt2="5.1f"))
```

### Deferred Initialization

```python
V1 = Vec(None)
V1.initialize(r"5 +j10 \parallel")

V2 = Vec(None)
V2.initialize(r"3 +A22 \parallel")
```

### Attributes

```python
V = Vec("0.3 +j0.10")
V.addAttrib(r"\parallel")
V.addAttrib(r"\admittance")

if V.hasAttrib(r"\admittance"):
    print("This vector represents admittance.")

V.delAttrib(r"\parallel")
```

### Operator Examples

```python
V1 = Vec("3 +j4")
V2 = Vec("1 -j2")

V3 = V1 + V2          # Vector addition
V4 = V1 * V2          # Vector multiplication
V5 = -V1              # Negation: -3 -j4
mag = abs(V1)         # Magnitude: 5.0
Vc = V1.conjugate()   # Conjugate: 3 -j4
V6 = V1.copy()        # Independent copy

print(V1 == V2)       # False (epsilon-tolerant comparison)
```

### Radians Mode

```python
V = Vec(r"5.0 +A1.5708 \rad")   # angle in radians (~90°)
print(V.ang())                   # returns angle in radians
print(V.asString(POLAR))         # displays angle in radians
```

---

*End of Specification*
