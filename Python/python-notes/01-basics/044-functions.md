---

# 044. Functions — Complete Guide
# हिंदी में: Functions — पूरी Guide

---

## 🔵 Simple Definition (English)
A function is a reusable block of code that takes inputs (parameters), does something, and returns an output. Python functions are first-class objects — they can be stored in variables, passed as arguments, returned from other functions, and stored in data structures. This enables decorators, closures, callbacks, and functional programming.

## 🔵 सरल परिभाषा (Hindi)
Function reusable code block है जो inputs लेता है, कुछ करता है, output return करता है। Python में functions first-class objects हैं — variables में store, arguments में pass, functions से return हो सकते हैं। इससे decorators, closures, callbacks possible होते हैं।

---

## 💻 Code Example — Basic
```python
# ─── Basic function anatomy ──────────────────────────────────────
def greet(name: str, greeting: str = "Hello") -> str:   # type hints (optional)
    """Return a greeting message.                        # docstring
    
    Args:
        name: The person's name.
        greeting: The greeting word. Defaults to "Hello".
    
    Returns:
        Formatted greeting string.
    """
    return f"{greeting}, {name}!"

print(greet("Priya"))              # "Hello, Priya!" (default greeting)
print(greet("Raj", "Namaste"))     # "Namaste, Raj!"
print(greet(greeting="Hi", name="Amit"))  # keyword arguments — order doesn't matter

# ─── *args — variable positional arguments ───────────────────────
def total(*numbers: int) -> int:
    """Accept any number of positional arguments."""
    return sum(numbers)         # numbers is a tuple

print(total(1, 2, 3))        # 6
print(total(10, 20))         # 30
print(total())               # 0

# ─── **kwargs — variable keyword arguments ───────────────────────
def create_user(**fields: str) -> dict:
    """Accept any keyword arguments."""
    return {"type": "user", **fields}    # unpack kwargs into dict

user = create_user(name="Priya", email="p@z.com", role="admin")
print(user)   # {'type': 'user', 'name': 'Priya', 'email': 'p@z.com', 'role': 'admin'}

# ─── Combined: order matters! ────────────────────────────────────
# def func(pos1, pos2, *args, kw_only1, kw_only2, **kwargs):
def log_event(level: str, *messages: str, timestamp: str = "now", **metadata) -> None:
    print(f"[{level}] {' '.join(messages)} at {timestamp} | {metadata}")

log_event("INFO", "User", "logged", "in", timestamp="10:30", user_id=42)
# [INFO] User logged in at 10:30 | {'user_id': 42}

# ─── Positional-only (/) and keyword-only (*) parameters ─────────
def strict_func(a, b, /, c, *, d, e):
    # a, b: positional ONLY (can't use as keyword)
    # c: can be positional or keyword
    # d, e: keyword ONLY (must use d=, e=)
    return a + b + c + d + e

strict_func(1, 2, 3, d=4, e=5)          # OK
# strict_func(a=1, b=2, c=3, d=4, e=5)  # TypeError! a,b are positional-only

# ─── Lambda — anonymous one-liner function ───────────────────────
square = lambda x: x ** 2
print(square(5))   # 25

# Use lambda with sorted, map, filter:
users = [{"name": "Raj", "age": 25}, {"name": "Priya", "age": 22}]
sorted_users = sorted(users, key=lambda u: u["age"])
print(sorted_users[0]["name"])   # "Priya" (youngest first)
```

## 💻 Code Example — Advanced
```python
# First-class functions + higher-order functions

from typing import Callable, Any

# ─── Functions as arguments ──────────────────────────────────────
def apply_twice(func: Callable[[int], int], value: int) -> int:
    """Apply a function twice to a value."""
    return func(func(value))

double = lambda x: x * 2
print(apply_twice(double, 3))    # double(double(3)) = double(6) = 12

# ─── Functions as return values ──────────────────────────────────
def make_multiplier(factor: int) -> Callable[[int], int]:
    """Return a function that multiplies by factor (closure)."""
    def multiply(x: int) -> int:
        return x * factor   # 'factor' captured from outer scope
    return multiply

triple = make_multiplier(3)
print(triple(5))    # 15
print(triple(7))    # 21

# ─── Functions stored in data structures ─────────────────────────
operations = {
    "add":  lambda a, b: a + b,
    "sub":  lambda a, b: a - b,
    "mul":  lambda a, b: a * b,
    "div":  lambda a, b: a / b if b != 0 else None,
}

def calculate(op: str, a: float, b: float) -> float | None:
    func = operations.get(op)
    if func is None:
        raise ValueError(f"Unknown operation: {op}")
    return func(a, b)

print(calculate("add", 10, 5))   # 15
print(calculate("div", 10, 0))   # None

# ─── Unpacking arguments ──────────────────────────────────────────
def add(a: int, b: int, c: int) -> int:
    return a + b + c

args = [1, 2, 3]
print(add(*args))       # unpacks list as positional args

kwargs = {"a": 1, "b": 2, "c": 3}
print(add(**kwargs))    # unpacks dict as keyword args

# ─── Type hints for complex signatures ───────────────────────────
from typing import Optional, Union

def process(
    data: list[int],
    transform: Callable[[int], int] = lambda x: x,
    filter_fn: Optional[Callable[[int], bool]] = None,
    output: Union[list, None] = None,
) -> list[int]:
    result = [transform(x) for x in data]
    if filter_fn:
        result = [x for x in result if filter_fn(x)]
    return result

print(process([1,2,3,4,5], transform=lambda x: x**2, filter_fn=lambda x: x > 5))
# [9, 16, 25]

# ─── Mutable default argument gotcha ─────────────────────────────
# WRONG — default list is shared across all calls!
def bad_append(item, lst=[]):
    lst.append(item)
    return lst

print(bad_append(1))   # [1]
print(bad_append(2))   # [1, 2]  ← SURPRISE! list persisted!

# CORRECT — use None as default, create new list inside:
def good_append(item: int, lst: list | None = None) -> list:
    if lst is None:
        lst = []    # new list created fresh each call
    lst.append(item)
    return lst

print(good_append(1))   # [1]
print(good_append(2))   # [2]  ← fresh list each time
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python — multiple returns via tuple:
def min_max(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)

low, high = min_max([3, 1, 4, 1, 5, 9])
print(low, high)    # 1 9

# Default argument:
def greet(name, msg="Hello"):
    return f"{msg} {name}"

# *args:
def total(*nums):
    return sum(nums)

total(1, 2, 3)    # 6
```

```javascript
// JavaScript — no native multiple return (use array/object):
function minMax(numbers) {
    return [Math.min(...numbers), Math.max(...numbers)];
}
const [low, high] = minMax([3, 1, 4]);

// Default argument:
function greet(name, msg = "Hello") {
    return `${msg} ${name}`;
}

// ...rest:
function total(...nums) {
    return nums.reduce((a, b) => a + b, 0);
}
total(1, 2, 3);   // 6
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutable default argument
```python
def bad(items=[]):   # list created ONCE at function definition time
    items.append(1)
    return items

bad()   # [1]
bad()   # [1, 1]  ← NOT a fresh list!

# Fix:
def good(items=None):
    if items is None:
        items = []
    items.append(1)
    return items
```

❌ Mistake 2: Calling a function vs passing it
```python
# Wrong — calls the function immediately, passes None:
sorted_users = sorted(users, key=lambda u: u["age"]())   # () calls age — TypeError!

# Also wrong — passes result of sorted() to key, not the function:
result = apply(transform())   # transform() is called, result passed

# Correct — pass the function object, not a call:
sorted_users = sorted(users, key=lambda u: u["age"])     # no ()
result = apply(transform)                                  # no ()
```

---

## 🧠 Tricky Interview Question

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

print([f() for f in funcs])
```
Answer: `[2, 2, 2]` — all three lambdas capture the variable `i` by reference, not value. When the lambdas are called, `i` is 2 (loop's final value). Fix: `lambda i=i: i` — captures current value as default argument.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between arguments and parameters?
A1: Parameters are the names in the function definition: `def greet(name, age)` — `name` and `age` are parameters. Arguments are the actual values passed when calling: `greet("Priya", 25)` — `"Priya"` and `25` are arguments. Informal usage often conflates them, but technically: parameters define, arguments supply.

Q2: What are keyword-only parameters and how do you define them?
A2: Parameters after `*` in the signature must be passed as keyword arguments — can't use positional. `def func(a, b, *, name, age):` — `name` and `age` are keyword-only. Use when: function has many optional params and you want to force explicit naming for clarity. Also prevents accidentally passing wrong values due to positional confusion.

Q3: What is the difference between `*args` and `**kwargs`?
A3: `*args` collects extra positional arguments into a tuple. `**kwargs` collects extra keyword arguments into a dict. Both are conventions — you could name them anything (`*numbers`, `**options`). Order: `def func(a, b, *args, kw_only, **kwargs)`. Use `*args` when function should accept variable number of values; `**kwargs` when accepting variable keyword config options.

Q4: Can a Python function return multiple values?
A4: Python functions can return a tuple of values — looks like multiple returns. `return a, b, c` is really `return (a, b, c)`. Unpack with `x, y, z = func()`. This is different from JavaScript which needs `return [a, b]` or `return {a, b}`. Python's tuple packing/unpacking makes multiple returns feel natural.

Q5: What is a first-class function?
A5: Functions are first-class when they can be: (1) stored in variables, (2) passed as arguments to other functions, (3) returned from other functions, (4) stored in data structures. Python supports all four — this is what enables decorators (functions that take and return functions), `map/filter` (take functions as args), and callback patterns. JavaScript also has first-class functions; Java and C do not by default.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Parameter | Variable in function definition | Function definition में variable |
| Argument | Value passed when calling | Call करते समय दी गई value |
| *args | Variable positional args (tuple) | Variable positional args |
| **kwargs | Variable keyword args (dict) | Variable keyword args |
| Lambda | Anonymous one-liner function | Anonymous one-liner function |
| First-class | Functions are objects | Functions objects हैं |
| Default argument | Pre-set value for parameter | Parameter की pre-set value |

---

## ⚡ 3-Line Summary
English: Python functions accept positional args, keyword args, `*args` (variable positional → tuple), and `**kwargs` (variable keyword → dict). Functions are first-class objects — store, pass, return them. NEVER use a mutable default argument (`def f(lst=[])`): create it inside with `if lst is None: lst = []`.
Hindi: Python functions: positional, keyword, `*args` (tuple), `**kwargs` (dict) accept करते हैं। Functions first-class objects हैं। Mutable default argument कभी मत use करो — `None` से check करो।

---

## ➡️ Next Topic
**045. *args + **kwargs Deep Dive** — unpacking operators, combining, real use cases. Then **050. Lambda Functions** — when to use and when to avoid.
