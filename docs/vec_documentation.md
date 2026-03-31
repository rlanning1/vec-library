# Vec — Python Vector Library
## User Documentation

**Version:** 1.0  
**Package:** `vec`

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Quick Start](#3-quick-start)
4. [Importing the Library](#4-importing-the-library)
5. [Creating Vectors](#5-creating-vectors)
6. [Initialization String Reference](#6-initialization-string-reference)
7. [Value Extraction Methods](#7-value-extraction-methods)
8. [Arithmetic Operations](#8-arithmetic-operations)
9. [String Representation](#9-string-representation)
10. [Attribute Switches](#10-attribute-switches)
11. [Utility Methods](#11-utility-methods)
12. [Error Handling](#12-error-handling)
13. [Worked Examples](#13-worked-examples)

---

## 1. Introduction

`Vec` is a Python library for representing and manipulating complex vectors (phasors). It is designed for engineering and scientific applications where quantities are most naturally expressed in either rectangular (`a + jb`) or polar (`M ∠ θ`) form.

Key features:

- Flexible initialization strings support both rectangular and polar input, with or without explicit angle notation
- Both forms are maintained internally at all times, so you can query either without conversion
- Full arithmetic operator support (`+`, `-`, `*`, `/`, negation, `abs()`) accepting both `Vec` operands and plain scalars
- An attribute switch system allows user-defined metadata to be attached to vectors and propagated through calculations
- Angles default to degrees, with optional radians mode via the `\rad` attribute
- A `VecError` exception is raised for all library-specific error conditions

---

## 2. Installation

### Option A — Install from the package directory (editable install)

This is the recommended approach for local development and use.

```bash
cd vec-library
pip install -e .
```

After this, `from vec import Vec, RECT, POLAR` works in any Python script or interpreter session.

### Option B — Drop-in usage

If you prefer not to install the package, copy the `vec/` folder directly into your project directory. The import statement is the same.

### Requirements

- Python 3.10 or later
- No third-party dependencies

### Verifying the installation

```python
from vec import Vec, RECT, POLAR

V = Vec("3 +j4")
print(V.asString(RECT))    # 3.0 +j4.0
print(V.asString(POLAR))   # 5.0 ∠ 53.13010235415598
```

---

## 3. Quick Start

```python
from vec import Vec, RECT, POLAR

# Create two phasors in rectangular form
V1 = Vec("120 +j0")           # 120 V at 0°
V2 = Vec("0 -j50")            # Capacitive reactance

# Add them
Vtotal = V1 + V2
print(Vtotal.asString(RECT))           # 120.0 -j50.0
print(Vtotal.asString(POLAR, fmt2="4.1f"))  # 130.0 ∠ -22.6°

# Scale a vector
Vscaled = 2.5 * V1
print(Vscaled.asString(RECT))          # 300.0 +j0.0

# Query components individually
print(f"Real: {Vtotal.real()}, Imag: {Vtotal.img()}")
print(f"Magnitude: {Vtotal.mag():.4f}, Angle: {Vtotal.ang():.2f}°")
```

---

## 4. Importing the Library

```python
from vec import Vec, RECT, POLAR
```

The three public names are:

| Name    | Type  | Value | Purpose                              |
|---------|-------|-------|--------------------------------------|
| `Vec`   | class | —     | The vector class                     |
| `RECT`  | int   | `0`   | Rectangular form selector for `asString()` |
| `POLAR` | int   | `1`   | Polar form selector for `asString()`  |

---

## 5. Creating Vectors

### 5.1 Direct initialization

Pass an initialization string to the constructor. The string defines the vector's value and optional attribute switches.

```python
V1 = Vec("3 +j4")           # Rectangular: 3 + j4
V2 = Vec("10 <45")          # Polar: magnitude 10, angle 45°
V3 = Vec("-j4.1")           # Rectangular: 0 − j4.1
```

### 5.2 Deferred initialization

Pass `None` to create an uninitialized vector, then call `initialize()` when ready.

```python
V = Vec(None)
# ... some time later ...
V.initialize("3 +j4")
```

Any operation on an uninitialized vector raises a `VecError`. Deferred initialization is useful when the vector's value is not yet known at the point of declaration.

### 5.3 Re-initialization

Calling `initialize()` on an already-initialized vector replaces its value entirely. The previous value and all attributes are discarded before the new string is parsed.

```python
V = Vec("5 +j0")
V.initialize("3 +j4")          # V now represents 3 + j4
V.initialize(r"10 <90 \source") # V now represents 10 ∠ 90° with \source attribute
```

---

## 6. Initialization String Reference

The initialization string specifies the vector's value and any attribute switches. Parsing is flexible: extra whitespace is tolerated and several equivalent notations are accepted.

### 6.1 Rectangular form

**Syntax:** `[real] [sign]j[imaginary] [\attr ...]`

The string is in rectangular form if it contains the letter `j`.

- The real component is a signed floating-point number. If omitted, it defaults to `0`.
- The imaginary component follows a `+j` or `-j` prefix.
- A space between the sign character and `j` is permitted.
- Scientific notation is supported (e.g., `1e-3`).

| Initialization string | Value              |
|-----------------------|--------------------|
| `"3.2 +j1.5"`         | 3.2 + j1.5         |
| `"+3.2 +j1.5"`        | 3.2 + j1.5         |
| `"3.3 -j1.5"`         | 3.3 − j1.5         |
| `"-1 -j6.1"`          | −1 − j6.1          |
| `"-j4.1"`             | 0 − j4.1           |
| `"3.2 + j1.5"`        | 3.2 + j1.5 (space before j allowed) |
| `"1e-3 +j2e-3"`       | 0.001 + j0.002     |

### 6.2 Polar form

**Syntax:** `[magnitude] [angle_notation][angle] [\attr ...]`

The string is in polar form if it does not contain `j`.

- The magnitude is a non-negative floating-point number. A negative magnitude (e.g., `-3.3`) is accepted and treated as the same magnitude rotated by 180°.
- The angle follows one of the three notations described below. If the angle is omitted entirely, it defaults to 0°.
- Angles are interpreted as **degrees** by default. Include the `\rad` attribute to interpret the angle as radians.

| Initialization string         | Value                         |
|-------------------------------|-------------------------------|
| `"10.41 +A15.2"`              | Magnitude 10.41, angle +15.2° |
| `"10 -A30"`                   | Magnitude 10, angle −30°      |
| `"10 <45"`                    | Magnitude 10, angle +45°      |
| `"10 ∠45"`                    | Magnitude 10, angle +45°      |
| `"3.3"`                       | Magnitude 3.3, angle 0°       |
| `"-3.3"`                      | Magnitude 3.3, angle 180°     |
| `r"5.0 -A1.33 \rad"`          | Magnitude 5.0, angle −1.33 rad |

### 6.3 Angle notations (polar)

All three notations are fully equivalent:

| Notation  | Example       | Notes                        |
|-----------|---------------|------------------------------|
| `+A`/`-A` | `"10 +A45"`   | Sign explicitly given        |
| `<`       | `"10 <45"`    | Always a positive angle      |
| `∠`       | `"10 ∠45"`    | Unicode angle symbol U+2220  |

### 6.4 Including attributes in the initialization string

Attribute switches can be embedded at the end of the initialization string. Each attribute begins with `\` followed by 1–15 characters.

```python
V1 = Vec(r"5 +j10 \parallel \admittance")
V2 = Vec(r"10 +A45 \source")
V3 = Vec(r"5.0 +A1.5708 \rad")   # angle is in radians
```

---

## 7. Value Extraction Methods

All value extraction methods raise `VecError` if called on an uninitialized vector.

### `real()` — real component

```python
V = Vec("3 +j4")
print(V.real())    # 3.0
```

### `img()` — imaginary component

```python
V = Vec("3 +j4")
print(V.img())     # 4.0
```

### `mag()` — magnitude

```python
V = Vec("3 +j4")
print(V.mag())     # 5.0
```

### `ang()` — angle

Returns the angle in **degrees** by default, or in **radians** if the `\rad` attribute is set.

```python
V = Vec("3 +j4")
print(V.ang())     # 53.13010235415598  (degrees)

Vr = Vec(r"3 +j4 \rad")
print(Vr.ang())    # 0.9272952180016122  (radians)
```

### `rect()` — rectangular tuple

Returns `(real, imaginary)` as a `(float, float)` tuple.

```python
V = Vec("3 +j4")
a, b = V.rect()
print(a, b)        # 3.0  4.0
```

### `polar()` — polar tuple

Returns `(magnitude, angle)` as a `(float, float)` tuple. The angle unit follows the `\rad` attribute, same as `ang()`.

```python
V = Vec("3 +j4")
m, theta = V.polar()
print(m, theta)    # 5.0  53.13010235415598
```

---

## 8. Arithmetic Operations

All arithmetic operators accept either a `Vec` operand or a plain scalar (`int` or `float`). Scalars are automatically treated as a purely real vector (`scalar + j0`) with no attributes.

Every operation returns a **new** `Vec` object. The original operands are never modified.

### Addition

```python
V1 = Vec("3 +j4")
V2 = Vec("1 -j2")
V3 = V1 + V2               # Vec: 4 + j2

V4 = V1 + 5               # Vec: 8 + j4
V5 = 5 + V1               # Vec: 8 + j4  (scalar on the left)
```

### Subtraction

```python
V3 = V1 - V2               # Vec: 2 + j6
V4 = V1 - 1               # Vec: 2 + j4
V5 = 10 - V1              # Vec: 7 - j4  (scalar on the left)
```

### Multiplication

Complex multiplication: `(a + jb)(c + jd) = (ac − bd) + j(ad + bc)`

```python
V3 = V1 * V2               # Complex multiplication
V4 = 3 * V1               # Scalar scaling: 9 + j12
V5 = V1 * 3               # Same result
```

### Division

```python
V3 = V1 / V2               # Complex division
V4 = V1 / 2               # Scalar division: 1.5 + j2
V5 = 10 / V1              # Scalar divided by Vec
```

Dividing by a zero vector raises `VecError`.

### Negation

```python
V = Vec("3 +j4")
Vn = -V                    # Vec: -3 - j4
```

### Magnitude via `abs()`

`abs()` returns a plain `float`, not a `Vec`.

```python
V = Vec("3 +j4")
m = abs(V)                 # 5.0  (float)
```

### Equality

`==` uses an epsilon tolerance of `1e-9` on both components.

```python
V1 = Vec("3 +j4")
V2 = Vec("5 <53.13010235415598")   # Same point, polar form

print(V1 == V2)             # True
print(V1 == Vec("1 +j0"))   # False
```

### Chaining

Operations can be chained freely:

```python
result = (V1 + V2) * V3 / 2
result = 5 * V1 - V2 + Vec("1 +j0")
```

---

## 9. String Representation

### `asString(form, fmt1=None, fmt2=None)`

Returns a formatted string of the vector.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `form` | `int` | `RECT` for rectangular form, `POLAR` for polar form |
| `fmt1` | `str`, optional | Python format spec for the first component (real part or magnitude) |
| `fmt2` | `str`, optional | Python format spec for the second component (imaginary part or angle) |

**Rectangular output format:** `[real] [+|-]j[imaginary]`

```python
V = Vec("-3.124479 -j4.5678987")

V.asString(RECT)
# '-3.124479 -j4.5678987'

V.asString(RECT, fmt1=".2f", fmt2=".2f")
# '-3.12 -j4.57'

V.asString(RECT, fmt1="10.4f", fmt2="10.4f")
# '   -3.1245 -j   4.5679'
```

**Polar output format:** `[magnitude] ∠ [angle]`

The angle is in degrees by default, or radians if `\rad` is set.

```python
V = Vec("5.12345 <15.7654")

V.asString(POLAR)
# '5.12345 ∠ 15.7654'

V.asString(POLAR, fmt1="6.2f", fmt2=".1f")
# '  5.12 ∠ 15.8'
```

**Radians mode:**

```python
V = Vec(r"5.0 +A1.5708 \rad")

V.asString(POLAR)
# '5.0 ∠ 1.5708'   (angle displayed in radians)
```

### `repr()`

Returns a developer-friendly string intended for use in a Python REPL or debugger. The format is always rectangular.

```python
V = Vec("3 +j4")
repr(V)
# "Vec('3.0 +j4.0')"

V_uninit = Vec(None)
repr(V_uninit)
# 'Vec(None)'
```

---

## 10. Attribute Switches

Every `Vec` object maintains an internal list of user-defined string attributes. Attributes function as on/off switches: an attribute is either present in the list or it is not.

Attributes are conventionally written with a leading `\`, for example `\parallel` or `\source`. The backslash is part of the attribute name itself. The name portion (after the `\`) must be 1–15 characters.

### Adding and removing attributes

```python
V = Vec("0.3 +j0.1")

V.addAttrib(r"\parallel")
V.addAttrib(r"\admittance")

V.hasAttrib(r"\parallel")     # True
V.hasAttrib(r"\source")       # False

V.delAttrib(r"\parallel")
V.hasAttrib(r"\parallel")     # False

V.delAttrib(r"\source")       # No error if not present
```

### Attribute propagation through arithmetic

When an arithmetic operation is performed, the result vector carries the **union** of the attribute lists of both operands. Duplicate attributes appear only once.

```python
V1 = Vec(r"5 +j10 \parallel")
V2 = Vec(r"3 +j4 \admittance")
V3 = V1 + V2

V3.hasAttrib(r"\parallel")    # True
V3.hasAttrib(r"\admittance")  # True
```

This propagation happens automatically — you do not need to manage result attributes manually.

**Note:** The library performs the union mechanically without checking whether the combination of attributes makes semantic sense. If `V1` represents an admittance and `V2` represents something else, the result carrying both attributes is technically correct per the library's rules but may require interpretation by your application.

### The reserved `\rad` attribute

`\rad` is a built-in reserved attribute with a special effect on angle handling:

| When `\rad` is set | Behavior |
|--------------------|----------|
| Initialization string | The angle value is interpreted as **radians** (not degrees) |
| `ang()` | Returns the angle in **radians** |
| `polar()` | Returns the angle in **radians** |
| `asString(POLAR, ...)` | Displays the angle in **radians** |

Internally, all angles are always stored as radians regardless of this attribute. The `\rad` attribute affects only how angles are read and displayed.

Because `\rad` follows the same union rule as all other attributes, a result carries `\rad` if **either** operand had it set — even if the other operand's angle was in degrees.

```python
V1 = Vec(r"5 +A1.5708 \rad")    # angle in radians
V2 = Vec("3 +j4")               # angle in degrees, no \rad

V3 = V1 + V2
V3.hasAttrib(r"\rad")            # True — inherited from V1
print(V3.ang())                  # angle in radians
```

---

## 11. Utility Methods

### `conjugate()`

Returns a new `Vec` that is the complex conjugate of the original (the imaginary component is negated). The original is not modified. Attributes are copied to the result.

```python
V  = Vec("3 +j4")
Vc = V.conjugate()

print(Vc.asString(RECT))    # 3.0 -j4.0
print(V.asString(RECT))     # 3.0 +j4.0  (unchanged)
```

### `copy()`

Returns a new, independent `Vec` with the same value and attributes. Modifying the copy does not affect the original.

```python
V1 = Vec(r"3 +j4 \source")
V2 = V1.copy()

V2.addAttrib(r"\modified")
V1.hasAttrib(r"\modified")     # False — V1 is unaffected
```

---

## 12. Error Handling

The library defines a custom exception class:

```python
from vec import Vec
# VecError is also available if you need to catch it:
from vec.core import VecError
```

All library errors raise `VecError`. The conditions that trigger it are:

| Condition | Message |
|-----------|---------|
| Operation on an uninitialized vector | `"Operation on an uninitialized Vec."` |
| Invalid initialization string | Describes the malformed input |
| Division by a zero vector | `"Division by a zero vector."` |
| Invalid attribute name (empty or > 15 chars) | Describes the invalid name |

**Catching errors:**

```python
from vec import Vec
from vec.core import VecError

try:
    V = Vec("not a valid string")
except VecError as e:
    print(f"Vec error: {e}")

try:
    V = Vec(None)
    print(V.real())          # raises VecError
except VecError as e:
    print(f"Vec error: {e}")
```

---

## 13. Worked Examples

### Example 1 — Parallel impedance

Two impedances in parallel: `Z_total = (Z1 * Z2) / (Z1 + Z2)`

```python
from vec import Vec, RECT, POLAR

Z1 = Vec("0 +j100")       # Pure inductor: 100 Ω inductive reactance
Z2 = Vec("75 +j0")        # Pure resistor: 75 Ω

Z_parallel = (Z1 * Z2) / (Z1 + Z2)

print(Z_parallel.asString(RECT,  fmt1=".3f", fmt2=".3f"))
# 36.585 +j48.780

print(Z_parallel.asString(POLAR, fmt1=".3f", fmt2=".2f"))
# 60.976 ∠ 53.13
```

### Example 2 — Voltage divider with phasors

A sinusoidal source drives a series R–L circuit. Find the voltage across the resistor.

```python
from vec import Vec, RECT, POLAR

Vs  = Vec("120 <0")        # Source voltage, 120 V at 0°
R   = Vec("40 +j0")        # Resistor
XL  = Vec("0 +j30")        # Inductive reactance
Z   = R + XL               # Total series impedance

I   = Vs / Z               # Current phasor
VR  = I * R                # Voltage across resistor

print("Current:  ", I.asString(POLAR, fmt1="6.3f", fmt2="5.2f"))
# Current:   2.400 ∠ -36.87

print("V_R:      ", VR.asString(POLAR, fmt1="6.3f", fmt2="5.2f"))
# V_R:       96.000 ∠ -36.87
```

### Example 3 — Using `\rad` for radian-mode phasors

```python
from vec import Vec, RECT, POLAR
import math

V1 = Vec(r"10 +A0.7854 \rad")    # 10 ∠ 45° expressed in radians (π/4 ≈ 0.7854)
V2 = Vec(r"5 +A1.5708 \rad")     # 5 ∠ 90° expressed in radians (π/2 ≈ 1.5708)

V3 = V1 + V2
print(V3.asString(POLAR, fmt1=".4f", fmt2=".4f"))
# Result in radians (because both operands had \rad)
```

### Example 4 — Attribute switches for circuit annotation

Attributes let you tag vectors with semantic labels and check them later:

```python
from vec import Vec, RECT, POLAR

Y1 = Vec(r"0.01 +j0.005 \admittance \branch1")
Y2 = Vec(r"0.02 -j0.003 \admittance \branch2")

Y_total = Y1 + Y2

if Y_total.hasAttrib(r"\admittance"):
    Z_total = Vec("1 +j0") / Y_total
    print("Total impedance:", Z_total.asString(RECT, fmt1=".4f", fmt2=".4f"))
    # Total impedance: 29.0323 -j2.5806
```

### Example 5 — Deferred initialization and re-initialization

```python
from vec import Vec, RECT, POLAR

# Allocate placeholders for a three-phase system
Va = Vec(None)
Vb = Vec(None)
Vc = Vec(None)

# Assign values later
Va.initialize("120 <0")
Vb.initialize("120 <-120")
Vc_mag = 120
Vc.initialize(f"{Vc_mag} <120")

V_zero_seq = (Va + Vb + Vc) * (1/3)
print("Zero-sequence voltage:", V_zero_seq.asString(RECT, fmt1=".6f", fmt2=".6f"))
# For a balanced system this is approximately 0 +j0
```

### Example 6 — Conjugate and `abs()` in power calculations

Apparent power: `S = V * I_conjugate`

```python
from vec import Vec, RECT, POLAR

V = Vec("120 <0")          # Voltage phasor
I = Vec("10 <-30")         # Current phasor (lagging)

S = V * I.conjugate()      # Complex power

print(f"Apparent power:  {abs(S):.2f} VA")
print(f"Real power (P):  {S.real():.2f} W")
print(f"Reactive (Q):    {S.img():.2f} VAR")
print(f"Power factor:    {S.real()/abs(S):.4f}")
# Apparent power:  1200.00 VA
# Real power (P):  1039.23 W
# Reactive (Q):    600.00 VAR
# Power factor:    0.8660
```

---

*End of Documentation*
