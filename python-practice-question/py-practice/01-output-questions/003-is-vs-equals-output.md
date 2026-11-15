---

# Q003. is vs == Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b, a is b, a is c)

class AlwaysEqual:
    def __eq__(self, other):
        return True

x = AlwaysEqual()
print(x == 42, x is None, x == None)
```

---

## 💡 Quick Concept (2 lines only)
`==` asks "do these have equal VALUE?" (calls `__eq__`); `is` asks "are these the SAME object?" (compares identity, cannot be overloaded).
हिंदी: `==` value बराबर है या नहीं देखता है; `is` देखता है कि दोनों एक ही object हैं या नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: two separate lists with equal contents
a = [1, 2, 3]                           # object #1
b = [1, 2, 3]                           # object #2 (equal value, different identity)
c = a                                   # c is another name for object #1

print(a == b, a is b, a is c)           # Expected: True False True

# Step 2: a class whose __eq__ always says "equal"
class AlwaysEqual:                      # custom class overriding equality
    def __eq__(self, other):            # == calls this method
        return True                     # claims equality with anything

x = AlwaysEqual()                       # create one instance
print(x == 42, x is None, x == None)    # Expected: True False True
# x == 42   -> __eq__ -> True
# x is None -> identity check, x is not the None singleton -> False
# x == None -> __eq__ -> True  (this is why PEP 8 says use `is None`)
```

---

## 🔍 Why This Works (3 lines max)
`a == b` compares contents via `list.__eq__`, but they are two objects so `a is b` is False; `c` is just a second label for `a`. `is` compares `id()`s and can't be overridden, so `is None` is the only reliable None check.
हिंदी: `==` को class बदल सकती है, `is` को नहीं — इसलिए None के लिए हमेशा `is None`।

---

## ⚡ Alternative Solution
```python
# Show identity explicitly with id()
a = [1, 2, 3]                           # first list
b = [1, 2, 3]                           # second list
print(id(a) == id(b))                   # Expected: False  (different objects)
print(None is None)                     # Expected: True   (None is a singleton)
print([] is [])                         # Expected: False  (two new empty lists)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: comparing against None (or a value) with the wrong operator
# if x == None: ...        # can be fooled by custom __eq__ (e.g. numpy arrays, AlwaysEqual)
# if name is "admin": ...  # identity on strings: SyntaxWarning, works only by accident

# ✅ Correct
# if x is None: ...        # singleton identity check
# if name == "admin": ...  # value comparison
```

---

## 🎯 Interview Tip (1 line)
Say: "`==` is value equality via `__eq__`, `is` is identity; I use `is` only for singletons like `None`, `True`, `False`."

---

## 🔗 Related Questions
→ Q004 (small int caching) | Q007 (string interning) | Q128 (fix is vs == bug) | Q174 (is, == and interning)
