---

# Q098. Implement Observable
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement a minimal RxJS-style `Observable`: `Observable(subscribe_fn)` where `subscribe_fn(next, error, complete)` pushes values. Provide `.subscribe(next, error, complete)` returning a subscription with `.unsubscribe()`, plus `.map()` and `.filter()` operators. After `error`/`complete`/unsubscribe, no more values may be delivered.

```python
from_iterable([1,2,3,4,5]).filter(odd).map(x10).subscribe(print)   # 10, 30, 50
```

---

## 💡 Quick Concept (2 lines only)
An Observable is a lazy function describing how to produce values; nothing runs until `subscribe`. Operators wrap the source and return a new Observable.
हिंदी: Observable lazy होता है — subscribe करने पर ही values बहना शुरू होती हैं; map/filter नया Observable बनाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any, Callable, Generic, TypeVar  # typing helpers

T = TypeVar("T")  # value type


class Subscription:
    def __init__(self, unsubscribe: Callable[[], None]) -> None:
        self._unsubscribe = unsubscribe  # store teardown
    def unsubscribe(self) -> None:
        self._unsubscribe()  # run teardown


class Observable(Generic[T]):
    def __init__(self, subscribe_fn) -> None:
        self._subscribe_fn = subscribe_fn  # Step 1: describes HOW to produce values (lazy)

    def subscribe(self, next_fn: Callable[[T], None],
                  error_fn: Callable[[Exception], None] = lambda e: None,
                  complete_fn: Callable[[], None] = lambda: None) -> Subscription:
        closed = False  # Step 2: once True, nothing more is delivered

        def next_(v: T) -> None:
            if not closed:  # ignore values after close
                next_fn(v)

        def error_(e: Exception) -> None:
            nonlocal closed
            if not closed:
                closed = True  # error ends the stream
                error_fn(e)

        def complete_() -> None:
            nonlocal closed
            if not closed:
                closed = True  # complete ends the stream
                complete_fn()

        teardown = self._subscribe_fn(next_, error_, complete_)  # Step 3: START producing now

        def unsub() -> None:
            nonlocal closed
            closed = True  # stop delivering
            if teardown:
                teardown()  # release resources
        return Subscription(unsub)  # Step 4: handle for the caller

    def map(self, fn: Callable[[T], Any]) -> "Observable[Any]":
        return Observable(lambda n, e, c: self.subscribe(lambda v: n(fn(v)), e, c).unsubscribe)  # Step 5: new Observable

    def filter(self, pred: Callable[[T], bool]) -> "Observable[T]":
        return Observable(lambda n, e, c: self.subscribe(lambda v: n(v) if pred(v) else None, e, c).unsubscribe)


def from_iterable(items) -> Observable:  # helper source
    def sub(next_, error, complete):
        for x in items:
            next_(x)  # push each value
        complete()  # then finish
        return None  # nothing to tear down
    return Observable(sub)


# ============================================
# TEST CASES
# ============================================
obs = from_iterable([1, 2, 3, 4, 5]).filter(lambda x: x % 2 == 1).map(lambda x: x * 10)
obs.subscribe(lambda v: print("value", v), complete_fn=lambda: print("done"))
# Expected: value 10 / value 30 / value 50 / done

def boom(next_, error, complete):  # source that errors
    next_(1); error(ValueError("bad")); next_(2); complete()  # 2 and complete must be ignored


Observable(boom).subscribe(print, lambda e: print("error:", e), lambda: print("complete"))
# Expected: 1 / error: bad   (no 2, no complete)
```

---

## 🔍 Why This Works (3 lines max)
Nothing runs until `subscribe`, which calls `subscribe_fn` with guarded callbacks. The `closed` flag enforces the Rx contract: no values after error, complete or unsubscribe.
हिंदी: closed flag गारंटी देता है कि error/complete/unsubscribe के बाद कोई value नहीं आएगी।

---

## ⚡ Alternative Solution
```python
# For pull-based, synchronous streams a generator is the Pythonic tool:
def gen():
    for x in [1, 2, 3]:  # source
        yield x * 2  # lazily produced


print(list(gen()))  # Expected: [2, 4, 6]

# For async push streams use an `async def` generator + `async for`
# (consumer pulls, so there is no need for subscribe/unsubscribe).
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no `closed` guard — values arrive after complete()
class Bad:
    def __init__(self, f): self.f = f
    def subscribe(self, n, c=lambda: None): self.f(n, c)

Bad(lambda n, c: (n(1), c(), n(2))).subscribe(print)  # prints 1 then 2 — 2 came AFTER complete

# ✅ Correct: wrap callbacks with a closed flag (see solution); also run teardown on unsubscribe
```

---

## 🎯 Interview Tip (1 line)
Say: "Observable = lazy push-based stream; subscribe starts it, operators compose by wrapping, and the closed flag plus teardown enforce the contract — vs an event emitter which is eager and has no completion."

---

## 🔗 Related Questions
→ Q096 (event emitter) | Q097 (pub/sub) | Q120 (iterator class) | Q145 (complete generator) | Q263 (observer pattern)
