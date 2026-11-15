---

# 105. __eq__ __lt__ __gt__
# हिंदी में: Comparison Methods (बराबरी और छोटा-बड़ा तय करना)

---

## 🔵 Simple Definition (English)
These are the comparison magic methods. `__eq__` defines `==`, `__lt__` defines `<`, `__gt__` defines `>` (and `__le__`, `__ge__`, `__ne__` complete the set). They tell Python when two of your objects are equal and which one comes first when sorting.

## 🔵 सरल परिभाषा (Hindi)
ये comparison magic methods हैं। `__eq__` से `==`, `__lt__` से `<`, `__gt__` से `>` तय होता है (`__le__`, `__ge__`, `__ne__` बाकी सेट पूरा करते हैं)। ये Python को बताते हैं कि आपके दो objects कब बराबर हैं और sorting में कौन पहले आएगा।

---

## 🔴 Problem it Solves
By default, two objects are equal only if they are the exact same object in memory (`==` behaves like `is`). So `User(1, "a") == User(1, "a")` is `False`, and `sorted(users)` raises `TypeError`. You need to define what "equal" and "smaller" mean for your data: same id? same email? lowest price first? These methods encode that business rule once.

## 🔴 यह क्यों बना? (Hindi)
Default में दो objects तभी बराबर होते हैं जब memory में वही एक object हों (`==` का व्यवहार `is` जैसा)। इसलिए `User(1, "a") == User(1, "a")` `False` होता है और `sorted(users)` `TypeError` देता है। आपको तय करना होता है कि "बराबर" और "छोटा" का मतलब क्या है: same id? same email? सबसे कम price पहले? ये methods वह business rule एक बार लिख देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → a == b   calls  a.__eq__(b)
Step 2 → a < b    calls  a.__lt__(b);   a > b calls a.__gt__(b)
Step 3 → If the method returns NotImplemented, Python tries the mirror on b:
         a < b  ->  b.__gt__(a)   (reflected comparison)
Step 4 → If both fail: == falls back to identity (is); < or > raises TypeError
Step 5 → sorted(), min(), max(), list.sort() only need __lt__
Step 6 → Defining __eq__ removes the default __hash__ (set it again if hashable is needed)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → a == b   असल में  a.__eq__(b)  call करता है
Step 2 → a < b    a.__lt__(b) को;   a > b a.__gt__(b) को call करता है
Step 3 → Method NotImplemented लौटाए तो Python b पर mirror method आज़माता है:
         a < b  ->  b.__gt__(a)   (reflected comparison)
Step 4 → दोनों fail: == identity (is) पर गिरता है; < या > में TypeError
Step 5 → sorted(), min(), max(), list.sort() को सिर्फ __lt__ चाहिए
Step 6 → __eq__ लिखने पर default __hash__ हट जाता है (hashable चाहिए तो फिर से लिखें)
```

---

## 🟡 Real World Example
A Swiggy-like system sorts restaurants by rating (higher first), then by delivery time. An e-commerce platform deduplicates products by SKU (`==` compares SKU only). A job scheduler keeps tasks ordered by `(priority, created_at)`. Version numbers (`"1.10.0" > "1.9.0"`) need custom comparison because string order is wrong.

## 🟡 Real Example Hindi mein
Swiggy जैसा system restaurants को rating (ज़्यादा पहले) फिर delivery time से sort करता है। E-commerce platform products को SKU से deduplicate करता है (`==` सिर्फ SKU compare करता है)। Job scheduler tasks को `(priority, created_at)` के क्रम में रखता है। Version numbers (`"1.10.0" > "1.9.0"`) के लिए custom comparison चाहिए क्योंकि string order गलत होता है।

---

## 💻 Code Example — Basic
```python
# Basic comparison methods
class Student:                                  # simple class
    def __init__(self, name: str, marks: int) -> None:    # constructor
        self.name: str = name                   # student name
        self.marks: int = marks                 # marks

    def __eq__(self, other: object) -> bool:    # a == b
        if not isinstance(other, Student):      # different type
            return NotImplemented               # let Python try the other side
        return self.marks == other.marks        # equal if marks are equal

    def __lt__(self, other: "Student") -> bool: # a < b (needed by sorted)
        return self.marks < other.marks

    def __gt__(self, other: "Student") -> bool: # a > b
        return self.marks > other.marks

    def __repr__(self) -> str:                  # readable output
        return f"{self.name}({self.marks})"


a, b, c = Student("Asha", 90), Student("Ravi", 75), Student("Neha", 90)
print(a == c, a == b, a != b)                   # == custom, != derived from ==
print(a > b, b < a, a < c)                      # ordering
print(sorted([a, b, c]))                        # sorted needs only __lt__
print(max(a, b), min(a, b))                     # max/min use comparison
print(a == "Asha")                              # unsupported type -> False (identity fallback)

# Output:
# True False True
# True True False
# [Ravi(75), Asha(90), Neha(90)]
# Asha(90) Ravi(75)
# False
```

## 💻 Code Example — Advanced
```python
# Production style: version type with total_ordering, hash, tuple compare, key functions
from __future__ import annotations              # allow forward references
from dataclasses import dataclass, field        # dataclass tools
from functools import total_ordering            # derive the other comparisons


@total_ordering                                 # we give __eq__ and __lt__; it adds <=, >, >=
class Version:
    __slots__ = ("parts",)                      # small and fixed

    def __init__(self, text: str) -> None:
        try:
            self.parts: tuple[int, ...] = tuple(int(p) for p in text.split("."))   # "1.10.0" -> (1, 10, 0)
        except ValueError:
            raise ValueError(f"Invalid version: {text!r}") from None   # clear error

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts        # tuple equality

    def __lt__(self, other: Version) -> bool:
        return self.parts < other.parts         # tuples compare element by element

    def __hash__(self) -> int:                  # needed because we defined __eq__
        return hash(self.parts)

    def __repr__(self) -> str:
        return f"Version('{'.'.join(map(str, self.parts))}')"


print("1.10.0" > "1.9.0")                       # plain strings: WRONG answer
print(Version("1.10.0") > Version("1.9.0"))     # Version: correct
print(sorted([Version("2.0"), Version("1.10"), Version("1.9.1")]))
print(max(Version("1.2"), Version("1.10")))
print(len({Version("1.0"), Version("1.0")}))    # hash + eq -> set dedupes
try:
    Version("1.x")                              # invalid text
except ValueError as e:
    print("Error:", e)


@dataclass(order=True, frozen=True)             # dataclass generates all comparisons
class Task:
    priority: int                               # compared first (lower = more urgent)
    created: int                                # tie-breaker
    name: str = field(compare=False)            # ignored in comparisons


tasks = [Task(2, 1, "email"), Task(1, 5, "pay"), Task(1, 2, "fraud")]
print([t.name for t in sorted(tasks)])          # by (priority, created)
print(Task(1, 1, "a") == Task(1, 1, "b"))       # name is ignored -> equal

# Output:
# False
# True
# [Version('1.9.1'), Version('1.10'), Version('2.0')]
# Version('1.10')
# 1
# Error: Invalid version: '1.x'
# ['fraud', 'pay', 'email']
# True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Custom `==` | `__eq__` | Cannot overload `==` / `===` |
| Custom `<`, `>` | `__lt__`, `__gt__` | Uses `valueOf()` indirectly |
| Sorting objects | `sorted(xs)` uses `__lt__`, or `key=` | `arr.sort((a, b) => a.x - b.x)` always needs a comparator |
| Deep equality | `==` on lists/dicts/tuples is deep | `[1] == [1]` is false; need lodash `isEqual` |
| Identity | `is` | `===` for objects |

```python
# Python way
class P:
    def __init__(self, v: int) -> None:
        self.v = v
    def __eq__(self, o: object) -> bool:
        return isinstance(o, P) and self.v == o.v
    def __lt__(self, o: "P") -> bool:
        return self.v < o.v

print(P(1) == P(1), sorted([P(3), P(1)])[0].v)    # True 1
```
```javascript
// JavaScript way
class P { constructor(v) { this.v = v; } }
console.log(new P(1) === new P(1));               // false - compares identity, cannot overload
const sorted = [new P(3), new P(1)].sort((a, b) => a.v - b.v);   // comparator required
console.log(sorted[0].v);                          // 1
console.log([1, 2] == [1, 2]);                     // false (Python: True)
```

Key difference: in Python `==` is deep and customizable, so lists of objects compare by value. In JavaScript, `===` on objects always compares references and you must write comparator functions for sorting.

---

## 🟠 FastAPI Connection
Pydantic models and dataclasses already implement `__eq__` by field values, which makes endpoint tests simple (`assert response_model == expected`). Sorting results server-side also uses these methods or `key=`.

```python
# FastAPI example — sort response items using comparison on a model
from fastapi import FastAPI                     # app
from fastapi.testclient import TestClient       # test client
from pydantic import BaseModel                  # schema


class Item(BaseModel):
    name: str
    price: int

    def __lt__(self, other: "Item") -> bool:    # makes sorted(items) work
        return self.price < other.price


app: FastAPI = FastAPI()                        # create app


@app.get("/items", response_model=list[Item])   # GET /items
def items() -> list[Item]:
    data = [Item(name="pen", price=20), Item(name="bag", price=500), Item(name="ink", price=5)]
    return sorted(data)                         # uses Item.__lt__


client: TestClient = TestClient(app)            # test client
r = client.get("/items")
print([i["name"] for i in r.json()])
print(Item(name="a", price=1) == Item(name="a", price=1))    # pydantic compares by fields

# Output:
# ['ink', 'pen', 'bag']
# True
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Defining `__eq__` and forgetting `__hash__`
✅ Correct: define `__hash__` consistently (equal objects must have equal hashes)

```python
class Wrong:
    def __init__(self, v: int) -> None:
        self.v = v
    def __eq__(self, o: object) -> bool:
        return isinstance(o, Wrong) and self.v == o.v

try:
    {Wrong(1): "x"}                    # unhashable now
except TypeError as e:
    print("Error:", e)

class Right(Wrong):
    def __hash__(self) -> int:
        return hash(self.v)

print({Right(1): "x"}[Right(1)])       # x
```

❌ Mistake 2: Raising an error instead of returning `NotImplemented` for foreign types
✅ Correct: return `NotImplemented`

```python
class A:
    def __eq__(self, o: object) -> bool:
        return o.v == 1                # Wrong: AttributeError when o has no .v

try:
    A() == 5
except AttributeError as e:
    print("Error:", e)

class B:
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, B):
            return NotImplemented      # Right
        return True

print(B() == 5)                        # False
```

❌ Mistake 3: Comparing floats with `==` or an inconsistent `__lt__` / `__eq__`
✅ Correct: use `math.isclose` for floats, and keep ordering consistent with equality

```python
import math

print(0.1 + 0.2 == 0.3)                # False  <- float precision
print(math.isclose(0.1 + 0.2, 0.3))    # True
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class X:
    def __eq__(self, other: object) -> bool:
        print("X.__eq__")
        return True

class Y(X):
    def __eq__(self, other: object) -> bool:
        print("Y.__eq__")
        return False

print(X() == Y())
print(Y() == X())
print(X() == 1)
print(X() != 1)
```
Answer: First: `Y.__eq__` then `False`. If the right operand is a subclass of the left operand's type and overrides the reflected method, Python tries the right operand FIRST. Second: `Y.__eq__`, `False`. Third: `X.__eq__`, `True`. Fourth: `X.__eq__` then `False`, because `__ne__` by default inverts the result of `__eq__`.

---

## ⚫ Interview Questions + Answers

Q1: What is the minimum you must define to sort objects?
A1: Only `__lt__`. `sorted()`, `min()`, `max()` and `list.sort()` use `<`. Or skip all of it and pass `key=lambda o: o.field`.

Q2: How do you get all six comparisons with little code?
A2: `@functools.total_ordering` with `__eq__` and one ordering method, or `@dataclass(order=True)`, which compares fields as a tuple in the order they are declared.

Q3: What is the relationship between `__eq__` and `__hash__`?
A3: Equal objects must have equal hashes. If you define `__eq__` only, Python sets `__hash__` to `None` (unhashable). Mutable objects should usually stay unhashable; immutable value objects should define both.

Q4: Why does `sorted()` need `__lt__` and not `__gt__`?
A4: The sort algorithm (Timsort) is written using only `<`. If `a < b` is missing, Python also tries the reflected `b > a`, so `__gt__` alone can work, but always define `__lt__` to be safe.

Q5: `key=` vs defining comparison methods?
A5: `key=` is local and flexible (sort the same class several ways). Comparison methods define the one natural order of the type. Use `key=` first; define methods when there is a single obvious ordering.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Value objects (money, version, coordinates) compared by content
- Entities that have one natural order (priority tasks)
- You need set/dict membership by business identity

❌ Avoid when:
- The ordering depends on context - use `key=` instead
- Objects are mutable and used as dict keys (hash changes break lookups)
- Comparing unrelated types (return `NotImplemented`)

---

## 📊 Visual Diagram
```
 a == b  --> a.__eq__(b) --NotImplemented--> b.__eq__(a) --NotImplemented--> a is b
 a <  b  --> a.__lt__(b) --NotImplemented--> b.__gt__(a) --NotImplemented--> TypeError
 a != b  --> not a.__eq__(b)  (default __ne__)

 Subclass rule: if type(b) is a subclass of type(a) and overrides the method,
                b's method is tried FIRST.

 sorted(xs) ------------ uses only < -------------> __lt__
 total_ordering: from __eq__ + __lt__ it builds <=, >, >=
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__eq__` | Defines `==` | `==` तय करता है |
| `__lt__` / `__gt__` | Define `<` / `>` | `<` / `>` तय करते हैं |
| `total_ordering` | Builds missing comparisons | बाकी comparisons बनाता है |
| `NotImplemented` | "I cannot compare this type" | "इस type की तुलना मैं नहीं कर सकता" |
| Hashable | Usable in sets and as dict keys | Set/dict key बन सकने वाला |
| Natural ordering | Default order of a type | Type का default क्रम |

---

## ⚡ 3-Line Summary
English: `__eq__`, `__lt__` and `__gt__` define equality and ordering for your objects. `sorted()` needs only `__lt__`; use `total_ordering` or `dataclass(order=True)` for the rest. Define `__hash__` with `__eq__` and return `NotImplemented` for unknown types.
Hindi: `__eq__`, `__lt__` और `__gt__` आपके objects की बराबरी और क्रम तय करते हैं। `sorted()` को सिर्फ `__lt__` चाहिए; बाकी के लिए `total_ordering` या `dataclass(order=True)` लें। `__eq__` के साथ `__hash__` लिखें और अनजान types पर `NotImplemented` लौटाएं।

---

## ➡️ Next Topic
**106. `__enter__` and `__exit__` (Context Managers)** — the `with` statement: safe setup and cleanup for files, locks and database connections.
