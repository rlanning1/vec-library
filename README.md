# Vec — Python Vector Library

A Python library for representing and manipulating complex vectors (phasors). Vectors can be expressed in rectangular (`a + jb`) or polar (`M ∠ θ`) form and used directly in arithmetic expressions.

This vector arithmetic module represents an upgrade to a Python class I created years ago to aid in the design of UHF and Microwave amplifiers. The library would be especially useful to engineering students who analyze electrical circuits containing reactive components. Considering my humble introduction to A.C. Circuit Analysis in the early 1970s, where vector operations were carried out on a slide rule, modern computer solutions allow students to focus on theory without becoming lost in the repetitive conversions between rectangular and polar form vectors.


Feel free to email feedback and offer suggestions for feature updates.

---

## Features

- Flexible initialization strings for both rectangular and polar input
- Both forms maintained internally — query either at any time
- Full arithmetic operator support: `+`, `-`, `*`, `/`, negation, `abs()`
- Scalars can be used directly as operands alongside `Vec` objects
- User-defined attribute switches that propagate through calculations
- Angles default to degrees; optional radians mode via the `\rad` attribute
- Clear error reporting through a custom `VecError` exception

---

## Installation

**Requirements:** Python 3.10 or later. No third-party dependencies.

Clone or download this repository, then install with pip:

```bash
cd vec-library
pip install -e .
```

Alternatively, copy the `vec/` folder directly into your project directory — no installation needed.

---

## Quick Start

```python
from vec import Vec, RECT, POLAR

# Create vectors from initialization strings
V1 = Vec("3 +j4")          # Rectangular: 3 + j4
V2 = Vec("10 <45")          # Polar: magnitude 10, angle 45°

# Arithmetic
V3 = V1 + V2
V4 = 2 * V1

# Display results
print(V3.asString(RECT,  fmt1=".3f", fmt2=".3f"))   # 10.071 +j11.071
print(V3.asString(POLAR, fmt1=".3f", fmt2=".2f"))   # 15.021 ∠ 47.73

# Extract components
print(V1.real(), V1.img())  # 3.0  4.0
print(V1.mag(),  V1.ang())  # 5.0  53.13...
```

---

## Initialization String Formats

### Rectangular

```python
Vec("3.2 +j1.5")      # 3.2 + j1.5
Vec("-1 -j6.1")        # -1 - j6.1
Vec("-j4.1")           # 0 - j4.1
```

### Polar (degrees by default)

```python
Vec("10 <45")          # magnitude 10, angle 45°
Vec("10 ∠45")          # same, using Unicode angle symbol
Vec("10 +A45")         # same, using +A notation
Vec("10 -A30")         # magnitude 10, angle -30°
```

### Polar (radians)

```python
Vec(r"5 +A1.5708 \rad")   # magnitude 5, angle ≈ π/2 rad
```

---

## Arithmetic Operators

```python
V1 = Vec("3 +j4")
V2 = Vec("1 -j2")

V3 = V1 + V2       # Addition
V4 = V1 - V2       # Subtraction
V5 = V1 * V2       # Complex multiplication
V6 = V1 / V2       # Complex division
V7 = -V1           # Negation
m  = abs(V1)       # Magnitude — returns float (5.0)

# Scalars work on either side
V8 = 3 * V1
V9 = V1 + 5
```

---

## Attribute Switches

Attribute switches are string tags you can attach to a vector. They propagate to the result whenever two vectors are combined in an arithmetic operation.

```python
V1 = Vec(r"5 +j10 \parallel")
V2 = Vec(r"3 +j4 \admittance")
V3 = V1 + V2

V3.hasAttrib(r"\parallel")    # True — inherited from V1
V3.hasAttrib(r"\admittance")  # True — inherited from V2
```

You can also add and remove attributes manually:

```python
V = Vec("3 +j4")
V.addAttrib(r"\source")
V.delAttrib(r"\source")
```

---

## Worked Example — Parallel Impedance

```python
from vec import Vec, RECT, POLAR

Z1 = Vec("0 +j100")    # Inductive reactance
Z2 = Vec("75 +j0")     # Resistance

Z = (Z1 * Z2) / (Z1 + Z2)

print(Z.asString(RECT,  fmt1=".3f", fmt2=".3f"))   # 36.585 +j48.780
print(Z.asString(POLAR, fmt1=".3f", fmt2=".2f"))   # 60.976 ∠ 53.13
```

---

## Worked Example — Complex Power

```python
from vec import Vec, RECT, POLAR

V = Vec("120 <0")      # Voltage phasor
I = Vec("10 <-30")     # Current phasor (lagging)

S = V * I.conjugate()  # Apparent power

print(f"Apparent power: {abs(S):.2f} VA")
print(f"Real power (P): {S.real():.2f} W")
print(f"Reactive  (Q):  {S.img():.2f} VAR")
```

---

## Documentation

Full reference documentation is in [`docs/vec_documentation.md`](docs/vec_documentation.md), covering:

- All initialization string formats with examples
- All methods with parameters, return types, and examples
- Attribute switch system and propagation rules
- Error handling
- Additional worked examples

The internal design specification is in [`docs/spec/vec_specification.md`](docs/spec/vec_specification.md).

---

## License

MIT License — see [LICENSE](LICENSE) for details.
