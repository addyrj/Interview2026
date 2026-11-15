---

# Q301. Instance vs class vs static methods
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain instance methods, `@classmethod` and `@staticmethod`. Show what each receives, and give a real use for each (hint: alternative constructors).

```python
# NOT RUN (question stub)
class User: ...
User("ada", 30)                 # normal
User.from_string("ada-30")      # alternative constructor
User.is_adult(30)               # utility
```

---

## 💡 Quick Concept (2 lines only)
Instance method gets `self` (the object), classmethod gets `cls` (the class, works with inheritance), staticmethod gets nothing automatically (just a function living in the class namespace).
हिंदी: instance → `self`, classmethod → `cls`, staticmethod → कुछ नहीं; alternative constructor के लिए classmethod।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

class User:
    count = 0                                       # class-level counter

    def __init__(self, name: str, age: int) -> None:
        self.name = name                            # per-instance data
        self.age = age                              # per-instance data
        User.count += 1                             # shared across all instances

    def greet(self) -> str:                         # INSTANCE method: needs an object
        return f"Hi, {self.name}"                   # uses instance state

    @classmethod
    def from_string(cls, text: str) -> "User":      # CLASS method: gets the class
        name, age = text.split("-")                 # parse "ada-30"
        return cls(name, int(age))                  # cls (not User) so subclasses work

    @staticmethod
    def is_adult(age: int) -> bool:                 # STATIC method: no self / cls
        return age >= 18                            # pure utility, no state needed


class Admin(User):                                  # subclass to show cls behaviour
    pass


# ============================================
# TEST CASES
# ============================================

u = User("ada", 30)                                 # normal construction
print(u.greet())                                    # bound to u
print(User.greet(u))                                # same call written explicitly

v = User.from_string("bob-17")                      # alternative constructor
print(v.name, v.age)                                # parsed values
print(User.is_adult(v.age), u.is_adult(30))         # callable via class or instance

a = Admin.from_string("eve-40")                     # cls is Admin here
print(type(a).__name__, User.count)                 # right subclass, 3 users created

# Expected output:
# Hi, ada
# Hi, ada
# bob 17
# False True
# Admin 3
```

---

## 🔍 Why This Works (3 lines max)
Functions in a class are descriptors: accessing them on an instance binds `self`; `@classmethod` binds the class instead; `@staticmethod` returns the raw function unchanged. Because `from_string` uses `cls(...)`, `Admin.from_string` builds an `Admin`, not a `User`.
हिंदी: Descriptor binding से `self`/`cls` मिलता है; `cls(...)` इस्तेमाल करने से subclass भी सही बनता है।

---

## ⚡ Alternative Solution
```python
# Same alternative-constructor idea with dataclass + classmethod
from dataclasses import dataclass                   # less boilerplate

@dataclass
class Point:
    x: int                                          # field
    y: int                                          # field

    @classmethod
    def origin(cls) -> "Point":
        return cls(0, 0)                            # named constructor

    @staticmethod
    def dist(a: "Point", b: "Point") -> float:
        return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5  # helper, no state

print(Point.origin())
print(Point.dist(Point(0, 0), Point(3, 4)))

# Expected output:
# Point(x=0, y=0)
# 5.0
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting self, or calling an instance method on the class without an object
class A:
    def hello(self) -> str:
        return "hi"

try:
    A.hello()                                       # no instance to bind
except TypeError as e:
    print(e)

# ❌ Wrong: hard-coding the class in a classmethod breaks subclasses
class B:
    @classmethod
    def make(cls):
        return B()                                  # always B, even for C.make()

class C(B):
    pass

print(type(C.make()).__name__)                      # B (surprise)

# ✅ Correct: return cls() and pass an instance (or use @staticmethod if no state is needed)

# Expected output:
# A.hello() missing 1 required positional argument: 'self'
# B
```

---

## 🎯 Interview Tip (1 line)
Say: "Instance for object state, classmethod for alternative constructors/class state (uses `cls`, inheritance-friendly), staticmethod for a related utility that needs neither."

---

## 🔗 Related Questions
→ Q037 (@staticmethod vs @classmethod output) | Q028 (class vs instance variable) | Q036 (property setter) | Q306 (dunder methods)
