---

# 150. Stacked Decorators
# हिंदी में: एक के ऊपर एक Decorators (Stacked Decorators)

---

## 🔵 Simple Definition (English)
Stacked decorators means putting more than one `@decorator` line above a single function. They are applied from the bottom one upward (closest to `def` first), but when the function is called, the top wrapper runs first. Think of wrapping a gift: the last wrapper added is the first one opened.

## 🔵 सरल परिभाषा (Hindi)
Stacked decorators का मतलब है एक function के ऊपर एक से ज्यादा `@decorator` लाइनें लगाना। ये नीचे से ऊपर की ओर apply होते हैं (`def` के सबसे पास वाला पहले), लेकिन function call होने पर सबसे ऊपर वाला wrapper पहले चलता है। गिफ्ट पैक करने जैसा समझें: जो wrapper आखिर में लगा, वही सबसे पहले खुलता है।

---

## 🔴 Problem it Solves
A real endpoint needs several cross-cutting features at once: authentication, timing, caching, logging. Without stacking, you must write one giant decorator or call helpers manually inside the body. Stacking lets each concern stay a small reusable decorator and be combined in any order, but the order changes behaviour, so it must be understood.

## 🔴 यह क्यों बना? (Hindi)
असली endpoint को एक साथ कई features चाहिए: authentication, timing, caching, logging। Stacking के बिना एक बहुत बड़ा decorator लिखना पड़ता या body में helpers हाथ से call करने पड़ते। Stacking से हर concern एक छोटा reusable decorator रहता है और किसी भी क्रम में जोड़ा जा सकता है, लेकिन क्रम से behaviour बदलता है, इसलिए इसे समझना जरूरी है।

---

## 🟢 How it Works — Step by Step

```
@A
@B
def f(): ...          is the same as          f = A(B(f))

Step 1 → Python creates the plain function f
Step 2 → The decorator closest to def (B) is applied first:   B(f)  -> wrapperB
Step 3 → Then A is applied to that result:                    A(wrapperB) -> wrapperA
Step 4 → The name f now points to wrapperA (decoration order: bottom -> top)
Step 5 → Calling f() runs wrapperA first (top), which calls wrapperB, which calls the real f
Step 6 → Results travel back out: real f -> wrapperB -> wrapperA -> caller
Step 7 → Rule of thumb: applied bottom-up, executed top-down (on the way in)
```

## 🟢 कैसे काम करता है? (Hindi)
```
@A
@B
def f(): ...          बराबर है          f = A(B(f))

Step 1 → Python सादा function f बनाता है
Step 2 → `def` के सबसे पास वाला decorator (B) पहले apply होता है:   B(f)  -> wrapperB
Step 3 → फिर A उस result पर apply होता है:                         A(wrapperB) -> wrapperA
Step 4 → नाम f अब wrapperA की ओर इशारा करता है (decoration क्रम: नीचे -> ऊपर)
Step 5 → f() call करने पर पहले wrapperA (ऊपर वाला) चलता है, फिर wrapperB, फिर असली f
Step 6 → Results वापस बाहर आते हैं: असली f -> wrapperB -> wrapperA -> caller
Step 7 → याद रखने का नियम: नीचे से ऊपर apply होता है, अंदर जाते समय ऊपर से नीचे चलता है
```

---

## 🟡 Real World Example
A report endpoint in an admin dashboard uses three decorators: `@require_role("admin")` (block guests immediately), `@timed` (measure latency for metrics) and `@lru_cache` (reuse a heavy monthly report). Auth must be outermost, otherwise a guest could read cached data, and the cache must be innermost so timing still records cache hits.

## 🟡 Real Example Hindi mein
Admin dashboard के report endpoint पर तीन decorators हैं: `@require_role("admin")` (guests को तुरंत रोके), `@timed` (metrics के लिए latency नापे) और `@lru_cache` (भारी monthly report दोबारा इस्तेमाल करे)। Auth सबसे बाहर होना चाहिए, वरना guest cached data पढ़ सकता है, और cache सबसे अंदर होना चाहिए ताकि timing में cache hits भी गिने जाएं।

---

## 💻 Code Example — Basic
```python
# Stacked decorators: applied bottom-up, executed top-down
import functools                                          # wraps
from collections.abc import Callable                      # callable type


def tag(name: str) -> Callable[[Callable[[], str]], Callable[[], str]]:
    def deco(func: Callable[[], str]) -> Callable[[], str]:
        @functools.wraps(func)
        def wrapper() -> str:
            print(f"enter {name}")                        # runs on the way IN
            result: str = func()                          # inner layer
            print(f"exit {name}")                         # runs on the way OUT
            return f"<{name}>{result}</{name}>"
        print(f"decorating with {name}")                  # runs at definition time
        return wrapper
    return deco


@tag("outer")                                             # applied second
@tag("inner")                                             # applied first
def hello() -> str:
    return "hi"


print("--- calling ---")
print(hello())                                            # outer wrapper runs first

# Output:
# decorating with inner
# decorating with outer
# --- calling ---
# enter outer
# enter inner
# exit inner
# exit outer
# <outer><inner>hi</inner></outer>
```

## 💻 Code Example — Advanced
```python
# Production style: auth + timing + cache stacked on a service function
import functools                                          # wraps, lru_cache
import time                                               # timing
from collections.abc import Callable                      # callable type
from typing import Any, ParamSpec, TypeVar                # generic typing

P = ParamSpec("P")
R = TypeVar("R")
CALL_LOG: list[str] = []                                  # records execution order


def require_role(role: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def deco(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            CALL_LOG.append("auth")                       # first check: who is calling?
            user_role: Any = kwargs.pop("user_role", None)   # take role out of kwargs
            if user_role != role:                         # deny early, skip inner layers
                raise PermissionError(f"need role {role!r}, got {user_role!r}")
            return func(*args, **kwargs)
        return wrapper
    return deco


def timed(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        CALL_LOG.append("timed")
        start: float = time.perf_counter()                # start clock
        try:
            return func(*args, **kwargs)
        finally:
            CALL_LOG.append("timed-done")                 # runs even on exceptions
            _ = time.perf_counter() - start               # elapsed (would be sent to metrics)
    return wrapper


@require_role("admin")                                    # 1. auth runs first
@timed                                                    # 2. then timing
@functools.lru_cache(maxsize=None)                        # 3. closest to function: cache
def report(month: int) -> str:
    CALL_LOG.append("compute")                            # real work
    return f"report-{month}"


print(report(1, user_role="admin"))                       # compute runs
print(report(1, user_role="admin"))                       # cached: no compute
try:
    report(2, user_role="guest")                          # blocked by auth
except PermissionError as e:
    print("Error:", e)
print(CALL_LOG)

# Output:
# report-1
# report-1
# Error: need role 'admin', got 'guest'
# ['auth', 'timed', 'compute', 'timed-done', 'auth', 'timed', 'timed-done', 'auth']
```
Both blocks were run on Python 3.13.3 and the output is real. Notice the cached second call has no `compute`, and the guest call never reaches `timed`.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Stacking syntax | several `@` lines | several `@` lines (TS/Babel) or nested calls |
| Equivalent code | `f = A(B(f))` | `f = A(B(f))` |
| Apply order | bottom to top | bottom to top (same rule for class decorators) |
| Everyday relative | decorators on routes | Express middleware chain `app.use(a, b, c)` (runs LEFT to RIGHT) |

```python
# Python way
def A(f): return lambda: "A(" + f() + ")"          # wraps with A
def B(f): return lambda: "B(" + f() + ")"          # wraps with B

@A                                                 # outer
@B                                                 # inner
def x() -> str:
    return "x"
print(x())                                         # A(B(x))
```
```javascript
// JavaScript way — compose by hand (outer first in the call expression)
const A = (f) => () => "A(" + f() + ")";           // wrapper A
const B = (f) => () => "B(" + f() + ")";           // wrapper B
const x = A(B(() => "x"));                         // same as stacked @A @B
console.log(x());                                  // A(B(x))
// Express: app.get("/r", auth, timing, handler)  -> auth runs first, like the TOP decorator
```

Key difference: Express lists middleware in the order they run (first listed runs first). Python lists the outermost wrapper first too, but it is applied last. Think "top decorator = first middleware".

---

## 🟠 FastAPI Connection
In FastAPI the route decorator `@app.get(...)` must be the TOP decorator. It registers whatever function is below it at that moment. If a custom decorator is placed above the route decorator, FastAPI registers the unwrapped function and your decorator never runs.

```python
# FastAPI example — decorator order matters (run with TestClient)
import functools                                          # wraps
from collections.abc import Awaitable, Callable           # callable types
from typing import Any                                    # any type
from fastapi import FastAPI                               # FastAPI app
from fastapi.testclient import TestClient                 # in-process client

app: FastAPI = FastAPI()                                  # create app


def shout(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return (await func(*args, **kwargs)).upper()      # uppercase the response text
    return wrapper


@app.get("/right")                                        # route decorator on TOP: registers wrapper
@shout
async def right() -> str:
    return "hello"


@shout                                                    # WRONG order: shout wraps the router's return
@app.get("/wrong")                                        # route registered with the raw function
async def wrong() -> str:
    return "hello"


client = TestClient(app)                                  # test client
print(client.get("/right").json(), client.get("/wrong").json())   # HELLO hello

# Output:
# HELLO hello
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Putting auth/validation decorators in the wrong order
✅ Correct: the security decorator must be the outermost (top) one

```python
# Wrong: cache above auth -> a cached result is returned to anyone
# @lru_cache
# @require_role("admin")
# def report(): ...
# Right: auth on top, cache below it
# @require_role("admin")
# @lru_cache
# def report(): ...
```

❌ Mistake 2: Thinking the top decorator is applied first
✅ Correct: bottom is applied first, top runs first on call

```python
import functools
def a(f):
    @functools.wraps(f)
    def w(*x): return "A(" + f(*x) + ")"
    return w
def b(f):
    @functools.wraps(f)
    def w(*x): return "B(" + f(*x) + ")"
    return w
@a
@b
def f(): return "x"
print(f())        # A(B(x))
@b
@a
def g(): return "x"
print(g())        # B(A(x))  <- swapping order changes the result
```

❌ Mistake 3: Stacking a wrapper above `@classmethod` / `@staticmethod`
✅ Correct: put `@classmethod` on TOP

```python
class C:
    @classmethod
    @a                       # Right: classmethod outermost -> C.ok() == "A(ok)"
    def ok(cls): return "ok"
# Wrong: @a above @classmethod makes the wrapper call a classmethod object
# -> TypeError: 'classmethod' object is not callable (on call)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def a(f):
    def w(): return "A(" + f() + ")"
    return w

def b(f):
    def w(): return "B(" + f() + ")"
    return w

@a
@b
def f(): return "x"

@b
@a
def g(): return "x"

print(f(), g())
```
Answer: `A(B(x)) B(A(x))`. `@a @b def f` equals `f = a(b(f))`, so `b` wraps first and `a` becomes outermost, giving `A(B(x))`. For `g` the order is reversed, so the result is `B(A(x))`. Order of decorators changes behaviour, not just style.

---

## ⚫ Interview Questions + Answers

Q1: In what order are stacked decorators applied and executed?
A1: Applied bottom to top (`f = A(B(f))`, so `B` first). On a call, the outermost wrapper (top decorator) starts first, then the next one, then the real function; the return path is the reverse.

Q2: Why does order matter for caching and auth?
A2: If the cache is outside auth, a cached response is served without any permission check. Put security outermost, then rate limiting/timing, then cache next to the function.

Q3: How can you reach the original function under many decorators?
A3: If every wrapper used `functools.wraps`, `__wrapped__` chains down; `inspect.unwrap(f)` walks all the way to the original.

Q4: Where must `@app.get` go in FastAPI?
A4: At the top. It registers the function object that exists at that line. A decorator placed above it wraps the return value of the router decorator and is never used by the routing table.

Q5: How do you combine many decorators into one reusable decorator?
A5: Write a helper that applies them in a loop, for example `def combine(*decos): return lambda f: functools.reduce(lambda acc, d: d(acc), reversed(decos), f)`; then `@combine(auth, timed)`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several independent cross-cutting concerns apply to one function
- Each concern is already a tested reusable decorator
- You can clearly document the order (auth, timing, cache)

❌ Avoid when:
- More than three or four decorators make the call path hard to debug
- Order dependencies are subtle and untested
- A simple function call inside the body would be clearer

---

## 📊 Visual Diagram
```
@A
@B
def f(): ...          f = A( B( f ) )

 call f()
    │
    ▼
 ┌─────────── wrapperA ───────────┐   (top decorator: runs first)
 │  before A                      │
 │   ┌──────── wrapperB ───────┐  │
 │   │  before B               │  │
 │   │   ┌── original f ──┐    │  │
 │   │   │   f body       │    │  │
 │   │   └────────────────┘    │  │
 │   │  after B                │  │
 │   └─────────────────────────┘  │
 │  after A                       │
 └────────────────────────────────┘
Applied: B first, then A.   Entered: A first, then B.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stacking | Several decorators on one function | एक function पर कई decorators |
| Outermost | The top decorator, entered first | सबसे ऊपर वाला, पहले चलता है |
| Innermost | The decorator closest to `def` | `def` के सबसे पास वाला |
| `__wrapped__` | Link to the function being wrapped | Wrap हुए function का link |
| `inspect.unwrap` | Follows `__wrapped__` to the original | Original function तक पहुंचाता है |
| Middleware | Request pipeline, similar to a decorator stack | Request pipeline, decorator stack जैसी |

---

## ⚡ 3-Line Summary
English: `@A @B def f` equals `f = A(B(f))`: applied bottom-up, executed top-down on the way in. Order changes behaviour, so put auth outermost and cache innermost. In FastAPI the route decorator must be on top.
Hindi: `@A @B def f` का मतलब `f = A(B(f))` है: नीचे से ऊपर apply होता है और अंदर जाते समय ऊपर से नीचे चलता है। क्रम से behaviour बदलता है, इसलिए auth सबसे बाहर और cache सबसे अंदर रखें। FastAPI में route decorator सबसे ऊपर होना चाहिए।

---

## ➡️ Next Topic
**151. Descriptor Protocol** — the `__get__`, `__set__` and `__delete__` hooks that power properties, methods and ORM fields.
