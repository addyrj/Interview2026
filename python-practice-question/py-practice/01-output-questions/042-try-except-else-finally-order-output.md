---

# Q042. try/except/else/finally order output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What does `run("ok")`, `run("err")` and `run("ret")` print?

```python
def run(mode):
    try:
        print("try")
        if mode == "err": raise ValueError("boom")
        if mode == "ret": return "from try"
    except ValueError:
        print("except")
        return "from except"
    else:
        print("else")
        return "from else"
    finally:
        print("finally")

for m in ("ok", "err", "ret"):
    print("->", run(m))
```

---

## 💡 Quick Concept (2 lines only)
`else` runs only if `try` finished without an exception AND without returning; `finally` always runs last, even on `return` or an unhandled exception.
हिंदी: `else` तभी चलता है जब try बिना error और बिना return के खत्म हो; `finally` हर हाल में चलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def run(mode: str) -> str:
    try:
        print("try")                      # always first
        if mode == "err":
            raise ValueError("boom")      # jumps to except
        if mode == "ret":
            return "from try"             # returns, but finally still runs; else is skipped
    except ValueError:
        print("except")                   # only on ValueError
        return "from except"
    else:
        print("else")                     # only when try completed normally
        return "from else"
    finally:
        print("finally")                  # runs before the function actually returns

# ============================================
# TEST CASES
# ============================================
for m in ("ok", "err", "ret"):
    print("->", run(m))
# Expected:
# try
# else
# finally
# -> from else
# try
# except
# finally
# -> from except
# try
# finally
# -> from try

def e2() -> None:
    try:
        raise KeyError("k")               # not a ValueError -> no handler matches
    except ValueError:
        print("no match")
    else:
        print("else")
    finally:
        print("finally runs, then KeyError propagates")
try:
    e2()
except KeyError as e:
    print("caught", repr(e))
# Expected:
# finally runs, then KeyError propagates
# caught KeyError('k')
```

---

## 🔍 Why This Works (3 lines max)
The return value is computed first, then `finally` executes, then the function returns. `else` is skipped when `try` exits via `return` or an exception. Exceptions raised inside `else` are NOT caught by the sibling `except`.
हिंदी: Return value पहले तय होती है, फिर `finally` चलता है, तब function वाकई return करता है।

---

## ⚡ Alternative Solution
```python
# contextlib.suppress + explicit success flag instead of else
from contextlib import suppress

with suppress(ZeroDivisionError):        # swallow only this error
    print(1 / 0)                         # raises, suppressed
print("continues")                       # Expected: continues
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: putting risky code in `else` and expecting `except` to catch it
#    try: ... / except ValueError: ... / else: int("x")  -> ValueError escapes (not run)
# ✅ Correct: keep only the code that may raise inside `try`; success-only code goes in `else`
```

---

## 🎯 Interview Tip (1 line)
Say: "try = risky code, except = handle, else = success-only code outside the handler's reach, finally = guaranteed cleanup."

---

## 🔗 Related Questions
→ Q043 (finally overriding return) | Q044 (exception chaining) | Q045 (with and __exit__) | Q130 (too-broad except bug)
