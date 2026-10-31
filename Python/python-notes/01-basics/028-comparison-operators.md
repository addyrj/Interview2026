---

# 028. Comparison Operators
# हिंदी में: Comparison Operators — तुलना वाले operators

---

## 🔵 Simple Definition (English)
Comparison operators compare two values and return a `bool` (`True` or `False`): `==` equal, `!=` not equal, `>` greater, `<` less, `>=` greater or equal, `<=` less or equal. Python allows **chaining**: `1 < x < 10` means `1 < x and x < 10`.

## 🔵 सरल परिभाषा (Hindi)
Comparison operators दो values की तुलना करके `bool` (`True` या `False`) देते हैं: `==` बराबर, `!=` बराबर नहीं, `>` बड़ा, `<` छोटा, `>=` बड़ा या बराबर, `<=` छोटा या बराबर। Python में **chaining** होती है: `1 < x < 10` का मतलब `1 < x and x < 10`।

---

## 🔴 Problem it Solves
Every decision in a program (`if`, `while`, filters, sorting, validation) needs a yes/no answer about how two values relate. Comparison operators give that answer. Python also lets you compare many types (numbers, strings, lists, tuples) with one syntax, and custom classes can define their own rules through `__eq__` and `__lt__`.

## 🔴 यह क्यों बना? (Hindi)
Program के हर फैसले (`if`, `while`, filter, sorting, validation) के लिए दो values के रिश्ते का हाँ/ना जवाब चाहिए। Comparison operators यही देते हैं। Python में numbers, strings, lists, tuples सबकी तुलना एक ही syntax से होती है, और custom classes `__eq__` व `__lt__` से अपने नियम बना सकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → a < b  calls  a.__lt__(b)       (== calls __eq__, != calls __ne__ ...)
Step 2 → If it returns NotImplemented, Python tries the mirror on b:  b.__gt__(a)
Step 3 → If both give NotImplemented:
            == / !=  → falls back to identity (is)
            < > <= >= → TypeError: '<' not supported between 'str' and 'int'
Step 4 → Sequences (str, list, tuple) compare element by element, like a dictionary
Step 5 → Chained a < b < c  →  (a < b) and (b < c), b evaluated only ONCE
Step 6 → Result is a bool (for built-in types)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → a < b दरअसल a.__lt__(b) call करता है
Step 2 → NotImplemented मिले तो b का mirror method आज़माया जाता है
Step 3 → दोनों fail: ==/!= में identity check, बाकी में TypeError
Step 4 → Sequences element-by-element compare होती हैं (dictionary की तरह)
Step 5 → a < b < c = (a < b) and (b < c), और b सिर्फ एक बार evaluate होता है
Step 6 → Built-in types में नतीजा bool होता है
```

---

## 🟡 Real World Example
Razorpay-style checks: `if amount > 0`, `if balance >= amount`, `if status != "FAILED"`. An age filter `18 <= age < 60`. Sorting orders by `(priority, created_at)` tuples relies on tuple comparison. Versions: `(3, 12) >= (3, 10)` is a common way to check the Python version via `sys.version_info`. In a pricing API, `if price == 0` with floats can be dangerous; use `math.isclose` or `Decimal`.

## 🟡 Real Example Hindi mein
Razorpay जैसी checks: `if amount > 0`, `if balance >= amount`, `if status != "FAILED"`। Age filter `18 <= age < 60`। Orders को `(priority, created_at)` tuple से sort करना tuple comparison पर टिका है। Python version check: `sys.version_info >= (3, 10)`। Pricing API में floats के साथ `price == 0` खतरनाक हो सकता है; `math.isclose` या `Decimal` लें।

---

## 💻 Code Example — Basic
```python
# Comparison operators basics

a: int = 10                                  # first value
b: int = 20                                  # second value

print(a == b)                                # Output: False   equal?
print(a != b)                                # Output: True    not equal?
print(a < b)                                 # Output: True
print(a > b)                                 # Output: False
print(a <= 10)                               # Output: True    less or equal
print(a >= 11)                               # Output: False

# Chained comparison (very Pythonic)
age: int = 25
print(18 <= age < 60)                        # Output: True    same as 18 <= age and age < 60

# Different numeric types compare by value
print(1 == 1.0, 1 == True)                   # Output: True True

# Strings compare character by character (by Unicode code point)
print("apple" < "banana")                    # Output: True
print("Zebra" < "apple")                     # Output: True   (uppercase letters come first)
print("abc" == "ABC".lower())                # Output: True

# Lists and tuples compare element by element
print([1, 2, 3] < [1, 2, 4])                 # Output: True
print((1, 5) < (2, 0))                       # Output: True   first element decides
print([1, 2] == [1, 2])                      # Output: True

# Result of a comparison is a bool and can be stored
is_adult: bool = age >= 18                   # store the answer
print(is_adult)                              # Output: True

# Comparing different types: == is allowed, ordering is not
print("5" == 5)                              # Output: False
try:
    print("5" < 5)                           # str vs int ordering is not allowed
except TypeError as exc:                     # Python 3 raises TypeError
    print("TypeError:", exc)
    # Output: TypeError: '<' not supported between instances of 'str' and 'int'

# None checks use `is`, not ==
value = None
print(value is None)                         # Output: True
```

## 💻 Code Example — Advanced
```python
# Advanced comparisons: custom ordering, float safety, sorting by tuple, version checks
import sys                                         # for version info
from dataclasses import dataclass, field           # model helper
from functools import total_ordering               # fill missing comparison methods
from math import isclose                           # safe float comparison


@total_ordering                                    # define __eq__ and __lt__, get the rest
@dataclass(frozen=True)
class Version:
    """Semantic version like 3.12.1 that compares correctly."""

    major: int                                     # first number
    minor: int = 0                                 # second number
    patch: int = 0                                 # third number
    label: str = field(default="", compare=False)  # ignored in comparisons

    def _key(self) -> tuple[int, int, int]:        # one place for the ordering rule
        return (self.major, self.minor, self.patch)

    def __eq__(self, other: object) -> bool:       # ==
        if not isinstance(other, Version):         # unknown type
            return NotImplemented                  # let Python decide
        return self._key() == other._key()         # compare numbers only

    def __lt__(self, other: object) -> bool:       # <   (others come from total_ordering)
        if not isinstance(other, Version):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self) -> int:                     # keep it usable in sets and dict keys
        return hash(self._key())


def parse(text: str) -> Version:
    """Parse '3.12.1' into a Version."""
    parts: list[int] = [int(p) for p in text.split(".")]     # numbers, not strings
    return Version(*parts)


def main() -> None:
    v1: Version = parse("3.9.18")
    v2: Version = parse("3.12.1")
    print(v1 < v2)                                 # Output: True
    print("3.9.18" < "3.12.1")                     # Output: False  (string compare is WRONG)
    print(v1 >= v2, v1 != v2)                      # Output: False True  (from total_ordering)
    print(sorted([v2, v1, parse("3.10.0")])[0] == v1)   # Output: True

    # Tuple ordering for sort keys: priority desc, then name asc
    tasks: list[tuple[int, str]] = [(2, "b"), (1, "z"), (2, "a")]
    tasks.sort(key=lambda t: (-t[0], t[1]))        # negative priority = descending
    print(tasks)                                   # Output: [(2, 'a'), (2, 'b'), (1, 'z')]

    # Floats: never use == after calculations
    x: float = 0.1 * 3
    print(x == 0.3)                                # Output: False
    print(isclose(x, 0.3, rel_tol=1e-9))           # Output: True

    # NaN is never equal to anything, even itself
    nan: float = float("nan")
    print(nan == nan, nan != nan)                  # Output: False True
    print(nan != nan)                              # classic NaN check; use math.isnan in real code

    # Chained comparison evaluates the middle value once
    def noisy(n: int) -> int:                      # prints when called
        print("called", n)
        return n

    print(1 < noisy(5) < 10)                       # Output: called 5 / True (called ONCE)

    # Python version check with tuple comparison
    print(sys.version_info >= (3, 10))             # Output: True (on Python 3.10+)

    # all() / any() combine comparisons over many items
    prices: list[float] = [10.0, 25.5, 99.9]
    print(all(0 < p <= 100 for p in prices))       # Output: True
    print(any(p > 50 for p in prices))             # Output: True


if __name__ == "__main__":
    main()                                         # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
print(1 == 1.0)               # True
print("5" == 5)               # False  (no type coercion)
print(1 < 2 < 3)              # True   (real chaining)
print(3 > 2 > 1)              # True
print([1, 2] == [1, 2])       # True   (compares contents)
print({"a": 1} == {"a": 1})   # True
print(None == False)          # False
print("a" < "b")              # True
```
```javascript
// JavaScript
console.log(1 == 1.0);              // true
console.log("5" == 5);              // true   loose equality coerces!
console.log("5" === 5);             // false  strict equality
console.log(1 < 2 < 3);             // true   but only by luck
console.log(3 > 2 > 1);             // false! (3>2)=true -> true>1 -> 1>1 -> false
console.log([1, 2] == [1, 2]);      // false  compares references
console.log(({a: 1}) == ({a: 1}));  // false
console.log(null == false);         // false
console.log("a" < "b");             // true
```

Key differences: Python has a single `==` that never coerces between str and int, and it compares **contents** of lists and dicts. JS has `==` (coerces) and `===` (strict), and arrays/objects compare by reference. Python's `3 > 2 > 1` is `True` (chaining); JS gives `false`.

---

## 🟠 FastAPI Connection
Pydantic and FastAPI validators are comparison operators in disguise: `Query(ge=1, le=100)` means `1 <= value <= 100`, `Field(gt=0)` means `> 0`, `lt`, `le`, `ge`, `gt` all map to these. In endpoint logic you compare ids, statuses and permissions. SQLAlchemy overloads `==`, `<`, `>` on columns to build SQL (`User.age >= 18` becomes `WHERE age >= 18`), so these are not booleans there.

```python
# FastAPI example (needs: pip install fastapi pydantic)
from fastapi import FastAPI, HTTPException         # framework + errors
from pydantic import BaseModel, Field              # validation model

app: FastAPI = FastAPI()                           # create app
BALANCE: dict[str, float] = {"priya": 500.0}       # fake wallet database


class Withdraw(BaseModel):
    user: str                                      # who withdraws
    amount: float = Field(gt=0, le=10000)          # 0 < amount <= 10000


@app.post("/withdraw")                             # POST /withdraw
async def withdraw(body: Withdraw) -> dict[str, float]:
    balance: float = BALANCE.get(body.user, 0.0)   # current balance
    if body.amount > balance:                      # comparison decides the response
        raise HTTPException(status_code=400, detail="Insufficient balance")
    BALANCE[body.user] = balance - body.amount     # update balance
    return {"balance": BALANCE[body.user]}         # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `=` instead of `==`
```python
x = 5
# Wrong: SyntaxError (assignment is not allowed in if)
# if x = 5:

# Right
if x == 5:
    print("five")        # Output: five
```

❌ Mistake 2: Comparing numbers stored as strings
```python
# Wrong: string comparison, "10" < "9" is True!
print("10" < "9")                  # Output: True

# Right: convert first
print(int("10") < int("9"))        # Output: False
```

❌ Mistake 3: `== None` instead of `is None`
```python
value = None
# Wrong: works, but a class can override __eq__ and break it
print(value == None)               # Output: True

# Right: None is a singleton, compare identity
print(value is None)               # Output: True
```

❌ Mistake 4: Comparing floats with `==`
```python
# Wrong
print(0.1 + 0.2 == 0.3)            # Output: False

# Right
import math
print(math.isclose(0.1 + 0.2, 0.3))   # Output: True
```

---

## 🧠 Tricky Interview Question

```python
print(1 < 2 < 3, 3 > 2 > 2, 1 == 1 < 2)
print((1 < 2) < 3)
print(True == 1, True + True, True > False)
print("a" < "B", "a" < "b")
print([1, 2, 3] == (1, 2, 3))
print((1, 2) < (1, 2, 0))
print(float("nan") in [float("nan")])
n = float("nan")
print(n in [n])
```

**Answer:**
```
True False True
True
True 2 True
False True
False
True
False
True
```
`1 == 1 < 2` chains as `(1 == 1) and (1 < 2)`. `True` is the integer 1, so `True == 1` and `True + True = 2`. `"a" < "B"` is `False` because lowercase `a` (97) is greater than uppercase `B` (66). A list never equals a tuple. For tuples, a shorter sequence that is a prefix is smaller, so `(1, 2) < (1, 2, 0)`. The last two lines show NaN: `x in list` first checks identity (`is`) and then `==`; two separate NaN objects fail both checks, but the *same* object `n` passes the identity check.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `==` and `is`?
A1: `==` asks "do these have equal value?" (calls `__eq__`). `is` asks "are these the same object?" (same `id`). `[1] == [1]` is `True`, `[1] is [1]` is `False`. Use `is` for `None`, `True`, `False` only.

Q2: How does chained comparison work, and what is its benefit?
A2: `a < b < c` is translated to `a < b and b < c`, with `b` evaluated only once and short-circuiting if the first part is false. It reads like maths, avoids repeating variables, and avoids bugs from nested expressions. It also works with mixed operators: `a == b != c`.

Q3: How are strings and sequences compared?
A3: Lexicographically, element by element: the first differing element decides. Strings use Unicode code points (so `"Z" < "a"`). For case-insensitive comparison use `.casefold()`. For human-friendly sorting (accents, locale) use `locale` or `icu`. A shorter sequence that is a prefix of a longer one is smaller.

Q4: What happens when you compare incompatible types?
A4: `==` and `!=` never raise: they return `False`/`True` for different types (`"5" == 5` is `False`). Ordering (`<`, `>`, `<=`, `>=`) raises `TypeError` in Python 3 (Python 2 allowed it, which hid bugs). Numbers (`int`, `float`, `Decimal`, `Fraction`, `bool`) are mutually comparable.

Q5: How do you make your own class comparable?
A5: Implement `__eq__` and `__lt__` (return `NotImplemented` for unknown types), then use `@functools.total_ordering` to generate `<=`, `>`, `>=`. With `@dataclass(order=True)` all of this is generated from the fields in order. If you define `__eq__`, also define `__hash__` (or set it to `None`) because defining `__eq__` alone makes the class unhashable.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Validations (`amount > 0`, `18 <= age < 60`)
- Sorting keys with tuples
- Version checks (`sys.version_info >= (3, 10)`)
- Filtering with `all()` / `any()` / list comprehensions

❌ Avoid when:
- Comparing floats with `==` (use `isclose`)
- Comparing version strings or numeric strings as text
- Using `== None` / `== True` (use `is None`, or just `if flag:`)
- Using `is` for numbers or strings

---

## 📊 Visual Diagram
```
 x = 25
 18 <= x < 60
   │     │
   │     └─ x < 60 ──► True ┐
   └─ 18 <= x ──► True      ├─► and ──► True
                            ┘
 (x evaluated once; if the left test is False, the right one is skipped)

 Tuple compare:  (1, 5)  vs  (1, 9)
                  =  → equal, go on
                  5 < 9 → decided: (1, 5) < (1, 9) is True
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `==` | Value equality | Value बराबर है? |
| `!=` | Value inequality | Value बराबर नहीं |
| Chained comparison | `a < b < c` in one expression | एक में कई तुलनाएँ |
| Lexicographic | Dictionary-style ordering | शब्दकोश जैसा क्रम |
| `__eq__` / `__lt__` | Magic methods for comparison | तुलना के magic methods |
| total_ordering | Decorator generating missing comparisons | बाकी comparison methods बनाता है |
| NaN | Not a Number, never equal to itself | Not a Number, खुद के बराबर भी नहीं |

---

## ⚡ 3-Line Summary
English: Comparison operators return `bool`; sequences compare element by element and `a < b < c` is a real chained check. `==` compares values, `is` compares identity, and ordering different types raises `TypeError`. Use `isclose` for floats and `total_ordering` for custom classes.
Hindi: Comparison operators `bool` देते हैं; sequences element-by-element compare होती हैं और `a < b < c` असली chaining है। `==` value देखता है, `is` identity, और अलग types का ordering `TypeError` देता है। Floats के लिए `isclose`, custom classes के लिए `total_ordering`।

---

## ➡️ Next Topic
**029. Logical Operators (and, or, not)** — short-circuiting, truthy/falsy values, and why `and`/`or` return operands.
