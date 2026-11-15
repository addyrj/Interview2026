---

# Q087. Implement Once Decorator
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write a `@once` decorator so the decorated function runs only on its **first** call. Later calls skip the function and return the **first result**. Keep `__name__`/docstring intact.

```python
@once
def init_db(name): ...
init_db("pg")     # runs
init_db("mysql")  # does NOT run, returns first result
```

---

## 💡 Quick Concept (2 lines only)
A decorator keeps state in a closure: a "called" flag plus the cached result. `nonlocal` lets the wrapper update them. Used for init/setup code.
हिंदी: Once decorator function को सिर्फ पहली बार चलाता है — बाद में पुराना result लौटाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from functools import wraps  # keep original metadata
from typing import Any, Callable  # type hints


def once(fn: Callable) -> Callable:  # decorator receives the function
    called = False  # Step 1: closure flag
    result: Any = None  # Step 2: closure storage for first result

    @wraps(fn)  # Step 3: copy __name__, __doc__
    def wrapper(*args, **kwargs):  # accept any arguments
        nonlocal called, result  # Step 4: we rebind closure variables
        if not called:  # first call only
            called = True  # mark as done
            result = fn(*args, **kwargs)  # run and store result
        return result  # always return the first result
    return wrapper  # return the wrapped function


# ============================================
# TEST CASES
# ============================================
@once
def init_db(name: str) -> str:  # sample function
    print(f"connecting to {name}")  # side effect we want only once
    return f"conn:{name}"  # value to cache


print(init_db("pg"))  # Expected: connecting to pg  then  conn:pg
print(init_db("mysql"))  # Expected: conn:pg   (no "connecting" line, args ignored)
print(init_db.__name__)  # Expected: init_db

@once
def boom():  # function that raises
    print("boom call")  # shows it ran
    raise ValueError("x")  # fails on first call


try:
    boom()  # Expected: boom call
except ValueError:
    print("raised")  # Expected: raised
print(boom())  # Expected: None  (flag already set, so it is NOT retried)
```

---

## 🔍 Why This Works (3 lines max)
The closure variables `called` and `result` live as long as the wrapper does, so they remember state between calls. `nonlocal` is needed because we assign to them.
Note: the flag is set before calling, so a failing first call is not retried.
हिंदी: closure में flag और result याद रहते हैं; assign करने के लिए nonlocal ज़रूरी है।

---

## ⚡ Alternative Solution
```python
import threading  # for a thread-safe version
from functools import wraps  # metadata


def once_safe(fn):  # thread-safe once
    lock = threading.Lock()  # guards the check + run
    done = False  # flag
    res = None  # cached value

    @wraps(fn)
    def w(*a, **k):
        nonlocal done, res
        with lock:  # only one thread enters at a time
            if not done:  # check inside the lock
                res = fn(*a, **k)  # run exactly once
                done = True  # set only after success (failure can be retried)
        return res  # same value for all callers
    return w


@once_safe
def g():
    print("g run")  # printed once even with 5 threads
    return 1


ts = [threading.Thread(target=g) for _ in range(5)]  # 5 racing threads
[t.start() for t in ts]  # start all
[t.join() for t in ts]  # wait for all  -> Expected: g run (only once)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting nonlocal
def bad_once(fn):
    called = False
    def w(*a):
        if not called:
            called = True  # ❌ makes 'called' local -> error on read
            return fn(*a)
    return w

try:
    bad_once(print)("x")
except UnboundLocalError as e:
    print("UnboundLocalError:", e)
    # cannot access local variable 'called' where it is not associated with a value

# ✅ Correct: add `nonlocal called, result` inside wrapper
```

---

## 🎯 Interview Tip (1 line)
Say: "State lives in the closure with nonlocal, @wraps keeps metadata, and I would add a lock for thread safety — and decide whether failures should be retried."

---

## 🔗 Related Questions
→ Q083 (memoize) | Q081 (debounce) | Q139 (decorator losing metadata) | Q261 (singleton)
