---

# Q122. Fix late binding closure bug
# Category: FIX THE BUG
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
We want three functions returning 0, 1, 2, but all return 2. Fix it.

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)      # BUG
print([f() for f in funcs])      # expected [0, 1, 2], got [2, 2, 2]
```

---

## 💡 Quick Concept (2 lines only)
Closures capture the VARIABLE `i`, not its value; they look it up when called — after the loop ended, `i == 2`.
हिंदी: Closure variable को capture करता है, value को नहीं — call के समय `i` का आखिरी मान (2) मिलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Symptom (buggy):
funcs = []                                   # list of callbacks
for i in range(3):                           # i is ONE variable, rebound each iteration
    funcs.append(lambda: i)                  # lambda reads i at call time
print([f() for f in funcs])                  # Output: [2, 2, 2]  <- BUG
print(i)                                     # Output: 2  (module-level i; inside a function it would be one shared closure cell)

# Fix: bind the current value as a default argument (evaluated NOW)
funcs = [lambda i=i: i for i in range(3)]    # i=i snapshots the value per lambda

# ============================================
# TEST CASES
# ============================================
print([f() for f in funcs])                  # Expected: [0, 1, 2]
```

---

## 🔍 Why This Works (3 lines max)
Default arguments are evaluated when the lambda is created, so each lambda stores its own copy of `i`. Without it, all lambdas read the same variable, which holds the final value.
हिंदी: `i=i` default बनाते समय value सुरक्षित कर लेता है, इसलिए हर lambda का अपना `i` होता है।

---

## ⚡ Alternative Solution
```python
# 1) functools.partial — bind the value explicitly
from functools import partial                      # stdlib
def show(i): return i                              # plain function
funcs = [partial(show, i) for i in range(3)]       # value bound at creation
print([f() for f in funcs])                        # Output: [0, 1, 2]

# 2) Factory function — new scope (and new cell) per call
def make(i):
    return lambda: i                               # captures this call's own i
funcs = [make(i) for i in range(3)]
print([f() for f in funcs])                        # Output: [0, 1, 2]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: the default-arg trick can be overridden by accident
funcs = [lambda i=i: i for i in range(3)]
print(funcs[0](99))                      # Output: 99  (extra argument replaces the snapshot)

# ✅ Better: partial or a factory function — callers can't clobber the bound value
# Also note: late binding is true for ANY free variable, not just loops:
x = 10
fs = [lambda: x for _ in range(2)]
x = 20
print([f() for f in fs])                 # Output: [20, 20]
```

---

## 🎯 Interview Tip (1 line)
Say: "Closures bind variables, not values — fix with default args, `functools.partial`, or a factory function that creates a new scope."

---

## 🔗 Related Questions
→ Q002 (late binding output) | Q161 (closures) | Q040 (global vs nonlocal) | Q041 (LEGB scope)
