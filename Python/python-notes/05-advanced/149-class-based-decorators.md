---

# 149. Class-based Decorators
# हिंदी में: Class पर आधारित Decorators

---

## 🔵 Simple Definition (English)
A class-based decorator is a class whose instance acts like a function because it defines `__call__`. The class receives the function in `__init__` (or in `__call__` when it takes arguments), and it can keep state such as counters and caches as normal attributes on the instance.

## 🔵 सरल परिभाषा (Hindi)
Class-based decorator ऐसी class है जिसका instance `__call__` define करने की वजह से function की तरह काम करता है। Class function को `__init__` में लेती है (या arguments हों तो `__call__` में), और counters व caches जैसी state को instance के attributes में रख सकती है।

---

## 🔴 Problem it Solves
Function decorators keep state in closure variables, which needs `nonlocal` and is hard to inspect from outside. When a decorator needs counters, a cache, statistics or a `reset()` method, nested functions become messy. A class gives named attributes, methods and easy testing: `greet.count`, `cache.hits`.

## 🔴 यह क्यों बना? (Hindi)
Function decorators state को closure variables में रखते हैं, जिसके लिए `nonlocal` चाहिए और बाहर से उसे देखना मुश्किल है। जब decorator को counter, cache, statistics या `reset()` method चाहिए, nested functions उलझ जाते हैं। Class named attributes, methods और आसान testing देती है: `greet.count`, `cache.hits`।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `@CountCalls` above def greet runs  greet = CountCalls(greet)
Step 2 → __init__ receives the function and stores it, plus initial state (count = 0)
Step 3 → `greet` is now an INSTANCE of CountCalls, not a function
Step 4 → greet("x") triggers CountCalls.__call__(self, "x") because instances are callable
Step 5 → __call__ updates state and calls the stored original function
Step 6 → functools.update_wrapper(self, func) copies __name__ and __doc__ to the instance

With arguments:  @TTLCache(ttl=60)
   TTLCache(ttl=60)  -> instance made (config in __init__)
   instance(func)    -> __call__ receives the function and returns a wrapper

Methods: an instance is NOT a function, so it has no __get__ -> add __get__ to bind `self`.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → def greet के ऊपर `@CountCalls` चलाता है  greet = CountCalls(greet)
Step 2 → __init__ function को लेकर store करता है, साथ में शुरुआती state (count = 0)
Step 3 → `greet` अब CountCalls का INSTANCE है, function नहीं
Step 4 → greet("x") असल में CountCalls.__call__(self, "x") चलाता है क्योंकि instances callable हैं
Step 5 → __call__ state update करता है और stored original function को call करता है
Step 6 → functools.update_wrapper(self, func) __name__ और __doc__ instance पर copy करता है

Arguments के साथ:  @TTLCache(ttl=60)
   TTLCache(ttl=60)  -> instance बना (config __init__ में)
   instance(func)    -> __call__ को function मिलता है और वह wrapper लौटाता है

Methods: instance function नहीं है, इसलिए उसमें __get__ नहीं होता -> `self` bind करने के लिए __get__ जोड़ें।
```

---

## 🟡 Real World Example
An exchange-rate service calls a slow external API. A `TTLCache(ttl=60)` class decorator caches each currency pair for 60 seconds and exposes `hits` and `misses` so a `/metrics` endpoint can report the cache hit ratio. A rate limiter such as "5 calls per minute per function" is another common class-based decorator because it must remember timestamps.

## 🟡 Real Example Hindi mein
Exchange-rate service धीमी external API call करती है। `TTLCache(ttl=60)` class decorator हर currency pair को 60 seconds तक cache करता है और `hits` व `misses` दिखाता है ताकि `/metrics` endpoint cache hit ratio बता सके। "प्रति मिनट 5 calls" वाला rate limiter भी आम class-based decorator है क्योंकि उसे timestamps याद रखने पड़ते हैं।

---

## 💻 Code Example — Basic
```python
# Class-based decorator: __init__ takes the function, __call__ runs it
import functools                                          # update_wrapper
from collections.abc import Callable                      # callable type
from typing import Any                                    # any type


class CountCalls:
    def __init__(self, func: Callable[..., Any]) -> None:
        functools.update_wrapper(self, func)              # copy __name__, __doc__ onto the instance
        self.func: Callable[..., Any] = func              # keep the original function
        self.count: int = 0                               # state lives on the instance

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.count += 1                                   # update state on every call
        return self.func(*args, **kwargs)                 # run the original


@CountCalls                                               # greet = CountCalls(greet)
def greet(name: str) -> str:
    """Say hello."""
    return f"Hello {name}"


greet("Aditya")                                           # first call
greet("Riya")                                             # second call
print(greet.count, greet.__name__, type(greet).__name__)  # state + metadata + real type

# Output:
# 2 greet CountCalls
```

## 💻 Code Example — Advanced
```python
# Production style: class-based decorators (with arguments, and method-safe)
import functools                                          # wraps / update_wrapper
import time                                               # monotonic clock
from collections.abc import Callable                      # callable type
from types import MethodType                              # bind instance to callable
from typing import Any                                    # any type


class TTLCache:
    """Decorator WITH arguments: __init__ gets config, __call__ gets the function."""

    def __init__(self, ttl: float = 60.0) -> None:
        self.ttl: float = ttl                             # seconds a value stays fresh
        self.store: dict[tuple[Any, ...], tuple[float, Any]] = {}   # args -> (expiry, value)
        self.hits: int = 0                                # statistics
        self.misses: int = 0

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:   # decorator step
        @functools.wraps(func)                            # wrapper looks like func
        def wrapper(*args: Any) -> Any:
            now: float = time.monotonic()                 # current time
            entry = self.store.get(args)                  # cached (expiry, value) or None
            if entry is not None and entry[0] > now:      # still fresh
                self.hits += 1
                return entry[1]
            self.misses += 1                              # stale or missing
            value: Any = func(*args)                      # compute the real value
            self.store[args] = (now + self.ttl, value)    # remember with expiry time
            return value
        return wrapper


cache = TTLCache(ttl=0.2)                                 # configure once


@cache                                                    # used as an instance
def usd_to_inr(amount: int) -> float:
    return amount * 83.5                                  # pretend this is a slow API call


print(usd_to_inr(10), usd_to_inr(10))                     # miss then hit
time.sleep(0.25)                                          # let TTL expire
print(usd_to_inr(10))                                     # miss again
print(cache.hits, cache.misses)                           # 1 hit, 2 misses


class CountMethod:
    """Class-based decorator that works on METHODS: needs __get__ (descriptor protocol)."""

    def __init__(self, func: Callable[..., Any]) -> None:
        functools.update_wrapper(self, func)              # copy metadata
        self.func = func                                  # original function
        self.count = 0                                    # shared counter

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.count += 1                                   # count the call
        return self.func(*args, **kwargs)                 # run it

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:                                   # accessed via the class
            return self
        return MethodType(self, obj)                      # bind obj as `self` argument


class Wallet:
    @CountMethod                                          # decorate a method
    def pay(self, amount: int) -> str:
        return f"paid {amount}"


w = Wallet()
print(w.pay(100), Wallet.pay.count)                       # works only because of __get__

# Output:
# 835.0 835.0
# 835.0
# 1 2
# paid 100 1
```
Both blocks were run on Python 3.13.3. The cache counts (`1 2`) rely on the 0.25s sleep exceeding the 0.2s TTL.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Callable object | any class with `__call__` | no equivalent; functions are objects, classes are not callable |
| State holder | instance attributes | closure variables or properties on the function object |
| Read state later | `greet.count` | `greet.count` (function property) |
| Method binding | needs `__get__` | arrow/`bind` handles `this` |

```python
# Python way
class Counter:
    def __init__(self, f):             # receive the function
        self.f, self.n = f, 0          # keep function and state
    def __call__(self, *a):            # make instance callable
        self.n += 1                    # update state
        return self.f(*a)              # call original
@Counter
def ping() -> str:
    return "pong"
ping(); ping()
print(ping.n)                          # 2
```
```javascript
// JavaScript way — state on the function object, or a closure
function counter(f) {
  const wrapped = (...args) => { wrapped.n++; return f(...args); };  // wrapper
  wrapped.n = 0;                                                      // state as property
  return wrapped;
}
const ping = counter(() => "pong");
ping(); ping();
console.log(ping.n);                                                  // 2
```

Key difference: Python can make a real object callable with `__call__`, so state and methods are tidy. JavaScript uses closures or properties on the function itself, because class instances cannot be called.

---

## 🟠 FastAPI Connection
FastAPI's dependency injection accepts any callable, including instances of classes with `__call__`. A class holds configuration (for example a required role) and is used in `Depends(...)`. That is the same pattern as a class-based decorator.

```python
# FastAPI example — callable class as dependency (run with TestClient)
from typing import Annotated                                # Annotated for Depends
from fastapi import Depends, FastAPI, Header, HTTPException  # FastAPI parts
from fastapi.testclient import TestClient                   # in-process client

app: FastAPI = FastAPI()                                    # create app


class RequireRole:
    def __init__(self, role: str) -> None:
        self.role: str = role                               # config stored on the instance

    def __call__(self, x_role: Annotated[str | None, Header()] = None) -> str:
        if x_role != self.role:                             # compare header with required role
            raise HTTPException(status_code=403, detail=f"{self.role} only")
        return x_role                                       # pass role to the route


@app.get("/admin")                                          # protected route
def admin(role: Annotated[str, Depends(RequireRole("admin"))]) -> dict[str, str]:
    return {"role": role}                                   # reached only when allowed


client = TestClient(app)                                    # test client
print(client.get("/admin", headers={"X-Role": "admin"}).json())   # {'role': 'admin'}
print(client.get("/admin").status_code)                     # 403
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Decorating a method without `__get__`
✅ Correct: implement `__get__` that returns `MethodType(self, obj)`

```python
class NoGet:
    def __init__(self, f): self.f = f
    def __call__(self, *a): return self.f(*a)
class W:
    @NoGet                      # Wrong: instance is not bound, so `self` is not passed
    def pay(self, amt): return amt
# W().pay(5) -> TypeError: W.pay() missing 1 required positional argument: 'amt'
# Right: add __get__ (see the advanced example) or use a function decorator
```

❌ Mistake 2: Expecting state to be per-function when it is per-decorator-instance
✅ Correct: create a separate instance for every function that needs its own state

```python
class Count:
    def __init__(self, f): self.f = f; self.n = 0     # state per decorated function: OK
    def __call__(self, *a): self.n += 1; return self.f(*a)
@Count
def a(): pass
@Count
def b(): pass
a(); a(); b()
print(a.n, b.n)                 # 2 1  <- separate because each decoration makes a new instance
# Wrong: sharing ONE TTLCache() instance across many functions mixes their stores
```

❌ Mistake 3: Forgetting that the decorated name is no longer a function
✅ Correct: remember `type(greet)` is the class, use `update_wrapper` for metadata

```python
# Wrong: assuming inspect.isfunction(greet) is True or that it can be pickled like a function
# Right: check callable(greet); copy metadata with functools.update_wrapper(self, func)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class Count:
    def __init__(self, f):
        self.f = f
        self.n = 0
    def __call__(self, *a):
        self.n += 1
        return self.f(*a)

@Count
def a(): pass

@Count
def b(): pass

a(); a(); b()
print(a.n, b.n)
print(type(a), callable(a))
```
Answer: `2 1` and then `<class '__main__.Count'> True`. Every `@Count` creates a new `Count` instance, so `a` and `b` have separate counters. `a` is no longer a function; it is a `Count` object, but `callable(a)` is still `True` because the class defines `__call__`.

---

## ⚫ Interview Questions + Answers

Q1: Why use a class instead of a function for a decorator?
A1: When the decorator needs readable state (counters, caches), extra methods (`reset`, `stats`) or configuration. Instance attributes are easier to read and test than closure variables with `nonlocal`.

Q2: How do `__init__` and `__call__` split work in a decorator without arguments?
A2: `__init__` receives the function at decoration time and sets up state. `__call__` runs on every call of the decorated name and forwards to the stored function.

Q3: How does it change when the decorator takes arguments?
A3: `__init__` receives the arguments (`ttl=60`). Then `__call__` receives the function once and returns a wrapper function. Later calls go to the wrapper, not to `__call__` of the class.

Q4: Why does a class-based decorator break on methods?
A4: Functions are descriptors: `obj.method` triggers `function.__get__` which binds `self`. A plain class instance has no `__get__`, so `self` is never passed. Define `__get__` returning `MethodType(self, obj)`.

Q5: Which is faster, class-based or function-based?
A5: Function wrappers are slightly faster, since a call on an instance goes through `__call__` lookup. The difference is tiny; choose by clarity, not speed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The decorator keeps state: counters, caches, rate-limit timestamps
- You want to expose methods or stats on the decorated name
- Configuration is complex and fits well in `__init__`

❌ Avoid when:
- A simple stateless wrapper is enough, use a function
- The decorator will mostly be applied to methods and you do not want to write `__get__`
- You need the result to still be a real function (for example some tools check `inspect.isfunction`)

---

## 📊 Visual Diagram
```
@CountCalls
def greet(...)         greet  ───►  CountCalls instance
                                    ├── func  ─► original greet
                                    ├── count = 0 ... 2
                                    └── __call__(*args)

greet("Riya")  ──►  CountCalls.__call__(self, "Riya")
                        1. self.count += 1
                        2. return self.func("Riya")

@TTLCache(ttl=60)   =   TTLCache(ttl=60)  ──►  instance(func)  ──►  wrapper
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__call__` | Makes an instance callable like a function | Instance को function की तरह call करने लायक बनाता है |
| `__init__` | Receives the function (or the config) | Function (या config) को लेता है |
| `update_wrapper` | Copies metadata onto any object | किसी भी object पर metadata copy करता है |
| `__get__` | Descriptor hook that binds `self` | `self` bind करने वाला descriptor hook |
| TTL | Time a cached value stays valid | Cached value कितनी देर valid रहे |
| Stateful | Remembers data between calls | Calls के बीच data याद रखना |

---

## ⚡ 3-Line Summary
English: A class-based decorator is an object with `__call__` that wraps a function and stores state in attributes. With arguments, `__init__` takes the config and `__call__` takes the function and returns a wrapper. For methods, add `__get__` so `self` is bound.
Hindi: Class-based decorator `__call__` वाला object है जो function को wrap करता है और state attributes में रखता है। Arguments हों तो `__init__` config लेता है और `__call__` function लेकर wrapper लौटाता है। Methods के लिए `__get__` जोड़ें ताकि `self` bind हो।

---

## ➡️ Next Topic
**150. Stacked Decorators** — applying several decorators on one function and understanding the order in which they are applied and executed.
