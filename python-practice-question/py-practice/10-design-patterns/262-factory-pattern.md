---

# Q262. Factory Pattern
# Category: DESIGN PATTERNS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a Factory that creates the right notification object (`Email`, `SMS`, `Push`) from a string, without the caller using `if/elif` or knowing concrete classes.

```python
# NOT RUN (question stub; create_notifier is defined in the solution)
n = create_notifier("sms")
n.send("hello")   # SMS: hello
```

---

## 💡 Quick Concept (2 lines only)
A factory centralises object creation behind one function/class so callers depend on an interface, not concrete classes. In Python a dict registry replaces long `if/elif` chains.
हिंदी: Factory object बनाने की ज़िम्मेदारी एक जगह रखता है — caller को concrete class जानने की ज़रूरत नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from abc import ABC, abstractmethod              # interface support

class Notifier(ABC):                             # common interface
    @abstractmethod
    def send(self, msg: str) -> str: ...         # every notifier must implement

class Email(Notifier):
    def send(self, msg: str) -> str:
        return f"Email: {msg}"                   # email behaviour

class SMS(Notifier):
    def send(self, msg: str) -> str:
        return f"SMS: {msg}"                     # sms behaviour

class Push(Notifier):
    def send(self, msg: str) -> str:
        return f"Push: {msg}"                    # push behaviour

_REGISTRY: dict[str, type[Notifier]] = {         # name -> class (no if/elif)
    "email": Email,
    "sms": SMS,
    "push": Push,
}

def create_notifier(kind: str) -> Notifier:
    try:
        return _REGISTRY[kind.lower()]()         # look up and instantiate
    except KeyError:
        raise ValueError(f"unknown notifier: {kind!r}") from None  # clean error

# ============================================
# TEST CASES
# ============================================
print(create_notifier("sms").send("hello"))      # SMS
print(create_notifier("EMAIL").send("hi"))       # case-insensitive
try:
    create_notifier("fax")                       # unknown type
except ValueError as e:
    print(e)

# Output:
# SMS: hello
# Email: hi
# unknown notifier: 'fax'
```

---

## 🔍 Why This Works (3 lines max)
The registry maps names to classes, and classes are first-class objects, so `_REGISTRY[kind]()` instantiates without branching. Adding a new notifier = one new class + one registry line (open/closed principle). Callers only know the `Notifier` interface.
हिंदी: Classes भी objects हैं, इसलिए dict में रखकर `dict[key]()` से सीधे instance बन जाता है।

---

## ⚡ Alternative Solution
```python
# Self-registering factory with __init_subclass__ + classmethod factory
class Shape:
    registry: dict[str, type["Shape"]] = {}      # shared registry

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)      # cooperate with parents
        Shape.registry[cls.__name__.lower()] = cls  # auto-register every subclass

    @classmethod
    def create(cls, name: str) -> "Shape":
        return cls.registry[name]()              # factory method

class Circle(Shape): ...                         # registered automatically
class Square(Shape): ...                         # registered automatically

print(sorted(Shape.registry))                    # what got registered
print(type(Shape.create("circle")).__name__)     # build one

# Output:
# ['circle', 'square']
# Circle
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: growing if/elif chain - must edit the factory for every new type
def create(kind):
    if kind == "email":
        return Email()
    elif kind == "sms":
        return SMS()
    # ... every new type = edit this function

# ✅ Correct: registry dict (or __init_subclass__ auto-registration)
```

---

## 🎯 Interview Tip (1 line)
Say: "Factory hides construction; in Python a dict registry or `__init_subclass__` replaces if/elif and keeps the code open for extension, closed for modification."

---

## 🔗 Related Questions
→ Q149 (complete ABC) | Q264 (strategy pattern) | Q269 (builder pattern) | Q270 (adapter pattern)
