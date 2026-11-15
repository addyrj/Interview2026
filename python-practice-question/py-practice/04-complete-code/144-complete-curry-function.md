---

# Q144. Complete Curry Function
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks so `curry(add3)(1)(2)(3)`, `curry(add3)(1, 2)(3)` and `curry(add3)(1)(2, 3)` all return `6`.

```python
import inspect
from typing import Any, Callable


def curry(fn: Callable) -> Callable:
    arity = len(inspect.____(fn).parameters)       # BLANK 1: read fn's signature

    def curried(*args: Any) -> Any:
        if len(args) ____ arity:                   # BLANK 2: enough arguments yet?
            return fn(*args)                       # call the real function
        return lambda *more: curried(*args, ____)  # BLANK 3: collect the next arguments
    return curried
```

---

## 💡 Quick Concept (2 lines only)
Currying turns `f(a, b, c)` into `f(a)(b)(c)`: keep collecting arguments until you have as many as the function needs, then call it.
हिंदी: Curry तब तक arguments जमा करता है जब तक function के सारे parameters पूरे न हो जाएँ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import inspect                                     # to read the parameter count
from typing import Any, Callable


def curry(fn: Callable) -> Callable:               # takes a normal function
    arity = len(inspect.signature(fn).parameters)  # BLANK 1: number of required parameters

    def curried(*args: Any) -> Any:                # collects arguments so far
        if len(args) >= arity:                     # BLANK 2: enough arguments?
            return fn(*args)                       # Step 1: yes -> call original
        return lambda *more: curried(*args, *more)  # BLANK 3: Step 2: no -> wait for more
    return curried                                 # return the curried version


# ============================================
# TEST CASES
# ============================================
def add3(a: int, b: int, c: int) -> int:
    return a + b + c                               # simple 3-argument function

c = curry(add3)                                    # curried version
print(c(1)(2)(3))                                  # Expected: 6
print(c(1, 2)(3))                                  # Expected: 6
print(c(1)(2, 3))                                  # Expected: 6
print(c(1, 2, 3))                                  # Expected: 6

add10 = c(10)                                      # partially applied, reusable
print(add10(1)(2), add10(5, 5))                    # Expected: 13 20
```

---

## 🔍 Why This Works (3 lines max)
`inspect.signature` tells how many arguments are needed. Until that many arrive, `curried` returns a lambda that merges new arguments with the old ones (closure keeps `args`). Intermediate functions are reusable.
हिंदी: Closure पुराने args याद रखता है, नए args जोड़ता है और पूरे होते ही original function चलाता है।

---

## ⚡ Alternative Solution
```python
# Using functools.partial (also works with keyword arguments)
import inspect
from functools import partial
from typing import Any, Callable


def curry(fn: Callable) -> Callable:
    sig = inspect.signature(fn)                    # remember signature

    def curried(*args: Any, **kwargs: Any) -> Any:
        try:
            sig.bind(*args, **kwargs)              # do we have enough arguments?
        except TypeError:
            return partial(curried_with, args, kwargs)  # not yet -> keep waiting
        return fn(*args, **kwargs)                 # enough -> call

    def curried_with(prev_args: tuple, prev_kwargs: dict, *a: Any, **k: Any) -> Any:
        return curried(*prev_args, *a, **{**prev_kwargs, **k})  # merge old and new

    return curried

def greet(greeting: str, name: str) -> str:
    return f"{greeting}, {name}!"                  # two-parameter function

g = curry(greet)
print(g("Hi")("Ada"))                              # Expected: Hi, Ada!
print(g("Hi")(name="Bob"))                         # Expected: Hi, Bob!
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: hard-coding the number of arguments (e.g. always 3)
#    -> breaks for functions with 2 or 4 parameters
# ❌ Wrong: *args / **kwargs functions have no fixed arity -> curry never finishes
#    (len(signature.parameters) counts `args` as 1 parameter, so it calls too early)
# ✅ Correct: derive arity from inspect.signature (or accept an explicit `arity` argument)
```

---

## 🎯 Interview Tip (1 line)
Say: "Currying = one argument at a time, partial application = fix some arguments now; both rely on closures."

---

## 🔗 Related Questions
→ Q084 (implement curry) | Q088 (partial application) | Q085 (compose) | Q161 (closures)
