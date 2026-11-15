---

# Q045. with Statement and __exit__ Suppression Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will this code print?

```python
class Quiet:
    def __enter__(self):
        print("enter")
        return self
    def __exit__(self, et, ev, tb):
        print("exit", et.__name__ if et else None)
        return et is ValueError          # True only for ValueError

with Quiet():
    print("body")
    raise ValueError("hidden")
    print("never")
print("after 1")

try:
    with Quiet():
        raise KeyError("shown")
except KeyError as e:
    print("caught", repr(e))
```

---

## 💡 Quick Concept (2 lines only)
If `__exit__` returns a truthy value, the exception raised in the `with` body is suppressed; otherwise it propagates after `__exit__` runs. `__exit__` always runs.
हिंदी: `__exit__` में True return करो तो exception दब जाता है, वरना आगे जाता है — `__exit__` हमेशा चलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from types import TracebackType               # for type hints

class Quiet:
    def __enter__(self) -> "Quiet":
        print("enter")                        # Step 1: runs when entering the with block
        return self                           # value bound to `as` target
    def __exit__(self, et: type[BaseException] | None,
                 ev: BaseException | None,
                 tb: TracebackType | None) -> bool:
        print("exit", et.__name__ if et else None)  # Step 3: always runs, gets exception info
        return et is ValueError               # Step 4: True -> suppress, False -> re-raise

with Quiet():
    print("body")                             # Step 2: body runs
    raise ValueError("hidden")                # exception -> goes to __exit__, gets suppressed
    print("never")                            # skipped: body stops at the raise
print("after 1")                              # runs because ValueError was suppressed

try:
    with Quiet():
        raise KeyError("shown")               # __exit__ returns False -> KeyError propagates
except KeyError as e:
    print("caught", repr(e))                  # outer handler sees it

# ============================================
# TEST CASES (real output, Python 3.13)
# ============================================
# enter
# body
# exit ValueError
# after 1
# enter
# exit KeyError
# caught KeyError('shown')
```

---

## 🔍 Why This Works (3 lines max)
`with` calls `__exit__(type, value, tb)` even on error; its return value decides the fate of the exception. Falsy/None means re-raise (the default), truthy means swallow and continue after the `with`. A suppressed `return` or error in the body means code after the `raise` never runs.
हिंदी: `with` error पर भी `__exit__` बुलाता है; return value तय करती है कि exception दबेगा या आगे जाएगा।

---

## ⚡ Alternative Solution
```python
from contextlib import suppress               # stdlib helper for suppression

with suppress(ZeroDivisionError):             # suppress only this exception type
    1 / 0                                     # raises, swallowed
    print("skipped")                          # never runs
print("done")                                 # Output: done

class Bad:
    def __enter__(self): return self          # minimal enter
    def __exit__(self, *a): return True       # swallows EVERYTHING

def fn() -> str:
    with Bad():
        raise RuntimeError                    # swallowed
    return "after with"                       # execution continues here

print(fn())                                   # Output: after with
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: always returning True hides real bugs (even KeyboardInterrupt-like errors)
class Sloppy:
    def __enter__(self): return self
    def __exit__(self, *a): return True       # swallows every exception, silently

# ✅ Correct: suppress only what you intend, let the rest propagate
class Careful:
    def __enter__(self): return self
    def __exit__(self, et, ev, tb):
        return et is not None and issubclass(et, FileNotFoundError)  # narrow suppression
```

---

## 🎯 Interview Tip (1 line)
Say: "`__exit__` gets (type, value, tb); returning True suppresses the exception — do it narrowly, and prefer `contextlib.suppress` or `@contextmanager`."

---

## 🔗 Related Questions
→ Q043 (finally overriding return) | Q044 (exception chaining) | Q119 (context manager class) | Q167 (explain context managers)
