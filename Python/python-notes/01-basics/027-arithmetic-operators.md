---

# 027. Arithmetic Operators
# हिंदी में: Arithmetic Operators — गणित वाले operators

---

## 🔵 Simple Definition (English)
Arithmetic operators do maths on numbers: `+` add, `-` subtract, `*` multiply, `/` true division (always float), `//` floor division, `%` remainder (modulo), `**` power. Python also has unary `-x` / `+x` and `@` for matrix multiplication.

## 🔵 सरल परिभाषा (Hindi)
Arithmetic operators numbers पर गणित करते हैं: `+` जोड़, `-` घटाव, `*` गुणा, `/` true division (हमेशा float), `//` floor division, `%` शेषफल (modulo), `**` power। Unary `-x` / `+x` और matrix multiplication के लिए `@` भी है।

---

## 🔴 Problem it Solves
Calculating bills, taxes, pagination, time conversion, and hashing all need maths. Languages differ in odd ways (integer division in C, overflow in Java). Python gives clean rules: integers never overflow (arbitrary size), `/` never silently truncates, and `//`/`%` follow a consistent mathematical rule so that `a == (a // b) * b + a % b` always holds.

## 🔴 यह क्यों बना? (Hindi)
Bill, tax, pagination, time conversion और hashing सबमें गणित चाहिए। दूसरी languages में अजीब बातें होती हैं (C में integer division, Java में overflow)। Python साफ़ नियम देता है: integers कभी overflow नहीं होते, `/` चुपचाप truncate नहीं करता, और `//` व `%` ऐसे बने हैं कि `a == (a // b) * b + a % b` हमेशा सही रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python evaluates operands (left to right)
Step 2 → Applies precedence:  **  >  unary -  >  * / // % @  >  + -
Step 3 → Type rules:
           int  op int   → int      (except /  which → float)
           int  op float → float
           float op complex → complex
Step 4 → // floors (rounds toward negative infinity):  -7 // 2 = -4
Step 5 → % takes the sign of the DIVISOR:              -7 %  2 =  1
Step 6 → Division by zero → ZeroDivisionError
Step 7 → Float results use IEEE-754 → 0.1 + 0.2 = 0.30000000000000004
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Operands left to right evaluate होते हैं
Step 2 → Precedence: ** > unary - > * / // % > + -
Step 3 → int op int → int (सिवाय / के जो float देता है); int op float → float
Step 4 → // नीचे की ओर (negative infinity) round करता है: -7 // 2 = -4
Step 5 → % का sign divisor जैसा होता है: -7 % 2 = 1
Step 6 → शून्य से भाग → ZeroDivisionError
Step 7 → Float IEEE-754 है → 0.1 + 0.2 = 0.30000000000000004
```

---

## 🟡 Real World Example
Zomato bill: `subtotal = price * qty`, `gst = subtotal * 0.05`, `total = subtotal + gst + delivery`. Pagination in an API: `pages = (total_items + page_size - 1) // page_size`. Converting 3725 seconds to hours/minutes/seconds uses `//` and `%` (`divmod`). A payments system never uses `float` for money: it uses integer paise or `Decimal`, because `0.1 + 0.2 != 0.3`.

## 🟡 Real Example Hindi mein
Zomato bill: `subtotal = price * qty`, `gst = subtotal * 0.05`, `total = subtotal + gst + delivery`। API pagination: `pages = (total_items + page_size - 1) // page_size`। 3725 seconds को घंटे/मिनट/सेकंड में बदलने के लिए `//` और `%` (`divmod`)। Payments में पैसे के लिए `float` कभी नहीं, integer paise या `Decimal` use होता है क्योंकि `0.1 + 0.2 != 0.3`।

---

## 💻 Code Example — Basic
```python
# Arithmetic operators, one by one

a: int = 17                          # first number
b: int = 5                           # second number

print(a + b)                         # Output: 22     addition
print(a - b)                         # Output: 12     subtraction
print(a * b)                         # Output: 85     multiplication
print(a / b)                         # Output: 3.4    true division -> always float
print(a // b)                        # Output: 3      floor division -> whole part
print(a % b)                         # Output: 2      remainder
print(a ** 2)                        # Output: 289    power (17 squared)

# / always gives float, even when exact
print(10 / 2)                        # Output: 5.0

# Mixing int and float gives float
print(3 + 0.5)                       # Output: 3.5

# Negative numbers: // floors toward negative infinity
print(-7 // 2)                       # Output: -4   (NOT -3 like C)
print(-7 % 2)                        # Output: 1    (sign follows divisor)
print(7 % -2)                        # Output: -1

# divmod gives both quotient and remainder at once
q, r = divmod(3725, 60)              # 3725 seconds -> minutes and seconds
print(q, r)                          # Output: 62 5

# Even / odd check with %
number: int = 8
print("even" if number % 2 == 0 else "odd")   # Output: even

# Power with fractions = roots
print(9 ** 0.5)                      # Output: 3.0

# Integers can be huge, no overflow
print(2 ** 100)                      # Output: 1267650600228229401496703205376

# Unary minus
print(-a)                            # Output: -17

# round() and abs() often go together with arithmetic
print(round(3.14159, 2), abs(-9))    # Output: 3.14 9

# Float precision surprise
print(0.1 + 0.2)                     # Output: 0.30000000000000004
```

## 💻 Code Example — Advanced
```python
# Production style arithmetic: money with Decimal, pagination, time split, safe divide
from decimal import Decimal, ROUND_HALF_UP     # exact decimal maths
from math import ceil, isclose                 # ceil and float comparison


def gst_total(price: str, qty: int, rate: str = "0.18") -> Decimal:
    """Return total with GST, rounded to 2 decimals (Decimal built from str!)."""
    subtotal: Decimal = Decimal(price) * qty            # Decimal * int stays Decimal
    gst: Decimal = subtotal * Decimal(rate)             # tax amount
    total: Decimal = subtotal + gst                     # final amount
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)   # 2 places


def total_pages(total_items: int, page_size: int) -> int:
    """How many pages are needed (ceiling division using only integers)."""
    if page_size <= 0:                                  # invalid input
        raise ValueError("page_size must be positive")
    return -(-total_items // page_size)                 # ceil without floats


def split_seconds(seconds: int) -> tuple[int, int, int]:
    """Convert seconds to (hours, minutes, seconds)."""
    hours, rest = divmod(seconds, 3600)                 # whole hours + remainder
    minutes, secs = divmod(rest, 60)                    # whole minutes + seconds
    return hours, minutes, secs


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Divide, but return default instead of crashing on zero."""
    try:
        return a / b                                    # normal path
    except ZeroDivisionError:                           # b was 0
        return default                                  # fallback value


def percent(part: int, whole: int) -> float:
    """Percentage rounded to 1 decimal; 0 if whole is 0."""
    return round(part * 100 / whole, 1) if whole else 0.0


def main() -> None:
    print(gst_total("199.99", 3))                       # Output: 707.96
    print(0.1 + 0.2 == 0.3)                             # Output: False
    print(isclose(0.1 + 0.2, 0.3))                      # Output: True
    print(Decimal("0.1") + Decimal("0.2"))              # Output: 0.3
    print(total_pages(101, 10), ceil(101 / 10))         # Output: 11 11
    print(split_seconds(3725))                          # Output: (1, 2, 5)
    print(safe_divide(10, 0))                           # Output: 0.0
    print(percent(1, 3))                                # Output: 33.3

    # Invariant: a == (a // b) * b + a % b  (holds for negatives too)
    a, b = -7, 2
    print(a == (a // b) * b + a % b)                    # Output: True

    # Banker's rounding: round() goes to the nearest EVEN number on .5
    print(round(0.5), round(1.5), round(2.5))           # Output: 0 2 2

    # Integer to float conversion is exact only up to 2**53
    print(float(2**53) == float(2**53 + 1))             # Output: True

    # In-place style: use augmented assignment for running totals
    total: int = 0
    for n in range(1, 6):                               # 1..5
        total += n ** 2                                 # sum of squares
    print(total)                                        # Output: 55


if __name__ == "__main__":
    main()                                              # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
print(7 / 2)            # 3.5
print(7 // 2)           # 3          floor division operator
print(-7 // 2)          # -4
print(-7 % 2)           # 1          sign follows divisor
print(2 ** 10)          # 1024
print(2 ** 100)         # 1267650600228229401496703205376 (exact)
print(0.1 + 0.2)        # 0.30000000000000004
print("ab" * 3)         # ababab     operators work on str too
x = 5
x += 1                  # no x++ in Python
```
```javascript
// JavaScript
console.log(7 / 2);              // 3.5
console.log(Math.floor(7 / 2));  // 3   (no // operator)
console.log(Math.floor(-7 / 2)); // -4
console.log(-7 % 2);             // -1   sign follows DIVIDEND (different!)
console.log(2 ** 10);            // 1024
console.log(2 ** 100);           // 1.2676506002282294e+30 (float, inexact)
console.log(0.1 + 0.2);          // 0.30000000000000004 (same)
console.log("ab".repeat(3));     // ababab
let x = 5;
x++;                             // ++ exists in JS
console.log(2n ** 100n);         // BigInt needed for exact big numbers
```

Key differences: `%` with negatives differs (Python `-7 % 2 = 1`, JS `-1`). Python has real `//`. Python ints are unlimited; JS needs `BigInt` beyond 2^53. Python has no `++`/`--`. Both share the same float problem.

---

## 🟠 FastAPI Connection
Arithmetic shows up in pagination (`offset = (page - 1) * size`), rate limits, price calculations and Pydantic computed fields. Money fields should use `Decimal` (Pydantic supports it), never `float`. Note that `Decimal` is serialised to a string/number depending on the Pydantic config, so decide the contract with the frontend.

```python
# FastAPI example (needs: pip install fastapi)
from decimal import Decimal                      # exact money type
from fastapi import FastAPI, Query               # framework + query validation

app: FastAPI = FastAPI()                         # create app


@app.get("/products")                            # GET /products?page=2&size=20
async def products(
    page: int = Query(1, ge=1),                  # page numbers start at 1
    size: int = Query(20, ge=1, le=100),         # items per page
) -> dict[str, int]:
    offset: int = (page - 1) * size              # rows to skip in SQL OFFSET
    return {"offset": offset, "limit": size}     # JSON response


@app.get("/bill")                                # GET /bill?price=199.99&qty=3
async def bill(price: Decimal, qty: int = 1) -> dict[str, str]:
    total: Decimal = (price * qty * Decimal("1.18")).quantize(Decimal("0.01"))
    return {"total": str(total)}                 # send money as string
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using float for money
```python
# Wrong
print(0.1 + 0.2)                     # Output: 0.30000000000000004

# Right: Decimal from STRINGS (or integer paise)
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))   # Output: 0.3
```

❌ Mistake 2: Building Decimal from a float
```python
from decimal import Decimal
# Wrong: the float is already inexact
print(Decimal(0.1))                  # Output: 0.1000000000000000055511151231257827021181583404541015625

# Right
print(Decimal("0.1"))                # Output: 0.1
```

❌ Mistake 3: Expecting `/` to return int, or `//` to truncate
```python
# Wrong assumptions
print(10 / 5)                        # Output: 2.0 (float, not 2)
print(-7 // 2)                       # Output: -4  (floors, does not truncate to -3)

# Right: use int(-7 / 2) to truncate toward zero
print(int(-7 / 2))                   # Output: -3
```

❌ Mistake 4: Dividing by zero without a check
```python
# Wrong: crashes with ZeroDivisionError
# average = total / count

# Right
total, count = 10, 0
average: float = total / count if count else 0.0
print(average)                       # Output: 0.0
```

---

## 🧠 Tricky Interview Question

```python
print(7 // 2, -7 // 2, 7 // -2, -7 // -2)
print(7 % 3, -7 % 3, 7 % -3, -7 % -3)
print(round(2.5), round(3.5), round(-2.5))
print(5 / 2 * 2, 5 // 2 * 2)
print(2 ** -1, (-8) ** (1 / 3))
```

**Answer:**
```
3 -4 -4 3
1 2 -2 -1
2 4 -2
5.0 4
0.5 (1.0000000000000002+1.7320508075688772j)
```
`//` floors toward negative infinity, so `-7 // 2 = -4` and `7 // -2 = -4`. `%` takes the sign of the divisor: `-7 % 3 = 2`, `7 % -3 = -2`. `round()` uses banker's rounding (half to even): `2.5 -> 2`, `3.5 -> 4`, `-2.5 -> -2`. `5 / 2 * 2` is `2.5 * 2 = 5.0` (float), while `5 // 2 * 2` is `2 * 2 = 4`. A negative exponent gives a float (`0.5`), and a negative number to a fractional power returns a **complex** number in Python 3, not an error.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `/` and `//`?
A1: `/` is true division and always returns a float (`7 / 2 = 3.5`, `4 / 2 = 2.0`). `//` is floor division: it divides and rounds down to the nearest integer toward negative infinity (`7 // 2 = 3`, `-7 // 2 = -4`). With floats, `//` returns a float (`7.0 // 2 = 3.0`).

Q2: How does `%` work with negative numbers?
A2: Python guarantees `a == (a // b) * b + a % b`, and the result of `%` has the same sign as the divisor `b`. So `-7 % 3 = 2` (because `-7 = -3*3 + 2`). In C/JS the sign follows the dividend (`-7 % 3 = -1`). Python's rule is useful for circular indexes: `(i - 1) % n` is always in `0..n-1`.

Q3: Why does `0.1 + 0.2 != 0.3`, and how do you fix it?
A3: Floats are binary (IEEE-754) and cannot store 0.1 exactly, so tiny errors accumulate. Compare with `math.isclose(a, b)`, or use `decimal.Decimal` (built from strings) for money, or store integer paise. Never use `==` on floats from calculations.

Q4: Does Python integer overflow?
A4: No. `int` has arbitrary precision limited only by memory, so `2 ** 1000` works. This is why Python is good for cryptography and big-number maths. The cost: big ints are slower than fixed-size C ints. NumPy ints, in contrast, are fixed-size and can overflow.

Q5: What does `**` do with `pow(a, b, mod)`?
A5: `pow(a, b, mod)` computes `(a ** b) % mod` efficiently using modular exponentiation without building the huge number. It is used in cryptography and competitive programming, e.g. `pow(2, 10**9, 10**9 + 7)`. Also `pow(a, -1, mod)` gives the modular inverse (Python 3.8+).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- `//` and `%` for pagination, time conversion, circular buffers, even/odd
- `Decimal` or integer paise for money
- `math.isclose` for float comparison
- `divmod()` when you need both quotient and remainder

❌ Avoid when:
- Using `float` for currency
- Comparing floats with `==`
- Expecting C-style truncation from `//` on negatives
- Using `**` with huge exponents on untrusted input (can freeze the server)

---

## 📊 Visual Diagram
```
 17 / 5   → 3.4        (true division, float)
 17 // 5  → 3          (floor)
 17 % 5   → 2          (remainder)
 17 == 3*5 + 2         ✔  (a == (a//b)*b + a%b)

 Number line for -7 // 2 :
   -5   -4   -3.5  -3   -2
         ▲     ▲
     floor(-3.5) = -4   (goes DOWN, not toward zero)

 Precedence:  **  →  -x  →  * / // % @  →  + -
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| True division `/` | Exact division, returns float | सटीक भाग, float देता है |
| Floor division `//` | Division rounded down | नीचे round किया हुआ भाग |
| Modulo `%` | Remainder after division | भाग के बाद शेषफल |
| Exponent `**` | Power | घात |
| divmod | Quotient and remainder together | भागफल और शेषफल साथ में |
| Decimal | Exact decimal number type | सटीक दशमलव type |
| IEEE-754 | Standard float format | Float का standard format |
| Banker's rounding | Round half to even | .5 पर सम संख्या की ओर round |

---

## ⚡ 3-Line Summary
English: `/` always returns a float, `//` floors toward negative infinity, and `%` follows the sign of the divisor, so `a == (a // b) * b + a % b`. Python ints never overflow, but floats are inexact, so use `Decimal` or integer paise for money. Use `divmod` and `pow(a, b, mod)` for clean, fast maths.
Hindi: `/` हमेशा float देता है, `//` negative infinity की ओर floor करता है, `%` का sign divisor जैसा होता है। Python ints overflow नहीं होते, पर floats inexact हैं, इसलिए पैसे के लिए `Decimal` या integer paise। `divmod` और `pow(a, b, mod)` काम आते हैं।

---

## ➡️ Next Topic
**028. Comparison Operators** — `== != < > <= >=`, chained comparisons, comparing strings, lists and mixed types.
