---

# 127. Functools Module
# हिंदी में: functools Module (functions के लिए औज़ारों का डिब्बा)

---

## 🔵 Simple Definition (English)
`functools` is a standard-library module of tools that work on and with functions: `wraps`, `lru_cache`/`cache`, `partial`, `reduce`, `cmp_to_key`, `singledispatch`, `cached_property`, `total_ordering`. No install needed.

## 🔵 सरल परिभाषा (Hindi)
`functools` standard library का module है जिसमें functions पर और functions के साथ काम करने वाले औज़ार हैं: `wraps`, `lru_cache`/`cache`, `partial`, `reduce`, `cmp_to_key`, `singledispatch`, `cached_property`, `total_ordering`। Install की जरूरत नहीं।

---

## 🔴 Problem it Solves
Functions are objects in Python, so people constantly write the same helper patterns by hand: caching results, pre-filling arguments, writing decorators that keep metadata, folding a list into one value, or generating comparison methods. `functools` ships tested, fast (often C-implemented) versions of all of these.

## 🔴 यह क्यों बना? (Hindi)
Python में functions objects हैं, इसलिए लोग वही helper patterns हाथ से बार-बार लिखते हैं: results cache करना, arguments पहले से भरना, metadata बचाने वाले decorators, list को एक value में समेटना, या comparison methods बनाना। `functools` इन सबके tested, तेज़ (अक्सर C में लिखे) versions देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → import functools (or from functools import ...)
Step 2 → Decorator tools wrap a function: wraps, lru_cache, cache, singledispatch
Step 3 → Builders create new callables: partial, partialmethod
Step 4 → Folding tool: reduce(f, items, start)
Step 5 → Class helpers: total_ordering, cached_property
Step 6 → Adapter: cmp_to_key turns an old comparator into a sort key

Cheat map:  remember results -> cache | pre-fill args -> partial | fold -> reduce
            keep metadata -> wraps    | one name, many types -> singledispatch
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → import functools (या from functools import ...)
Step 2 → Decorator tools function को wrap करते हैं: wraps, lru_cache, cache, singledispatch
Step 3 → Builders नए callables बनाते हैं: partial, partialmethod
Step 4 → Folding tool: reduce(f, items, start)
Step 5 → Class helpers: total_ordering, cached_property
Step 6 → Adapter: cmp_to_key पुराने comparator को sort key बनाता है
```

---

## 🟡 Real World Example
An AI-app backend calls an embeddings API: `@cache` avoids paying twice for the same text. A Swiggy service builds `partial(send_sms, sender="SWIGGY")` so every caller only passes number and text. A model class uses `@cached_property` for an expensive feature vector. A DSL router uses `@singledispatch` to format money, dates and lists differently.

## 🟡 Real Example Hindi mein
AI-app backend embeddings API बुलाता है: `@cache` एक ही text के लिए दोबारा पैसे खर्च होने से बचाता है। Swiggy service `partial(send_sms, sender="SWIGGY")` बनाती है ताकि हर caller सिर्फ number और text दे। Model class महंगे feature vector के लिए `@cached_property` लगाती है। Router `@singledispatch` से पैसे, तारीख और lists को अलग तरह format करता है।

---

## 💻 Code Example — Basic
```python
# Basic tour of functools
from functools import cache, cached_property, partial, reduce, singledispatch, total_ordering


@cache                                             # unbounded memoization (3.9+)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2) # exponential without the cache


print(fib(60))                                     # instant thanks to cache

power_of_two = partial(pow, 2)                     # pow(2, ?) with base pre-filled
print(power_of_two(10))                            # 2 ** 10

print(reduce(lambda a, b: a * b, [1, 2, 3, 4], 1)) # fold into one product


@singledispatch                                    # choose implementation by arg type
def fmt(x: object) -> str:
    return f"obj:{x}"                              # default case


@fmt.register                                      # type taken from the annotation
def _(x: int) -> str:
    return f"int:{x}"                              # int case


@fmt.register
def _(x: list) -> str:
    return "list:" + ",".join(map(str, x))         # list case


print(fmt(5), fmt([1, 2]), fmt(2.5))               # three different paths


@total_ordering                                    # fill in <=, >, >= from __eq__ and __lt__
class Version:
    def __init__(self, n: int) -> None:
        self.n = n                                 # numeric version

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Version) and self.n == o.n   # equality

    def __lt__(self, o: "Version") -> bool:
        return self.n < o.n                        # less-than


print(Version(2) >= Version(1), Version(1) <= Version(1))   # derived operators


class Report:
    @cached_property                               # computed once per instance
    def total(self) -> int:
        print("computing...")                      # shows it runs only once
        return sum(range(100))

r = Report()                                       # new object
print(r.total, r.total)                            # second access uses the stored value

# Output:
# 1548008755920
# 1024
# 24
# int:5 list:1,2 obj:2.5
# True True
# computing...
# 4950 4950
```

## 💻 Code Example — Advanced
```python
# Production style: combine wraps + lru_cache + partial + cmp_to_key + partialmethod
import time                                        # timing decorator
from collections.abc import Callable               # function types
from functools import cmp_to_key, lru_cache, partial, partialmethod, wraps
from typing import Any, TypeVar                    # typing helpers

F = TypeVar("F", bound=Callable[..., Any])         # any callable


def timed(func: F) -> F:
    """Log how long a call took, keeping metadata."""
    @wraps(func)                                   # keep name and docstring
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()                # high-resolution clock
        try:                                       # always log, even on error
            return func(*args, **kwargs)           # run the real function
        finally:                                   # runs on success or failure
            took = (time.perf_counter() - start) * 1000   # milliseconds
            wrapper.last_ms = took                 # type: ignore[attr-defined]
    return wrapper  # type: ignore[return-value]


@timed
@lru_cache(maxsize=128)                            # bounded cache: safe for servers
def price_with_gst(amount: int, rate: int = 18) -> float:
    """Pretend this calls a slow tax service."""
    return round(amount * (1 + rate / 100), 2)


print(price_with_gst(1000), price_with_gst(1000))  # second call is a cache hit
print(price_with_gst.__name__)                     # metadata kept by wraps


def send(channel: str, to: str, text: str) -> str:
    return f"{channel}->{to}: {text}"              # fake notification sender


send_sms = partial(send, "sms")                    # fix the first argument
send_mail = partial(send, "email")                 # same function, other channel
print(send_sms("9999", "OTP 1234"))                # only two args left
print(send_mail("a@b.com", "Welcome"))


class Notifier:
    def notify(self, channel: str, text: str) -> str:
        return f"[{channel}] {text}"               # instance method

    notify_sms = partialmethod(notify, "sms")      # partial for METHODS (keeps self)


print(Notifier().notify_sms("hello"))              # [sms] hello


def by_len_then_alpha(a: str, b: str) -> int:
    """Old-style comparator: negative, zero, positive."""
    if len(a) != len(b):                           # shorter first
        return len(a) - len(b)
    return (a > b) - (a < b)                       # then alphabetical


print(sorted(["bb", "a", "ab", "c"], key=cmp_to_key(by_len_then_alpha)))
print(price_with_gst.__wrapped__.cache_info())     # inspect the inner lru_cache

# Output:
# 1180.0 1180.0
# price_with_gst
# sms->9999: OTP 1234
# email->a@b.com: Welcome
# [sms] hello
# ['a', 'c', 'ab', 'bb']
# CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python `functools` | JavaScript |
|---------|-------------------|-----------|
| Pre-fill arguments | `partial(f, a)` | `f.bind(null, a)` |
| Memoize | `@cache` / `@lru_cache` | lodash `_.memoize` or hand-made |
| Fold list | `reduce(f, xs, init)` | `xs.reduce(f, init)` (built into Array) |
| Keep wrapper metadata | `@wraps` | not needed |
| Overload by type | `@singledispatch` | `typeof` checks / TypeScript overloads |

```python
# Python way
from functools import partial
double = partial(lambda a, b: a * b, 2)            # fix a = 2
print(double(21))                                  # 42
```
```javascript
// JavaScript way
const mul = (a, b) => a * b;
const double = mul.bind(null, 2);                  // bind pre-fills arguments
console.log(double(21));                           // 42
```

Key difference: In JS, `reduce` lives on arrays and `bind` is on every function. In Python they are separate tools in `functools`, and memoization is a one-line decorator in the standard library.

---

## 🟠 FastAPI Connection
FastAPI apps use `functools` constantly: `@lru_cache` on a `get_settings()` function is the official pattern for loading config once; `@wraps` is required in custom decorators so FastAPI sees the right signature; `partial` helps build dependency callables.

```python
# FastAPI example — official settings pattern with lru_cache + Depends
from functools import lru_cache                    # cache the settings object
from fastapi import Depends, FastAPI               # app and DI
from pydantic import BaseModel                     # simple settings model

app: FastAPI = FastAPI()                           # create app


class Settings(BaseModel):
    app_name: str = "shop-api"                     # default config value


@lru_cache                                         # built once, reused on every request
def get_settings() -> Settings:
    print("loading settings")                      # appears only the first time
    return Settings()


@app.get("/info")                                  # GET /info
def info(s: Settings = Depends(get_settings)) -> dict[str, str]:
    return {"name": s.app_name}                    # same cached object each request
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Caching functions with unhashable arguments
✅ Correct: pass tuples / frozen values, not lists or dicts

```python
from functools import cache
@cache
def total(xs): return sum(xs)
# Wrong
# total([1, 2])        # TypeError: unhashable type: 'list'
# Right
print(total((1, 2)))   # 3
```

❌ Mistake 2: Using `@cache` on methods or huge input spaces in servers
✅ Correct: bound it with `lru_cache(maxsize=...)` and avoid caching `self`

```python
# Wrong — unbounded growth and keeps every `self` alive (memory leak)
# Right — @lru_cache(maxsize=1024) on module-level functions
```

❌ Mistake 3: Forgetting `@wraps` in decorators
✅ Correct: always add it

```python
from functools import wraps
def deco(f):
    @wraps(f)                                      # keeps f.__name__
    def w(*a, **k): return f(*a, **k)
    return w
@deco
def hello(): "doc"
print(hello.__name__)                              # hello (not "w")
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from functools import partial, reduce
add = partial(lambda a, b, c: a + b + c, 1)
print(add(2, 3))
print(reduce(lambda a, b: a - b, [10, 2, 3]))
print(reduce(lambda a, b: a + b, [], 0))
print(partial(int, base=2)("101"))
```
Answer: `6`; then `5` (since `(10 - 2) - 3`, reduce folds from the left); then `0` (the initializer is returned for an empty sequence, without it a `TypeError` is raised); finally `5` (`int("101", base=2)`).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `cache` and `lru_cache`?
A1: `@cache` (3.9+) is `lru_cache(maxsize=None)`: unbounded, a little faster. `@lru_cache(maxsize=N)` evicts the least recently used entry after N items, which prevents memory growth in long-running servers.

Q2: What does `partial` return?
A2: A `partial` object, a callable that remembers the function plus fixed positional and keyword arguments. Later arguments are appended; keyword arguments can be overridden.

Q3: What does `singledispatch` do?
A3: It dispatches on the type of the FIRST argument, so one function name has different implementations per type. It is Python's answer to overloading. Use `singledispatchmethod` for methods.

Q4: What does `total_ordering` need?
A4: A class that defines `__eq__` and at least one of `__lt__`, `__le__`, `__gt__`, `__ge__`. The decorator fills in the rest. It is slightly slower than hand-written methods; `dataclass(order=True)` is an alternative.

Q5: `cached_property` versus `property`?
A5: `property` runs the getter on each access. `cached_property` runs it once, stores the result in the instance `__dict__`, and later reads the stored value. It needs a writable `__dict__` (no `__slots__`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Memoizing pure, expensive functions
- Pre-filling arguments for callbacks and handlers
- Writing decorators (always `wraps`)
- Folding sequences into one value

❌ Avoid when:
- The function has side effects (caching hides them)
- Inputs are unhashable or the input space is unlimited
- A plain loop or `sum`/`max` is clearer than `reduce`

---

## 📊 Visual Diagram
```
functools
 ├─ wraps(f)            keep f's name/doc on wrapper
 ├─ cache / lru_cache   f(args) -> store -> reuse
 ├─ partial(f, a)       f(a, ...) with a pre-filled
 ├─ reduce(f, xs, i)    ((i f x1) f x2) f x3
 ├─ singledispatch      same name, behavior by type
 ├─ cached_property     compute once per object
 ├─ total_ordering      derive <=, >, >= from < and ==
 └─ cmp_to_key          old comparator -> sort key
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memoization | Store results of calls | Calls के results सहेजना |
| partial | Function with some args fixed | कुछ args तय वाला function |
| Fold / reduce | Combine items into one | Items को एक में मिलाना |
| Dispatch | Choose code by type | Type के हिसाब से code चुनना |
| Hashable | Can be a dict key | Dict key बन सकने वाला |
| Metadata | Name, doc, module of a function | Function का नाम, doc, module |

---

## ⚡ 3-Line Summary
English: `functools` offers caching (`cache`, `lru_cache`), argument pre-filling (`partial`), folding (`reduce`), decorator hygiene (`wraps`) and class helpers (`total_ordering`, `cached_property`). They are fast, tested and need no install. Use them instead of reinventing these patterns.
Hindi: `functools` caching (`cache`, `lru_cache`), arguments पहले भरना (`partial`), folding (`reduce`), decorator की सफाई (`wraps`) और class helpers (`total_ordering`, `cached_property`) देता है। ये तेज़, tested हैं और install नहीं करने पड़ते। इन patterns को दोबारा मत बनाइए।

---

## ➡️ Next Topic
**128. functools.wraps** — why every decorator needs it and what it copies.
