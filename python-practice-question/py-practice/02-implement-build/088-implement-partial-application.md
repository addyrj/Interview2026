---

# Q088. Implement Partial Application
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `my_partial(fn, *pre_args, **pre_kwargs)` like `functools.partial`: it returns a new function with some arguments pre-filled. Call-time keyword arguments must override the pre-filled ones.

```python
square = my_partial(power, exp=2)
square(5)   # power(5, exp=2) -> 25
```

---

## 💡 Quick Concept (2 lines only)
Partial application fixes some arguments now and supplies the rest later. Positional pre-args go first; keyword args are merged with later ones winning.
हिंदी: Partial कुछ arguments पहले से भर देता है — बाकी बाद में call के समय आते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Callable  # type hint


def my_partial(fn: Callable, *pre_args, **pre_kwargs) -> Callable:  # capture the fixed args
    def wrapper(*args, **kwargs):  # Step 1: receive the remaining args
        merged = {**pre_kwargs, **kwargs}  # Step 2: call-time kwargs override stored ones
        return fn(*pre_args, *args, **merged)  # Step 3: stored positionals come first
    return wrapper  # Step 4: return the specialised function


# ============================================
# TEST CASES
# ============================================
def power(base: int, exp: int) -> int:  # sample function
    return base ** exp  # base raised to exp


square = my_partial(power, exp=2)  # fix keyword arg
cube = my_partial(power, exp=3)  # fix keyword arg
two_to = my_partial(power, 2)  # fix positional arg (base)

print(square(5))  # Expected: 25
print(cube(2))  # Expected: 8
print(two_to(10))  # Expected: 1024
print(my_partial(power, 3, exp=2)())  # Expected: 9
print(my_partial(power, exp=2)(5, exp=3))  # Expected: 125  (override wins)
```

---

## 🔍 Why This Works (3 lines max)
The closure stores `pre_args` and `pre_kwargs`; at call time they are combined with the new arguments. Pre-args are placed first (like `functools.partial`), and the dict merge order lets new kwargs override old ones.
हिंदी: पुराने args पहले, नए kwargs पुराने को override करते हैं।

---

## ⚡ Alternative Solution
```python
from functools import partial  # the standard library version

p = partial(power, exp=2)  # built-in partial object
print(p(5), p.func.__name__, p.keywords)  # Expected: 25 power {'exp': 2}
print(int("101", 2), partial(int, base=2)("101"))  # Expected: 5 5

# partial also fixes the late-binding lambda trap:
fs = [partial(lambda i, x: x * i, i) for i in range(3)]  # i is bound NOW
print([f(10) for f in fs])  # Expected: [0, 10, 20]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: appending pre-args AFTER the new args
def bad_partial(fn, *pre):
    def w(*args):
        return fn(*args, *pre)  # ❌ order reversed
    return w

print(bad_partial(pow, 2)(10))  # 100   -> pow(10, 2), not pow(2, 10)
print(my_partial(pow, 2)(10))   # 1024  ✅ pow(2, 10)

# ❌ Also wrong: lambda in a loop (late binding)
fs = [lambda x: x * i for i in range(3)]
print([f(10) for f in fs])  # [20, 20, 20]
```

---

## 🎯 Interview Tip (1 line)
Say: "Pre-filled positionals go first, kwargs are merged with call-time winning; in production I use functools.partial, which also exposes .func/.args/.keywords."

---

## 🔗 Related Questions
→ Q084 (curry) | Q085 (compose) | Q122 (late binding closure bug) | Q251 (functools)
