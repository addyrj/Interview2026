---

# Q131. Fix Bare except Swallowing KeyboardInterrupt
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
A long-running worker cannot be stopped with Ctrl+C — it just keeps going. Find and fix the bug.

```python
# BUGGY CODE:
def worker_buggy() -> str:
    n = 0                           # iteration counter
    while True:                     # long-running loop
        try:
            n += 1                  # do "work"
            if n > 5:               # finished normally
                return f"finished n={n}"
        except:                     # ❌ bare except also catches KeyboardInterrupt
            pass                    # Ctrl+C silently ignored
```

---

## 💡 Quick Concept (2 lines only)
A bare `except:` catches `BaseException` — including `KeyboardInterrupt`, `SystemExit` and `GeneratorExit`, which are NOT subclasses of `Exception`. Use `except Exception:` so Ctrl+C and `sys.exit()` still work.
हिंदी: bare `except:` Ctrl+C भी निगल जाता है — `except Exception:` use करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import os, signal, time                          # to simulate Ctrl+C (SIGINT) deterministically

def worker_buggy() -> str:
    n = 0                                        # counter
    while True:                                  # loop
        try:
            n += 1                               # work
            if n == 3:                           # at iteration 3...
                os.kill(os.getpid(), signal.SIGINT)  # ...simulate the user pressing Ctrl+C
                time.sleep(0.05)                 # give the signal handler time to raise
            if n > 5:                            # normal finish
                return f"finished n={n}"
        except:  # noqa                          # ❌ swallows KeyboardInterrupt
            pass                                 # Ctrl+C ignored

print(worker_buggy())                            # Expected: finished n=6  (Ctrl+C was ignored!)

def worker() -> str:
    n = 0                                        # counter
    try:
        while True:                              # loop
            try:
                n += 1                           # work
                if n == 3:                       # simulate Ctrl+C again
                    os.kill(os.getpid(), signal.SIGINT)
                    time.sleep(0.05)             # let the signal be delivered
                if n > 5:                        # normal finish
                    return "finished"
            except Exception:                    # Step 1: only ordinary errors
                pass                             # KeyboardInterrupt is NOT caught here
    except KeyboardInterrupt:                    # Step 2: handle shutdown at the top level
        return f"stopped cleanly at n={n}"       # graceful exit

# ============================================
# TEST CASES
# ============================================
print(worker())                                                     # Expected: stopped cleanly at n=3
print(issubclass(KeyboardInterrupt, BaseException), issubclass(KeyboardInterrupt, Exception))  # Expected: True False
print(issubclass(SystemExit, Exception), issubclass(GeneratorExit, Exception))                 # Expected: False False
```

---

## 🔍 Why This Works (3 lines max)
The hierarchy is `BaseException` -> (`Exception`, `KeyboardInterrupt`, `SystemExit`, `GeneratorExit`). `except Exception` skips the three "control-flow" exceptions, so the process can still be interrupted or exited. Catch `KeyboardInterrupt` once at the top level for graceful cleanup.
हिंदी: `KeyboardInterrupt`, `SystemExit` — `Exception` के child नहीं हैं, इसलिए `except Exception` इन्हें नहीं पकड़ता।

---

## ⚡ Alternative Solution
```python
# Alternative 1: catch BaseException ONLY to clean up, then re-raise
def alt2() -> None:
    try:
        raise KeyboardInterrupt        # simulate Ctrl+C
    except BaseException:              # catch everything for cleanup
        print("cleanup")               # release resources
        raise                          # ✅ re-raise so the interrupt still propagates

try:
    alt2()                             # run it
except KeyboardInterrupt:
    print("re-raised")                 # Output: cleanup  then  re-raised

# Alternative 2: try/finally for cleanup — no except needed
def alt3() -> None:
    try:
        raise KeyboardInterrupt        # simulate Ctrl+C
    finally:
        print("finally runs")          # always runs, interrupt keeps propagating
try:
    alt3()                             # run it
except KeyboardInterrupt:
    print("interrupt propagated")      # Output: finally runs  then  interrupt propagated
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: "except BaseException" without re-raise = same bug as bare except
def bad() -> str:
    try:
        raise KeyboardInterrupt        # Ctrl+C
    except BaseException as e:         # catches it
        return f"swallowed {type(e).__name__}"  # program cannot be stopped

print(bad())                           # Output: swallowed KeyboardInterrupt

# ✅ Correct: except Exception (or re-raise inside BaseException handlers)
```

---

## 🎯 Interview Tip (1 line)
Say: "Never use bare `except:` — `KeyboardInterrupt` and `SystemExit` derive from `BaseException`, so I catch `Exception`, or re-raise after cleanup."

---

## 🔗 Related Questions
→ Q042 (try/except/else/finally order) | Q043 (finally overriding return) | Q130 (too-broad except) | Q045 (with statement and __exit__)
