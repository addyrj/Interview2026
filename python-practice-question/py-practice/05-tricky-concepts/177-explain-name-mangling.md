---

# Q177. Explain Name Mangling
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What does a double-underscore attribute like `self.__balance` really do? Is it private? What does the subclass example print?

---

## 💡 Quick Concept (2 lines only)
Inside a class body, `__name` (two leading underscores, not ending in two) is rewritten to `_ClassName__name`. It prevents accidental clashes in subclasses; it is not real privacy.
हिंदी: `__x` का नाम बदलकर `_ClassName__x` हो जाता है — यह security नहीं, subclass में नाम टकराव रोकने के लिए है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Account:
    def __init__(self) -> None:
        self.__balance = 100                 # stored as _Account__balance
        self._hint = "single underscore"     # only a convention, no rewriting
        self.__dunder__ = "no mangling"      # ends with __ -> NOT mangled
    def get(self) -> int:
        return self.__balance                # compiled as self._Account__balance

# ============================================
# TEST CASES
# ============================================
acc = Account()                              # create
print(acc.get())                             # Expected: 100
try:
    print(acc.__balance)                     # outside the class: no mangling applied -> name not found
except AttributeError as e:
    print("AttributeError:", e)              # Expected: AttributeError: 'Account' object has no attribute '__balance'
print(acc._Account__balance)                 # Expected: 100  (still reachable)
print(sorted(k for k in vars(acc)))          # Expected: ['_Account__balance', '__dunder__', '_hint']

class Base:
    def __init__(self) -> None:
        self.__secret = "base"               # _Base__secret
    def reveal(self) -> str:
        return self.__secret                 # _Base__secret
class Child(Base):
    def __init__(self) -> None:
        super().__init__()                   # sets _Base__secret
        self.__secret = "child"              # separate _Child__secret
c = Child()
print(c.reveal(), c._Child__secret, c._Base__secret)  # Expected: base child base
```

---

## 🔍 Why This Works (3 lines max)
The compiler rewrites `__x` to `_Class__x` only for code lexically inside the class, using the enclosing class name. So parent and child each get their own attribute, avoiding accidental overrides; anyone can still access `obj._Class__x`.
हिंदी: Compiler सिर्फ class के अंदर लिखे code में नाम बदलता है, इसलिए parent और child के attributes अलग रहते हैं।

---

## ⚡ Alternative Solution
```python
class T:
    def __x(self) -> str:                    # methods get mangled too
        return "private method"
    def call(self) -> str:
        return self.__x()                    # resolved as self._T__x()
print(T().call(), [n for n in dir(T) if "x" in n and n.startswith("_T")])  # Expected: private method ['_T__x']

# Prefer single underscore (_name) for "internal"; use __name only to protect from subclass clashes.
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assigning t.__a outside the class creates a NEW, unrelated attribute
class Tricky:
    def __init__(self) -> None:
        self.__a = 1                         # _Tricky__a
t = Tricky()
t.__a = 99                               # no mangling outside a class body
print(t.__a, t._Tricky__a)                   # Output: 99 1

# ✅ Correct: expose a property/method instead of poking at mangled names
```

---

## 🎯 Interview Tip (1 line)
Say: "Name mangling is namespacing, not privacy — Python's 'we're all consenting adults'; use `_x` for internal and `__x` only to avoid subclass collisions."

---

## 🔗 Related Questions
→ Q036 (property setter) | Q031 (inheritance & super) | Q138 (fix shared class variable state) | Q306 (dunder methods)
