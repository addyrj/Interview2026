---

# Q044. Exception Chaining (raise from) Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What do the three `print` lines output?

```python
try:
    try:
        int("abc")
    except ValueError as e:
        raise RuntimeError("wrapped") from e
except RuntimeError as err:
    print(repr(err), "|", repr(err.__cause__), "|", err.__suppress_context__)

try:
    try:
        1 / 0
    except ZeroDivisionError:
        raise KeyError("k")
except KeyError as err:
    print(repr(err.__context__), "|", err.__cause__, "|", err.__suppress_context__)

try:
    try:
        1 / 0
    except ZeroDivisionError:
        raise KeyError("k") from None
except KeyError as err:
    print(repr(err.__context__), "|", err.__cause__, "|", err.__suppress_context__)
```

---

## 💡 Quick Concept (2 lines only)
`raise X from Y` sets `__cause__` (explicit chain); a plain `raise` inside `except` sets only `__context__` (implicit chain). `from None` hides the context in the traceback.
हिंदी: `from e` = जानबूझकर cause; सिर्फ `raise` = अपने-आप context; `from None` = पुराना error छुपाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import sys                                    # to print tracebacks to stdout
import traceback                              # to show the chained traceback text

# Case 1: explicit chaining
try:
    try:
        int("abc")                            # Step 1: raises ValueError
    except ValueError as e:
        raise RuntimeError("wrapped") from e  # Step 2: sets __cause__ = e (and suppress_context=True)
except RuntimeError as err:
    print(repr(err), "|", repr(err.__cause__), "|", err.__suppress_context__)

# Case 2: implicit chaining
try:
    try:
        1 / 0                                 # Step 1: raises ZeroDivisionError
    except ZeroDivisionError:
        raise KeyError("k")                   # Step 2: only __context__ is set automatically
except KeyError as err:
    print(repr(err.__context__), "|", err.__cause__, "|", err.__suppress_context__)

# Case 3: suppress with from None
try:
    try:
        1 / 0
    except ZeroDivisionError:
        raise KeyError("k") from None         # Step 3: __cause__ None, __suppress_context__ True
except KeyError as err:
    print(repr(err.__context__), "|", err.__cause__, "|", err.__suppress_context__)

# ============================================
# TEST CASES (real output, Python 3.13)
# ============================================
# Line 1: RuntimeError('wrapped') | ValueError("invalid literal for int() with base 10: 'abc'") | True
# Line 2: ZeroDivisionError('division by zero') | None | False
# Line 3: ZeroDivisionError('division by zero') | None | True
```

---

## 🔍 Why This Works (3 lines max)
`from e` stores `__cause__` and flips `__suppress_context__` to True, so the traceback says "direct cause of". Without `from`, Python still stores `__context__` and prints "During handling of the above exception...". `from None` keeps `__context__` but hides it from the traceback.
हिंदी: `from` cause set करता है, बिना `from` के context अपने-आप जुड़ता है, `from None` display बंद करता है।

---

## ⚡ Alternative Solution
```python
import sys, traceback                          # to print traceback text

try:
    try:
        int("abc")                             # inner error
    except ValueError as e:
        raise RuntimeError("wrapped") from e   # explicit chain
except RuntimeError:
    traceback.print_exc(file=sys.stdout)       # prints both exceptions

# Output (file paths/line numbers vary):
# ValueError: invalid literal for int() with base 10: 'abc'
#
# The above exception was the direct cause of the following exception:
#
# RuntimeError: wrapped
#
# (implicit version prints "During handling of the above exception,
#  another exception occurred:" instead)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: losing the original error when translating exceptions
def get_port(cfg: dict) -> int:
    try:
        return int(cfg["port"])
    except (KeyError, ValueError):
        raise RuntimeError("bad config")       # implicit chain is confusing ("during handling...")

# ✅ Correct: chain explicitly so the cause is clear
def get_port_ok(cfg: dict) -> int:
    try:
        return int(cfg["port"])
    except (KeyError, ValueError) as e:
        raise RuntimeError("bad config") from e  # "direct cause" in the traceback
```

---

## 🎯 Interview Tip (1 line)
Say: "Use `raise NewError from e` when translating exceptions; `from None` only when the original is noise or sensitive."

---

## 🔗 Related Questions
→ Q042 (try/except/else/finally) | Q043 (finally overriding return) | Q130 (too-broad except) | Q260 (exception groups, add_note)
