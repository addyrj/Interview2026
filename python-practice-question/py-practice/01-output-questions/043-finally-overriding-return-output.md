---

# Q043. finally Overriding return Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
def f() -> int:
    try:
        return 1
    finally:
        return 2

def g() -> str:
    try:
        raise ValueError("boom")
    finally:
        return "swallowed"

def h() -> list:
    x = [1]
    try:
        return x
    finally:
        x.append(2)

def k() -> int:
    n = 1
    try:
        return n
    finally:
        n = 99

print(f())
print(g())
print(h())
print(k())
```

---

## 💡 Quick Concept (2 lines only)
`finally` always runs before the function really returns. A `return` inside `finally` replaces the earlier return value and even throws away a pending exception.
हिंदी: `finally` हमेशा चलता है — उसमें `return` हो तो पुराना return और exception दोनों खत्म हो जाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def f() -> int:
    try:
        return 1              # Step 1: return value 1 is computed and parked
    finally:
        return 2              # Step 2: finally runs and its return REPLACES the parked 1

def g() -> str:
    try:
        raise ValueError("boom")  # Step 1: exception is pending
    finally:
        return "swallowed"    # Step 2: return inside finally cancels the exception

def h() -> list:
    x = [1]                   # a mutable list
    try:
        return x              # Step 1: the reference to the list is parked
    finally:
        x.append(2)           # Step 2: mutates the SAME object -> caller sees [1, 2]

def k() -> int:
    n = 1                     # an immutable int
    try:
        return n              # Step 1: value 1 is parked (already evaluated)
    finally:
        n = 99                # Step 2: rebinding the name does not change the parked value

# ============================================
# TEST CASES
# ============================================
print(f())   # Expected: 2
print(g())   # Expected: swallowed   (no ValueError escapes)
print(h())   # Expected: [1, 2]
print(k())   # Expected: 1
```

---

## 🔍 Why This Works (3 lines max)
The return value of `try` is evaluated first, then `finally` runs, and only then the function exits. A `return` in `finally` overrides everything; a mutation in `finally` is visible (same object), but rebinding a name is not. Python 3.14 emits a SyntaxWarning for `return` in `finally` (PEP 765); 3.13 stays silent.
हिंदी: `try` की value पहले तय होती है, फिर `finally` चलता है; mutate करो तो दिखता है, rebind करो तो नहीं।

---

## ⚡ Alternative Solution
```python
# finally with print + loop continue (verified on Python 3.13)
def alt() -> int:
    try:
        return 1                  # value parked
    finally:
        print("cleanup")          # runs BEFORE the caller receives 1

print(alt())   # Output: cleanup  then  1

def m() -> int:
    try:
        raise ValueError("x")     # raise
    except ValueError:
        return 1                  # except returns 1
    finally:
        print("fin")              # still runs first

print(m())     # Output: fin  then  1

def loop() -> list:
    out = []                      # collects order of events
    for i in range(3):            # three iterations
        try:
            if i == 1:
                continue          # continue still triggers finally
            out.append(i)         # normal path
        finally:
            out.append(f"f{i}")   # runs on every iteration
    return out

print(loop())  # Output: [0, 'f0', 'f1', 2, 'f2']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: return in finally hides real errors (bug becomes invisible)
def load() -> str:
    try:
        return open("missing.txt").read()   # FileNotFoundError ...
    finally:
        return "default"                    # ... silently swallowed

# ✅ Correct: use finally only for cleanup, handle errors in except
def load_ok() -> str:
    try:
        return open("missing.txt").read()
    except FileNotFoundError:
        return "default"                    # explicit and visible
```

---

## 🎯 Interview Tip (1 line)
Say: "finally runs before the function returns; never `return`/`break` inside it — it silently swallows exceptions."

---

## 🔗 Related Questions
→ Q042 (try/except/else/finally order) | Q044 (exception chaining) | Q045 (with + __exit__) | Q130 (too-broad except)
