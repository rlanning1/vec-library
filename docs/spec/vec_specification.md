# pyVectors — Python Vector Library
## Finalized Specification

**Version:** 1.1.0
**Date:** 2026-04-01
**Status:** Approved
**Authors:** Ron Lanning, Claude Sonnet 4.6

> **Note:** This is an internal design document intended for developers and maintainers. It records the design decisions, implementation rules, and rationale behind the `pyVectors` library. For installation and usage instructions, see `docs/vec_documentation.md` and `README.md`.

---

## Table of Contents

1. [Overview](#overview)
2. [Package Structure](#package-structure)
3. [Module-Level Constants and Variables](#module-level-constants-and-variables)
4. [Class: Vector](#class-vector)
5. [Initialization Strings](#initialization-strings)
6. [Variable Substitution in Initialization Strings](#variable-substitution-in-initialization-strings)
7. [Attribute Switches](#attribute-switches)
8. [Angle Unit Selection](#angle-unit-selection)
9. [Operator Methods](#operator-methods)
10. [Value Extraction Methods](#value-extraction-methods)
11. [String Representation Methods](#string-representation-methods)
12. [Utility Methods](#utility-methods)
13. [Internal Representation](#internal-representation)
14. [Scalar Conversion Rules](#scalar-conversion-rules)
15. [Result Vector Rules](#result-vector-rules)
16. [Error Handling](#error-handling)
17. [Backward Compatibility](#backward-compatibility)
18. [General Usage Examples](#general-usage-examples)

---

## 1. Overview

`pyVectors` is a Python library for representing and manipulating complex vectors (phasors). Each vector is maintained internally in both rectangular (`a + jb`) and polar (`c ∠ θ`) forms. Vectors can participate in standard Python arithmetic expressions via operator overloading. An attribute switch system allows user-defined metadata to be attached to vector objects.

---

## 2. Package Structure

```
pyVectors/                 # GitHub repository root
├── vec/                   # Installable Python package
│   ├── __init__.py        # Public API: exports Vector, Vec, RECT, POLAR, RADIANS
│   ├── core.py            # Vector class implementation
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

## 3. Module-Level Constants and Variables

Defined in `vec/__init__.py` and available upon import:

```python
RECT    = 0      # Rectangular form selector for asString()
POLAR   = 1      # Polar form selector for asString()
RADIANS = False  # Global angle-unit flag (mutable)
```

**Usage:**
```python
from vec import Vector, RECT, POLAR

import vec
vec.RADIANS = True    # enable global radians mode
```

`RADIANS` is a mutable module-level variable. It must be set via the module reference (`vec.RADIANS = True`), not via a `from` import, since the `from` import creates a local copy that is disconnected from the module namespace.

---

## 4. Class: Vector

### Constructor

```python
V = Vector(init_str | None)
```

- When a valid initialization string is provided, the vector is initialized immediately.
- When `None` is passed, the vector is created in an **uninitialized** state. Any operation attempted on an uninitialized vector raises a `VecError`.

**Examples:**
```python
V1 = Vector("-j4.1")
V2 = Vector(r"5.0 -A1.33 \rad")
V3 = Vector(None)                  # Uninitialized
V3.initialize("3 +j4")             # Initialized later
```

### `initialize(init_str)` Method

Initializes or **re-initializes** a vector from an initialization string.

- If the vector was previously initialized, the attribute list is **cleared** before parsing the new string.
- After re-initialization, the vector holds the new value and any attributes found in the new string.

```python
V = Vector(None)
V.initialize("10 +A45")                   # Initialize
V.initialize(r"2 -j3 \parallel")         # Re-initialize; prior attributes cleared
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
- The angle unit is determined by the rules in Section 7.

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
V = Vector(r"5 +j10 \parallel \admittance")
V = Vector(r"10 +A45 \rad \source")
```

---

## 6. Variable Substitution in Initialization Strings

### 6.1 Overview

Starting in v1.1.0, initialization strings may contain Python variable names in place of numeric literals. The pre-parser resolves each variable by looking it up in the **caller's local scope** at the moment `Vector()` or `initialize()` is called.

```python
R11 = 10000.0
Xc  = 452.0
m   = 20.22
a   = 45.0

V1 = Vector("R11 +j Xc")    # resolved to "10000.0 +j 452.0"
V2 = Vector("m < a")         # resolved to "20.22 < 45.0"
V3 = 5.0 * V1 / V2
```

Variable substitution is applied to **every** initialization string before any parsing occurs. No opt-in is required.

### 6.2 Resolution Rules

1. Every token in the value portion of the string that matches the Python identifier pattern `[A-Za-z_][A-Za-z0-9_]*` is a candidate for substitution.
2. The token is looked up in the caller's `f_locals` dictionary at call time.
3. If found and the value is `int` or `float`, it is replaced with `str(float(value))`.
4. If not found, `VecError` is raised immediately.
5. If found but the value is not `int` or `float`, `VecError` is raised.

### 6.3 Protected Tokens

The single-character tokens `j` and `A` are **always** protected — they are structural syntax characters in the init string and are never treated as variable names:

- `j` is the imaginary-unit separator in rectangular form (`+j`, `-j`)
- `A` is the angle separator in polar form (`+A`, `-A`)

Compact fused forms such as `j4`, `j10`, or `A45` (operator letter immediately followed by digits) are also protected. These are the standard compact notation for the rectangular and polar forms and are not variable references.

Attribute-switch tokens (e.g., `ad`, `\parallel`) are exempt from substitution because the pre-parser's token regex uses a negative lookbehind on `\` and only the value portion before any attribute switches is scanned.

### 6.4 Variable Naming Constraints and Recommendations

Variable names used inside initialization strings must satisfy the standard Python identifier rules:

- Must begin with a letter (`A–Z`, `a–z`) or underscore (`_`)
- Remaining characters may be letters, digits (`0–9`), or underscores
- Single-character names `j` and `A` are reserved by the parser and cannot be substituted

The following examples illustrate valid and invalid usages:

| Variable name | Valid? | Reason |
|---|---|---|
| `R11` | ✓ | Letter prefix, digits allowed after |
| `R001` | ✓ | Letter prefix, zero-padded digits allowed |
| `Xc` | ✓ | Standard identifier |
| `_r`, `_x` | ✓ | Underscore prefix allowed |
| `resistance` | ✓ | Fully alphabetic |
| `j` | ✗ | Protected structural token |
| `A` | ✗ | Protected structural token |
| `2R` | ✗ | Starts with a digit — not a valid Python identifier |

> **Recommendation — use a space before the variable name in rectangular form.**
>
> The compact fused forms (`+j4`, `-j10`) are protected from substitution, but forms like `+jXc` — where `j` and a variable name are written without a space — may produce unexpected behavior because the pre-parser will see `jXc` as a single identifier token and attempt to look it up as a variable named `jXc`.
>
> Always write a space between `j` and a variable name:
>
> ```python
> Xc = 452.0
> V = Vector("R11 +j Xc")    # correct — space after j
> V = Vector("R11 +jXc")     # avoid — 'jXc' is parsed as one identifier
> ```
>
> Similarly for polar `A` notation:
>
> ```python
> theta = 45.0
> V = Vector("10 +A theta")   # correct — space after A
> V = Vector("10 +Atheta")    # avoid — 'Atheta' is parsed as one identifier
> ```
>
> The `<` and `∠` notations do not have this adjacency issue and are safe to use with or without a space.

### 6.5 Variable Substitution with `initialize()`

The `initialize()` method also performs variable substitution from its **own** caller's local scope:

```python
def setup_circuit():
    R = 330.0
    X = 75.5
    V = Vector(None)
    V.initialize("R +j X")    # R and X resolved from setup_circuit's locals
    return V
```

### 6.6 Scope Limitation

The pre-parser looks only one frame up the call stack — the direct caller of `Vector()` or `initialize()`. Variables defined in enclosing scopes (e.g., outer functions, module globals not imported into the local namespace) that are not present in the immediate caller's `f_locals` will not be found and will raise `VecError`.

To use a module-level or outer-scope variable, either assign it locally first or pass it as a literal:

```python
MODULE_R = 1000.0   # module-level

def build_vector():
    R = MODULE_R    # bring into local scope
    V = Vector("R +j0")    # works
    return V
```


---

## 7. Attribute Switches

Every `Vector` object maintains an internal list of attribute strings. Attributes function as on/off switches — an attribute either exists in the list or it does not.

### 6.1 Format

An attribute is a string of 1–15 characters, conventionally prefixed with `\` in usage (though the backslash is part of the string itself).

### 6.2 Reserved Attribute: `\rad`

`\rad` is a reserved attribute name with special meaning:

- When set, the initialization string's polar angle is interpreted in **radians**.
- When set (and `\deg` is not set), `ang()` returns the angle in **radians**.
- When set (and `\deg` is not set), `polar()` returns the angle in **radians**.
- When set (and `\deg` is not set), `asString(POLAR)` displays the angle in **radians**.
- Internally, all angles are always stored as **radians** regardless of this attribute.
- `\rad` follows the same union rule as all other attributes (see Section 14).

### 6.3 Reserved Attribute: `\deg`

`\deg` is a reserved attribute name that overrides the angle unit to degrees:

- When set, the initialization string's polar angle is interpreted in **degrees**, regardless of the `RADIANS` global flag.
- When set, `ang()`, `polar()`, and `asString(POLAR)` output the angle in **degrees**.
- When both `\rad` and `\deg` are present (e.g., inherited via result union), `\deg` takes priority for all angle output.
- `\deg` follows the same union rule as all other attributes.

### 6.4 Attribute Methods

```python
V.addAttrib(r"\myattr")      # Add an attribute
V.delAttrib(r"\myattr")      # Remove an attribute (no error if not present)
V.hasAttrib(r"\myattr")      # Returns True if attribute exists, False otherwise
```

**Example:**
```python
V = Vector("0.3 +j0.10")
V.addAttrib(r"\parallel")
V.addAttrib(r"\admittance")

if V.hasAttrib(r"\parallel"):
    print("Vector components are in parallel.")
```

---

## 8. Angle Unit Selection

Angle unit selection is resolved at three levels, applied in the following priority order:

| Priority | Mechanism | Description |
|----------|-----------|-------------|
| 1 (highest) | `\deg` attribute on the vector | Forces degrees for input parsing and all angle output |
| 2 | `\rad` attribute on the vector | Forces radians for input parsing and all angle output |
| 3 (lowest) | `RADIANS` module-level variable | Sets the default when neither `\rad` nor `\deg` is present |

### 7.1 RADIANS = False (default)

- Polar angle input is parsed as degrees unless `\rad` is present.
- Angle output is in degrees unless `\rad` is present.
- `\deg` has no visible effect (already in degrees mode), but is stored and propagates via union.

### 7.2 RADIANS = True

- Every vector created from an initialization string automatically receives the `\rad` attribute, **unless** `\deg` is present in the init string.
- If `\deg` is present, `\rad` is not injected, and `\deg` governs the vector's angle I/O.
- Polar angle input is parsed as radians by default (or degrees if `\deg` is present).
- Angle output is in radians by default (or degrees if `\deg` is present).

### 7.3 Auto-injection applies to init-string construction only

The `RADIANS` auto-injection of `\rad` applies only when a vector is constructed from an initialization string (`Vector(init_str)` or `initialize(init_str)`). Arithmetic result vectors are **not** subject to auto-injection — they inherit their angle unit attributes purely through the union rule (Section 14.1).

### 7.4 Parsing interaction

The `parser.parse()` function receives the `global_radians` flag from `Vector._parse_and_set()`. The parser resolves the effective `rad_flag` for polar angle parsing as follows:

1. If `\rad` is present in attrs → `rad_flag = True`
2. If `\deg` is present in attrs → `rad_flag = False`
3. Otherwise → `rad_flag = global_radians`

After parsing, `Vector._parse_and_set()` applies the RADIANS auto-injection to the attribute list.

---

## 9. Operator Methods

The following operator methods are implemented. Each operator accepts either a `Vector` object or a scalar (numeric) value as the second operand. Scalars are automatically converted to a `Vector` internally before the operation is performed (see Section 13).

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

Every arithmetic operation **always returns a new `Vector` object**. The operand vectors are never modified.

---

## 10. Value Extraction Methods

```python
V.real()          # Returns the real component (float)
V.img()           # Returns the imaginary component (float)
V.mag()           # Returns the magnitude (float)
V.ang()           # Returns the angle per Section 7 rules (float)
a, b = V.rect()   # Returns (real, imaginary) as a tuple
mag, ang = V.polar()  # Returns (magnitude, angle) as a tuple
```

**Note:** `ang()` and `polar()` respect the angle unit selection rules in Section 7.

---

## 11. String Representation Methods

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

- Angle unit follows the rules in Section 7.

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
# --> "Vector('3.2 +j1.5')"
```

---

## 12. Utility Methods

### `conjugate()`

Returns a new `Vector` object that is the complex conjugate of the vector (negates the imaginary component).

```python
V  = Vector("3 +j4")
Vc = V.conjugate()   # --> Vector representing 3 -j4
```

### `copy()`

Returns a new, independent `Vector` object with the same value and attributes as the original.

```python
V2 = V1.copy()
```

---

## 13. Internal Representation

- Vectors are stored internally in **both** rectangular (`a + jb`) and polar (`c ∠ θ`) forms at all times.
- Angles are **always stored internally in radians**, regardless of any attribute setting or the `RADIANS` flag.
- The angle unit attributes and `RADIANS` flag affect only **input parsing** and **output formatting**.

---

## 14. Scalar Conversion Rules

When an arithmetic operator receives a scalar (non-`Vector`) operand, the scalar is converted to a `Vector` internally as follows:

- The scalar value becomes the **real component**.
- The imaginary component is set to **+j0**.
- The resulting angle is **0** (pure real vector).
- The scalar-as-vector carries **no attributes**.

```python
result = 5 * V1     # 5 is converted to Vector("5 +j0") internally
result = V1 + 2.5   # 2.5 is converted to Vector("2.5 +j0") internally
```

---

## 15. Result Vector Rules

When an operation produces a result vector, the following rules govern its state:

### 14.1 Attribute List

The result vector's attribute list is the **union** of the attribute lists of both operands. If both operands carry the same attribute, it appears only once in the result.

```python
V1 = Vector(r"5 +j10 \parallel")
V2 = Vector(r"3 +j4 \admittance")
V3 = V1 + V2
# V3 has attributes: \parallel, \admittance
```

> **Note:** The `Vector` class performs the union mechanically and does not validate whether the combination of attributes is semantically meaningful. It is the responsibility of the calling application to ensure that attributes on operand vectors are compatible before performing operations.

### 14.2 The `\rad` and `\deg` Attributes on Results

Both `\rad` and `\deg` follow the same union rule as all other attributes. If **either** operand has `\rad` set, the result will have `\rad` set. Likewise for `\deg`.

When a result carries both `\rad` and `\deg`, `\deg` takes priority for all angle output (degrees mode).

> **Important:** If `V1` has `\rad` and `V2` does not, the result `V3 = V1 + V2` will display angles in radians, even if `V2`'s angle was originally expressed in degrees. This is expected behavior.

### 14.3 RADIANS Auto-Injection Does Not Apply to Results

The `RADIANS` global flag auto-injects `\rad` only when a vector is created directly from an initialization string. Arithmetic result vectors are **never** subject to auto-injection. Their angle unit attributes are determined purely by the union of their operands' attributes.

### 14.4 Initialization State

All result vectors are considered **fully initialized**.

---

## 16. Error Handling

The library defines a custom exception class `VecError` (inheriting from `Exception`) for all library-specific errors.

| Condition | Error Raised |
|---|---|
| Operation on an uninitialized vector | `VecError` |
| Invalid initialization string format | `VecError` |
| Division by a zero vector | `VecError` (division by zero) |
| Invalid attribute name (length 0 or > 15) | `VecError` |
| Variable name in init string not found in caller's local scope | `VecError` |
| Variable in init string is not `int` or `float` | `VecError` |

---

## 17. Backward Compatibility

The `Vec` name from v1.0.0 is preserved as a module-level alias:

```python
Vec = Vector   # defined in vec/core.py and exported from vec/__init__.py
```

All code written against v1.0.0 continues to work without modification. `Vec` and `Vector` are the same class object — `Vec is Vector` evaluates to `True`.

---

## 18. General Usage Examples

### Basic Instantiation and Arithmetic

```python
from vec import Vector, RECT, POLAR

V1 = Vector(r"5 +j10 \parallel")
V2 = Vector(r"3 +A22 \parallel")
V3 = 5 * V1 / V2

print(V3.asString(RECT))
print(V3.asString(POLAR, fmt1="6.3f", fmt2="5.1f"))
```

### Deferred Initialization

```python
V1 = Vector(None)
V1.initialize(r"5 +j10 \parallel")

V2 = Vector(None)
V2.initialize(r"3 +A22 \parallel")
```

### Attributes

```python
V = Vector("0.3 +j0.10")
V.addAttrib(r"\parallel")
V.addAttrib(r"\admittance")

if V.hasAttrib(r"\admittance"):
    print("This vector represents admittance.")

V.delAttrib(r"\parallel")
```

### Operator Examples

```python
V1 = Vector("3 +j4")
V2 = Vector("1 -j2")

V3 = V1 + V2          # Vector addition
V4 = V1 * V2          # Vector multiplication
V5 = -V1              # Negation: -3 -j4
mag = abs(V1)         # Magnitude: 5.0
Vc = V1.conjugate()   # Conjugate: 3 -j4
V6 = V1.copy()        # Independent copy

print(V1 == V2)       # False (epsilon-tolerant comparison)
```

### Per-Vector Radians Mode

```python
V = Vector(r"5.0 +A1.5708 \rad")   # angle in radians (~90°)
print(V.ang())                        # returns angle in radians
print(V.asString(POLAR))              # displays angle in radians
```

### Global Radians Mode

```python
import vec
from vec import Vector, RECT, POLAR

vec.RADIANS = True

V1 = Vector("10 +A1.5708")           # parsed as radians; \rad auto-injected
V2 = Vector(r"10 +A90 \deg")        # \deg override; parsed as degrees

print(V1.ang())                       # radians
print(V2.ang())                       # degrees

vec.RADIANS = False
```

---

*End of Specification*
