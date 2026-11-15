---

# 107. __call__ Method
# हिंदी में: __call__ Method (Object को Function की तरह call करना)

---

## 🔵 Simple Definition (English)
`__call__` is a magic method. If a class defines it, you can use its objects like functions: `obj(args)` runs `obj.__call__(args)`. Such objects are called "callables" and, unlike plain functions, they can remember state between calls.

## 🔵 सरल परिभाषा (Hindi)
`__call__` एक magic method है। अगर class में यह define हो, तो उसके object को function की तरह use कर सकते हैं: `obj(args)` असल में `obj.__call__(args)` चलाता है। ऐसे objects "callable" कहलाते हैं और सामान्य function के उलट ये calls के बीच state याद रख सकते हैं।

---

## 🔴 Problem it Solves
A plain function forgets everything after it returns. If you need a function that keeps a counter, a cache, a config, or a connection, you either use a global variable (ugly, not testable) or a closure (hard to inspect or extend). A class with `__call__` gives you "a function with memory": configured once in `__init__`, used many times like a function, and still a normal object you can inspect, subclass and unit-test.

## 🔴 यह क्यों बना? (Hindi)
सामान्य function return होते ही सब भूल जाता है। अगर function को counter, cache, config या connection याद रखना है, तो global variable (गंदा, test करना मुश्किल) या closure (inspect/extend करना मुश्किल) use करना पड़ता है। `__call__` वाली class "याददाश्त वाला function" देती है: `__init__` में एक बार configure करो, function की तरह बार-बार use करो, और फिर भी वह एक normal object है जिसे inspect, subclass और test कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write class Foo with a method def __call__(self, *args)
Step 2 → You create an object: f = Foo(config)    (state is saved on self)
Step 3 → You write f(10)
Step 4 → Python looks at type(f), not at f itself, and finds __call__
Step 5 → It runs type(f).__call__(f, 10)
Step 6 → callable(f) is True because the class defines __call__

Note: a function is also just an object of class `function`
      which has its own __call__. Classes are callable too:
      Foo(config) runs type(Foo).__call__ -> the metaclass `type`.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप class Foo लिखते हो जिसमें def __call__(self, *args) है
Step 2 → Object बनाते हो: f = Foo(config)    (state self पर save होती है)
Step 3 → आप f(10) लिखते हो
Step 4 → Python f को नहीं, type(f) को देखता है और __call__ ढूंढता है
Step 5 → वह type(f).__call__(f, 10) चलाता है
Step 6 → callable(f) True होता है क्योंकि class में __call__ define है

Note: function भी बस `function` class का object है जिसका अपना __call__ है।
      Class भी callable है: Foo(config) असल में metaclass `type` का __call__ चलाता है।
```

---

## 🟡 Real World Example
Razorpay-style payment service: a `RateLimiter` object is configured once ("5 calls per minute per user") and then used like a function inside every endpoint. A `Retry` object wraps API calls to a bank with configured attempts. In ML apps, PyTorch's `nn.Module` is called like `model(x)` - that is `__call__` running `forward()` plus hooks. FastAPI's dependency system accepts class instances with `__call__`, e.g. a configurable `RoleChecker("admin")`.

## 🟡 Real Example Hindi mein
Razorpay जैसी payment service में `RateLimiter` object एक बार configure होता है ("5 calls प्रति मिनट प्रति user") और फिर हर endpoint में function की तरह use होता है। `Retry` object bank API calls को configured attempts के साथ wrap करता है। ML apps में PyTorch का `nn.Module` `model(x)` से call होता है - यह `__call__` है जो `forward()` और hooks चलाता है। FastAPI की dependency system में `__call__` वाले class instance चलते हैं, जैसे configurable `RoleChecker("admin")`।

---

## 💻 Code Example — Basic
```python
# Basic __call__ examples
class Counter:                                    # a callable object that counts its calls
    def __init__(self) -> None:                   # runs once when the object is created
        self.count: int = 0                       # state that survives between calls

    def __call__(self) -> int:                    # runs on counter()
        self.count += 1                           # update the saved state
        return self.count                         # give back the new count


class Multiplier:                                 # a configurable function
    def __init__(self, factor: int) -> None:      # factor is fixed at creation time
        self.factor: int = factor                 # store the configuration

    def __call__(self, x: int) -> int:            # runs on double(5)
        return x * self.factor                    # use stored config + argument


counter: Counter = Counter()                      # create the object
print(counter(), counter(), counter())            # call it like a function three times
print(counter.count)                              # state is a normal attribute

double: Multiplier = Multiplier(2)                # configure once
triple: Multiplier = Multiplier(3)                # another configuration
print(double(5), triple(5))                       # reuse like functions
print(list(map(double, [1, 2, 3])))               # works anywhere a function is expected
print(callable(double), callable(5), callable(len))   # callable() checks for __call__
print(double.__call__(7))                         # the explicit form of double(7)

# Output:
# 1 2 3
# 3
# 10 15
# [2, 4, 6]
# True False True
# 14
```

## 💻 Code Example — Advanced
```python
# Production style: configurable retry + rate limiter objects used as callables
import time                                       # for the sliding window
from collections import deque                     # fast pop from the left
from typing import Any, Callable                  # type hints for callables


class RateLimitError(Exception):                  # our own error type
    """Raised when a caller exceeds the allowed rate."""


class RateLimiter:
    """Allow at most `limit` calls per `window` seconds, per key."""

    def __init__(self, limit: int, window: float, clock: Callable[[], float] = time.monotonic) -> None:
        if limit <= 0 or window <= 0:             # validate configuration early
            raise ValueError("limit and window must be positive")
        self.limit: int = limit                   # max calls in a window
        self.window: float = window               # window size in seconds
        self._clock: Callable[[], float] = clock  # injectable clock makes tests easy
        self._hits: dict[str, deque[float]] = {}  # key -> timestamps of recent calls

    def __call__(self, key: str) -> None:         # limiter("user-1") raises or returns None
        now: float = self._clock()                # current time
        hits: deque[float] = self._hits.setdefault(key, deque())   # this key's history
        while hits and now - hits[0] >= self.window:   # drop timestamps outside the window
            hits.popleft()                        # O(1) removal from the left
        if len(hits) >= self.limit:               # already used the whole quota
            raise RateLimitError(f"{key}: max {self.limit} calls per {self.window}s")
        hits.append(now)                          # record this call


class Retry:
    """Callable that wraps a function and retries it on failure."""

    def __init__(self, attempts: int = 3, exceptions: tuple[type[Exception], ...] = (Exception,)) -> None:
        self.attempts: int = attempts             # how many tries in total
        self.exceptions: tuple[type[Exception], ...] = exceptions   # which errors to retry

    def __call__(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        last: Exception | None = None             # remember the last error
        for attempt in range(1, self.attempts + 1):   # 1, 2, ... attempts
            try:                                  # try the real call
                return func(*args, **kwargs)      # success: return result immediately
            except self.exceptions as exc:        # only retry the listed errors
                last = exc                        # keep it for the final raise
                print(f"attempt {attempt} failed: {exc}")   # simple logging
        assert last is not None                   # we only get here after failures
        raise last                                # give up with the last error


fake_time: list[float] = [0.0]                    # a fake clock so output is deterministic
limiter: RateLimiter = RateLimiter(2, 60.0, clock=lambda: fake_time[0])   # 2 calls/minute
limiter("u1"); limiter("u1")                      # two calls allowed
try:                                              # third call in the same window
    limiter("u1")                                 # should be blocked
except RateLimitError as e:                       # catch our error
    print("blocked:", e)                          # blocked: u1: max 2 calls per 60.0s
limiter("u2")                                     # another user has own quota
fake_time[0] = 61.0                               # time moves past the window
limiter("u1")                                     # allowed again
print("u1 allowed again")                         # proof that no error was raised

calls: list[int] = []                             # track how often the flaky function runs


def flaky_bank_api(amount: int) -> str:           # fails twice, then works
    calls.append(1)                               # count the call
    if len(calls) < 3:                            # first two calls fail
        raise ConnectionError("bank timeout")     # simulate a network problem
    return f"paid {amount}"                       # third call succeeds


retry: Retry = Retry(attempts=3, exceptions=(ConnectionError,))   # configure once
print(retry(flaky_bank_api, 500))                 # use like a function -> paid 500

# Output:
# blocked: u1: max 2 calls per 60.0s
# u1 allowed again
# attempt 1 failed: bank timeout
# attempt 2 failed: bank timeout
# paid 500
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Callable object | any class with `__call__` | functions are objects; a class instance is NOT callable |
| Function with state | class + `__call__` or closure | closure or function property (`fn.count`) |
| Check callable | `callable(x)` | `typeof x === "function"` |
| Call a class | `Foo()` (classes are callable) | `new Foo()` (`Foo()` without `new` fails) |

```python
# Python way - an object that behaves like a function
class Greeter:                                # class with state
    def __init__(self, greeting: str) -> None:   # configure once
        self.greeting: str = greeting         # saved on the object

    def __call__(self, name: str) -> str:     # makes greet("Amit") work
        return f"{self.greeting}, {name}!"    # use state + argument

greet: Greeter = Greeter("Namaste")           # create
print(greet("Amit"))                          # Namaste, Amit!
```
```javascript
// JavaScript way - closure, because instances cannot be called
const makeGreeter = (greeting) => (name) => `${greeting}, ${name}!`;  // closure keeps greeting
const greet = makeGreeter("Namaste");        // returns a function
console.log(greet("Amit"));                  // Namaste, Amit!
// A class instance is not callable: new Greeter()("Amit") -> TypeError
```

Key difference: in JavaScript, "a function with state" is almost always a closure. In Python you can choose a closure or a class with `__call__`. The class version is easier to inspect (`greet.greeting`), subclass, and test.

---

## 🟠 FastAPI Connection
FastAPI treats any callable as a dependency. A class instance with `__call__` lets you create a parametrized dependency: configure it at import time (`RoleChecker("admin")`), and FastAPI calls it on every request, injecting the parameters of `__call__` (headers, query params, etc.).

```python
# FastAPI example - parametrized dependency using __call__
from fastapi import Depends, FastAPI, Header, HTTPException   # core FastAPI pieces
from fastapi.testclient import TestClient                     # to run it without a server

app: FastAPI = FastAPI()                                      # create app


class RoleChecker:                                            # callable dependency
    def __init__(self, required: str) -> None:                # role is configured once
        self.required: str = required                         # store it

    def __call__(self, x_role: str = Header(default="guest")) -> str:   # runs per request
        if x_role != self.required:                           # compare with header value
            raise HTTPException(status_code=403, detail=f"{self.required} role needed")
        return x_role                                         # pass role to the endpoint


@app.get("/admin")                                            # GET /admin
def admin_panel(role: str = Depends(RoleChecker("admin"))) -> dict[str, str]:
    return {"welcome": role}                                  # only reached if check passed


client: TestClient = TestClient(app)                          # in-process client
print(client.get("/admin").status_code)                       # 403 (default guest)
print(client.get("/admin", headers={"X-Role": "admin"}).json())   # {'welcome': 'admin'}

# Output:
# 403
# {'welcome': 'admin'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Defining `__call__` on the instance instead of the class
✅ Correct: Python looks up `__call__` on the type, so define it in the class body

```python
class A:
    pass

a = A()
# Wrong - assigning to the instance does nothing for a(...)
a.__call__ = lambda: 1
try:
    a()
except TypeError as e:
    print(e)                      # 'A' object is not callable
# Right - define it on the class
class B:
    def __call__(self) -> int:
        return 1
print(B()())                      # 1
```

❌ Mistake 2: Forgetting that `Foo()` creates an object and does NOT call `__call__`
✅ Correct: `Foo()` runs `__init__`; `Foo()()` runs `__call__`

```python
class Foo:
    def __init__(self) -> None:
        print("init")
    def __call__(self) -> None:
        print("call")
# Wrong - expecting "call" here
f = Foo()                         # init   (only __init__ ran)
# Right
f()                               # call
```

❌ Mistake 3: Sharing mutable state at class level
✅ Correct: create the state in `__init__` so each object has its own

```python
class Bad:
    seen: list[int] = []          # shared by ALL instances
    def __call__(self, x: int) -> int:
        self.seen.append(x)
        return len(self.seen)
a, b = Bad(), Bad()
a(1)
print(b(2))                       # Wrong: 2 (b sees a's data)
class Good:
    def __init__(self) -> None:
        self.seen: list[int] = [] # per-object state
    def __call__(self, x: int) -> int:
        self.seen.append(x)
        return len(self.seen)
c, d = Good(), Good()
c(1)
print(d(2))                       # Right: 1
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def __call__(self) -> str:
        return "class"

a = A()
a.__call__ = lambda: "instance"
print(a())
print(a.__call__())
print(callable(A), callable(a))
```
Answer: `class`, then `instance`, then `True True`. Implicit calls like `a()` look up `__call__` on `type(a)` and skip the instance dictionary, so the class method runs. Only the explicit `a.__call__()` finds the instance attribute first. Every class is callable too (`callable(A)` is True) because its metaclass `type` has `__call__`, and that is what creates instances.

---

## ⚫ Interview Questions + Answers

Q1: What does `__call__` do?
A1: It makes instances callable. `obj(x)` becomes `type(obj).__call__(obj, x)`. The object can keep state in attributes and still be used wherever a function is expected (`map`, callbacks, decorators, FastAPI dependencies).

Q2: Closure vs class with `__call__` - when do you pick which?
A2: A closure is shorter for tiny, single-purpose state. A `__call__` class is better when you need several methods, inspectable attributes, inheritance, `__repr__`, or easy unit tests. Both keep state between calls.

Q3: How does `callable()` work?
A3: It returns True if the object's type defines `__call__` (functions, lambdas, classes, bound methods, and instances of classes with `__call__`). It does not check that the call will succeed.

Q4: Is `Foo()` a call to `Foo.__call__`?
A4: Not to the `__call__` you write inside Foo. It calls `type(Foo).__call__(Foo)`, i.e. the metaclass `type.__call__`, which runs `Foo.__new__` and then `Foo.__init__`. To call an instance you write `Foo()()`.

Q5: Can a decorator be a class?
A5: Yes. A class decorator-wrapper stores the function in `__init__` and runs it in `__call__`. Use `functools.update_wrapper(self, func)` to copy `__name__` and `__doc__`. Note that methods decorated this way need `__get__` to bind `self`, a known gotcha.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A function needs configuration plus state (rate limiter, retry, cache, counter)
- Building FastAPI dependencies with parameters (`RoleChecker("admin")`)
- Strategy objects passed as callbacks
- Wrapping ML models so `model(x)` feels natural

❌ Avoid when:
- A plain function does the job (no state needed)
- A short closure or `functools.partial` is enough
- A named method such as `limiter.check(key)` would be clearer for readers
- State is shared across threads without locks

---

## 📊 Visual Diagram
```
double = Multiplier(2)         double(5)
        |                          |
        v                          v
  +-----------+            type(double).__call__(double, 5)
  | factor: 2 |  <------------------+
  +-----------+                    |
   (state on self)                 v
                                  10

Foo(...)    -> type.__call__(Foo, ...) -> __new__ -> __init__  -> instance
instance(...) -> Foo.__call__(instance, ...)                   -> your result
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Callable | Anything you can call with `()` | जिसे `()` से call कर सकें |
| `__call__` | Method run on `obj()` | `obj()` पर चलने वाला method |
| Closure | Function that remembers outer variables | बाहरी variables याद रखने वाला function |
| Stateful object | Object that keeps data between calls | calls के बीच data रखने वाला object |
| Dependency | Callable FastAPI runs before the endpoint | endpoint से पहले चलने वाला callable |
| Metaclass | Class of a class (`type`) | class की class |

---

## ⚡ 3-Line Summary
English: `__call__` lets an object be called like a function, so you get a function with memory and configuration. Python looks it up on the class, not the instance. It is perfect for rate limiters, retries and FastAPI dependencies.
Hindi: `__call__` से object को function की तरह call कर सकते हैं, यानी याददाश्त और configuration वाला function मिलता है। Python इसे instance पर नहीं, class पर ढूंढता है। Rate limiter, retry और FastAPI dependencies के लिए यह बिल्कुल सही है।

---

## ➡️ Next Topic
**108. __slots__** - fix the attributes of a class to save memory and speed up attribute access, important when you create millions of small objects.
