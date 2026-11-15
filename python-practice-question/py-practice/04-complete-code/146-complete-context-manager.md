---

# Q146. Complete Context Manager
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Complete the `Transaction` context manager: it prints `commit` when the block succeeds, `rollback` when it raises, and swallows only `ValueError`.

```python
from types import TracebackType


class Transaction:
    def ____(self) -> "Transaction":               # BLANK 1: called on entering `with`
        print("begin")
        return self

    def ____(                                      # BLANK 2: called on leaving `with`
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            print("commit")
        else:
            print("rollback")
        return ____                                # BLANK 3: True only for ValueError
```

---

## 💡 Quick Concept (2 lines only)
`with` calls `__enter__` first and ALWAYS calls `__exit__` at the end; if `__exit__` returns a truthy value, the exception is suppressed.
हिंदी: `with` हमेशा `__exit__` चलाता है — अगर वह True लौटाए तो exception दब जाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from types import TracebackType                    # type for the traceback argument


class Transaction:
    def __enter__(self) -> "Transaction":          # BLANK 1: setup
        print("begin")                             # Step 1: start of the block
        return self                                # value bound by `as`

    def __exit__(                                  # BLANK 2: cleanup, always runs
        self,
        exc_type: type[BaseException] | None,      # exception class or None
        exc: BaseException | None,                 # exception instance or None
        tb: TracebackType | None,                  # traceback or None
    ) -> bool:
        if exc_type is None:                       # Step 2: no error
            print("commit")                        # success path
        else:
            print("rollback")                      # failure path
        return exc_type is not None and issubclass(exc_type, ValueError)  # BLANK 3: suppress ValueError only


# ============================================
# TEST CASES
# ============================================
with Transaction():                                # normal block
    print("work")                                  # Expected: begin / work / commit

with Transaction():                                # ValueError is swallowed
    raise ValueError("bad")                        # Expected: begin / rollback (no traceback)
print("after ValueError")                          # Expected: after ValueError

try:
    with Transaction():                            # KeyError is NOT swallowed
        raise KeyError("k")                        # Expected: begin / rollback
except KeyError as e:
    print("caught", e)                             # Expected: caught 'k'
```

---

## 🔍 Why This Works (3 lines max)
`__exit__` receives the exception details, so it can pick commit or rollback. Returning `True` suppresses the exception; returning `False`/`None` lets it propagate, which is why `KeyError` still reaches the outer `try`.
हिंदी: `__exit__` को exception की जानकारी मिलती है — True लौटाने पर दबता है, वरना आगे जाता है।

---

## ⚡ Alternative Solution
```python
# Generator-based with contextlib.contextmanager
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def transaction() -> Iterator[None]:
    print("begin")                                 # runs on enter
    try:
        yield                                      # the with-block executes here
    except ValueError:
        print("rollback")                          # swallow ValueError (no re-raise)
    except BaseException:
        print("rollback")                          # other errors: rollback ...
        raise                                      # ... and propagate
    else:
        print("commit")                            # no error

with transaction():
    raise ValueError("x")                          # Expected: begin / rollback
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: always `return True` in __exit__ -> hides EVERY bug, even KeyboardInterrupt
# ❌ Wrong: __exit__(self) without the 3 parameters -> TypeError when the block ends
# ❌ Wrong: in @contextmanager, no try/finally around yield -> cleanup skipped on error
# ✅ Correct: decide per exception type, keep the 3-argument signature
```

---

## 🎯 Interview Tip (1 line)
Say: "`__exit__` always runs, its return value decides suppression, and `@contextmanager` needs try/finally around `yield` for guaranteed cleanup."

---

## 🔗 Related Questions
→ Q045 (__exit__ suppression) | Q119 (implement context manager) | Q167 (explain context managers) | Q253 (contextlib)
