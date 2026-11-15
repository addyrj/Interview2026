---

# Q128. Fix is vs == Comparison Bug
# Category: Fix the Bug
# Difficulty: ⭐ Easy

---

## ❓ Question
`is_admin` works in your tests with a literal `"admin"`, but returns `False` in production when the role comes from user input or a database. Find and fix the bug.

```python
# BUGGY CODE:
def is_admin_buggy(role: str) -> bool:
    return role is "admin"  # ❌ compares identity (memory address), not value
```

---

## 💡 Quick Concept (2 lines only)
`is` checks if two names point to the SAME object; `==` checks if the VALUES are equal. Equal strings built at runtime are usually different objects, so `is` fails. Use `is` only for `None`, `True`, `False`.
हिंदी: `is` identity देखता है, `==` value — strings/numbers के लिए हमेशा `==` use करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def is_admin_buggy(role: str) -> bool:
    return role is "admin"  # noqa  # identity check (Python 3.12+ warns: SyntaxWarning)

def is_admin(role: str) -> bool:
    return role == "admin"  # Step 1: compare VALUES with ==

role_from_input = "".join(["ad", "min"])  # built at runtime -> a NEW str object

# ============================================
# TEST CASES
# ============================================
print(is_admin_buggy(role_from_input))  # Expected: False  (same text, different object)
print(is_admin(role_from_input))        # Expected: True
print(is_admin("admin"), is_admin("user"))  # Expected: True False

def is_none(x: object) -> bool:
    return x is None                    # ✅ correct use of `is`: singleton None

print(is_none(None), is_none(0), is_none(""))  # Expected: True False False
```

---

## 🔍 Why This Works (3 lines max)
`==` calls `__eq__` and compares content; `is` compares `id()`. Only literals that CPython interns/caches happen to be the same object, so `is` "works" by accident in tests. Since 3.8 `x is "abc"` gives a SyntaxWarning for exactly this reason.
हिंदी: tests में `is` कभी-कभी चल जाता है (interning), production में fail होता है।

---

## ⚡ Alternative Solution
```python
# Alternative: membership test with a set (also uses ==/hash, never identity)
ROLES = {"admin", "root"}                     # allowed admin roles
role_from_input = "".join(["ad", "min"])      # runtime-built string
print(role_from_input in ROLES)               # Output: True

# Numbers: equal ints outside the small-int cache are different objects
x = int("1000")                               # runtime-built int
y = int("1000")                               # another runtime-built int
print(x is y, x == y)                         # Output: False True  (CPython 3.13)

# Lists: equal content, different objects
print([1, 2] is [1, 2], [1, 2] == [1, 2])     # Output: False True (SyntaxWarning for the literal compare is possible)

# 1 == True but 1 is not True
v = 1                                         # an int
print(v == True, v is True)                   # Output: True False
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using `is` for value comparison because it "worked" once
a = "hello"                      # literal, interned by CPython
b = "hello"                      # same literal in same module -> same object
print(a is b)                    # Output: True  (by accident, not a guarantee)

# ✅ Correct: always == for values
print(a == b)                    # Output: True  (guaranteed)
# Use `is` only for singletons: None, True, False
```

---

## 🎯 Interview Tip (1 line)
Say: "`is` is identity, `==` is equality — I use `is` only for `None` (and sentinels); interning makes `is` look correct on strings by accident."

---

## 🔗 Related Questions
→ Q003 (is vs == output) | Q004 (small integer caching) | Q007 (string interning) | Q174 (is, == and interning) | Q294 (is vs ==)
