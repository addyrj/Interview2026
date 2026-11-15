---

# 170. __dict__ attribute
# हिंदी में: __dict__ attribute (attributes का भंडार)

---

## 🔵 Simple Definition (English)
`__dict__` is the dictionary where Python stores an object's attributes. Writing `u.name = "Asha"` simply adds the key `"name"` to `u.__dict__`. Classes have their own `__dict__` (read-only view) that holds methods and class attributes.

## 🔵 सरल परिभाषा (Hindi)
`__dict__` वह dictionary है जिसमें Python किसी object के attributes रखता है। `u.name = "Asha"` लिखना असल में `u.__dict__` में key `"name"` जोड़ना है। Classes का अपना `__dict__` (read-only view) होता है जिसमें methods और class attributes रहते हैं।

---

## 🔴 Problem it Solves
Python objects are dynamic: you can add attributes at any time. A simple, fast, flexible way to do this is a per-object dictionary. Understanding `__dict__` explains why attribute lookup works the way it does, why instance values shadow class values, how `pickle`/`copy` save objects, and why millions of small objects use too much memory (and when `__slots__` helps).

## 🔴 यह क्यों बना? (Hindi)
Python objects dynamic हैं: आप कभी भी attributes जोड़ सकते हैं। इसका सरल, तेज़ और लचीला तरीका हर object के लिए एक dictionary है। `__dict__` समझने से पता चलता है कि attribute lookup ऐसे क्यों चलता है, instance की values class की values को क्यों ढक देती हैं, `pickle`/`copy` objects कैसे save करते हैं, और लाखों छोटे objects ज़्यादा memory क्यों लेते हैं (और `__slots__` कब काम आता है)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Each normal instance gets its own dict at creation: obj.__dict__
Step 2 → self.x = 1 stores {"x": 1} in that dict
Step 3 → Reading obj.x searches in this order:
           a. data descriptors on the class (property with setter, etc.)
           b. obj.__dict__
           c. class and parents (methods, class attributes, non-data descriptors)
           d. __getattr__ if defined
Step 4 → Class __dict__ is a mappingproxy: read-only, edit with setattr(Class, ...)
Step 5 → __slots__ removes the per-instance dict and uses fixed storage (less memory)
Step 6 → Python 3.11+ can store instance values inline without a real dict until you ask for __dict__
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर सामान्य instance को बनते समय अपना dict मिलता है: obj.__dict__
Step 2 → self.x = 1 उस dict में {"x": 1} रखता है
Step 3 → obj.x पढ़ने पर खोज इस क्रम में होती है:
           a. class के data descriptors (setter वाला property आदि)
           b. obj.__dict__
           c. class और parents (methods, class attributes, non-data descriptors)
           d. __getattr__ अगर परिभाषित हो
Step 4 → Class का __dict__ mappingproxy है: read-only, बदलने के लिए setattr(Class, ...)
Step 5 → __slots__ हर instance का dict हटाकर तय जगह इस्तेमाल करता है (कम memory)
Step 6 → Python 3.11+ में जब तक आप __dict__ न माँगें, values बिना असली dict के inline रखी जा सकती हैं
```

---

## 🟡 Real World Example
A game server keeps 2 million `Particle` objects. Each normal object carries a dict, so memory explodes; adding `__slots__ = ("x", "y")` cuts memory a lot. A caching layer saves objects by dumping `obj.__dict__` to JSON and restores them using `cls.__new__(cls)` plus `__dict__.update(data)`, the same idea `pickle` and ORMs use.

## 🟡 Real Example Hindi mein
Game server में 20 लाख `Particle` objects हैं। हर सामान्य object एक dict ढोता है, इसलिए memory बहुत बढ़ती है; `__slots__ = ("x", "y")` जोड़ने से memory काफी घटती है। Caching layer `obj.__dict__` को JSON में डालकर objects save करती है और `cls.__new__(cls)` व `__dict__.update(data)` से वापस बनाती है, यही idea `pickle` और ORMs भी इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic __dict__ examples
class User:
    role: str = "guest"                           # class attribute -> User.__dict__

    def __init__(self, name: str) -> None:
        self.name: str = name                     # instance attribute -> u.__dict__


u: User = User("Asha")
print(u.__dict__)                                 # {'name': 'Asha'}
u.age = 30                                        # adding an attribute = adding a dict key
print(u.__dict__)                                 # {'name': 'Asha', 'age': 30}
u.__dict__["city"] = "Pune"                       # writing the dict directly also works
print(u.city)                                     # Pune
print("role" in u.__dict__, "role" in User.__dict__)   # False True
print(sorted(k for k in User.__dict__ if not k.startswith("__")))   # dunder names hidden -> ['role']
print(type(User.__dict__).__name__)               # mappingproxy (read-only view)
try:
    User.__dict__["x"] = 1                        # cannot write class dict directly
except TypeError as e:
    print("TypeError:", e)
u.role = "admin"                                  # instance attribute shadows the class one
print(u.role, User.role)                          # admin guest

# Output:
# {'name': 'Asha'}
# {'name': 'Asha', 'age': 30}
# Pune
# False True
# ['role']
# mappingproxy
# TypeError: 'mappingproxy' object does not support item assignment
# admin guest
```

## 💻 Code Example — Advanced
```python
# Production style: attribute lookup order, slots memory, to/from dict, key-sharing
import sys                                        # sizes
from typing import Any                            # typing


class Base:
    x: str = "class-x"                            # found only if instance lacks x


class Child(Base):
    pass


c: Child = Child()
print(c.x)                                        # class-x  (Child -> Base)
c.x = "inst-x"                                    # instance dict wins over class attribute
print(c.x, Base.x, c.__dict__)                    # inst-x class-x {'x': 'inst-x'}


class Desc:
    """Data descriptor: wins over the instance __dict__."""

    def __get__(self, obj: Any, owner: type) -> str:
        return "from-descriptor"

    def __set__(self, obj: Any, value: Any) -> None:
        obj.__dict__["shadow"] = value            # store somewhere else


class WithDesc:
    d = Desc()                                    # data descriptor on the class


w: WithDesc = WithDesc()
w.__dict__["d"] = "in-dict"                       # try to hide the descriptor
print(w.d)                                        # from-descriptor (data descriptor has priority)


class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y


class SlotPoint:
    __slots__ = ("x", "y")                        # no __dict__ -> smaller objects

    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y


p, sp = Point(1, 2), SlotPoint(1, 2)
print(hasattr(p, "__dict__"), hasattr(sp, "__dict__"))   # True False
print(sys.getsizeof(p) + sys.getsizeof(p.__dict__) > sys.getsizeof(sp))   # True: slots are smaller
try:
    sp.z = 3                                      # slots forbid new attributes
except AttributeError as e:
    print("AttributeError:", e)


def from_dict(cls: type, data: dict[str, Any]) -> Any:
    obj = cls.__new__(cls)                        # skip __init__
    obj.__dict__.update(data)                     # bulk-load attributes
    return obj


q = from_dict(Point, {"x": 9, "y": 8})
print(q.x, q.y, q.__dict__)                       # 9 8 {'x': 9, 'y': 8}
print(c.__dict__ == {"x": "inst-x"}, vars(c) is c.__dict__)   # True True

# Output:
# class-x
# inst-x class-x {'x': 'inst-x'}
# from-descriptor
# True False
# True
# AttributeError: 'SlotPoint' object has no attribute 'z' and no __dict__ for setting new attributes
# 9 8 {'x': 9, 'y': 8}
# True True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Attribute storage | `obj.__dict__` | the object itself (hidden class / shape) |
| Own keys | `obj.__dict__.keys()` | `Object.keys(obj)` |
| Methods live in | class `__dict__` | `Class.prototype` |
| Block new attributes | `__slots__` | `Object.seal(obj)` / `Object.freeze(obj)` |
| Shadowing | instance beats class | own property beats prototype |

```python
# Python way
class A: v = 1
a = A(); a.v = 2
print(a.__dict__, A.v)                          # {'v': 2} 1
```
```javascript
// JavaScript way
class A {}
A.prototype.v = 1;
const a = new A(); a.v = 2;
console.log(Object.keys(a), A.prototype.v);     // [ 'v' ] 1
```

Key difference: Both languages let an own property shadow a shared one. Python exposes the storage as a real dict you can read and write; JavaScript hides it behind engine internals.

---

## 🟠 FastAPI Connection
Pydantic v2 models keep field values in `__dict__` (the verified output shows it), but you should still use `model_dump()` because it handles nested models, aliases and exclusions. SQLAlchemy ORM instances also keep loaded column values and a `_sa_instance_state` in `__dict__`, which is why returning `row.__dict__` leaks internals.

```python
# FastAPI/Pydantic: pydantic v2 keeps field values in __dict__
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # in-process client
from pydantic import BaseModel                    # models


class Item(BaseModel):
    name: str
    price: float = 1.0


it: Item = Item(name="pen")                       # create model
print(it.__dict__)                                # {'name': 'pen', 'price': 1.0}
print(it.model_dump() == it.__dict__)             # True for simple models

app: FastAPI = FastAPI()                          # create app


@app.post("/items")                               # POST /items
def create(item: Item) -> dict[str, object]:
    return item.__dict__                          # works, but prefer model_dump() in real code


client: TestClient = TestClient(app)              # test client
print(client.post("/items", json={"name": "ink", "price": 5}).json())   # {'name': 'ink', 'price': 5.0}

# Output:
# {'name': 'pen', 'price': 1.0}
# True
# {'name': 'ink', 'price': 5.0}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A mutable class attribute shared by all instances
✅ Correct: create the list in `__init__`

```python
class A: items = []                             # Wrong - one list for every instance
class B:
    def __init__(self) -> None:
        self.items = []                         # Right - each object gets its own
a, b = A(), A(); a.items.append(1)
print(b.items)                                  # [1]  <- surprise
```

❌ Mistake 2: Returning `row.__dict__` of an ORM object from an API
✅ Correct: return a Pydantic schema (`response_model`); `__dict__` contains `_sa_instance_state` and lazy-load details

❌ Mistake 3: Using `__slots__` and then expecting `__dict__`, pickling quirks, or multiple inheritance to work freely
✅ Correct: add `"__dict__"` or `"__weakref__"` to `__slots__` if you need them; avoid mixing slotted bases with conflicting layouts

❌ Mistake 4: Writing to `Class.__dict__[...]`
✅ Correct: it is a `mappingproxy`; use `setattr(Class, "x", 1)`

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A: items = []
a, b = A(), A()
a.items.append(1)
print(b.items, a.__dict__, A.__dict__['items'])
a.items = a.items + [2]
print(a.__dict__, b.items)
a.items += [3]
print(a.__dict__, A.items)
```
Answer (verified on 3.13):
```
[1] {} [1]
{'items': [1, 2]} [1]
{'items': [1, 2, 3]} [1]
```
`a.items.append(1)` mutates the shared class list; the instance dict stays empty. `a.items + [2]` builds a NEW list, and the assignment stores it in the instance dict (shadowing the class attribute). After that, `a.items += [3]` extends the instance's own list in place, so the class list `A.items` still has only `[1]`.

---

## ⚫ Interview Questions + Answers

Q1: Where are instance attributes stored?
A1: In the instance's `__dict__` (unless the class uses `__slots__`). Methods and class attributes live in the class's `__dict__`.

Q2: Attribute lookup order?
A2: Data descriptor on the type, then the instance `__dict__`, then non-data descriptors and other class attributes through the MRO, then `__getattr__`.

Q3: What does `__slots__` do and what are the trade-offs?
A3: It replaces the per-instance dict with fixed slots: smaller objects and slightly faster access, but no arbitrary new attributes, no default `__dict__`/`__weakref__` unless declared, and care with inheritance.

Q4: Why is `Class.__dict__` a `mappingproxy`?
A4: To stop you bypassing Python's type caches and descriptor rules by editing the class dict directly. Use `setattr(Class, name, value)` so caches are invalidated.

Q5: How do `pickle` and `copy` use `__dict__`?
A5: By default they create a new object without calling `__init__` and then update its `__dict__` with the saved state (customisable through `__getstate__`/`__setstate__`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging object state
- Writing generic serialisers, copy helpers, simple ORMs
- Explaining attribute shadowing

❌ Avoid when:
- A public API can use dataclasses `asdict` or Pydantic `model_dump`
- The object uses `__slots__` or properties for the real data
- You want to write attributes (prefer `setattr`, which respects descriptors)

---

## 📊 Visual Diagram
```
   a = A()          A (class)
 ┌────────────┐    ┌────────────────────────┐
 │ a.__dict__ │    │ A.__dict__             │
 │ {'age':30} │    │ {'role':'guest',       │
 └─────┬──────┘    │  '__init__': <fn> ...} │
       │ not found └──────────┬─────────────┘
       └───────────────────►  │  then parents (object)
 a.role -> 1) a.__dict__ (miss)  2) A.__dict__ (hit: 'guest')
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__dict__` | Attribute storage dict | attributes का भंडार dict |
| mappingproxy | Read-only view of class dict | class dict का read-only view |
| Shadowing | Instance value hides class value | instance की value class को ढकती है |
| `__slots__` | Fixed attributes, no dict | तय attributes, dict नहीं |
| Descriptor | Object controlling attribute access | attribute access नियंत्रित करने वाला object |
| MRO | Class search order | class खोजने का क्रम |

---

## ⚡ 3-Line Summary
English: `__dict__` stores attributes: instances hold their own data, classes hold methods and shared values. Lookup goes data descriptor, instance dict, then class chain. `__slots__` removes the dict to save memory.
Hindi: `__dict__` attributes रखता है: instance अपना data और class methods व साझा values। Lookup क्रम: data descriptor, instance dict, फिर class chain। Memory बचाने के लिए `__slots__` dict हटा देता है।

---

## ➡️ Next Topic
**171. Modules in Python** — what a module is and how files become importable objects.
