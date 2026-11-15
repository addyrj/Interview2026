---

# Q036. Property setter output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is printed, in order?

```python
class Temp:
    def __init__(self, c):
        print("init")
        self.celsius = c
    @property
    def celsius(self):
        print("get")
        return self._c
    @celsius.setter
    def celsius(self, v):
        print("set", v)
        self._c = v

t = Temp(20)
print(t.celsius)
t.celsius = 30
```

---

## 💡 Quick Concept (2 lines only)
A property is a descriptor: `obj.attr` calls the getter and `obj.attr = v` calls the setter — even inside `__init__`. The real value lives in a different name (`_c`).
हिंदी: Property पर read/write करने पर getter/setter function चलते हैं; असली value `_c` जैसे अलग नाम में रहती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Temp:
    def __init__(self, c: float) -> None:
        print("init")                 # Step 1
        self.celsius = c              # Step 2: goes through the SETTER, not a plain assign
    @property
    def celsius(self) -> float:
        print("get")                  # runs on every read
        return self._c                # backing field
    @celsius.setter
    def celsius(self, v: float) -> None:
        print("set", v)               # runs on every write
        if v < -273.15:               # validation lives here
            raise ValueError("below absolute zero")
        self._c = v                   # store in backing field

# ============================================
# TEST CASES
# ============================================
t = Temp(20)               # Expected: init, set 20
print(t.celsius)           # Expected: get, then 20
t.celsius = 30             # Expected: set 30
print(t.celsius)           # Expected: get, then 30
try:
    t.celsius = -300       # Expected: set -300
except ValueError as e:
    print("ValueError:", e)  # Expected: ValueError: below absolute zero
print(t.celsius)           # Expected: get, then 30 (old value kept)

class RO:
    @property
    def v(self) -> int:
        return 1                         # no setter defined
try:
    RO().v = 2                           # write to read-only property
except AttributeError as e:
    print("AttributeError:", e)          # Expected: AttributeError: property 'v' of 'RO' object has no setter
```

---

## 🔍 Why This Works (3 lines max)
`property` is a data descriptor stored on the class, so it takes priority over the instance `__dict__`. Without a setter, assignment raises `AttributeError`. The setter runs even in `__init__`, so validation always applies.
हिंदी: Property class पर रहती है और instance से ऊपर priority पाती है, इसलिए validation हमेशा चलती है।

---

## ⚡ Alternative Solution
```python
# Same behaviour with property() as a function (no decorators)
class T2:
    def _get(self) -> int:
        return self._v                    # getter
    def _set(self, v: int) -> None:
        self._v = v                       # setter
    value = property(_get, _set)          # attach both

t2 = T2()                                 # create
t2.value = 5                              # calls _set
print(t2.value)                           # Expected: 5
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: setter stores into the SAME name -> infinite recursion
#    @celsius.setter
#    def celsius(self, v): self.celsius = v   # RecursionError (not run)
# ❌ Wrong: redefining `def v(self, x)` without @v.setter replaces the property with a plain function
# ✅ Correct: store in self._c and use @celsius.setter
```

---

## 🎯 Interview Tip (1 line)
Say: "Properties give attribute syntax with validation and let you start with a plain attribute and add logic later without breaking callers."

---

## 🔗 Related Questions
→ Q035 (repr vs str) | Q037 (staticmethod vs classmethod) | Q162 (descriptors) | Q148 (dataclass)
