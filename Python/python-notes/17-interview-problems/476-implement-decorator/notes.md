---

# 476. Implement Decorator
# हिंदी में: Decorator बनाना (Function को लपेटना)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13).

---

## 🔵 Simple Definition (English)
A decorator is a function that takes another function and returns a new function with extra behavior (logging, timing, retry, caching) without changing the original code. `@name` above a function is shortcut for `f = name(f)`.

## 🔵 सरल परिभाषा (Hindi)
Decorator एक function है जो दूसरा function लेता है और extra behavior (logging, timing, retry, caching) वाला नया function लौटाता है, मूल code बदले बिना। Function के ऊपर `@name` लिखना `f = name(f)` का shortcut है।

---

## 🔴 Problem it Solves
Cross-cutting concerns (timing, auth, retry, logging) would otherwise be copy-pasted into every function. Decorators let you write it once and apply it with one line. Interviewers check that you know closures, `*args/**kwargs`, `functools.wraps`, and decorators with arguments (a factory returning a decorator).

## 🔴 यह क्यों बना? (Hindi)
Timing, auth, retry, logging जैसे साझा काम हर function में copy-paste करने पड़ते। Decorator से इन्हें एक बार लिखकर एक लाइन में लगाया जाता है। Interviewer देखते हैं कि आपको closures, `*args/**kwargs`, `functools.wraps` और arguments वाले decorators (decorator लौटाने वाली factory) आते हैं या नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write outer(func): takes the function to wrap
Step 2 → Inside, define wrapper(*args, **kwargs) that calls func(*args, **kwargs)
Step 3 → Add behavior before/after the call (try/finally for cleanup)
Step 4 → Decorate wrapper with @functools.wraps(func) to keep __name__ and __doc__
Step 5 → outer returns wrapper (not wrapper())
Step 6 → With arguments: @retry(times=3) -> retry(3) returns decorator -> decorator(func)
Step 7 → Python runs the decoration ONCE at definition time, wrapper runs on every call
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → outer(func) लिखो: जो wrap होने वाला function लेता है
Step 2 → अंदर wrapper(*args, **kwargs) बनाओ जो func(*args, **kwargs) बुलाता है
Step 3 → call से पहले/बाद में behavior जोड़ो (cleanup के लिए try/finally)
Step 4 → wrapper पर @functools.wraps(func) लगाओ ताकि __name__ और __doc__ बचे रहें
Step 5 → outer, wrapper लौटाता है (wrapper() नहीं)
Step 6 → Arguments के साथ: @retry(times=3) -> retry(3) decorator लौटाता है -> decorator(func)
Step 7 → Decoration सिर्फ एक बार definition के समय होता है, wrapper हर call पर चलता है
```

---

## 🟡 Real World Example
Razorpay-style payment client calls: `@retry(times=3)` on network calls, `@timer` to log latency, `@require_role("admin")` for permissions, `@cache` for expensive lookups. Libraries do the same: `@app.get("/")` in FastAPI, `@pytest.fixture`, `@functools.lru_cache`.

## 🟡 Real Example Hindi mein
Razorpay जैसे payment client में network calls पर `@retry(times=3)`, latency log के लिए `@timer`, permission के लिए `@require_role("admin")`, महंगे lookups के लिए `@cache`। Libraries भी यही करती हैं: FastAPI में `@app.get("/")`, `@pytest.fixture`, `@functools.lru_cache`।

---

## 💻 Code Example — Basic
```python
# Basic decorator: log every call
import functools                               # for wraps
from typing import Any, Callable               # type hints

def logged(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)                     # keep original name and docstring
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"calling {func.__name__}{args}")    # before the call
        result = func(*args, **kwargs)         # run the real function
        print(f"{func.__name__} -> {result}")  # after the call
        return result                          # pass the result through
    return wrapper                             # return the new function

@logged                                        # same as add = logged(add)
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

print(add(2, 3))                               # runs wrapper
print(add.__name__, add.__doc__)               # preserved thanks to wraps

# Output:
# calling add(2, 3)
# add -> 5
# 5
# add Add two numbers.
```

## 💻 Code Example — Advanced
```python
# Production style: typed decorator factory with ParamSpec (full file + tests in main.py)
import functools
import time
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")                             # captures the wrapped function's parameters
R = TypeVar("R")                               # captures its return type


def retry(times: int = 3, delay: float = 0.0,
          exceptions: tuple[type[BaseException], ...] = (Exception,)
          ) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Factory: retry(...) returns the actual decorator."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)                 # keep metadata
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last: BaseException | None = None  # remember the last error
            for attempt in range(1, times + 1):    # try up to `times`
                try:
                    return func(*args, **kwargs)   # success -> return
                except exceptions as exc:      # only expected errors
                    last = exc                 # keep it
                    if attempt < times:
                        time.sleep(delay)      # wait before retrying
            raise last  # type: ignore[misc]   # out of attempts: re-raise
        return wrapper
    return decorator


calls = {"n": 0}                               # count attempts

@retry(times=3, exceptions=(ConnectionError,)) # retry only connection errors
def fetch() -> str:
    calls["n"] += 1                            # one more attempt
    if calls["n"] < 3:
        raise ConnectionError("network down")  # fail twice
    return "payload"                           # then succeed

print(fetch(), calls["n"])                     # result and attempts used

# Output:
# payload 3
```

---

## 🟠 JavaScript vs Python Comparison
JS has higher-order functions too (`const timed = fn => (...a) => ...`), and TypeScript has experimental `@decorator` syntax for classes. In Python, the `@` syntax is built in for functions and classes.

```python
# Python way
def twice(fn):
    def wrapper(*a, **k):
        fn(*a, **k); return fn(*a, **k)
    return wrapper

@twice
def hi(): print("hi")
```
```javascript
// JavaScript way
const twice = (fn) => (...args) => { fn(...args); return fn(...args); };
const hi = twice(() => console.log("hi"));   // no @ syntax for plain functions
```

---

## 🟠 FastAPI Connection
FastAPI routes are decorators: `@app.get(...)` registers the function and returns it. When you write your own decorator for route handlers you MUST use `functools.wraps`, otherwise FastAPI sees `wrapper(*args, **kwargs)` and loses the type hints it needs for validation. For auth and shared logic prefer `Depends`.

```python
import functools, time
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

def timed(fn):
    @functools.wraps(fn)                       # without wraps FastAPI cannot read fn's signature
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return await fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} took {(time.perf_counter() - start) * 1000:.1f} ms")
    return wrapper

@app.get("/items/{item_id}")                   # outer decorator registers the route
@timed                                         # inner decorator wraps the handler first
async def read_item(item_id: int) -> dict[str, int]:
    return {"id": item_id}

print(TestClient(app).get("/items/5").json())  # {'id': 5}  (a timing line prints too)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: forgetting `functools.wraps` (name becomes `wrapper`, docs and signatures are lost).
✅ Correct: always decorate wrapper with `@functools.wraps(func)`.

```python
# Wrong
def deco(f):
    def wrapper(*a, **k): return f(*a, **k)
    return wrapper
# Right
import functools
def deco(f):
    @functools.wraps(f)
    def wrapper(*a, **k): return f(*a, **k)
    return wrapper
```

❌ Mistake 2: returning `wrapper()` instead of `wrapper`, or forgetting to `return func(...)` inside, so the result becomes `None`.
✅ Correct: return the function object, and return the result of the call.

❌ Mistake 3: using `@retry` without parentheses on a factory (`@retry` passes the function as `times`).
✅ Correct: `@retry()` or `@retry(times=3)`; or support both forms.

---

## 🧠 Tricky Interview Question
```python
def deco(f):
    print("decorating", f.__name__)
    def wrapper(*a, **k):
        print("calling")
        return f(*a, **k)
    return wrapper

@deco
def hello(): pass

print("defined")
hello(); hello()
```
Answer: `decorating hello`, `defined`, `calling`, `calling`. The decorator body runs once when the function is defined (import time); the wrapper runs on every call. Decorators with side effects therefore run at import time.

---

## ⚫ Interview Questions + Answers

Q1: What does `@d` do?
A1: It is exactly `func = d(func)`, executed once right after `def`.

Q2: Why `functools.wraps`?
A2: It copies `__name__`, `__doc__`, `__module__`, `__wrapped__` etc. from the original to the wrapper so debugging, docs, `inspect.signature` and FastAPI introspection keep working.

Q3: How do you write a decorator with arguments?
A3: Three layers: factory(args) -> decorator(func) -> wrapper(*a, **k). `@retry(3)` calls the factory first.

Q4: Order of stacked decorators?
A4: `@A @B def f` is `f = A(B(f))`: B wraps first (innermost), A runs first at call time.

Q5: Class-based decorator vs function-based?
A5: A class with `__init__(func)` and `__call__` can keep state easily (e.g. call counter). Use `functools.update_wrapper(self, func)`. Instance-method decorating needs `__get__`, so function-based is simpler.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The same behavior wraps many functions (timing, retry, logging, caching)
- You want to keep business logic clean
- Registering handlers (routes, signals, commands)

❌ Avoid when:
- The wrapping logic is complex and hidden (stack traces get confusing)
- You need per-request, injectable logic in FastAPI (use `Depends`)
- Only one function needs it (just call a helper)

---

## 📊 Visual Diagram
```
 @timer
 def add(a, b): ...          add = timer(add)

 caller --> wrapper(*args) --> [ start timer ]
                                    |
                                    v
                               original add(a, b)
                                    |
                               [ stop timer ] --> result --> caller

 Stacked:  @A @B def f   =>   A( B( f ) )
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Decorator | Function that wraps a function | function को लपेटने वाला function |
| Closure | Inner function remembering outer variables | बाहरी variables याद रखने वाला inner function |
| `*args, **kwargs` | Pass any arguments through | कोई भी arguments आगे भेजना |
| `functools.wraps` | Copies metadata to wrapper | metadata की नकल |
| ParamSpec | Typing for wrapped parameters | wrapped function के parameters का type |
| Factory | Function returning a decorator | decorator लौटाने वाला function |

---

## ⚡ 3-Line Summary
English: A decorator takes a function and returns an enhanced function; `@d` means `f = d(f)`.
English: Always use `*args/**kwargs` and `functools.wraps`; add one more layer for arguments.
English: Decoration runs once at definition time, the wrapper on every call.

Hindi: Decorator function लेकर बेहतर function लौटाता है; `@d` का मतलब `f = d(f)`।
Hindi: हमेशा `*args/**kwargs` और `functools.wraps` इस्तेमाल करो; arguments के लिए एक और परत जोड़ो।
Hindi: Decoration definition के समय एक बार चलता है, wrapper हर call पर।

---

## ➡️ Next Topic
**477. Implement Context Manager** — the `with` statement: guaranteed setup and cleanup.

---
