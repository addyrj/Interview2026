---

# 125. Decorators — Complete Guide
# हिंदी में: Decorators — पूरी Guide

---

## 🔵 Simple Definition (English)
A decorator is a function that takes another function as input, adds extra behavior to it, and returns a new function. It's written with `@` syntax above a function definition. Decorators let you modify functions without changing their source code.

## 🔵 सरल परिभाषा (Hindi)
Decorator एक function होता है जो दूसरे function को input लेता है, उसमें extra behavior add करता है, और एक नया function return करता है। `@` syntax से लिखते हैं। Source code बदले बिना function का behavior modify कर सकते हो।

---

## 🔴 Problem it Solves
Before decorators: if you wanted logging, timing, or auth checks in multiple functions, you had to copy-paste the same code everywhere. Every function repeated the same boilerplate. Changing that behavior required editing every function.

## 🔴 यह क्यों बना? (Hindi)
Decorators से पहले: logging, timing, auth check हर function में copy-paste करना पड़ता था। एक behavior change = सभी functions edit करो। Decorator = एक जगह logic लिखो, कहीं भी `@` से apply करो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define outer function (the decorator) that takes `func` as argument
Step 2 → Inside it, define `wrapper` function that adds extra behavior
Step 3 → wrapper calls the original `func` inside it
Step 4 → Outer function returns `wrapper` (not wrapper's result — the function itself!)
Step 5 → Use @decorator_name above any function → Python replaces function with wrapper
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Outer function define करो जो func को argument लेती है
Step 2 → अंदर wrapper function define करो जो extra behavior add करे
Step 3 → wrapper, original func को call करती है
Step 4 → Outer function, wrapper को return करती है (wrapper का result नहीं!)
Step 5 → @decorator function के ऊपर लिखो → Python उसे wrapper से replace कर देता है
```

---

## 🟡 Real World Example
Zomato API: every route needs auth check — is the user logged in? Without decorators, you'd write `if not user.is_authenticated: return 401` in every route. With a decorator `@require_auth`, you write the check once and apply it everywhere.

## 🟡 Real Example Hindi mein
Zomato API: हर route में auth check चाहिए। Decorator के बिना: हर function में `if not logged_in: return 401` copy करो। `@require_auth` decorator से: एक बार लिखो, `@` से कहीं भी apply करो।

---

## 💻 Code Example — Basic
```python
# Basic decorator — adds timing to any function
import time
from typing import Callable, Any

def timer(func: Callable) -> Callable:            # accepts a function
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # wrapper collects all args
        start = time.time()                        # record start time
        result = func(*args, **kwargs)             # call the original function
        end = time.time()                          # record end time
        print(f"{func.__name__} took {end - start:.4f}s")  # print duration
        return result                              # return original result
    return wrapper                                 # return wrapper (not result!)

@timer                                             # apply decorator
def slow_function() -> str:
    time.sleep(0.5)                                # simulate slow work
    return "done"

output = slow_function()    # slow_function took 0.5001s
print(output)               # done
```

## 💻 Code Example — Advanced
```python
# Production-ready decorator using functools.wraps
# Preserves original function metadata (name, docstring)
import time
import functools
import logging
from typing import Callable, Any, TypeVar, cast

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])  # type var for function type

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator with arguments — retries a function on exception."""
    def decorator(func: F) -> F:                  # outer wrapper takes the function
        @functools.wraps(func)                    # IMPORTANT: preserves __name__, __doc__
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)  # try calling the function
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for "
                        f"{func.__name__}: {e}"
                    )
                    if attempt < max_attempts:
                        time.sleep(delay * attempt)  # exponential-ish backoff
            raise last_error                       # all attempts exhausted
        return cast(F, wrapper)
    return decorator

@retry(max_attempts=3, delay=0.5)                 # decorator with arguments
def fetch_user_from_db(user_id: int) -> dict:
    """Fetch user — may fail on DB connection issues."""
    # Simulate flaky DB connection
    import random
    if random.random() < 0.7:
        raise ConnectionError("DB connection failed")
    return {"id": user_id, "name": "Alice"}

# Stacking decorators — order matters! Applied bottom-up
def log_call(func: F) -> F:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(f"Calling {func.__name__} with {args} {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__} returned: {result}")
        return result
    return cast(F, wrapper)

@log_call          # applied second (outer)
@retry(3, 0.1)     # applied first (inner — closest to function)
def get_order(order_id: int) -> dict:
    return {"order_id": order_id, "status": "pending"}
# Execution order: log_call → retry → get_order
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: decorator syntax
import functools

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log
def greet(name: str) -> str:
    return f"Hello {name}"
```

```javascript
// JavaScript: Higher-order function (manual decoration)
function log(func) {
    return function(...args) {
        console.log(`Calling ${func.name}`);
        return func(...args);
    };
}

const greet = log(function greet(name) {
    return `Hello ${name}`;
});

// JS doesn't have @decorator syntax natively
// (Babel/TypeScript decorators exist but different semantics)
// Python's @decorator is syntactic sugar for: greet = log(greet)
```

---

## 🟠 FastAPI Connection

```python
# FastAPI uses decorators everywhere:
from fastapi import FastAPI, Depends, HTTPException, status
from functools import wraps
from typing import Callable

app = FastAPI()

# 1. Route decorators (built-in FastAPI):
@app.get("/users/{user_id}")          # @app.get IS a decorator!
async def get_user(user_id: int):
    return {"user_id": user_id}

# 2. Custom auth decorator for FastAPI:
def require_role(role: str):
    """Decorator that checks user role before route handler."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user is None or current_user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires role: {role}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# NOTE: In FastAPI, prefer Depends() over decorators for dependency injection.
# Decorators are great for: retry logic, logging, rate limiting middleware.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `functools.wraps` — breaks introspection
```python
# Wrong — function loses its name and docstring
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(): """Says hello."""
print(greet.__name__)    # 'wrapper' ← WRONG! Should be 'greet'
print(greet.__doc__)     # None ← docstring lost!

# Correct — use @functools.wraps
import functools
def my_decorator(func):
    @functools.wraps(func)    # ← preserves __name__, __doc__, __wrapped__
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

❌ Mistake 2: Calling the function in return (returns result, not function)
```python
# Wrong
def my_decorator(func):
    def wrapper():
        return func()
    return wrapper()     # ← WRONG! Returns result of wrapper(), not wrapper itself!

# Correct
def my_decorator(func):
    def wrapper():
        return func()
    return wrapper       # ← return the function object, no ()
```

❌ Mistake 3: Decorator with args — missing the extra layer
```python
# Wrong — direct decorator when args needed
def repeat(times):      # this takes 'times', not 'func'
    @functools.wraps(times)   # WRONG! 'times' is an int, not a function!
    def wrapper(*args): ...

# Correct — 3 levels for decorator with arguments
def repeat(times: int):        # level 1: takes decorator args
    def decorator(func):       # level 2: takes the function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # level 3: takes function args
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(times=3)               # repeat(3) returns decorator, which wraps greet
def greet(): print("Hello")
```

---

## 🧠 Tricky Interview Question

```python
# What will this print?
import functools

def decorator_a(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("A before")
        result = func(*args, **kwargs)
        print("A after")
        return result
    return wrapper

def decorator_b(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("B before")
        result = func(*args, **kwargs)
        print("B after")
        return result
    return wrapper

@decorator_a
@decorator_b
def say_hello():
    print("Hello!")

say_hello()
```
Answer: Decorators apply **bottom-up** but **execute top-down**.
`@decorator_a @decorator_b` = `decorator_a(decorator_b(say_hello))`.
Output:
```
A before
B before
Hello!
B after
A after
```
The outermost decorator (`A`) runs first before, last after — like an onion.

---

## ⚫ Interview Questions + Answers

Q1: What is `functools.wraps` and why is it important?
A1: `@functools.wraps(func)` copies `__name__`, `__doc__`, `__module__`, `__qualname__`, `__dict__`, and `__annotations__` from the original function to the wrapper. Without it, all decorated functions would appear as `wrapper` in logs, stack traces, and `help()` — making debugging very hard. It also sets `__wrapped__` pointing to the original function, allowing unwrapping.

Q2: What is the difference between a decorator with arguments and without?
A2: Without arguments: `@timer` → Python calls `timer(func)`. With arguments: `@retry(3)` → Python first calls `retry(3)` which RETURNS a decorator, then that decorator is called with `func`. So decorators with arguments need 3 levels: args wrapper → decorator → wrapper.

Q3: What is the difference between decorator applied at class level vs function level?
A3: Class decorator: `@singleton class MyClass:` — replaces the class itself. Called once when class is defined. Function decorator: `@timer def func():` — called once per function definition, returns a wrapper called at each invocation. Class decorators can track instances, modify class attributes, register classes.

Q4: How do you apply multiple decorators? What is the order of execution?
A4: Applied bottom-up (closest to function first). `@A @B def f():` = `A(B(f))`. Execution order: A's before → B's before → f() → B's after → A's after. Think of it like nested function calls — innermost runs first on the way in, last on the way out.

Q5: How would you implement a memoization decorator?
A5:
```python
import functools
def memoize(func):
    cache = {}                          # captured in closure
    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)   # compute and cache
        return cache[args]
    wrapper.cache = cache               # expose cache for inspection
    return wrapper
# Python built-in: @functools.lru_cache(maxsize=None)
```

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Cross-cutting concerns: logging, timing, rate limiting, caching, auth
- You want to modify multiple functions' behavior from one place
- Adding retry logic, circuit breakers to external API calls
- Input validation / type checking applied to many functions
- FastAPI routes need common middleware behavior

❌ Avoid when:
- Logic is specific to one function only (just write it inline)
- Decorator logic is complex and tightly coupled to the function's internals
- You need the original function's signature to remain visible to the type checker (partial workaround with Protocols)
- Class-based solution is clearer (e.g., a base class with a method is clearer than a complex class decorator)

---

## 📊 Visual Diagram
```
WITHOUT DECORATOR:          WITH DECORATOR:
                            
def greet():                @log
    log("calling...")       @timer
    start = time.time()     def greet():
    result = "Hello"            return "Hello"
    end = time.time()       
    log(result)             ↓ Python transforms to:
    return result           greet = log(timer(greet))
                            
Every function              Write extra behavior ONCE
repeats this!               Apply with single @
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Decorator | Function that wraps another function | Function जो दूसरे function को wrap करती है |
| Wrapper | Inner function that adds behavior | अंदर की function जो behavior add करती है |
| functools.wraps | Copies metadata to wrapper | Wrapper को original function जैसा बनाता है |
| Closure | Inner function remembers outer scope | Inner function outer variables याद रखती है |
| @syntax | Syntactic sugar for decoration | `f = decorator(f)` का shorthand |
| Stacking | Multiple decorators on one function | एक function पर कई decorators |

---

## ⚡ 3-Line Summary
English: A decorator is a higher-order function — it takes a function, wraps it with extra behavior, and returns the new function. Use `@functools.wraps` always to preserve metadata. Decorators with arguments need 3 levels: argument-receiver → decorator → wrapper.
Hindi: Decorator, function को लेकर उसे extra behavior से wrap करता है और नया function return करता है। `@functools.wraps` हमेशा use करो — metadata preserve होती है। Arguments वाले decorator में 3 levels होती हैं।

---

## ➡️ Next Topic
**126. Decorator with Arguments** — Deep dive into parameterized decorators, class-based decorators, and decorator factories. Foundation for building reusable utility libraries.
