---

# 015. int + float + complex
# हिंदी में: int, float और complex (संख्याएँ)

---

## 🔵 Simple Definition (English)
Python has three built-in number types. `int` holds whole numbers of ANY size (no overflow). `float` holds decimal numbers using 64-bit binary floating point (about 15-17 digits of precision). `complex` holds numbers with a real and imaginary part, like `3 + 4j`.

## 🔵 सरल परिभाषा (Hindi)
Python में तीन built-in number types हैं। `int` किसी भी size की पूर्ण संख्या रखता है (overflow नहीं होता)। `float` 64-bit binary floating point में दशमलव संख्याएँ रखता है (करीब 15-17 digits की precision)। `complex` में real और imaginary हिस्सा होता है, जैसे `3 + 4j`।

---

## 🔴 Problem it Solves
In C or Java, an `int` has a fixed size (32 or 64 bits) and silently overflows. Programmers must pick `int`, `long`, `BigInteger`. Python removes that burden: ints grow as needed, so factorials and cryptography keys work without special types. For science and engineering, built-in `complex` avoids needing a library. The trade-off to understand: floats are approximate, so `0.1 + 0.2` is not exactly `0.3`.

## 🔴 यह क्यों बना? (Hindi)
C या Java में `int` का size तय (32 या 64 bits) होता है और overflow चुपचाप हो जाता है। Programmer को `int`, `long`, `BigInteger` में से चुनना पड़ता है। Python यह बोझ हटाता है: int ज़रूरत के हिसाब से बढ़ता है, इसलिए factorial और cryptography keys बिना special type के चलते हैं। Science और engineering के लिए built-in `complex` library की ज़रूरत हटाता है। ध्यान रखें: float approximate होता है, इसलिए `0.1 + 0.2` ठीक `0.3` नहीं होता।

---

## 🟢 How it Works — Step by Step

```
int
Step 1 → Stored as arbitrary-precision digits (30-bit "digits" in CPython)
Step 2 → Operations + - * // % ** are exact, never overflow (memory is the limit)
Step 3 → Division / always returns a float; // returns floor result

float
Step 1 → Stored as IEEE 754 double: 1 sign bit, 11 exponent bits, 52 fraction bits
Step 2 → Many decimals (0.1) have NO exact binary form -> stored as nearest value
Step 3 → Small errors appear: 0.1 + 0.2 = 0.30000000000000004
Step 4 → Compare with math.isclose(), not ==

complex
Step 1 → Two floats: .real and .imag, written like 3+4j
Step 2 → Supports + - * / ** ; abs(z) gives magnitude (sqrt(real² + imag²))

Mixing: int + float -> float ;  float + complex -> complex  (widening)
```

## 🟢 कैसे काम करता है? (Hindi)
```
int
Step 1 → Arbitrary-precision digits के रूप में store (CPython में 30-bit "digits")
Step 2 → + - * // % ** exact रहते हैं, overflow नहीं (memory ही सीमा है)
Step 3 → / हमेशा float देता है; // floor result देता है

float
Step 1 → IEEE 754 double: 1 sign bit, 11 exponent bits, 52 fraction bits
Step 2 → 0.1 जैसे कई decimals का exact binary रूप नहीं होता → नज़दीकी value store होती है
Step 3 → छोटी गलतियाँ: 0.1 + 0.2 = 0.30000000000000004
Step 4 → तुलना के लिए == नहीं, math.isclose() use करें

complex
Step 1 → दो floats: .real और .imag, जैसे 3+4j
Step 2 → abs(z) magnitude देता है

Mixing: int + float → float ; float + complex → complex
```

---

## 🟡 Real World Example
A Swiggy-style billing service totals cart items. Using `float` for prices gives bills like `₹499.99000000000001`, so production code stores money as integer paise (`49999`) or `Decimal`. Cryptography in an authentication service uses huge ints (2048-bit RSA numbers) that Python handles natively. Signal-processing and ML code uses complex numbers (FFT) through NumPy.

## 🟡 Real Example Hindi mein
Swiggy जैसी billing service cart items जोड़ती है। Prices के लिए `float` से `₹499.99000000000001` जैसे bills बन सकते हैं, इसलिए production code में पैसा integer paise (`49999`) या `Decimal` में रखते हैं। Authentication service की cryptography में बहुत बड़े ints (2048-bit RSA numbers) आते हैं जिन्हें Python सीधे संभालता है। Signal-processing और ML code में complex numbers (FFT) NumPy के ज़रिए use होते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: int, float and complex in action
import math  # math functions and isclose

# --- int: unlimited size ---
big: int = 2 ** 100  # a 31-digit number, no overflow
print(big)  # Output: 1267650600228229401496703205376
print(10 // 3, 10 % 3, -10 // 3)  # Output: 3 1 -4   (floor division rounds DOWN)
print(1_000_000 + 0b101 + 0xFF + 0o17)  # Output: 1000275  (underscores, binary, hex, octal)

# --- float: approximate decimals ---
print(0.1 + 0.2)  # Output: 0.30000000000000004
print(0.1 + 0.2 == 0.3)  # Output: False
print(math.isclose(0.1 + 0.2, 0.3))  # Output: True  (compare with tolerance)
print(round(2.5), round(3.5), round(2.675, 2))  # Output: 2 4 2.67  (banker's rounding)
print(7 / 2, type(7 / 2).__name__)  # Output: 3.5 float

# --- complex: real + imaginary ---
z: complex = 3 + 4j  # j is the imaginary unit (not i)
print(z.real, z.imag)  # Output: 3.0 4.0
print(abs(z))  # Output: 5.0  (magnitude = sqrt(3² + 4²))
print((1 + 2j) * (3 + 4j))  # Output: (-5+10j)
print(z.conjugate())  # Output: (3-4j)

# --- conversions ---
print(int("42"), int(3.9), float("2.5"), int(-3.9))  # Output: 42 3 2.5 -3  (int() truncates)
```

## 💻 Code Example — Advanced
```python
# Advanced: exact money math, special float values, and safe conversion
from __future__ import annotations  # modern hints on all 3.x

import math  # inf, nan, isclose
import sys  # float limits
from decimal import ROUND_HALF_UP, Decimal  # exact decimal arithmetic


def to_paise(rupees: str) -> int:
    """Convert a rupee string like '499.99' to integer paise without float errors."""
    amount = Decimal(rupees)  # parse text, NOT a float, so no error creeps in
    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def gst(amount_paise: int, rate_percent: int = 18) -> int:
    """Return GST in paise, rounded half-up."""
    exact = Decimal(amount_paise) * rate_percent / 100  # exact decimal math
    return int(exact.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


total = to_paise("499.99") + to_paise("250.50")  # integer math from here on
print(total)  # Output: 75049
print(gst(total))  # Output: 13509   (13508.82 rounds to 13509)
print(f"Rs {total / 100:.2f}")  # Output: Rs 750.49

# Decimal vs float
print(Decimal("0.1") + Decimal("0.2"))  # Output: 0.3
print(Decimal(0.1))  # Output: 0.1000000000000000055511151231257827021181583404541015625

# Special float values
inf: float = float("inf")  # positive infinity
nan: float = float("nan")  # "not a number"
print(inf > 10**308, nan == nan, math.isnan(nan))  # Output: True False True
print(sys.float_info.max)  # Output: 1.7976931348623157e+308
try:
    print(10.0 ** 400)  # float overflow raises, unlike silent wrap-around in C
except OverflowError as exc:
    print("OverflowError:", exc)  # Output: OverflowError: (34, 'Result too large')

# Ints never overflow, but huge ints cannot become floats
print(math.factorial(25))  # Output: 15511210043330985984000000
try:
    float(10 ** 400)  # too large for a double
except OverflowError as exc:
    print("OverflowError:", exc)  # Output: OverflowError: int too large to convert to float

# Safe parsing of user input
def parse_int(text: str, default: int = 0) -> int:
    """Return int(text) or default when the text is not a valid integer."""
    try:
        return int(text.strip())  # int() accepts surrounding spaces, signs, underscores
    except ValueError:  # e.g. "12.5" or "abc"
        return default  # fall back instead of crashing


print(parse_int(" 42 "), parse_int("12.5"), parse_int("abc", -1))  # Output: 42 0 -1
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has a single `Number` type (64-bit float) plus `BigInt` for large integers. So `10 / 4` is `2.5` in both, but in JS `2 ** 100` loses precision while Python's int is exact. Python has no `NaN`-producing silent math for integer division by zero: `1 / 0` raises `ZeroDivisionError`, whereas JS returns `Infinity`.

```python
# Python
print(2 ** 100)  # 1267650600228229401496703205376 (exact)
print(7 // 2, 7 % 2, -7 // 2)  # 3 1 -4
print(0.1 + 0.2)  # 0.30000000000000004 (same float problem)
try:
    print(1 / 0)
except ZeroDivisionError:
    print("error")  # Python raises
print(int("42"), float("3.5"))  # 42 3.5
```
```javascript
// JavaScript
console.log(2 ** 100); // 1.2676506002282294e+30 (approximate)
console.log(2n ** 100n); // 1267650600228229401496703205376n (BigInt needed)
console.log(Math.floor(7 / 2), 7 % 2, Math.floor(-7 / 2)); // 3 1 -4
console.log(0.1 + 0.2); // 0.30000000000000004 (same!)
console.log(1 / 0); // Infinity (no error)
console.log(parseInt("42"), parseFloat("3.5")); // 42 3.5
```

---

## 🟠 FastAPI Connection
FastAPI uses these types for validation. A path parameter `item_id: int` rejects `"abc"` with HTTP 422; a query parameter `price: float` accepts `"12.5"`; Pydantic constraints like `Field(gt=0, le=100000)` validate ranges. For money, use `Decimal` or integer paise in your models. Pydantic can return `Decimal` as a JSON string to avoid float rounding.

```python
from decimal import Decimal  # exact money type

from fastapi import FastAPI  # web framework
from pydantic import BaseModel, Field  # validation helpers

app: FastAPI = FastAPI()  # app object


class Order(BaseModel):
    quantity: int = Field(gt=0, le=100)  # whole number between 1 and 100
    unit_price: Decimal = Field(gt=0, decimal_places=2)  # exact money, max 2 decimals


@app.post("/orders/total")  # POST /orders/total
def total(order: Order) -> dict[str, str]:
    amount: Decimal = order.unit_price * order.quantity  # exact multiplication
    return {"total": str(amount)}  # string avoids float conversion in JSON
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Comparing floats with `==`
```python
# Wrong:
if 0.1 + 0.2 == 0.3:  # False!
    print("equal")
# Right:
import math
if math.isclose(0.1 + 0.2, 0.3):  # True
    print("equal")
```
✅ Correct: use `math.isclose` (or `Decimal`) for decimal comparisons.

❌ Mistake 2: Creating `Decimal` from a float
```python
from decimal import Decimal
# Wrong:
print(Decimal(0.1))  # 0.1000000000000000055511151231257827021181583404541015625
# Right:
print(Decimal("0.1"))  # 0.1  (build from a string)
```
✅ Correct: pass strings to `Decimal`.

❌ Mistake 3: Expecting `int()` to round
```python
# Wrong assumption:
print(int(3.9))  # 3 (it truncates toward zero, not rounds)
print(int(-3.9))  # -3
# Right:
print(round(3.9))  # 4
```
✅ Correct: use `round()` to round, `math.floor()`/`math.ceil()` for direction.

---

## 🧠 Tricky Interview Question

```python
# What will this output?
print(round(0.5), round(1.5), round(2.5))
print(-7 // 2, -7 % 2)
print(True + True, 5 // 2 * 2.0)
print(0.1 * 3 == 0.3)
```
Answer:
```
0 2 2
-4 1
2 4.0
False
```
`round()` uses banker's rounding (round half to even): 0.5 goes to 0, 1.5 to 2, 2.5 to 2. Floor division rounds toward negative infinity, so `-7 // 2` is `-4`, and the remainder keeps the same sign as the divisor so `-7 % 2` is `1` (check: `-4 * 2 + 1 = -7`). `True + True` is `2` because bool is an int. `5 // 2` is `2`, times `2.0` is `4.0`. `0.1 * 3` is `0.30000000000000004`, so `False`.

---

## ⚫ Interview Questions + Answers

Q1: Why does `0.1 + 0.2 != 0.3` in Python?
A1: Floats are stored in binary (base 2). Decimal fractions like 0.1 cannot be represented exactly in binary, just as 1/3 cannot be written exactly in decimal. Each value is stored as the nearest binary fraction, and the tiny errors add up to `0.30000000000000004`. This happens in every language that uses IEEE 754 (JS, Java, C). Use `math.isclose` or `Decimal`.

Q2: Is there an integer overflow in Python?
A2: No. Python ints have arbitrary precision; they grow until memory runs out (`2 ** 10000` works). This differs from C/Java. Very big ints are slower because operations take time proportional to their digit count. Floats DO overflow: `1e308 * 10` gives `inf`, while `10.0 ** 400` raises `OverflowError`.

Q3: What is the difference between `/`, `//` and `%`?
A3: `/` is true division and always returns a float (`7 / 2 = 3.5`). `//` is floor division (rounds toward negative infinity: `-7 // 2 = -4`). `%` is the remainder with the sign of the divisor, satisfying `a == (a // b) * b + (a % b)`. `divmod(a, b)` returns both at once.

Q4: When would you use `Decimal` instead of `float`?
A4: For money, taxes and anything that needs exact decimal results or controlled rounding. `Decimal` is slower than float, so avoid it for scientific or ML numeric work (use float/NumPy). Always create it from strings or ints. Another good option is storing integer paise/cents.

Q5: How are complex numbers used in Python?
A5: Write them as `a + bj`. Attributes `.real` and `.imag`, function `abs(z)` for magnitude, `z.conjugate()`, and the `cmath` module for complex math (`cmath.sqrt(-1)` gives `1j`, while `math.sqrt(-1)` raises ValueError). They appear in signal processing (FFT), electrical engineering, and quantum simulations, mostly through NumPy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `int` for counts, ids, paise, indexes and huge exact numbers
- `float` for measurements, ML, statistics, scientific values
- `complex` for signal processing and engineering math
- `Decimal` for money requiring exact decimals

❌ Avoid when:
- `float` for money or equality checks
- `==` between floats (use `math.isclose`)
- `Decimal(0.1)` built from floats
- Python `int` loops for heavy numeric work (use NumPy)

---

## 📊 Visual Diagram
```
 Number tower (automatic widening in mixed expressions):

        int  ───────►  float  ───────►  complex
        5               5.0              (5+0j)

   5 + 2.0   -> 7.0          (int + float  = float)
   2.0 + 1j  -> (2+1j)       (float + complex = complex)

 float layout (64 bits):
 ┌──────┬────────────┬──────────────────────────────┐
 │ sign │ exponent   │ fraction (mantissa)          │
 │ 1bit │  11 bits   │  52 bits                     │
 └──────┴────────────┴──────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `int` | Whole number, unlimited size | पूर्ण संख्या, असीमित size |
| `float` | 64-bit decimal approximation | 64-bit दशमलव approximation |
| `complex` | Number with real + imaginary part | Real + imaginary हिस्से वाली संख्या |
| IEEE 754 | Standard for floating-point math | Floating-point math का standard |
| Floor division | Division rounded down (`//`) | नीचे की ओर round होने वाला division |
| `Decimal` | Exact decimal arithmetic type | Exact decimal arithmetic type |

---

## ⚡ 3-Line Summary
English: `int` is exact and unlimited, `float` is a fast binary approximation, and `complex` holds real plus imaginary parts. Never compare floats with `==` and never use floats for money; use `math.isclose`, `Decimal` or integer paise. `/` gives float, `//` floors, and `round()` rounds half to even.
Hindi: `int` exact और असीमित है, `float` तेज़ binary approximation है, और `complex` में real व imaginary हिस्से होते हैं। Floats को `==` से compare न करें और पैसों के लिए float न लें; `math.isclose`, `Decimal` या integer paise लें। `/` float देता है, `//` नीचे floor करता है, और `round()` half को even की ओर ले जाता है।

---

## ➡️ Next Topic
**016. str — String Complete Guide** — creating, slicing, formatting and transforming text.
