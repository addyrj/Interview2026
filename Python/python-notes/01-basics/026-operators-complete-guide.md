---

# 026. Operators — Complete Guide
# हिंदी में: Operators — पूरी गाइड

---

## 🔵 Simple Definition (English)
An **operator** is a symbol or keyword (`+`, `==`, `and`, `in`, `is`) that performs an action on one or more values called **operands**. `3 + 4` has operator `+` and operands `3` and `4`. Python has 7 families: arithmetic, comparison, logical, bitwise, assignment, identity, membership.

## 🔵 सरल परिभाषा (Hindi)
**Operator** एक symbol या keyword (`+`, `==`, `and`, `in`, `is`) है जो एक या ज्यादा values (**operands**) पर action करता है। `3 + 4` में operator `+` है और operands `3` और `4`। Python में 7 families हैं: arithmetic, comparison, logical, bitwise, assignment, identity, membership।

---

## 🔴 Problem it Solves
Without operators you would call functions for everything: `add(3, 4)`, `greater(a, b)`. Operators give a short, math-like syntax that is easy to read. In Python they also map to **magic methods** (`+` calls `__add__`), so your own classes (money, vectors, tensors) can use the same natural syntax.

## 🔴 यह क्यों बना? (Hindi)
Operators न हों तो हर चीज़ के लिए function call करना पड़ता: `add(3, 4)`, `greater(a, b)`। Operators short, math जैसी syntax देते हैं। Python में ये **magic methods** से जुड़े हैं (`+` दरअसल `__add__` call करता है), इसलिए आपकी अपनी classes (money, vector, tensor) भी वही natural syntax use कर सकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python parses the expression:  a + b * c
Step 2 → Applies precedence: * before +  →  a + (b * c)
Step 3 → For each operator it calls the matching special method:
           a + b   →  a.__add__(b)
           a == b  →  a.__eq__(b)
           a < b   →  a.__lt__(b)
           x in y  →  y.__contains__(x)
Step 4 → If the left side returns NotImplemented, Python tries the
         reflected method on the right side:  b.__radd__(a)
Step 5 → If both fail → TypeError: unsupported operand type(s)
Step 6 → Result object is returned
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Expression parse होता है: a + b * c
Step 2 → Precedence लगती है: * पहले, फिर +
Step 3 → हर operator अपना special method call करता है (a + b → a.__add__(b))
Step 4 → Left side NotImplemented दे तो right side का reflected method चलता है
Step 5 → दोनों fail हों तो TypeError
Step 6 → Result object वापस मिलता है
```

---

## 🟡 Real World Example
A Swiggy bill: `total = price * qty + delivery - discount` (arithmetic), `if total >= 199 and is_member:` (comparison + logical) for free delivery, `if "pizza" in cart:` (membership), `if coupon is None:` (identity), and `flags & ADMIN` (bitwise) to check user permissions. All seven families appear in one small service.

## 🟡 Real Example Hindi mein
Swiggy का bill: `total = price * qty + delivery - discount` (arithmetic), `if total >= 199 and is_member:` (comparison + logical) free delivery के लिए, `if "pizza" in cart:` (membership), `if coupon is None:` (identity), और `flags & ADMIN` (bitwise) permissions check के लिए। एक छोटी service में सातों families आ जाती हैं।

---

## 💻 Code Example — Basic
```python
# A tour of all operator families

a: int = 10                           # operand 1
b: int = 3                            # operand 2

# 1. Arithmetic: + - * / // % **
print(a + b, a - b, a * b)            # Output: 13 7 30
print(a / b, a // b, a % b, a ** b)   # Output: 3.3333333333333335 3 1 1000

# 2. Comparison: == != > < >= <=  (result is bool)
print(a == b, a != b, a > b)          # Output: False True True

# 3. Logical: and or not
print(a > 5 and b > 5)                # Output: False
print(a > 5 or b > 5)                 # Output: True
print(not a > 5)                      # Output: False

# 4. Bitwise: & | ^ ~ << >>   (work on binary bits)
print(a & b, a | b, a ^ b)            # Output: 2 11 9
print(a << 1, a >> 1)                 # Output: 20 5

# 5. Assignment: = += -= *= /= //= %= **= &= |= ^= <<= >>= :=
c: int = a                            # plain assignment
c += 5                                # same as c = c + 5
print(c)                              # Output: 15

# 6. Identity: is, is not  (same object in memory?)
x: list[int] = [1, 2]                 # one list object
y: list[int] = x                      # y points to the SAME object
z: list[int] = [1, 2]                 # a different list with equal content
print(x is y, x is z, x == z)         # Output: True False True

# 7. Membership: in, not in
print("a" in "cat", 5 not in [1, 2])  # Output: True True

# Ternary (conditional) expression
label: str = "big" if a > 5 else "small"
print(label)                          # Output: big
```

## 💻 Code Example — Advanced
```python
# Advanced: operator overloading + the operator module + precedence
from __future__ import annotations      # allow "Money" as a type inside Money
import operator                         # operators as functions
from dataclasses import dataclass       # small model class
from functools import reduce            # fold a list into one value


@dataclass(frozen=True)
class Money:
    """Rupee amount stored in paise to avoid float errors."""

    paise: int                          # integer paise

    def __add__(self, other: object) -> Money:        # money + money
        if not isinstance(other, Money):              # unknown type
            return NotImplemented                     # let Python try other side
        return Money(self.paise + other.paise)        # new Money

    def __mul__(self, qty: object) -> Money:          # money * int
        if not isinstance(qty, int):                  # only ints allowed
            return NotImplemented                     # unsupported
        return Money(self.paise * qty)                # scaled amount

    __rmul__ = __mul__                                # int * money also works

    def __lt__(self, other: Money) -> bool:           # money < money
        return self.paise < other.paise               # compare paise

    def __bool__(self) -> bool:                       # truthiness: zero is False
        return self.paise != 0

    def __contains__(self, digit: str) -> bool:       # "5" in money
        return digit in str(self.paise)

    def __str__(self) -> str:                         # nice printing
        return f"Rs {self.paise / 100:.2f}"


def main() -> None:
    price: Money = Money(19900)                       # Rs 199.00
    total: Money = price * 2 + Money(4000)            # * runs before +
    print(total)                                      # Output: Rs 438.00
    print(3 * Money(100))                             # Output: Rs 3.00  (via __rmul__)
    print(Money(100) < Money(200))                    # Output: True
    print(bool(Money(0)))                             # Output: False
    print("9" in price)                               # Output: True

    try:
        Money(100) + 5                                # int is not Money
    except TypeError as exc:                          # both sides returned NotImplemented
        print("TypeError:", exc)
        # Output: TypeError: unsupported operand type(s) for +: 'Money' and 'int'

    # operator module: use operators as functions (useful in map / reduce / sorted)
    print(reduce(operator.add, [1, 2, 3, 4]))         # Output: 10
    print(reduce(operator.mul, [1, 2, 3, 4]))         # Output: 24
    pairs: list[tuple[str, int]] = [("b", 2), ("a", 9), ("c", 1)]
    print(sorted(pairs, key=operator.itemgetter(1)))  # sort by 2nd item
    # Output: [('c', 1), ('b', 2), ('a', 9)]

    # Precedence: ** > unary - > * / // % > + - > comparisons > not > and > or
    print(-2 ** 2)                                    # Output: -4   (** first, then minus)
    print(2 + 3 * 4 ** 2)                             # Output: 50
    print(not 1 == 2)                                 # Output: True
    print(1 or 0 and 0)                               # Output: 1   (and before or)

    # Chained comparison: reads like maths
    age: int = 25
    print(18 <= age < 60)                             # Output: True


if __name__ == "__main__":
    main()                                            # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
print(7 // 2)          # 3   floor division
print(2 ** 10)         # 1024 power
print(True and "x")    # 'x' (returns an operand, not just a bool)
print(1 < 2 < 3)       # True (chained)
print("a" in "cat")    # True membership
print([] is [])        # False identity
print(5 / 2)           # 2.5 (always float)
```
```javascript
// JavaScript
console.log(Math.floor(7 / 2));  // 3   no // operator
console.log(2 ** 10);            // 1024
console.log(true && "x");        // 'x' (also returns operand)
console.log(1 < 2 < 3);          // true by luck: (1<2)=true -> true<3 -> true
console.log("cat".includes("a"));// true   no 'in' for strings
console.log([] === []);          // false  identity-like
console.log(5 / 2);              // 2.5
console.log("5" == 5);           // true  loose equality (Python: False)
```

Key differences: Python uses words (`and`, `or`, `not`, `in`, `is`) instead of `&&`, `||`, `!`. Python has `//` and `%` that floors toward negative infinity, chained comparisons, and no `++`/`--`. JS has `==` vs `===` coercion problems; Python's `==` never converts types between str and int.

---

## 🟠 FastAPI Connection
FastAPI and Pydantic lean on operators in many places. `|` builds union types (`int | None`), comparison keywords `gt`, `le` mirror `>` and `<=`, SQLAlchemy overloads `==`, `&`, `|` to build SQL conditions, and `in` checks permissions or allowed values. Knowing precedence matters: in SQLAlchemy, `&` binds tighter than `==`, so you must write `(User.age > 18) & (User.active == True)` with brackets.

```python
# FastAPI example (needs: pip install fastapi)
from fastapi import FastAPI, Query                 # framework + validation helper

app: FastAPI = FastAPI()                           # create app
ADMINS: set[str] = {"priya", "rahul"}              # allowed admin users


@app.get("/items")                                 # GET /items?limit=10&user=priya
async def items(
    limit: int = Query(10, ge=1, le=100),          # ge/le = >= and <=
    user: str | None = None,                       # `|` operator in a type hint
) -> dict[str, object]:
    is_admin: bool = user in ADMINS                # membership operator
    capped: int = limit if limit <= 50 or is_admin else 50   # ternary + logical
    return {"limit": capped, "admin": is_admin}    # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `is` to compare values
```python
# Wrong: works by accident for small ints, fails for big ones and strings built at runtime
a = 1000
b = 1000
# print(a is b)    # may be False!

# Right: == for values, is only for None / True / False
print(a == b)      # Output: True
```

❌ Mistake 2: Ignoring precedence
```python
# Wrong: not has LOWER precedence than ==
x = 5
print(not x == 5)         # Output: False  -> means not (x == 5)

# Right: add brackets when in doubt
print((not x) == 5)       # Output: False (but different meaning!) - be explicit
```

❌ Mistake 3: Using `&` / `|` instead of `and` / `or`
```python
# Wrong: bitwise operators have HIGHER precedence than comparison
a, b = 5, 3
# print(a > 2 & b > 2)    # parsed as a > (2 & b) > 2  -> surprising

# Right: use and / or for logic
print(a > 2 and b > 2)    # Output: True
```

❌ Mistake 4: Expecting `/` to give an int
```python
# Wrong: assumes 4
print(8 / 2)       # Output: 4.0  (float!)

# Right: use // for integer division
print(8 // 2)      # Output: 4
```

---

## 🧠 Tricky Interview Question

```python
print(2 ** 3 ** 2)
print(-3 ** 2)
print(10 - 2 - 3)
print(1 < 2 == 2)
print(0 or [] or "hi")
print(3 and 0 and 5)
print(not None + 1 if False else 7)
```

**Answer:**
```
512
-9
5
True
hi
0
7
```
`**` is **right-associative**: `3 ** 2 = 9`, then `2 ** 9 = 512`. `-3 ** 2` is `-(3 ** 2) = -9` because `**` binds tighter than unary minus. `-` is left-associative: `(10 - 2) - 3 = 5`. `1 < 2 == 2` is chained: `(1 < 2) and (2 == 2)` = `True`. `or` returns the first truthy operand (`"hi"`); `and` returns the first falsy operand (`0`). Last line: the conditional expression is false, so `7` is returned, and `not None + 1` is never evaluated (it would have raised `TypeError`).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `==` and `is`?
A1: `==` compares values (calls `__eq__`). `is` compares identity: do both names point to the exact same object (`id(a) == id(b)`). Use `is` only for singletons: `None`, `True`, `False`. Small ints and some strings are cached, so `is` may appear to work, but this is an implementation detail.

Q2: What does `and` / `or` return in Python?
A2: They return one of the operands, not necessarily a bool. `a and b` returns `a` if `a` is falsy, else `b`. `a or b` returns `a` if `a` is truthy, else `b`. This enables patterns like `name = user_input or "guest"`. They also short-circuit: the right side is not evaluated if the left decides the result.

Q3: What is operator overloading?
A3: Defining magic methods (`__add__`, `__eq__`, `__lt__`, `__getitem__`, `__contains__`) in a class so operators work on its objects. NumPy arrays, `pathlib.Path` (`/` joins paths), `datetime` subtraction and SQLAlchemy columns all use it. Return `NotImplemented` (not raise) when the other type is unsupported, so Python can try the reflected method.

Q4: What is the walrus operator `:=`?
A4: Assignment expression (Python 3.8+): assigns and returns a value inside an expression, e.g. `if (n := len(items)) > 10:` or `while chunk := f.read(1024):`. It avoids computing twice. Do not overuse it; clarity first.

Q5: What is the order of precedence (high to low)?
A5: `()` > `**` > unary `+ - ~` > `* / // % @` > `+ -` > `<< >>` > `&` > `^` > `|` > comparisons, `in`, `is` > `not` > `and` > `or` > ternary `if-else` > `:=` / lambda. When unsure, use parentheses; readers will thank you.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Expressions are short and obvious: `a + b`, `x in items`
- Overloading for natural domain types (Money, Vector)
- `operator` module with `map`, `reduce`, `sorted(key=...)`

❌ Avoid when:
- Expression mixes many operators without brackets
- Overloading with surprising meaning (e.g. `+` that deletes data)
- Using `is` for value comparison, or `&` for logic
- Using the walrus operator in a way that hides intent

---

## 📊 Visual Diagram
```
Operator families
├── Arithmetic   + - * / // % **
├── Comparison   == != < > <= >=
├── Logical      and  or  not
├── Bitwise      &  |  ^  ~  <<  >>
├── Assignment   =  +=  -=  *=  ...  :=
├── Identity     is  is not
└── Membership   in  not in

Precedence (high → low)
 ()  →  **  →  -x  →  * / // %  →  + -  →  << >>  →  &  →  ^  →  |
     →  == < > in is  →  not  →  and  →  or  →  x if c else y
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Operator | Symbol/keyword that acts on values | Values पर action करने वाला symbol |
| Operand | Value the operator works on | जिस value पर operator चलता है |
| Precedence | Which operator runs first | कौन सा operator पहले चलेगा |
| Associativity | Direction for equal precedence | बराबर precedence पर दिशा |
| Short-circuit | Skip right side if result is known | नतीजा पता हो तो right side skip |
| Operator overloading | Custom class supports operators | Class में operators का custom मतलब |
| Walrus `:=` | Assign inside an expression | Expression के अंदर assignment |

---

## ⚡ 3-Line Summary
English: Python has seven operator families: arithmetic, comparison, logical, bitwise, assignment, identity and membership. Each one maps to a magic method, which is why classes can overload them. Learn precedence and use brackets when in doubt.
Hindi: Python में सात operator families हैं: arithmetic, comparison, logical, bitwise, assignment, identity, membership। हर operator एक magic method से जुड़ा है, इसलिए classes उन्हें overload कर सकती हैं। Precedence सीखो और शक हो तो brackets लगाओ।

---

## ➡️ Next Topic
**027. Arithmetic Operators** — `+ - * / // % **` in detail, floor division with negatives, float precision and `Decimal`.
