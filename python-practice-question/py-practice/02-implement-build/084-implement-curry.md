---

# Q084. Implement curry
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `curry(fn)` that turns `fn(a, b, c)` into a function callable as `f(a)(b)(c)`, `f(a, b)(c)` or `f(a)(b, c)`. Once enough arguments are collected, call the original function.

```python
@curry
def add3(a, b, c): return a + b + c
add3(1)(2)(3)   # 6
add3(1, 2)(3)   # 6
```

---

## 💡 Quick Concept (2 lines only)
Find the function's arity with `inspect.signature`; keep collecting arguments until you have that many, then call it. Otherwise return a new function that remembers the arguments so far.
हिंदी: जब तक पूरे arguments न मिलें, नया function लौटाते रहो; पूरे होते ही original call करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import inspect                                         # read the function's parameter count
from typing import Any, Callable                       # type hints

def curry(fn: Callable[..., Any], arity: int | None = None) -> Callable[..., Any]:
    n = len(inspect.signature(fn).parameters) if arity is None else arity  # Step 1: how many args we need

    def curried(*args: Any) -> Any:
        if len(args) >= n:                             # Step 2: enough arguments collected?
            return fn(*args)                           # call the original function
        return lambda *more: curried(*args, *more)     # Step 3: else wait for more, remembering `args`
    return curried                                     # Step 4: return the curried function

# ============================================
# TEST CASES
# ============================================
@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c                                   # plain 3-argument function

print(add3(1)(2)(3))                                   # Expected: 6
print(add3(1, 2)(3))                                   # Expected: 6
print(add3(1)(2, 3))                                   # Expected: 6
print(add3(1, 2, 3))                                   # Expected: 6
add10 = add3(10)                                       # partially applied: a=10
print(add10(1)(1))                                     # Expected: 12
print(curry(lambda *a: sum(a), 4)(1)(2)(3)(4))         # Expected: 10  (variadic functions need an explicit arity)
print(curry(max, 2)(3)(9))                             # Expected: 9
```

---

## 🔍 Why This Works (3 lines max)
Each call either has enough arguments (run `fn`) or returns a closure that carries the arguments collected so far. The closure keeps `args` alive, so `add3(10)` can be reused many times.
हिंदी: Closure पुराने arguments याद रखता है; पूरे होने पर original function चलता है।

---

## ⚡ Alternative Solution
```python
# Keyword-friendly curry using inspect.Signature.bind + functools.partial
import functools, inspect                              # tools
from functools import partial                          # partial application

def curry2(fn):
    sig = inspect.signature(fn)                        # signature knows required vs default params
    @functools.wraps(fn)
    def curried(*a, **k):
        try:
            sig.bind(*a, **k)                          # do we have enough arguments to call fn?
        except TypeError:                              # not yet -> return a partial waiting for more
            return partial(curried, *a, **k)
        return fn(*a, **k)                             # yes -> call it
    return curried

@curry2
def vol(l, w, h=1):                                    # h has a default
    return l * w * h

print(vol(2)(3), vol(2)(3, h=4), vol(2, 3, 5))         # Expected: 6 24 30
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: counting ALL parameters when some have defaults
@curry
def sh(a: int, b: int = 2) -> int:
    return a + b

print(callable(sh(1)))                                 # Output: True  <- sh(1) returns a function, not 3, because arity = 2
# ✅ Correct: count only REQUIRED params (curry2 above), or pass arity explicitly: curry(fn, 1)
# ⚠️ *args functions have no fixed arity — always pass arity yourself
```

---

## 🎯 Interview Tip (1 line)
Say: "Curry = one-arg-at-a-time chain via closures; in Python I'd usually reach for functools.partial, but curry shows I understand closures and arity."

---

## 🔗 Related Questions
→ Q085 (compose) | Q088 (partial application) | Q144 (complete curry) | Q161 (closures)
