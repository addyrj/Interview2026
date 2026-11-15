---

# Q271. Mixin Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Create two reusable mixins — `JsonMixin` (adds `to_json()`) and `ReprMixin` (adds a nice `__repr__`) — and combine them into a `User` class. Show where the mixins appear in the MRO.

---

## 💡 Quick Concept (2 lines only)
A mixin is a small class that adds one behaviour via multiple inheritance; it is not meant to be used alone. Put mixins BEFORE the main base class so their methods win in the MRO.
हिंदी: Mixin एक छोटी class है जो multiple inheritance से एक extra काम जोड़ती है; इसे अकेले use नहीं करते।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import json  # Step 1: needed for to_json


class JsonMixin:  # Step 2: adds JSON export
    def to_json(self) -> str:
        return json.dumps(vars(self), sort_keys=True)  # dump instance attributes


class ReprMixin:  # Step 3: adds a generic __repr__
    def __repr__(self) -> str:
        args = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())  # k=v pairs
        return f"{type(self).__name__}({args})"  # ClassName(k=v, ...)


class Base:  # Step 4: ordinary base class
    def __init__(self, name: str, age: int) -> None:
        self.name = name  # store name
        self.age = age  # store age


class User(JsonMixin, ReprMixin, Base):  # Step 5: mixins first, base last
    pass  # no extra code - behaviour comes from the mixins


# ============================================
# TEST CASES
# ============================================
u = User("Asha", 30)  # create instance
print(u)  # Expected: User(name='Asha', age=30)
print(u.to_json())  # Expected: {"age": 30, "name": "Asha"}
print([c.__name__ for c in User.__mro__])
# Expected: ['User', 'JsonMixin', 'ReprMixin', 'Base', 'object']
```

---

## 🔍 Why This Works (3 lines max)
Python looks for methods along the MRO: `User` -> `JsonMixin` -> `ReprMixin` -> `Base` -> `object`. Mixins use only `vars(self)`, so they work with any class without knowing it.
हिंदी: Method MRO के क्रम में खोजा जाता है; mixins सिर्फ `vars(self)` पर निर्भर हैं, इसलिए किसी भी class में चलते हैं।

---

## ⚡ Alternative Solution
```python
# Mixin that cooperates with super() - safe in any order
class LoggingMixin:
    def save(self) -> str:
        return "log+" + super().save()  # call next class in the MRO


class Model:
    def save(self) -> str:
        return "saved"  # base behaviour


class Order(LoggingMixin, Model):  # mixin extends Model.save
    pass


print(Order().save())  # Expected: log+saved
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: base class listed first, so its method hides the mixin's method
class A:
    def hello(self) -> str:
        return "A"


class M:
    def hello(self) -> str:
        return "M"


class Wrong(A, M):  # A comes first -> M.hello is never used
    pass


class Right(M, A):  # mixin first -> mixin wins
    pass


print(Wrong().hello())  # Output: A
print(Right().hello())  # Output: M
```

---

## 🎯 Interview Tip (1 line)
Say: "Mixins add one focused capability, have no state of their own, go left of the base in the bases list, and use `super()` to cooperate."

---

## 🔗 Related Questions
→ Q032 (diamond MRO) | Q033 (super chain) | Q163 (explain MRO) | Q302 (MRO)
