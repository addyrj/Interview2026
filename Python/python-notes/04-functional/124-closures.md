---

# 124. Closures — Complete Guide
# हिंदी में: Closures — पूरी Guide

---

## 🔵 Simple Definition (English)
A closure is a function that **remembers the variables from its enclosing scope** even after that scope has finished executing. When an inner function uses a variable from an outer function, Python captures that variable — the inner function "closes over" it. The outer function returns the inner function, carrying the captured variables with it.

## 🔵 सरल परिभाषा (Hindi)
Closure एक function है जो अपने **enclosing scope की variables याद रखता है** — भले ही वो scope खत्म हो चुकी हो। जब inner function किसी outer function की variable use करता है, Python उसे capture कर लेता है। Outer function inner function return करता है — variables उसके साथ "बंद" हो जाते हैं।

---

## 🔴 Problem it Solves
You need a function that remembers configuration without globals. You want to create multiple related functions with different "preset" values. You need to add behavior to functions without modifying them (foundation of decorators). Without closures: you'd need a global variable or a class just to maintain state between calls.

## 🔴 यह क्यों बना? (Hindi)
Function को configuration याद रखनी है बिना globals के। Multiple related functions create करने हैं different "preset" values के साथ। Functions में behavior add करना है उन्हें modify किए बिना (decorators की foundation)। Closures के बिना: global variable या class चाहिए होती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Outer function defines a variable (free variable)
Step 2 → Inner function uses that variable (captures it)
Step 3 → Outer function returns the inner function (not inner function's RESULT!)
Step 4 → Python stores the captured variables in __closure__ cell objects
Step 5 → When inner function is called later, it reads from those cells
Step 6 → Captured variables stay alive even after outer function returns
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Outer function एक variable define करता है (free variable)
Step 2 → Inner function वो variable use करता है (capture होती है)
Step 3 → Outer function inner function return करता है (result नहीं!)
Step 4 → Python captured variables को __closure__ cell objects में store करता है
Step 5 → Later inner function call होती है → cells से read करती है
Step 6 → Outer function return होने के बाद भी variables alive रहती हैं
```

---

## 🟡 Real World Example
API rate limiter at Swiggy: each endpoint needs its own call counter with its own limit. `make_rate_limiter(max_calls=100)` returns a function that remembers `max_calls` and `call_count` — each endpoint gets its own independent limiter without sharing global state.

## 🟡 Real Example Hindi mein
Swiggy API rate limiter: हर endpoint को अपना call counter चाहिए अपनी limit के साथ। `make_rate_limiter(max_calls=100)` एक function return करता है जो `max_calls` और `call_count` याद रखता है — बिना global state share किए।

---

## 💻 Code Example — Basic
```python
# Basic closure — counter factory
def make_counter(start: int = 0) -> callable:
    """Returns a counter function that remembers its count."""
    count = start              # 'count' is the free variable — will be captured

    def counter() -> int:
        nonlocal count         # 'nonlocal' lets us MODIFY (not just read) the outer variable
        count += 1
        return count

    return counter             # return the FUNCTION, not the result of calling it

# Each call to make_counter creates an independent closure:
counter_a = make_counter(0)
counter_b = make_counter(100)

print(counter_a())   # 1
print(counter_a())   # 2
print(counter_a())   # 3
print(counter_b())   # 101   ← independent of counter_a!
print(counter_a())   # 4     ← counter_a continues from where it left off

# Inspect the closure:
print(counter_a.__closure__)          # (<cell at 0x...>,)
print(counter_a.__closure__[0].cell_contents)  # 4 — current value of 'count'
print(counter_a.__code__.co_freevars)  # ('count',) — the captured variables
```

## 💻 Code Example — Advanced
```python
# Production: function factory for rate limiting + caching
import time
from typing import Callable, Any
from functools import wraps

def make_rate_limiter(max_calls: int, period_seconds: float) -> Callable:
    """Returns a decorator that rate-limits any function."""
    calls: list[float] = []    # captured — each limiter has its own call history

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            now = time.time()
            # Remove calls outside the window:
            while calls and calls[0] < now - period_seconds:
                calls.pop(0)

            if len(calls) >= max_calls:
                wait = period_seconds - (now - calls[0])
                raise RuntimeError(f"Rate limit exceeded. Retry in {wait:.1f}s")

            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Each endpoint gets its own rate limiter with independent state:
search_limiter = make_rate_limiter(max_calls=100, period_seconds=60)
order_limiter  = make_rate_limiter(max_calls=10,  period_seconds=60)

@search_limiter
def search_restaurants(query: str) -> list:
    return [f"result for {query}"]

@order_limiter
def place_order(order_data: dict) -> dict:
    return {"status": "placed"}

# ---- Closure as a configurable cache ----
def make_cache(max_size: int = 128) -> Callable:
    """Returns a caching decorator with configurable max_size."""
    cache: dict = {}       # captured by the wrapper below

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args) -> Any:
            if args not in cache:
                if len(cache) >= max_size:
                    oldest_key = next(iter(cache))
                    del cache[oldest_key]       # simple LRU: remove oldest
                cache[args] = func(*args)
            return cache[args]
        wrapper.cache = cache                   # expose cache for inspection/testing
        wrapper.clear_cache = cache.clear       # expose clear method
        return wrapper
    return decorator

small_cache = make_cache(max_size=10)
big_cache   = make_cache(max_size=1000)

@small_cache
def get_user(user_id: int) -> dict:
    print(f"DB hit for user {user_id}")    # only prints on first call
    return {"id": user_id, "name": f"User{user_id}"}

get_user(1)    # DB hit for user 1
get_user(1)    # (cached — no print)
get_user(2)    # DB hit for user 2
print(get_user.cache)   # {(1,): {...}, (2,): {...}}
get_user.clear_cache()  # clear for tests

# ---- Classic pitfall: late binding ----
# Wrong:
adders_wrong = [lambda x: x + i for i in range(5)]
print([f(0) for f in adders_wrong])   # [4,4,4,4,4] ← all use i=4 (loop's final value)

# Correct: capture current value with default argument:
adders_right = [lambda x, i=i: x + i for i in range(5)]
print([f(0) for f in adders_right])   # [0,1,2,3,4] ✅
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python closure:
def multiplier(factor: int):
    def multiply(x: int) -> int:
        return x * factor     # 'factor' captured from enclosing scope
    return multiply

double = multiplier(2)
triple = multiplier(3)
print(double(5))  # 10
print(triple(5))  # 15

# nonlocal keyword — needed to MODIFY (not just read) outer variable:
def make_accumulator():
    total = 0
    def add(n):
        nonlocal total    # needed for assignment; reading doesn't need nonlocal
        total += n
        return total
    return add

acc = make_accumulator()
print(acc(5))    # 5
print(acc(3))    # 8
```

```javascript
// JavaScript closures work almost identically!
function multiplier(factor) {
    return function(x) {     // or: return (x) => x * factor
        return x * factor;   // 'factor' captured from outer scope
    };
}

const double = multiplier(2);
const triple = multiplier(3);
console.log(double(5));  // 10
console.log(triple(5));  // 15

// JavaScript has the SAME late binding pitfall with var:
const wrong = [];
for (var i = 0; i < 5; i++) {
    wrong.push(() => i);        // captures reference to 'i', not its value
}
console.log(wrong.map(f => f()));   // [5,5,5,5,5] — same as Python pitfall!

// Fix with let (block-scoped) or IIFE:
const right = [];
for (let i = 0; i < 5; i++) {      // 'let' creates new binding per iteration
    right.push(() => i);
}
console.log(right.map(f => f()));   // [0,1,2,3,4] ✅
```

---

## 🟠 FastAPI Connection

```python
# Closures power FastAPI's dependency injection and middleware configuration
from fastapi import FastAPI, Request, HTTPException, Depends
from typing import Callable

app = FastAPI()

# Closure-based middleware factory — each route can have different config:
def require_role(allowed_roles: list[str]) -> Callable:
    """Returns a dependency that checks if user has one of the allowed roles."""
    # 'allowed_roles' is captured by the closure:
    async def check_role(request: Request) -> dict:
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Requires role: {allowed_roles}"
            )
        return user
    return check_role

# Different routes get different permission closures:
AdminOnly  = Depends(require_role(["admin"]))
EditorPlus = Depends(require_role(["admin", "editor"]))

@app.get("/admin/users")
async def list_users(user=AdminOnly):
    return {"users": []}

@app.get("/content")
async def get_content(user=EditorPlus):
    return {"content": []}

# Closure-based pagination factory:
def paginate(default_limit: int = 20, max_limit: int = 100):
    """Returns a dependency with baked-in defaults — reusable across routes."""
    def pagination_params(skip: int = 0, limit: int = default_limit):
        return {"skip": skip, "limit": min(limit, max_limit)}  # captures defaults
    return pagination_params

StandardPagination = Depends(paginate(default_limit=20, max_limit=100))
LargePagination    = Depends(paginate(default_limit=50, max_limit=500))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `nonlocal` when modifying outer variable
```python
def make_counter():
    count = 0
    def counter():
        count += 1       # UnboundLocalError! Python sees assignment → local variable
        return count     # but there's no local 'count' yet
    return counter

# Fix: add nonlocal
def make_counter():
    count = 0
    def counter():
        nonlocal count   # tells Python: 'count' is from outer scope
        count += 1
        return count
    return counter
```

❌ Mistake 2: Late binding — capturing loop variable by reference
```python
# Wrong — all functions see the FINAL value of i:
handlers = []
for i in range(5):
    handlers.append(lambda: print(i))   # captures 'i', not its current value

for h in handlers:
    h()    # prints: 4 4 4 4 4

# Fix — capture current value with default argument:
handlers = [lambda i=i: print(i) for i in range(5)]
for h in handlers:
    h()    # prints: 0 1 2 3 4
```

---

## 🧠 Tricky Interview Question

```python
def outer():
    x = 10
    def inner():
        print(x)        # reads 'x' from outer scope
    x = 20              # MUTATES 'x' AFTER inner is defined
    return inner

f = outer()
f()     # What does this print?
```
Answer: **20**. The closure captures the **variable** (the cell object), not the value at the time `inner` was defined. When `x = 20` runs, it updates the cell. When `inner()` is called, it reads the current cell value: `20`. This is the same mechanism that causes the loop late-binding pitfall.

---

## ⚫ Interview Questions + Answers

Q1: What is a closure? What three conditions must be true?
A1: A closure is an inner function that captures variables from its enclosing scope. Three conditions: (1) There is a nested function (function inside a function). (2) The inner function references a variable from the outer function. (3) The outer function returns the inner function. Python stores captured variables in `__closure__` cell objects on the inner function.

Q2: What is the difference between `global` and `nonlocal`?
A2: `global` modifies a module-level variable from inside a function. `nonlocal` modifies an enclosing function's variable from an inner function. `nonlocal` only goes one step out at a time — for deeply nested functions, Python searches outward until it finds the name. Neither `global` nor `nonlocal` is needed for just **reading** a variable — only for **assigning** to it inside a narrower scope.

Q3: How are closures related to decorators?
A3: Decorators ARE closures. A decorator is a function that takes a function as argument, defines an inner `wrapper` function that calls the original function (capturing it in its closure), and returns the `wrapper`. The `@functools.wraps(func)` is needed because without it, `wrapper.__name__` and `wrapper.__doc__` would be "wrapper" instead of the original function's name.

Q4: What is a free variable?
A4: A free variable is a variable that's used in a function but defined in an enclosing scope (not as a local variable and not as a global). You can inspect them: `func.__code__.co_freevars` lists free variable names; `func.__closure__` lists the corresponding cell objects.

Q5: How would you implement a memoization cache using closures (without `functools.lru_cache`)?
A5: `def memoize(func): cache = {}; def wrapper(*args): return cache.setdefault(args, func(*args)); return wrapper`. `cache` is a free variable shared across all calls to `wrapper`. The key insight: `cache` is defined in `memoize`'s scope, captured by `wrapper`, and persists as long as `wrapper` is referenced.

---

## 🔷 When to Use + When Not to Use

✅ Use closures when:
- Creating function factories (functions with different "presets")
- Building decorators
- Implementing callbacks with captured state
- Dependency injection factories (FastAPI `Depends`)
- Avoiding global state while maintaining state between calls

❌ Avoid when:
- State is complex — use a class instead (classes are closures with better syntax)
- Multiple methods need to share state — class is clearer
- Deep nesting — more than 2 levels of nesting becomes hard to read

---

## 📊 Visual Diagram
```
make_counter(start=0)
│
├── count = 0          ← free variable (captured)
│
└── def counter():
        nonlocal count
        count += 1
        return count
        └── references 'count' from outer scope

counter_a = make_counter(0)    counter_b = make_counter(100)
│                              │
│  __closure__                 │  __closure__
│  ┌─────────┐                 │  ┌─────────┐
│  │ count:4 │                 │  │count:101│
│  └─────────┘                 │  └─────────┘
│  (independent cell)          │  (independent cell)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Closure | Inner function capturing outer variables | Outer variables capture करने वाली inner function |
| Free variable | Variable used but not defined locally | Locally define नहीं, पर use होती है |
| Cell object | Python's storage for captured variables | Captured variables का storage |
| nonlocal | Keyword to modify outer scope variable | Outer scope variable modify करने का keyword |
| Late binding | Variable captured by reference, not value | Reference capture, value नहीं |
| Function factory | Function that creates and returns functions | Functions बनाने वाली function |

---

## ⚡ 3-Line Summary
English: A closure is an inner function that captures variables from an outer function's scope — those variables live in `__closure__` cells and persist after the outer function returns. Use `nonlocal` to modify (not just read) a captured variable. The classic pitfall: loop variables are captured by reference, not value — fix with `lambda i=i: ...`.
Hindi: Closure outer function की variables याद रखती है — `__closure__` cells में store होती हैं। Modify करने के लिए `nonlocal` चाहिए। Loop variable pitfall: `lambda i=i` से fix करो।

---

## ➡️ Next Topic
**125. Decorators** — which ARE closures applied to functions. Then **126. functools.wraps** — preserving function metadata in decorators.
