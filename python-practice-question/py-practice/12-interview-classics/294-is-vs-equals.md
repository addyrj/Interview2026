---

# Q294. is vs ==
# Category: Interview Classics
# Difficulty: ⭐ Easy

---

## ❓ Question
What is the difference between `is` and `==`? When must you use `is`?

---

## 💡 Quick Concept (2 lines only)
`==` compares values (calls `__eq__`); `is` compares identity (same object in memory, same `id()`).
हिंदी: `==` value देखता है, `is` देखता है कि दोनों नाम एक ही object को point करते हैं या नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
a = [1, 2, 3]  # Step 1: a list
b = [1, 2, 3]  # Step 2: another list with equal content
c = a  # Step 3: alias of a

# ============================================
# TEST CASES
# ============================================
print(a == b, a is b)  # Expected: True False (equal values, different objects)
print(a == c, a is c)  # Expected: True True
print(id(a) == id(c))  # Expected: True

x = None  # singleton
print(x is None)  # Expected: True (correct way to check None)

class AlwaysEqual:  # custom __eq__
    def __eq__(self, other: object) -> bool:
        return True  # claims equality with everything

print(AlwaysEqual() == None, AlwaysEqual() is None)  # Expected: True False (== can be overridden, is cannot)

m, n = 256, 256  # small ints are cached (-5..256)
print(m is n)  # Expected: True
big1 = int("1000")  # built at runtime
big2 = int("1000")  # another runtime int
print(big1 == big2, big1 is big2)  # Expected: True False
```

---

## 🔍 Why This Works (3 lines max)
`is` compares object identity and cannot be overridden; `==` can be customised. CPython caches small ints and interns some strings, so `is` on numbers/strings may work by accident - never rely on it.
हिंदी: Value compare के लिए `==`; `is` सिर्फ None/True/False जैसे singletons के लिए।

---

## ⚡ Alternative Solution
```python
a = "hello world"  # string
b = "hello world"  # same literal in one module may be shared (implementation detail)
c = "".join(["hello", " ", "world"])  # built at runtime
print(a == c, a is c)  # Expected: True False

import sys  # explicit interning
print(sys.intern(c) is sys.intern(a))  # Expected: True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: comparing values with 'is' (works for small ints, fails for big ones;
#    Python 3.8+ also warns: SyntaxWarning "is" with a literal)
# if user_count is 1000: ...

# ✅ Correct: == for values, 'is' only for None/True/False
user_count = 1000  # value
print(user_count == 1000)  # Expected: True
print(user_count is not None)  # Expected: True
```

---

## 🎯 Interview Tip (1 line)
Say: "== asks 'same value?', is asks 'same object?'; I use `is` only for None and sentinels."

---

## 🔗 Related Questions
→ Q003 (is vs == output) | Q004 (small int caching) | Q007 (string interning) | Q174 (is, == and interning)
