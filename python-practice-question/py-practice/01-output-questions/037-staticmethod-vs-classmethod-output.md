---

# Q037. @staticmethod vs @classmethod output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What does this print? Which class does `cls` refer to?

```python
class Pizza:
    base = "thin"
    def __init__(self, size): self.size = size
    @classmethod
    def big(cls):
        print("cls =", cls.__name__)
        return cls(16)
    @staticmethod
    def area(r): return round(3.14159 * r * r, 2)

class Veg(Pizza):
    base = "thick"

v = Veg.big()
print(type(v).__name__, Pizza.area(2))
```

---

## 💡 Quick Concept (2 lines only)
`@classmethod` receives the class it was called on (`cls`, subclass-aware); `@staticmethod` receives nothing extra and is just a function in the class namespace.
हिंदी: classmethod को class मिलती है (subclass भी), staticmethod को कुछ नहीं मिलता — वह सिर्फ़ namespace में रखा function है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Pizza:
    base = "thin"                          # class attribute
    def __init__(self, size: int) -> None:
        self.size = size                   # instance state
    def info(self) -> str:
        return f"instance {self.size} {self.base}"  # needs self
    @classmethod
    def big(cls) -> "Pizza":
        print("classmethod cls =", cls.__name__)    # shows which class called it
        return cls(16)                     # factory: builds the right subclass
    @staticmethod
    def area(r: float) -> float:
        return round(3.14159 * r * r, 2)   # no self/cls needed

class Veg(Pizza):
    base = "thick"                         # override class attribute

# ============================================
# TEST CASES
# ============================================
v = Veg.big()                    # Expected: classmethod cls = Veg
print(type(v).__name__, v.info())  # Expected: Veg instance 16 thick
print(Pizza.area(2), v.area(2))  # Expected: 12.57 12.57
print(Pizza.big().size)          # Expected: classmethod cls = Pizza, then 16
print(Pizza.info(Pizza(8)))      # Expected: instance 8 thin
try:
    Pizza.info()                 # plain method called on class, no instance
except TypeError as e:
    print("TypeError:", e)       # Expected: TypeError: Pizza.info() missing 1 required positional argument: 'self'
```

---

## 🔍 Why This Works (3 lines max)
`Veg.big()` binds `cls` to `Veg`, so `cls(16)` builds a `Veg` — a plain `Pizza(16)` would not. Static methods are never bound, so they work the same via class or instance.
हिंदी: `cls(...)` से subclass का object बनता है, इसलिए classmethod alternative constructors के लिए बेस्ट है।

---

## ⚡ Alternative Solution
```python
# Alternative constructor pattern (very common in interviews)
from datetime import date

class Person:
    def __init__(self, name: str, year: int) -> None:
        self.name, self.year = name, year      # store
    @classmethod
    def from_string(cls, s: str) -> "Person":
        name, year = s.split("-")              # parse "Ann-1990"
        return cls(name, int(year))            # cls keeps subclass support

print(Person.from_string("Ann-1990").year)     # Expected: 1990
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: hardcoding the class in a factory -> subclasses get the wrong type
#    @staticmethod
#    def big(): return Pizza(16)     # Veg.big() returns Pizza (not run)
# ✅ Correct: use @classmethod and return cls(...)
```

---

## 🎯 Interview Tip (1 line)
Say: "Instance method gets `self`, classmethod gets `cls` (alternative constructors, subclass-aware), staticmethod gets nothing (a namespaced utility)."

---

## 🔗 Related Questions
→ Q028 (class vs instance variable) | Q036 (property setter) | Q301 (instance vs class vs static) | Q262 (factory pattern)
