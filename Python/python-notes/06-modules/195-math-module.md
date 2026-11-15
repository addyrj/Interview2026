---

# 195. math Module
# हिंदी में: math Module (गणित के functions और constants)

---

## 🔵 Simple Definition (English)
`math` provides mathematical functions and constants for real (float) numbers: square root, powers, logarithms, trigonometry, rounding (`floor`, `ceil`), `pi`, `e`, and integer helpers like `factorial`, `gcd`, `comb`, `isqrt`. It is written in C, so it is fast.

## 🔵 सरल परिभाषा (Hindi)
`math` real (float) numbers के लिए गणित के functions और constants देता है: square root, power, logarithm, trigonometry, rounding (`floor`, `ceil`), `pi`, `e`, और `factorial`, `gcd`, `comb`, `isqrt` जैसे integer helpers। यह C में लिखा है, इसलिए तेज़ है।

---

## 🔴 Problem it Solves
Python operators cover `+ - * / ** // %`, but not square roots, logs, sine, exact integer roots or safe float comparison. Writing these yourself is slow and inaccurate. `math` gives correct, well-tested versions, plus tools to avoid float traps (`isclose`, `fsum`).

## 🔴 यह क्यों बना? (Hindi)
Python के operators `+ - * / ** // %` देते हैं, लेकिन square root, log, sine, सही integer root या float की सुरक्षित तुलना नहीं। इन्हें खुद लिखना धीमा और अशुद्ध होता है। `math` सही और tested versions देता है, साथ में float की गलतियों से बचने के tools (`isclose`, `fsum`)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → import math (a built in C module: no install needed)
Step 2 → Functions take int/float and (almost always) return float
Step 3 → Invalid input raises ValueError ("math domain error"), huge results OverflowError
Step 4 → Trig functions use RADIANS: convert with math.radians(deg)
Step 5 → Floats are binary approximations: 0.1 + 0.2 != 0.3 → use isclose
Step 6 → For exact big-integer work use isqrt, comb, factorial, gcd (they return int)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → import math (C का built in module: install नहीं करना)
Step 2 → Functions int/float लेते हैं और (लगभग हमेशा) float लौटाते हैं
Step 3 → गलत input पर ValueError ("math domain error"), बहुत बड़े result पर OverflowError
Step 4 → Trig functions RADIANS में चलते हैं: math.radians(deg) से बदलें
Step 5 → Floats binary approximation हैं: 0.1 + 0.2 != 0.3 → isclose इस्तेमाल करें
Step 6 → सटीक बड़े integer काम के लिए isqrt, comb, factorial, gcd (ये int लौटाते हैं)
```

---

## 🟡 Real World Example
A Swiggy backend ranks restaurants by distance with the haversine formula (`sin`, `cos`, `asin`, `sqrt`). A pagination helper uses `math.ceil(total / size)` for page count. A finance job uses `math.isclose` to compare amounts, and a data team uses `math.log` for log scaling of skewed values. An ML script uses `math.exp` for a sigmoid.

## 🟡 Real Example Hindi mein
Swiggy backend restaurants को haversine formula (`sin`, `cos`, `asin`, `sqrt`) से दूरी के हिसाब से rank करता है। Pagination helper page count के लिए `math.ceil(total / size)` लेता है। Finance job amounts की तुलना `math.isclose` से करती है और data team skewed values के लिए `math.log` से log scaling करती है। ML script sigmoid के लिए `math.exp` इस्तेमाल करती है।

---

## 💻 Code Example — Basic
```python
# Basic math examples - every line commented
import math  # math functions and constants

print(math.pi, math.e, math.tau)  # constants
print(math.sqrt(16), math.isqrt(17))  # float root, exact integer root (floor)
print(math.pow(2, 10), 2 ** 10)  # math.pow always returns float
print(math.floor(-2.5), math.ceil(-2.5), math.trunc(-2.5))  # -3, -2, -2
print(round(2.5), round(3.5), round(-2.5))  # banker's rounding: ties go to even
print(math.fabs(-3), abs(-3))  # absolute value
print(math.factorial(5), math.comb(5, 2), math.perm(5, 2))  # 120 10 20
print(math.gcd(12, 18), math.lcm(4, 6))  # greatest common divisor, least common multiple
print(math.log(math.e), math.log10(1000), math.log2(8), math.log(8, 2))  # logarithms
print(math.exp(0), math.exp(1) == math.e)  # e**x
print(round(math.sin(math.pi / 2), 3), round(math.cos(0), 3))  # radians, not degrees
print(math.degrees(math.pi), math.radians(180) == math.pi)  # unit conversion
print(math.hypot(3, 4))  # sqrt(3**2 + 4**2) -> 5.0
print(math.dist((0, 0), (3, 4)))  # distance between two points
print(math.fsum([0.1] * 10), sum([0.1] * 10))  # fsum is exact; sum() is also compensated since 3.12 (older: 0.9999999999999999)
print(math.isclose(0.1 + 0.2, 0.3), 0.1 + 0.2 == 0.3)  # compare floats safely
print(math.inf > 10**100, math.isnan(math.nan), math.nan == math.nan)  # special values
print(math.prod([2, 3, 4]))  # product of an iterable
```

Output (verified by running; ids/timestamps/paths may vary):
```
3.141592653589793 2.718281828459045 6.283185307179586
4.0 4
1024.0 1024
-3 -2 -2
2 4 -2
3.0 3
120 10 20
6 12
1.0 3.0 3.0 3.0
1.0 True
1.0 1.0
180.0 True
5.0
5.0
1.0 1.0
True False
True True False
24
```

## 💻 Code Example — Advanced
```python
# Production style: money rounding, float safety, haversine distance, percentiles, errors
import math  # math library
from decimal import ROUND_HALF_UP, Decimal  # exact money
from typing import List, Tuple  # type hints


def haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Great-circle distance in km between two (lat, lon) points (delivery ETA, nearby search)."""
    r: float = 6371.0088  # mean Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))  # degrees -> radians
    dlat, dlon = lat2 - lat1, lon2 - lon1  # differences
    h: float = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))  # haversine formula


delhi, mumbai = (28.6139, 77.2090), (19.0760, 72.8777)  # coordinates
print(round(haversine_km(delhi, mumbai)))  # about 1150 km


def round_money(x: str, places: int = 2) -> Decimal:
    """Round like humans expect: 2.675 -> 2.68 (round() on floats would give 2.67)."""
    q: Decimal = Decimal(1).scaleb(-places)  # 0.01
    return Decimal(x).quantize(q, rounding=ROUND_HALF_UP)  # half up


print(round(2.675, 2), round_money("2.675"))  # 2.67 vs 2.68
print(round(0.5), round(1.5), round(2.5))  # banker's rounding: 0 2 2


def pages(total: int, size: int) -> int:
    """Number of pages = ceil(total / size) using integers only."""
    return math.ceil(total / size)  # fine for small numbers


print(pages(101, 25), -(-101 // 25))  # integer-only ceil trick works for huge ints too


def percentile(data: List[float], p: float) -> float:
    """Nearest-rank percentile (p in 0..100)."""
    if not data:  # guard
        raise ValueError("empty data")  # clear error
    s: List[float] = sorted(data)  # sort a copy
    k: int = max(1, math.ceil(p / 100 * len(s)))  # rank, 1-based
    return s[k - 1]  # value at rank


latencies: List[float] = [120, 80, 95, 300, 110, 90, 105, 85, 99, 2000]
print(percentile(latencies, 50), percentile(latencies, 90), percentile(latencies, 99))

# Errors: domain errors raise ValueError, overflow raises OverflowError
for fn, arg in ((math.sqrt, -1), (math.log, 0), (math.exp, 1000)):
    try:  # call each
        fn(arg)  # may fail
    except (ValueError, OverflowError) as exc:  # math errors
        print(fn.__name__, type(exc).__name__, "-", exc)

# Floating point: accumulate error and the fixes
acc: float = 0.0  # manual running total
for _ in range(10):  # add 0.1 ten times
    acc += 0.1  # error accumulates
print(acc, acc == 1.0, math.fsum([0.1] * 10) == 1.0)  # 0.9999999999999999 False True
print(math.isclose(1e9 + 0.1, 1e9 + 0.1000001, rel_tol=1e-9))  # relative tolerance
print(math.isclose(0.0, 1e-12), math.isclose(0.0, 1e-12, abs_tol=1e-9))  # need abs_tol near 0
print(math.isqrt(10**40), int(math.sqrt(10**40)) == 10**20)  # exact for big ints
print(math.copysign(1.0, -0.0), math.fmod(-7, 3), -7 % 3)  # sign tricks: -1.0 -1.0 2

# Compound interest and growth
principal, rate, years = 100_000, 0.07, 10  # inputs
print(round(principal * math.exp(rate * years)), round(principal * (1 + rate) ** years))
print(math.ceil(math.log(2) / math.log(1 + rate)))  # years to double at 7%
```

Output (verified by running; ids/timestamps/paths may vary):
```
1148
2.67 2.68
0 2 2
5 5
99 300 2000
sqrt ValueError - math domain error
log ValueError - math domain error
exp OverflowError - math range error
0.9999999999999999 False True
True
False True
100000000000000000000 True
-1.0 -1.0 2
201375 196715
11
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import math
math.floor(2.7)          # 2   (int)
math.sqrt(16)            # 4.0
math.hypot(3, 4)         # 5.0
round(2.5)               # 2  (banker's rounding)
10 ** 20 + 1             # exact big integer
```

```javascript
// JavaScript
Math.floor(2.7);         // 2   (number)
Math.sqrt(16);           // 4
Math.hypot(3, 4);        // 5
Math.round(2.5);         // 3  (rounds half up)
10 ** 20 + 1;            // 100000000000000000000 (precision lost: 1e20)
```

Key differences: In JS `Math` is a global object; in Python you `import math`. JS has only one number type (double); Python has arbitrary-size `int` and `float`. Python `round()` uses banker's rounding (ties go to the even number) whereas `Math.round` rounds half up. Python `math.sqrt(-1)` raises `ValueError`; JS returns `NaN`. Python `/` always gives float, `//` gives floor division.

---

## 🟠 FastAPI Connection
FastAPI endpoints use `math` for geo distance, pagination (`ceil(total / size)`), scoring and ML post-processing (`exp`, `log`). Validate inputs with `Query(ge=..., le=...)` before calling math functions, so a bad latitude or a negative number becomes a clean HTTP 422 and not a 500 from `ValueError`.

```python
# FastAPI: nearby-store endpoint using math (pip install fastapi httpx)
import math  # trig functions
from typing import Dict, List  # type hints
from fastapi import FastAPI, Query  # app + validation

app: FastAPI = FastAPI()  # create app
STORES: Dict[str, tuple] = {"Connaught Place": (28.6315, 77.2167), "Gurugram": (28.4595, 77.0266), "Noida": (28.5355, 77.3910)}


def km(a: tuple, b: tuple) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))  # to radians
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))  # haversine


@app.get("/nearby")  # GET /nearby?lat=..&lon=..
def nearby(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180)) -> List[Dict[str, object]]:
    ranked = sorted(((round(km((lat, lon), p), 1), n) for n, p in STORES.items()))  # nearest first
    return [{"store": n, "km": d} for d, n in ranked]  # JSON list
```

Output (verified by running; ids/timestamps/paths may vary):
```
[{'store': 'Connaught Place', 'km': 2.5}, {'store': 'Noida', 'km': 19.5}, {'store': 'Gurugram', 'km': 24.5}]
422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Comparing floats with `==`
```python
# Wrong
# if 0.1 + 0.2 == 0.3: ...                 # False

# Correct
# if math.isclose(0.1 + 0.2, 0.3): ...
# (near zero add abs_tol: math.isclose(a, 0.0, abs_tol=1e-9))
```

❌ Mistake 2: Degrees instead of radians
```python
# Wrong - sin(90) is not 1
# math.sin(90)                              # 0.893996...

# Correct
# math.sin(math.radians(90))                # 1.0
```

❌ Mistake 3: Using floats for money, and expecting `round()` to round half up
```python
# Wrong - 2.675 is stored as 2.67499999..., and round(2.5) == 2
# round(2.675, 2)                           # 2.67

# Correct
# from decimal import Decimal, ROUND_HALF_UP
# Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)   # 2.68
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import math
print(0.1 + 0.2 == 0.3, math.isclose(0.1 + 0.2, 0.3))
print(round(2.5), round(3.5), round(2.675, 2))
print(math.floor(-0.5), int(-0.5), -7 // 2, math.fmod(-7, 2), -7 % 2)
print(math.nan == math.nan, math.nan in [math.nan], float("inf") - float("inf"))
print(type(math.floor(2.7)).__name__, type(math.sqrt(4)).__name__, 2 ** -1, type(2 ** 0.5).__name__)
```

**Answer**:
```
False True
2 4 2.67
-1 0 -4 -1.0 1
False True nan
int float 0.5 float
```
Floats are binary approximations, so `==` is False and `isclose` is True. `round` sends ties to the even number (2.5 → 2, 3.5 → 4), and 2.675 is really 2.67499... so it gives 2.67. `floor` goes toward minus infinity (-1) while `int()` truncates toward zero (0); `//` floors (-4); `fmod` keeps the sign of the first argument (-1.0) but `%` takes the sign of the second (1). `nan != nan`, yet `nan in [nan]` is True because `in` checks identity first. `floor` returns `int`, `sqrt` returns `float`. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: `math.sqrt(x)` vs `x ** 0.5` vs `math.isqrt(n)`?
A1: Both first are float results (the same value up to rounding; `sqrt` raises ValueError for negatives, `** 0.5` of a negative float gives a complex number in Python 3). `isqrt` returns the exact integer floor root even for huge ints, where float conversion loses precision.

Q2: Why is `0.1 + 0.2 != 0.3`?
A2: Numbers are stored in binary (IEEE 754) and 0.1 has no exact binary form. Use `math.isclose` for comparing, `Decimal` for money, and `math.fsum` for accurate sums of floats. Note: since Python 3.12 the builtin `sum()` of floats is also compensated, so it matches `fsum` in simple cases.

Q3: `math.floor` vs `int()` vs `round`?
A3: `floor` rounds toward −∞, `ceil` toward +∞, `int()` / `trunc` toward zero, `round` to nearest with ties to even. They differ for negative numbers.

Q4: When does `math` raise errors?
A4: Domain errors (`sqrt(-1)`, `log(0)`) raise `ValueError`; results too large (`exp(1000)`) raise `OverflowError`. Use `cmath` for complex results.

Q5: `math` vs `numpy`?
A5: `math` works on single numbers and is fast for scalars. `numpy` works on whole arrays (vectorised) and is the right tool for large data. `math` functions do not accept lists.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Single-number maths: distance, roots, logs, ceiling for pages
- Safe float comparison (`isclose`) and exact integer maths (`isqrt`, `comb`, `gcd`)
- Interviews and algorithms

❌ Avoid when:
- Handling money (use `Decimal`)
- Operating on large arrays (use NumPy)
- Needing statistics (use `statistics`) or complex numbers (use `cmath`)

---

## 📊 Visual Diagram

```
        floor(-2.5) = -3  ◄──┐
 -3      -2.5      -2        │ round(-2.5) = -2 (even)
  ├────────●────────┤         │ trunc(-2.5)  = -2  (toward 0)
        ceil(-2.5) = -2  ────┘

 radians:  180° = π     90° = π/2     sin(radians(90)) = 1.0
 float:    0.1 + 0.2 = 0.30000000000000004  → isclose(...) is True
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Radian | Angle unit (π = 180°) | कोण की इकाई |
| Floor / Ceil | Round down / up | नीचे / ऊपर गोल करना |
| Banker's rounding | Ties go to even number | tie पर सम संख्या चुनना |
| isclose | Tolerant float comparison | float की सहनशील तुलना |
| IEEE 754 | Standard float format | float का मानक format |
| NaN / inf | Not-a-number / infinity | अपरिभाषित / अनंत |

---

## ⚡ 3-Line Summary
English: `math` has fast scalar maths: roots, logs, trig (radians), `floor` / `ceil`, `gcd`, `comb`, `isqrt`. Compare floats with `isclose`, handle money with `Decimal`, and remember `round()` rounds ties to even.
Hindi: `math` में तेज़ scalar गणित है: roots, logs, trig (radians), `floor` / `ceil`, `gcd`, `comb`, `isqrt`। Floats की तुलना `isclose` से करें, पैसे के लिए `Decimal` लें और याद रखें कि `round()` tie को सम संख्या की ओर ले जाता है।

---

## ➡️ Next Topic
**196. random Module** — random numbers, shuffling and sampling (and why not to use it for passwords).
