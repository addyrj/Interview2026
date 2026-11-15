---

# 162. __new__ vs __init__
# हिंदी में: __new__ बनाम __init__ (object बनाना बनाम सजाना)

---

## 🔵 Simple Definition (English)
`__new__` creates the empty object and returns it. `__init__` then fills that object with data. `__new__` is a static-like method that receives the class; `__init__` receives the ready instance and must return `None`.

## 🔵 सरल परिभाषा (Hindi)
`__new__` खाली object बनाता है और उसे लौटाता है। फिर `__init__` उस object में data भरता है। `__new__` को class मिलती है; `__init__` को बना-बनाया instance मिलता है और वह `None` लौटाता है।

---

## 🔴 Problem it Solves
Most classes only need `__init__`. But some jobs must happen BEFORE the object exists: subclassing immutable types (`int`, `str`, `tuple`, where values cannot change after creation), returning an already existing object (singleton, cache, flyweight), or returning a different type. `__init__` is too late for these because the object is already built.

## 🔴 यह क्यों बना? (Hindi)
ज़्यादातर classes को सिर्फ `__init__` चाहिए। पर कुछ काम object बनने से पहले करने पड़ते हैं: immutable types (`int`, `str`, `tuple`) को subclass करना (जहाँ बनने के बाद value नहीं बदलती), पहले से मौजूद object लौटाना (singleton, cache, flyweight) या कोई दूसरा type लौटाना। `__init__` इनके लिए देर से चलता है क्योंकि object तब तक बन चुका होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You call  Demo(5)
Step 2 → type.__call__ runs Demo.__new__(Demo, 5)  -> returns an instance
Step 3 → If the returned object is an instance of Demo, Python calls
           instance.__init__(5)
Step 4 → If __new__ returns something else, __init__ is SKIPPED
Step 5 → The final value is handed back to the caller
Step 6 → __new__ runs on every call; __init__ also runs on every call
           (even when __new__ returned an old, cached object)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप Demo(5) लिखते हैं
Step 2 → type.__call__ Demo.__new__(Demo, 5) चलाता है -> एक instance लौटता है
Step 3 → अगर लौटा object Demo का instance है तो Python
           instance.__init__(5) बुलाता है
Step 4 → अगर __new__ कुछ और लौटाए तो __init__ SKIP हो जाता है
Step 5 → अंतिम value caller को मिलती है
Step 6 → __new__ हर call पर चलता है; __init__ भी हर call पर चलता है
           (भले ही __new__ ने पुराना cached object लौटाया हो)
```

---

## 🟡 Real World Example
A database layer keeps one `Connection` object per host: `Connection("db1")` twice returns the same object (flyweight, built in `__new__`). A fintech app defines `Money(float)` that rounds to 2 decimals; because `float` is immutable, rounding must happen in `__new__`. `Email(str)` that validates and lowercases on creation is another real pattern.

## 🟡 Real Example Hindi mein
Database layer हर host के लिए एक `Connection` object रखती है: `Connection("db1")` दो बार बुलाने पर वही object मिलता है (flyweight, `__new__` में बना)। Fintech app `Money(float)` बनाती है जो 2 decimals तक round करे; `float` immutable है इसलिए rounding `__new__` में ही होनी चाहिए। `Email(str)` जो बनते समय validate और lowercase करे, यह भी असली pattern है।

---

## 💻 Code Example — Basic
```python
# Basic __new__ vs __init__
class Demo:
    def __new__(cls, *args, **kwargs):            # step 1: CREATE the object
        print("__new__ called")                   # shows order
        return super().__new__(cls)               # must return the new instance

    def __init__(self, x: int) -> None:           # step 2: INITIALISE the object
        print("__init__ called")                  # runs after __new__
        self.x: int = x                           # set attribute


d: Demo = Demo(5)                                 # prints __new__ then __init__
print(d.x)                                        # 5


class Fake:
    def __new__(cls):                             # returns an object of ANOTHER type
        return 42                                 # not an instance of Fake

    def __init__(self) -> None:
        print("never printed")                    # skipped: result is not a Fake


print(Fake())                                     # 42, __init__ was skipped


class Meters(float):                              # subclass an immutable type
    def __new__(cls, value: float) -> "Meters":   # must use __new__, value is fixed at creation
        return super().__new__(cls, round(value, 2))   # round before creating

print(Meters(3.14159), type(Meters(1)).__name__)  # 3.14 Meters

# Output:
# __new__ called
# __init__ called
# 5
# 42
# 3.14 Meters
```

## 💻 Code Example — Advanced
```python
# Production style: singleton, instance pool, validated immutable type
from __future__ import annotations                # allow forward references in hints
import re                                         # email check
from typing import Any, ClassVar                  # typing helpers


class Config:
    """Singleton using __new__ (one object, __init__ guarded)."""

    _instance: ClassVar[Config | None] = None     # the single instance

    def __new__(cls, *args: Any, **kwargs: Any) -> Config:
        if cls._instance is None:                 # first call
            cls._instance = super().__new__(cls)  # create once
        return cls._instance                      # reuse afterwards

    def __init__(self, env: str = "dev") -> None:
        if getattr(self, "_ready", False):        # __init__ runs EVERY call, so guard it
            return                                # skip re-init
        self.env: str = env                       # set once
        self._ready: bool = True                  # mark initialised


c1: Config = Config("prod")                       # first creation
c2: Config = Config("dev")                        # same object, init skipped
print(c1 is c2, c2.env)                           # True prod


class Email(str):
    """Immutable validated string: validation must happen in __new__."""

    def __new__(cls, value: str) -> Email:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.\w+", value):   # simple pattern
            raise ValueError(f"invalid email: {value}")   # reject bad input
        return super().__new__(cls, value.lower())   # normalise to lowercase


print(Email("Asha@Example.COM"))                  # asha@example.com
try:                                              # invalid case
    Email("nope")                                 # raises before object exists
except ValueError as e:                           # handle
    print("Error:", e)


class Connection:
    """Flyweight: same host returns the same cached object."""

    _pool: ClassVar[dict[str, Connection]] = {}   # host -> object

    def __new__(cls, host: str) -> Connection:
        if host not in cls._pool:                 # not cached yet
            obj = super().__new__(cls)            # create
            obj.host = host                       # set attribute inside __new__
            cls._pool[host] = obj                 # remember
        return cls._pool[host]                    # reuse

    host: str                                     # attribute declaration


print(Connection("db1") is Connection("db1"))     # True
print(Connection("db1") is Connection("db2"))     # False

import pickle                                     # unpickle calls __new__ but NOT __init__
class Tracked:
    def __init__(self) -> None:
        print("init")                             # shown only on normal creation
        self.v: int = 1
t: Tracked = Tracked()                            # prints init
t2: Tracked = pickle.loads(pickle.dumps(t))       # no init printed
print(t2.v)                                       # state restored from __dict__

# Output:
# True prod
# asha@example.com
# Error: invalid email: nope
# True
# False
# init
# 1
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Create the object | `__new__(cls, ...)` | done by `new` (implicit) |
| Initialise the object | `__init__(self, ...)` | `constructor(...)` |
| Return another object | `__new__` can return anything | `constructor` can `return` an object |
| Detect `new` call | not needed | `new.target` |

```python
# Python way
class A:
    def __new__(cls):                           # create step
        print("new")
        return super().__new__(cls)
    def __init__(self) -> None:                 # init step
        print("init")
A()                                             # new, init
```
```javascript
// JavaScript way
class A {
  constructor() {                               // one step: create + init together
    console.log("constructor");
    // returning an object here replaces `this`, like __new__ returning another object
  }
}
new A();
```

Key difference: JavaScript has one `constructor` and `new` creates the object for you. Python splits creation (`__new__`) from initialisation (`__init__`), which is needed for immutable types.

---

## 🟠 FastAPI Connection
You rarely write `__new__` in FastAPI code. Pydantic models call `__init__` (with validation) for each request. Note that `Model.__new__(Model)` alone gives an empty shell with no validation, which is what `model_construct` and unpickling do internally. Singletons for settings are better done with `functools.lru_cache` and `Depends`.

```python
# FastAPI: validated value type used in a path parameter via Pydantic
from fastapi import FastAPI                       # FastAPI app
from fastapi.testclient import TestClient         # in-process client
from pydantic import BaseModel, field_validator   # validation helpers


class Order(BaseModel):                           # pydantic builds objects via __init__ with validation
    sku: str                                      # product code

    @field_validator("sku")                       # runs inside validation
    @classmethod
    def upper(cls, v: str) -> str:                # normalise the value
        return v.upper()                          # uppercase sku


app: FastAPI = FastAPI()                          # create app


@app.post("/orders")                              # POST /orders
def make(order: Order) -> dict[str, str]:
    return {"sku": order.sku}                     # normalised sku


client: TestClient = TestClient(app)              # test client
print(client.post("/orders", json={"sku": "ab-1"}).json())   # {'sku': 'AB-1'}
print(Order.__new__(Order).__dict__)              # __new__ alone gives an EMPTY shell, no validation

# Output:
# {'sku': 'AB-1'}
# {}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Changing an immutable value in `__init__`
✅ Correct: do it in `__new__`

```python
# Wrong - the str value is already fixed when __init__ runs
class Up(str):
    def __init__(self, v: str) -> None:
        self = v.upper()                        # does nothing useful
print(Up("a"))                                  # a
# Right
class Up2(str):
    def __new__(cls, v: str):
        return super().__new__(cls, v.upper())
print(Up2("a"))                                 # A
```

❌ Mistake 2: Forgetting `return` in `__new__`
✅ Correct: `return super().__new__(cls)`

```python
class A:
    def __new__(cls):
        super().__new__(cls)                    # Wrong - no return, A() gives None
class B:
    def __new__(cls):
        return super().__new__(cls)             # Right
print(A(), type(B()).__name__)                  # None B
```

❌ Mistake 3: Singleton via `__new__` but `__init__` resets state every time
✅ Correct: guard `__init__` with a flag (shown in the advanced example) or use a metaclass `__call__`

❌ Mistake 4: Passing extra arguments to `object.__new__`
✅ Correct: call `super().__new__(cls)` without them (`object.__new__` complains if `__new__` is overridden and extra args are given)

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def __new__(cls): print("new"); return object.__new__(B)
    def __init__(self): print("A init")
class B(A):
    def __init__(self): print("B init")
x = A()
print(type(x).__name__)

class C:
    def __new__(cls): print("C new"); return object.__new__(D)
    def __init__(self): print("C init")
class D: pass
y = C()
print(type(y).__name__)
```
Answer (verified on 3.13): `new`, `B init`, `B`, `C new`, `D`. For `A()`, `__new__` returns a `B` object. `B` is a subclass of `A`, so Python calls `__init__` on that object, which is `B.__init__`, not `A.__init__`. For `C()`, `D` is not a `C`, so `__init__` is skipped.

---

## ⚫ Interview Questions + Answers

Q1: Which runs first, `__new__` or `__init__`?
A1: `__new__`. It creates the instance; `__init__` then initialises it, only if `__new__` returned an instance of the class.

Q2: Why can't `__init__` change an immutable object?
A2: Because the value is fixed during creation. For `int`, `str`, `tuple`, `float`, `frozenset` the data is set by their `__new__`, so a subclass must override `__new__`.

Q3: How do you implement a singleton with `__new__`?
A3: Store the instance in a class attribute, create it only when it is `None`, and always return it. Guard `__init__` because it runs on each call.

Q4: Does unpickling call `__init__`?
A4: No. It calls `__new__` (through `copyreg`/`object.__reduce_ex__`) and then restores `__dict__`. Do not put required setup only in `__init__` if objects are pickled or copied.

Q5: Can `__new__` return an object of a different class?
A5: Yes. Then `__init__` of the original class is skipped (unless the object is an instance of the class). This is how some factory patterns work, but it surprises readers, so use it carefully.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Subclassing immutable built-ins (`int`, `str`, `tuple`, `float`)
- Singleton, flyweight or object pool
- Choosing which subclass to return (factory)

❌ Avoid when:
- A normal mutable class only needs attributes (use `__init__`)
- A simple factory function or `classmethod` is clearer
- Configuration singletons (a module-level object or `lru_cache` is simpler)

---

## 📊 Visual Diagram
```
 Demo(5)
    │
    ▼
 type.__call__(Demo, 5)
    │
    ├─► Demo.__new__(Demo, 5) ──► instance (empty shell)
    │
    ├─ isinstance(instance, Demo)?
    │       yes ─► instance.__init__(5)  ─► fills attributes
    │       no  ─► skip __init__
    ▼
 returns instance to the caller
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__new__` | Creates the instance | instance बनाता है |
| `__init__` | Initialises the instance | instance में data भरता है |
| Immutable | Cannot change after creation | बनने के बाद नहीं बदलता |
| Singleton | One shared instance | एक साझा instance |
| Flyweight | Reuse objects with same key | समान key पर object reuse |
| Factory | Code that decides what to build | तय करता है कि क्या बनाना है |

---

## ⚡ 3-Line Summary
English: `__new__` builds the object, `__init__` fills it. Override `__new__` for immutable types, singletons and pools. If `__new__` returns another type, `__init__` is skipped.
Hindi: `__new__` object बनाता है, `__init__` उसे भरता है। Immutable types, singleton और pool के लिए `__new__` override करें। अगर `__new__` दूसरा type लौटाए तो `__init__` skip हो जाता है।

---

## ➡️ Next Topic
**163. Abstract Syntax Tree (AST)** — how Python turns source text into a tree you can inspect, check and rewrite.
