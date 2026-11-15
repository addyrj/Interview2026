---

# 092. Multiple Inheritance
# हिंदी में: Multiple Inheritance (बहु-विरासत)

---

## 🔵 Simple Definition (English)
Multiple inheritance means a class has two or more parents: `class Duck(Flyer, Swimmer)`. The child gets the methods of all parents. When parents have the same method name, the parent listed first wins. Python resolves this with the MRO.

## 🔵 सरल परिभाषा (Hindi)
Multiple inheritance में class के दो या ज़्यादा parents होते हैं: `class Duck(Flyer, Swimmer)`। Child को सभी parents के methods मिलते हैं। अगर parents में एक ही नाम का method हो तो पहले लिखा हुआ parent जीतता है। Python इसे MRO से हल करता है।

---

## 🔴 Problem it Solves
Sometimes a class needs abilities from separate sources: a Duck can fly and swim; a `User` model needs JSON output, timestamps and a database base class. With single inheritance you would copy code or build a deep, unnatural chain. Multiple inheritance lets you combine small, focused classes (mixins). The danger is the diamond problem: two parents share one grandparent, so who runs first, and how many times?

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी class को अलग-अलग जगहों से abilities चाहिए: Duck उड़ भी सकती है और तैर भी; `User` model को JSON output, timestamps और database base class चाहिए। Single inheritance में code copy करना पड़ता या अजीब लंबी chain बनती। Multiple inheritance से छोटी focused classes (mixins) जोड़ी जा सकती हैं। ख़तरा diamond problem है: दो parents का एक ही grandparent हो तो कौन पहले चले और कितनी बार?

---

## 🟢 How it Works — Step by Step

```
Step 1 → `class D(B, C)` records both bases in order
Step 2 → Python builds the MRO using C3: D, B, C, A, object
Step 3 → Attribute lookup walks the MRO left to right; first match wins
Step 4 → `super()` in each class calls the NEXT class in this MRO, not 'the parent'
Step 5 → With cooperative `super().__init__()`, every class runs exactly once
Step 6 → If no consistent order exists, Python raises `TypeError` at class creation
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `class D(B, C)` दोनों bases क्रम से रखता है
Step 2 → Python C3 से MRO बनाता है: D, B, C, A, object
Step 3 → Lookup MRO में बाएँ से दाएँ चलता है; पहला match जीतता है
Step 4 → हर class का `super()` इसी MRO की अगली class बुलाता है, 'parent' नहीं
Step 5 → Cooperative `super().__init__()` से हर class ठीक एक बार चलती है
Step 6 → अगर सही क्रम बन ही न सके तो class बनते समय `TypeError` आता है
```

---

## 🟡 Real World Example
Mixins are the safe real use: `JsonMixin` adds `to_json`, `TimestampMixin` adds `created_at`, and `User(JsonMixin, TimestampMixin, Base)` combines them. SQLAlchemy models use a `TimestampMixin` with `created_at` columns. Django class-based views use `LoginRequiredMixin` plus `ListView`. A `LogMixin` wraps `save()` of any repository for auditing.

## 🟡 Real Example Hindi mein
Mixins इसका सुरक्षित असली उपयोग हैं: `JsonMixin` `to_json` जोड़ता है, `TimestampMixin` `created_at` जोड़ता है और `User(JsonMixin, TimestampMixin, Base)` सबको मिलाता है। SQLAlchemy models में `created_at` columns वाला `TimestampMixin` होता है। Django class-based views में `LoginRequiredMixin` और `ListView` साथ आते हैं। `LogMixin` किसी भी repository का `save()` audit के लिए लपेट देता है।

---

## 💻 Code Example — Basic
```python
# Basic: a class with more than one parent
class Flyer:                                      # ability 1
    def move(self) -> str:
        return "flies"

    def fly(self) -> str:
        return "flapping wings"


class Swimmer:                                    # ability 2
    def move(self) -> str:
        return "swims"

    def swim(self) -> str:
        return "paddling"


class Duck(Flyer, Swimmer):                       # two parents, left one is checked first
    pass


d: Duck = Duck()
print(d.fly(), "|", d.swim())                     # gets methods from both parents
print(d.move())                                   # conflict: Flyer wins (listed first)
print(Swimmer.move(d))                            # call the other one explicitly
print([c.__name__ for c in Duck.__mro__])         # the search order
print(Duck.__bases__ == (Flyer, Swimmer))

# Output:
# flapping wings | paddling
# flies
# swims
# ['Duck', 'Flyer', 'Swimmer', 'object']
# True
```

## 💻 Code Example — Advanced
```python
# Advanced: mixins (the safe, popular use of multiple inheritance) + cooperative super()
from __future__ import annotations
import json
from datetime import datetime, timezone


class JsonMixin:                                  # adds to_json to any class with __dict__
    def to_json(self) -> str:
        return json.dumps(self.__dict__, sort_keys=True, default=str)


class TimestampMixin:                             # adds created_at without knowing the other bases
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)         # pass the rest up the chain (cooperative)
        self.created_at: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)


class Base:
    def __init__(self, name: str) -> None:
        self.name: str = name


class User(JsonMixin, TimestampMixin, Base):      # mixins first, real base last
    pass


u = User(name="asha")
print(u.to_json())
print([c.__name__ for c in User.__mro__])


class LogMixin:
    def save(self) -> str:
        return "log>" + super().save()            # type: ignore[misc]


class Repo:
    def save(self) -> str:
        return "saved"


class AuditedRepo(LogMixin, Repo):
    pass


print(AuditedRepo().save())                       # log>saved

class A:
    def __init__(self) -> None:
        print("A")
        super().__init__()

class B(A):
    def __init__(self) -> None:
        print("B")
        super().__init__()

class C(A):
    def __init__(self) -> None:
        print("C")
        super().__init__()

class D(B, C):
    def __init__(self) -> None:
        print("D")
        super().__init__()

D()                                               # D B C A  (A only once)
try:
    class X(A, B): ...                            # inconsistent order
except TypeError as e:
    print("Error:", e)

# Output:
# {"created_at": "2026-01-01 00:00:00+00:00", "name": "asha"}
# ['User', 'JsonMixin', 'TimestampMixin', 'Base', 'object']
# log>saved
# D
# B
# C
# A
# Error: Cannot create a consistent method resolution order (MRO) for bases A, B
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Multiple parents | `class C(A, B)` | not supported |
| Workaround | not needed | mixin functions: `Object.assign` or `(Base) => class extends Base` |
| Conflict rule | MRO (left first) | last mixin wins (manual) |
| Diamond problem | solved by C3 MRO | not applicable |
| Check order | `C.__mro__` | prototype chain |

```python
# Python way
class JsonMixin:
    def to_json(self) -> str:
        import json
        return json.dumps(self.__dict__)

class Base:
    def __init__(self, name: str) -> None:
        self.name = name

class User(JsonMixin, Base):   # two parents
    pass

print(User("asha").to_json())
```
```javascript
// JavaScript way
const JsonMixin = (Base) => class extends Base {
  toJson() { return JSON.stringify(this); }
};
class Base { constructor(name) { this.name = name; } }
class User extends JsonMixin(Base) {}   // mixin factory
console.log(new User("asha").toJson());
```

Key difference: JavaScript allows only one `extends`, so mixins are written as functions that return classes. Python supports several parents directly and orders them with C3 linearization, which means order of bases matters.

---

## 🟠 FastAPI Connection
You meet multiple inheritance in SQLAlchemy (mixins like `TimestampMixin` before `Base`) and in Pydantic (combining models). The example below runs a SQLAlchemy 2.0 model with a mixin, and shows that mixins go before the declarative base.

```python
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase): ...


class TimestampMixin:                             # shared columns via mixin
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(User(name="asha")); s.commit()
    u = s.scalars(select(User)).one()
    print(u.name, u.created_at is not None, [c.__name__ for c in User.__mro__[:3]])

# Output:
# asha True ['User', 'TimestampMixin', 'Base']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming both parents' `__init__` run automatically
✅ Correct: use cooperative `super().__init__()` in every class

```python
class X:
    def __init__(self) -> None:
        print("X")
class Y:
    def __init__(self) -> None:
        print("Y")
class Z(X, Y):
    pass
Z()                          # Wrong: only X runs
class X2:
    def __init__(self) -> None:
        print("X2"); super().__init__()
class Y2:
    def __init__(self) -> None:
        print("Y2"); super().__init__()
class Z2(X2, Y2):
    pass
Z2()                         # Right: X2 then Y2
```

❌ Mistake 2: Putting the base class before mixins
✅ Correct: mixins first, concrete base last

```python
class Mixin:
    def hello(self) -> str:
        return "mixin"
class Base:
    def hello(self) -> str:
        return "base"
class Wrong(Base, Mixin): ...
class Right(Mixin, Base): ...
print(Wrong().hello(), Right().hello())
```

❌ Mistake 3: Mixing parents in an impossible order
✅ Correct: keep the same order everywhere

```python
class A: ...
class B(A): ...
try:
    class Bad(A, B): ...     # Wrong: parent before its child
except TypeError as e:
    print("Error:", e)
class Good(B, A): ...        # Right: child first
print([c.__name__ for c in Good.mro()])
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def f(self): return "A"
class B(A):
    pass
class C(A):
    def f(self): return "C"
class D(B, C):
    pass
class E(C, B):
    pass
print(D().f(), E().f())
class X:
    def __init__(self): print("X")
class Y:
    def __init__(self): print("Y")
class Z(X, Y):
    pass
Z()
```

Output:
```
C C
X
```

Answer: Many expect `D().f()` to return `A` because B inherits from A. But the MRO of D is D, B, C, A, object. B has no `f` of its own, so the search continues to C, which defines it; A comes after C. So both D and E return `C`. For Z, Python finds `__init__` in X first and runs only that, because X's init does not call `super().__init__()`; Y's init never runs. Output: `C C` then `X`.

---

## ⚫ Interview Questions + Answers

Q1: What is multiple inheritance?
A1: A class with more than one parent. It receives methods and attributes from all of them, searched in the order given by the MRO.

Q2: What is the diamond problem and how does Python solve it?
A2: When B and C both inherit from A and D inherits from B and C, A's method could run twice or be ambiguous. Python's C3 linearization produces a single consistent order (D, B, C, A) and `super()` calls each class once.

Q3: What is a mixin?
A3: A small class that adds one focused ability (JSON output, logging, timestamps) and is not meant to be used alone. Put mixins before the main base class in the bases list.

Q4: Why does `super()` not always mean 'the parent'?
A4: `super()` returns the next class after the current one in the MRO of the object's real type. In a diamond, `super()` inside B can call C, not A.

Q5: When would you avoid multiple inheritance?
A5: When parents have overlapping state or methods, when you cannot guarantee cooperative `super()` use, or when composition (holding another object) is simpler. Keep mixins stateless.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Adding independent, stateless abilities with mixins
- Framework patterns that expect it (Django views, SQLAlchemy mixins)
- Combining Pydantic models for shared fields
- Cooperative classes designed with `super()` everywhere

❌ Avoid when:
- Parents with the same method names and different meanings
- Complex diagrams where you must trace the MRO by hand
- When composition (HAS-A) expresses the idea better
- Parents that keep their own conflicting state

---

## 📊 Visual Diagram
```
      JsonMixin   TimestampMixin     Base
          \            |             /
           \           |            /
            +--------- User --------+

User.__mro__ = User -> JsonMixin -> TimestampMixin -> Base -> object

Diamond:        A
              /   \
             B     C
              \   /
                D      MRO: D, B, C, A, object
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multiple inheritance | Class with several parents | कई parents वाली class |
| Mixin | Small add-on ability class | छोटी add-on class |
| Diamond problem | Shared grandparent confusion | साझा grandparent की उलझन |
| C3 linearization | Algorithm that orders the MRO | MRO का क्रम तय करने वाला algorithm |
| Cooperative super | Every class calls super() | हर class का super() बुलाना |
| Method conflict | Same name in two parents | दो parents में एक नाम |

---

## ⚡ 3-Line Summary
English: Multiple inheritance gives a class several parents; the left-most parent wins on conflicts via the MRO. Use it mainly for small stateless mixins placed before the base. Make every class call `super().__init__()` so each runs once.
Hindi: Multiple inheritance में class के कई parents होते हैं; टकराव पर MRO से सबसे बाएँ वाला parent जीतता है। इसे मुख्यतः छोटे stateless mixins के लिए इस्तेमाल करें और base से पहले रखें। हर class `super().__init__()` बुलाए ताकि हर एक सिर्फ एक बार चले।

---

## ➡️ Next Topic
**093. MRO — Method Resolution Order** — how Python orders classes with C3, how `super()` uses it, and how to debug it.
