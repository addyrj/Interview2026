---

# Q129. Fix Shadowing Built-ins Bug
# Category: Fix the Bug
# Difficulty: ⭐ Easy

---

## ❓ Question
Code that worked yesterday now fails with `TypeError: 'list' object is not callable`. Someone added a variable earlier in the file. Find and fix the bug.

```python
# BUGGY CODE:
list = [3, 1, 2]  # ❌ module-level variable named after the built-in `list`

def unique(items: tuple[int, ...]) -> "list[int]":
    return sorted(list(set(items)))  # `list` is now our variable, not the type

unique((1, 1, 2))  # TypeError: 'list' object is not callable
```

---

## 💡 Quick Concept (2 lines only)
Built-in names (`list`, `sum`, `id`, `type`, `max`...) live in the outermost scope (LEGB "B"). Assigning to the same name in your module or function hides the built-in for that scope. Rename your variable.
हिंदी: अपना variable `list`/`sum`/`id` नाम से बनाओगे तो built-in छिप जाता है — नाम बदलो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

list = [3, 1, 2]  # ❌ shadows built-in list at module level

try:
    print(list("abc"))                  # call the "built-in"... it is a list now
except TypeError as e:                  # catch the crash
    print("TypeError:", e)              # Expected: TypeError: 'list' object is not callable

del list                                # Step 1: delete our name -> built-in visible again
print(list("abc"))                      # Expected: ['a', 'b', 'c']

# Step 2: real fix — use descriptive names, never built-in names
def stats(nums: list[int]) -> tuple[int, int]:
    positives = [n for n in nums if n > 0]   # NOT named `list`
    return len(positives), sum(positives)    # len and sum still work

# ============================================
# TEST CASES
# ============================================
print(stats([1, -2, 3]))    # Expected: (2, 4)
print(stats([]))            # Expected: (0, 0)

# The same trap with sum:
sum = 0                      # ❌ shadows built-in sum
try:
    print(sum([1, 2]))       # tries to call an int
except TypeError as e:       # catch
    print("TypeError:", e)   # Expected: TypeError: 'int' object is not callable
del sum                      # restore built-in sum
```

---

## 🔍 Why This Works (3 lines max)
Name lookup goes Local -> Enclosing -> Global -> Built-in; your assignment creates a name in an earlier scope, so the built-in is never reached. `del name` removes yours and the built-in becomes visible again. Linters (ruff `A001`/`A002`) catch this automatically.
हिंदी: lookup LEGB order में होता है — तुम्हारा नाम पहले मिल जाता है, built-in तक पहुँचता ही नहीं।

---

## ⚡ Alternative Solution
```python
# Alternative 1: trailing underscore (PEP 8 convention) for unavoidable names
def make_key(id_: int, type_: str) -> str:   # id_ and type_ avoid shadowing
    return f"{type_}:{id_}"                  # build the key

print(make_key(1, "user"))                   # Output: user:1

# Alternative 2: reach the real built-in explicitly if you must shadow
import builtins                              # module holding all built-ins
print(builtins.list("ab"))                   # Output: ['a', 'b']

# Function parameters can shadow too (legal but a bad habit)
def f(id: int) -> int:                       # `id` shadows built-in inside f only
    return id                                # works, but hides id() in this body
print(f(5))                                  # Output: 5
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using a built-in name locally BEFORE assigning it -> UnboundLocalError
def h() -> None:
    print(len("abc"))   # Python sees `len` assigned below, so it is LOCAL here
    len = 5             # makes `len` a local variable for the WHOLE function

try:
    h()                 # call it
except UnboundLocalError as e:
    print("UnboundLocalError:", e)  # Output: UnboundLocalError: cannot access local variable 'len' where it is not associated with a value

# ✅ Correct: pick a different name, e.g. `length = 5`
```

---

## 🎯 Interview Tip (1 line)
Say: "Never name variables after built-ins — I use descriptive names or a trailing underscore, and run ruff/flake8-builtins to catch it."

---

## 🔗 Related Questions
→ Q040 (global vs nonlocal) | Q041 (LEGB scope) | Q121 (mutable default argument bug) | Q179 (comprehension scoping)
