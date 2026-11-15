---

# Q174. Explain is, == and Interning
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is the difference between `is` and `==`? When do two equal strings/ints share identity (interning, small-int cache)? What does this print?

---

## 💡 Quick Concept (2 lines only)
`==` compares values (calls `__eq__`); `is` compares identity (same object in memory). CPython caches small ints and interns some strings, so `is` can look right by accident.
हिंदी: `==` value देखता है, `is` same object देखता है — small int/string cache की वजह से कभी-कभी `is` गलती से सही लगता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import sys                                   # for sys.intern

a = [1, 2]                                   # Step 1: two equal lists
b = [1, 2]                                   # separate object
c = a                                        # alias of a
print(a == b, a is b, a is c)                # Expected: True False True

x = 256                                      # Step 2: small int cache (-5..256)
y = 256
print(x is y)                                # Expected: True
big1 = int("1000")                           # built at runtime -> new objects
big2 = int("1000")
print(big1 == big2, big1 is big2)            # Expected: True False

s1 = "hello"                                 # Step 3: identifier-like literals are interned
s2 = "hello"
print(s1 is s2)                              # Expected: True
p1 = "".join(["he", "llo"])                  # built at runtime -> not interned automatically
print(p1 == s1, p1 is s1)                    # Expected: True False
print(sys.intern(p1) is s1)                  # Expected: True (explicit interning)

# ============================================
# TEST CASES
# ============================================
class Odd:                                   # custom __eq__ can lie
    def __eq__(self, other: object) -> bool:
        return True                          # equal to everything
o = Odd()                                    # instance
print(o == 1, o == "x", o is None, o == None)  # Expected: True True False True
```

---

## 🔍 Why This Works (3 lines max)
`is` is a pointer comparison and cannot be overridden; `==` runs `__eq__`, which a class can customize. Small-int caching and string interning are CPython implementation details (not guaranteed by the language) — never rely on them.
हिंदी: `is` pointer compare करता है, override नहीं होता; interning CPython की implementation detail है, इस पर भरोसा मत करो।

---

## ⚡ Alternative Solution
```python
# Singletons: always compare with `is`
print(None is None, id(None) == id(None))    # Expected: True True

# Equal values but different types: == True, is False
print(1 == 1.0, 1 is 1.0)                    # Expected: True False (3.13 also prints a SyntaxWarning for `is` with a literal)

# Rule of thumb helper
def same_object(a: object, b: object) -> bool:
    return a is b                            # identity only
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using == for None (works, but custom __eq__ can fool it)
n = None
print(n == None)                             # Output: True (fragile: Odd() == None is also True)

# ✅ Correct: use `is None` / `is not None`; use == for values
print(n is None)                             # Output: True
# ❌ Also wrong: `if name is "admin":` -> use ==
```

---

## 🎯 Interview Tip (1 line)
Say: "`==` = same value, `is` = same object; use `is` only for singletons like `None`/`True`/`False`, and treat int/str caching as an implementation detail."

---

## 🔗 Related Questions
→ Q003 (is vs ==) | Q004 (small int caching) | Q007 (string interning) | Q128 (fix is vs ==) | Q294 (is vs ==)
