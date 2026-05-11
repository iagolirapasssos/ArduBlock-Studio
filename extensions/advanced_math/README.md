# Advanced Mathematics Extension for ArduBlock Studio

## 📐 Description

This extension adds advanced mathematical functions to ArduBlock Studio, including:

- **Trigonometry**: sin, cos, tan, arcsin, arccos, arctan, arctan2
- **Roots & Powers**: square root, cube root, nth root, power
- **Logarithms**: natural log, base-10 log, custom base log, exponential
- **Geometry**: hypotenuse calculation
- **Combinatorics**: factorial
- **Number Theory**: GCD, LCM, prime number checking
- **Conversions**: degrees ↔ radians

## 🚀 Installation

### Method 1: Via Extension Manager (Recommended)
1. Open ArduBlock Studio
2. Click the "Extensions" button in the toolbar
3. Search for "Advanced Mathematics"
4. Click "Install"

### Method 2: Manual Installation
1. Download the `advanced_math.absx` file
2. In ArduBlock Studio, go to Extensions → Install from ZIP
3. Select the downloaded file

## 📚 Block Reference

### Trigonometry
| Block | Description | Arduino Code |
|-------|-------------|--------------|
| sin(angle) | Sine of angle in degrees | `sin(angle * PI / 180.0)` |
| cos(angle) | Cosine of angle in degrees | `cos(angle * PI / 180.0)` |
| tan(angle) | Tangent of angle in degrees | `tan(angle * PI / 180.0)` |
| arcsin(value) | Inverse sine (returns degrees) | `asin(value) * 180.0 / PI` |

### Roots & Powers
| Block | Description | Arduino Code |
|-------|-------------|--------------|
| √x | Square root | `sqrt(x)` |
| ∛x | Cube root | `cbrt(x)` |
| ⁿ√x | Nth root | `pow(x, 1.0/n)` |
| x^y | Power | `pow(x, y)` |

### Logarithms
| Block | Description | Arduino Code |
|-------|-------------|--------------|
| ln(x) | Natural logarithm | `log(x)` |
| log₁₀(x) | Base-10 logarithm | `log10(x)` |
| log_base(b, x) | Custom base logarithm | `log(x) / log(b)` |
| e^x | Exponential | `exp(x)` |

### Number Theory
| Block | Description | Arduino Code |
|-------|-------------|--------------|
| gcd(a, b) | Greatest common divisor | Custom implementation |
| lcm(a, b) | Least common multiple | Custom implementation |
| is prime?(n) | Prime number check | Custom implementation |

### Conversions
| Block | Description | Arduino Code |
|-------|-------------|--------------|
| degrees → radians | Angle conversion | `deg * PI / 180.0` |
| radians → degrees | Angle conversion | `rad * 180.0 / PI` |

## 💡 Examples

### Calculate the height of a tree using trigonometry
