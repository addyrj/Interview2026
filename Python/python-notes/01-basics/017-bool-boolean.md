---

# 017. bool — Boolean
# हिंदी में: bool — बूलियन (True / False)

---

## 🔵 Simple Definition (English)
`bool` is the Python type that has exactly two values: `True` and `False`. It is used for yes/no decisions in `if`, `while`, and filters. In Python, `bool` is a subclass of `int`, so `True == 1` and `False == 0`. Every object in Python also has a "truthiness" — it can be treated as True or False.

## 🔵 सरल परिभाषा (Hindi)
`bool` Python का वो type है जिसकी सिर्फ दो values होती हैं: `True` और `False`। यह `if`, `while` और filters में yes/no decision के लिए use होता है। Python में `bool`, `int` की subclass है, इसलिए `True == 1` और `False == 0`। हर object की एक "truthiness" भी होती है — उसे True या False की तरह treat किया जा सकता है।

---

## 🔴 Problem it Solves
Without a boolean type, languages use numbers (0/1) or strings ("yes"/"no") for decisions — easy to mix up and hard to read. `bool` gives a clear, standard type for conditions. Python's truthiness rules also remove boilerplate: `if items:` instead of `if len(items) > 0:`.

## 🔴 यह क्यों बना? (Hindi)
Boolean type के बिना decisions के लिए 0/1 या "yes"/"no" strings use होती थीं — confusion और bugs। `bool` conditions के लिए clear standard type देता है। Truthiness rules से code छोटा होता है: `if items:` बजाय `if len(items) > 0:`।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A condition is written: if value:
Step 2 → Python calls bool(value) internally
Step 3 → bool() checks __bool__() first, then __len__()
Step 4 → If __bool__ returns False or __len__ returns 0 → Falsy
Step 5 → Anything else → Truthy (default for objects)
Step 6 → The branch runs (or is skipped) based on the result
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Condition लिखी: if value:
Step 2 → Python अंदर से bool(value) call करता है
Step 3 → पहले __bool__() देखता है, फिर __len__()
Step 4 → __bool__ False दे या __len__ 0 दे → Falsy
Step 5 → बाकी सब → Truthy (objects का default)
Step 6 → Result के हिसाब से branch run होती है
```

---

## 🟡 Real World Example
Swiggy checks `is_open` for a restaurant, `has_coupon` for a cart, and `if cart_items:` before showing the checkout button. Razorpay returns `"captured": true` for payments. A FastAPI endpoint uses `is_active: bool` on a user model to block disabled accounts.

## 🟡 Real Example Hindi mein
Swiggy restaurant के लिए `is_open` check करता है, cart के लिए `has_coupon`, और checkout button दिखाने से पहले `if cart_items:`। Razorpay payment के लिए `"captured": true` देता है। FastAPI में user model पर `is_active: bool` से disabled accounts block होते हैं।

---

## 💻 Code Example — Basic
```python
# bool basics — values, truthiness, and arithmetic

# Two bool values (capital T and F — case matters):
is_open: bool = True            # restaurant is open
has_coupon: bool = False        # no coupon applied

print(is_open, has_coupon)      # True False
print(type(is_open))            # <class 'bool'>

# bool is a subclass of int:
print(isinstance(True, int))    # True
print(True + True)              # 2  (1 + 1)
print(False + 5)                # 5  (0 + 5)

# Comparisons produce bool:
age: int = 20                   # a number
print(age >= 18)                # True

# Falsy values — all of these become False:
print(bool(0))                  # False
print(bool(0.0))                # False
print(bool(""))                 # False
print(bool([]))                 # False
print(bool({}))                 # False
print(bool(None))               # False

# Truthy values — everything else:
print(bool(1))                  # True
print(bool("False"))            # True  (non-empty string!)
print(bool([0]))                # True  (non-empty list)

# Truthiness in if (no need to compare with len):
cart: list[str] = ["pizza"]     # one item in the cart
if cart:                        # same as: if len(cart) > 0
    print("show checkout")      # show checkout
```

## 💻 Code Example — Advanced
```python
# Advanced bool — custom __bool__, any/all, and safe parsing
from dataclasses import dataclass


@dataclass
class Wallet:
    """Wallet that is truthy only when it has money."""
    balance: float = 0.0                      # current balance

    def __bool__(self) -> bool:               # called by bool(obj) and `if obj:`
        return self.balance > 0               # truthy only if balance positive


def parse_bool(value: str) -> bool:
    """Convert env-style strings to bool safely (bool('false') would be True!)."""
    normalized: str = value.strip().lower()   # clean the input
    if normalized in {"1", "true", "yes", "on"}:   # accepted True words
        return True
    if normalized in {"0", "false", "no", "off", ""}:  # accepted False words
        return False
    raise ValueError(f"Cannot parse bool from {value!r}")  # reject garbage


def main() -> None:
    # 1. Custom truthiness:
    print(bool(Wallet(0)))                    # False
    print(bool(Wallet(250.0)))                # True

    # 2. any() and all() return bool:
    checks: list[bool] = [True, True, False]  # validation results
    print(any(checks))                        # True  (at least one True)
    print(all(checks))                        # False (not all True)
    print(all([]))                            # True  (empty -> vacuous truth)
    print(any([]))                            # False

    # 3. Safe parsing of config values:
    print(parse_bool("False"))                # False
    print(parse_bool(" YES "))                # True
    print(bool("False"))                      # True  <- the classic trap

    # 4. and / or return operands, not always bool:
    print("" or "default")                    # default
    print("x" and "y")                        # y
    print(bool("x" and "y"))                  # True

    # 5. Error handling:
    try:
        parse_bool("maybe")                   # invalid word
    except ValueError as exc:                 # catch it
        print(exc)                            # Cannot parse bool from 'maybe'

    # 6. bool in sums — count True values:
    flags: list[bool] = [True, False, True, True]
    print(sum(flags))                         # 3


if __name__ == "__main__":
    main()
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python — lowercase vs capital matters
x = True                  # capital T
print(bool([]))           # False  (empty list is falsy)
print(bool({}))           # False  (empty dict is falsy)
print(bool("0"))          # True   (non-empty string)
print(True + 1)           # 2      (bool is int)
print(True and "yes")     # yes
```
```javascript
// JavaScript — lowercase true/false
let x = true;                 // lowercase
console.log(Boolean([]));     // true   (empty array is TRUTHY!)
console.log(Boolean({}));     // true   (empty object is TRUTHY!)
console.log(Boolean("0"));    // true   (same as Python)
console.log(true + 1);        // 2
console.log(true && "yes");   // yes
```

Key differences: Python `True/False` (capital), JS `true/false`. Empty list and dict are **falsy** in Python but **truthy** in JS. Python has `and/or/not`, JS has `&&/||/!`.

---

## 🟠 FastAPI Connection
FastAPI uses `bool` for query parameters, request bodies, and response models. Query strings like `?active=true` are auto-converted by Pydantic: `"true"`, `"1"`, `"yes"`, `"on"` become `True`.

```python
# FastAPI example (needs: pip install fastapi)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()                                   # create app


class User(BaseModel):
    name: str                                     # required field
    is_active: bool = True                        # bool field with default


@app.get("/users")
def list_users(active: bool = True) -> dict[str, bool]:
    # GET /users?active=false  ->  active is False (auto-parsed)
    return {"active": active}                     # return parsed bool


@app.post("/users")
def create_user(user: User) -> User:
    # JSON {"name": "A", "is_active": "yes"} -> is_active becomes True
    return user                                   # echo validated user
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `bool("False")` to parse text
```python
# Wrong — any non-empty string is True:
flag = bool("False")
print(flag)                  # True  (surprise!)

# Correct — compare the text explicitly:
flag = "False".lower() == "true"
print(flag)                  # False
```

❌ Mistake 2: Comparing to True with `==`
```python
# Wrong — verbose and breaks for truthy values like 2:
x = 2
if x == True:                # False! 2 != 1
    print("yes")

# Correct — use truthiness:
if x:
    print("yes")             # yes
# For strict check use: if x is True
```

❌ Mistake 3: Writing `true` / `false` like JS
```python
# Wrong:
# is_ok = true     # NameError: name 'true' is not defined

# Correct:
is_ok = True
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
print(True == 1)
print(True is 1)       # SyntaxWarning, but runs
print(isinstance(True, int))
print({True: "a", 1: "b", 1.0: "c"})
print(sum([True, True, False]))
```
Answer: `True`, `False`, `True`, `{True: 'c'}`, `2`. `True == 1` is True because bool subclasses int. `True is 1` is False — different objects. In the dict, `True`, `1`, `1.0` hash equal and compare equal, so they are the same key: the first key (`True`) is kept and the last value (`"c"`) wins.

---

## ⚫ Interview Questions + Answers

Q1: Is `bool` a subclass of `int` in Python?
A1: Yes. `issubclass(bool, int)` is True. `True` is 1 and `False` is 0, so you can add them and use `sum()` to count True values. That is why `True + True == 2`. It also means `bool` cannot be subclassed (`class X(bool)` raises TypeError).

Q2: What values are falsy in Python?
A2: `None`, `False`, zero of any numeric type (`0`, `0.0`, `0j`, `Decimal(0)`), empty sequences and collections (`""`, `[]`, `()`, `{}`, `set()`, `range(0)`). Custom objects are truthy unless they define `__bool__` returning False or `__len__` returning 0.

Q3: What is the difference between `and` and `&`?
A3: `and` is the logical operator: short-circuits and returns one of its operands (`0 and 5` gives `0`). `&` is bitwise: works on bits of ints (`6 & 3` gives `2`) and on bools gives a bool (`True & False` is `False`) but does NOT short-circuit. Use `and`/`or` for conditions.

Q4: What does `all([])` return and why?
A4: `True`. "All elements satisfy the condition" is vacuously true for an empty collection. `any([])` returns `False`. This catches people in validation code: `all(checks)` passes when `checks` is empty, so also check that the list is non-empty if needed.

Q5: How do you convert the string "false" to a boolean?
A5: Not with `bool()` — it returns True for any non-empty string. Write a parser: compare lowercase text with a set of accepted values (`{"1","true","yes","on"}`), or use `distutils.util.strtobool` (removed in 3.12), or let Pydantic do it in a model field typed `bool`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Flags and state: `is_active`, `has_paid`, `is_admin`
- Return values of validators and predicates
- Query params and feature toggles in FastAPI
- Counting matches with `sum(cond for ...)`

❌ Avoid when:
- You need three states (True / False / unknown) — use `bool | None` or an `Enum`
- Flag arguments make a function do two jobs — split the function
- Parsing text with `bool(text)` — it is always a bug

---

## 📊 Visual Diagram
```
                 bool(value)
                      |
        +-------------+--------------+
        |                            |
  has __bool__()?              has __len__()?
        |                            |
  returns True/False           len == 0 ? False : True
        |                            |
        +-------------+--------------+
                      |
          neither defined -> True (default)

 int
  └── bool   (True = 1, False = 0)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| bool | Type with True / False | True / False वाला type |
| Truthy | Treated as True in conditions | Condition में True माना जाए |
| Falsy | Treated as False in conditions | Condition में False माना जाए |
| `__bool__` | Hook for custom truthiness | Custom truthiness का method |
| Short-circuit | Stops evaluating early | आगे evaluate नहीं करता |
| Vacuous truth | `all([])` is True | खाली पर all() True |

---

## ⚡ 3-Line Summary
English: `bool` has two values, `True` and `False`, and is a subclass of `int`. Every object has truthiness: empty/zero/None are falsy, the rest truthy. Never use `bool("text")` to parse strings.
Hindi: `bool` की दो values हैं, `True` और `False`, और यह `int` की subclass है। हर object की truthiness होती है: empty/zero/None falsy, बाकी truthy। String parse करने के लिए `bool("text")` कभी use न करें।

---

## ➡️ Next Topic
**018. None — NoneType** — Python's "no value", how it differs from False/0, and the `is None` rule.
