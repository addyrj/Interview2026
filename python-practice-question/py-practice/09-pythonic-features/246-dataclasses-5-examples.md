---

# Q246. dataclasses — 5 Examples
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 5 `@dataclass` features: basic auto methods, defaults with `field(default_factory=...)`, `frozen=True`, `__post_init__`, and `order=True` / `asdict`.

---

## 💡 Quick Concept (2 lines only)
`@dataclass` generates `__init__`, `__repr__` and `__eq__` from type-annotated fields. Mutable defaults must use `field(default_factory=...)`.
हिंदी: `@dataclass` annotations देखकर `__init__`, `__repr__`, `__eq__` खुद बना देता है — mutable default के लिए `default_factory`।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from dataclasses import dataclass, field, asdict      # Step 1: imports

@dataclass                                            # Example 1: basic
class User:                                           # simple record
    name: str                                         # required field
    age: int = 0                                      # field with default

u = User("Ana", 30)                                   # __init__ generated
print(u)                                              # Expected: User(name='Ana', age=30)
print(u == User("Ana", 30))                           # Expected: True  (__eq__ compares fields)

@dataclass                                            # Example 2: mutable default
class Team:                                           # team has a list of members
    members: list[str] = field(default_factory=list)  # NEW list per instance
t1, t2 = Team(), Team()                               # two teams
t1.members.append("x")                                # mutate only t1
print(t1.members, t2.members)                         # Expected: ['x'] []

@dataclass(frozen=True)                               # Example 3: immutable (and hashable)
class Point:                                          # frozen point
    x: int                                            # x
    y: int                                            # y
p = Point(1, 2)                                       # create
try:                                                  # try to mutate
    p.x = 5                                           # not allowed
except Exception as e:                                # FrozenInstanceError
    print(type(e).__name__)                           # Expected: FrozenInstanceError
print({p: "ok"})                                      # Expected: {Point(x=1, y=2): 'ok'} (hashable)

@dataclass                                            # Example 4: __post_init__
class Rect:                                           # rectangle
    w: int                                            # width
    h: int                                            # height
    area: int = field(init=False)                     # computed, not an init arg
    def __post_init__(self) -> None:                  # runs after __init__
        self.area = self.w * self.h                   # derive area
print(Rect(3, 4))                                     # Expected: Rect(w=3, h=4, area=12)

@dataclass(order=True)                                # Example 5: ordering + asdict
class Ver:                                            # version tuple
    major: int                                        # compared first
    minor: int                                        # compared second
print(Ver(1, 2) < Ver(1, 10))                         # Expected: True
print(asdict(u))                                      # Expected: {'name': 'Ana', 'age': 30}

# ============================================
# TEST CASES
# ============================================
print(sorted([Ver(2, 0), Ver(1, 5), Ver(1, 1)]))      # Expected: [Ver(major=1, minor=1), Ver(major=1, minor=5), Ver(major=2, minor=0)]
```

---

## 🔍 Why This Works (3 lines max)
The decorator reads `__annotations__` and writes methods onto the class. `frozen=True` blocks `__setattr__` and (with `eq=True`) adds `__hash__`. `order=True` compares fields as a tuple in declaration order.
हिंदी: Decorator annotations पढ़कर methods जोड़ता है — `frozen` से immutable + hashable, `order` से तुलना।

---

## ⚡ Alternative Solution
```python
# slots=True (3.10+) saves memory; kw_only=True forces keyword args
from dataclasses import dataclass                     # import decorator

@dataclass(slots=True, kw_only=True)                  # no __dict__, keyword-only init
class Cfg:                                            # config record
    host: str                                         # required
    port: int = 8000                                  # default
c = Cfg(host="localhost")                             # must use keywords
print(c)                                              # Expected: Cfg(host='localhost', port=8000)
print(hasattr(c, "__dict__"))                         # Expected: False (slots in use)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: mutable default -> ValueError at class definition
from dataclasses import dataclass, field              # imports
try:                                                  # catch the error
    @dataclass                                        # decorate
    class Bad:                                        # buggy class
        items: list = []                              # shared mutable default!
except ValueError as e:                               # dataclass refuses it
    print(e)                                          # Expected: mutable default <class 'list'> for field items is not allowed: use default_factory

# ✅ Correct
@dataclass                                            # decorate
class Good:                                           # fixed class
    items: list = field(default_factory=list)         # new list each time
print(Good())                                         # Expected: Good(items=[])
```

---

## 🎯 Interview Tip (1 line)
Say: "dataclass removes boilerplate; I use `frozen=True` for hashable value objects, `default_factory` for mutable defaults and `slots=True` to cut memory."

---

## 🔗 Related Questions
→ Q001 (mutable default argument) | Q034 (__eq__ without __hash__) | Q035 (__repr__ vs __str__) | Q118 (immutable dict)
