---

# 169. vars() + dir()
# हिंदी में: vars() और dir() (object का data और पहुँच योग्य नाम)

---

## 🔵 Simple Definition (English)
`vars(obj)` returns the object's `__dict__`: the attributes stored on that object itself. `dir(obj)` returns a sorted list of names you can reach on the object, including class attributes, methods and inherited ones. With no argument both work on the current scope.

## 🔵 सरल परिभाषा (Hindi)
`vars(obj)` object का `__dict__` लौटाता है: यानी उसी object पर रखे attributes। `dir(obj)` उन सभी नामों की sorted list देता है जिन तक आप object पर पहुँच सकते हैं, यानी class attributes, methods और inherited नाम भी। बिना argument के दोनों मौजूदा scope पर काम करते हैं।

---

## 🔴 Problem it Solves
When you meet an unknown object or want to turn an object into a dictionary, you need two different answers: "what data does this object hold?" (`vars`) and "what can I call or read on it?" (`dir`). Mixing them up causes bugs, like serialising methods or missing inherited fields. They also help in the REPL for discovering what a library offers, and in debugging to see local variables.

## 🔴 यह क्यों बना? (Hindi)
जब कोई अनजान object मिले या object को dictionary बनाना हो तो दो अलग जवाब चाहिए: "इस object में कौन सा data है?" (`vars`) और "इस पर मैं क्या call या read कर सकता हूँ?" (`dir`)। इन्हें गड़बड़ाने से bugs आते हैं, जैसे methods serialise करना या inherited fields छूट जाना। REPL में library की सुविधाएँ खोजने और debugging में local variables देखने में भी ये मदद करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → vars(obj) returns obj.__dict__ (the SAME dict, not a copy)
Step 2 → Objects without __dict__ (int, __slots__ classes) raise TypeError in vars()
Step 3 → dir(obj) calls obj.__dir__() and sorts the result
Step 4 → Default __dir__ merges: instance __dict__ + class + all parents
Step 5 → vars() with no argument = locals(); at module level that is globals()
Step 6 → dir() with no argument = sorted names in the current scope
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → vars(obj) obj.__dict__ लौटाता है (वही dict, copy नहीं)
Step 2 → जिन objects में __dict__ नहीं (int, __slots__ वाली classes) उन पर vars() TypeError देता है
Step 3 → dir(obj) obj.__dir__() बुलाकर नतीजा sort करता है
Step 4 → Default __dir__ मिलाता है: instance __dict__ + class + सभी parents
Step 5 → बिना argument के vars() = locals(); module level पर यह globals() है
Step 6 → बिना argument के dir() = मौजूदा scope के नामों की sorted list
```

---

## 🟡 Real World Example
A REST API converts an `Order` object to JSON using `vars(order)` and skips names starting with underscore. A support engineer opens a Python shell on a production-like box and types `dir(client)` to see what methods a payment SDK exposes. A test helper builds a `SimpleNamespace` from a dict, then uses `vars()` to turn it back.

## 🟡 Real Example Hindi mein
REST API `Order` object को `vars(order)` से JSON में बदलती है और underscore से शुरू होने वाले नाम छोड़ देती है। Support engineer production जैसी machine पर Python shell खोलकर `dir(client)` टाइप करता है और देखता है कि payment SDK कौन से methods देता है। Test helper dict से `SimpleNamespace` बनाता है और वापस `vars()` से dict।

---

## 💻 Code Example — Basic
```python
# Basic vars() and dir()
class User:
    role: str = "guest"                           # class attribute

    def __init__(self, name: str) -> None:
        self.name: str = name                     # instance attribute

    def greet(self) -> str:
        return "hi"


u: User = User("Asha")
print(vars(u))                                    # {'name': 'Asha'}  instance data only
print(u.__dict__ is vars(u))                      # True: same dict
print([a for a in dir(u) if not a.startswith("_")])   # ['greet', 'name', 'role'] everything reachable
print("greet" in vars(u), "greet" in dir(u))      # False True
print("greet" in vars(User))                      # True: methods live on the class
x: int = 10                                       # a module level variable
print("x" in vars())                              # vars() with no argument = current namespace
print(dir() == sorted(vars()))                    # dir() with no argument lists current names
try:
    vars(5)                                       # int has no __dict__
except TypeError as e:
    print("TypeError:", e)

# Output:
# {'name': 'Asha'}
# True
# ['greet', 'name', 'role']
# False True
# True
# True
# True
# TypeError: vars() argument must have __dict__ attribute
```

## 💻 Code Example — Advanced
```python
# Production style: object to dict, public API listing, __dir__ override, namespace audit
from typing import Any                            # typing


class Order:
    status: str = "new"                           # class default

    def __init__(self, id: int, total: float) -> None:
        self.id: int = id
        self.total: float = total
        self._secret: str = "x"                   # private-by-convention

    def pay(self) -> None: ...                    # public method


def to_dict(obj: Any) -> dict[str, Any]:
    """Serialise public instance data."""
    return {k: v for k, v in vars(obj).items() if not k.startswith("_")}


o: Order = Order(7, 99.5)
print(to_dict(o))                                 # {'id': 7, 'total': 99.5}


def public_api(obj: Any) -> dict[str, list[str]]:
    names: list[str] = [n for n in dir(obj) if not n.startswith("_")]   # sorted public names
    return {
        "methods": [n for n in names if callable(getattr(obj, n))],
        "data": [n for n in names if not callable(getattr(obj, n))],
    }


print(public_api(o))                              # methods: pay / data: id, status, total


class Dynamic:
    def __dir__(self) -> list[str]:               # dir() calls this, so we can add names
        return ["alpha", "beta"]                  # dir() sorts the result


print(dir(Dynamic()))                             # ['alpha', 'beta']

g: dict[str, Any] = {k: v for k, v in globals().items() if not k.startswith("__")}
print(sorted(g)[:4])                              # names defined in this module so far

import types                                      # SimpleNamespace
ns = types.SimpleNamespace(**to_dict(o))          # dict -> attribute access
print(ns.id, vars(ns))                            # 7 {'id': 7, 'total': 99.5}

class Slotted:
    __slots__ = ("a",)                            # no per-instance __dict__

    def __init__(self) -> None:
        self.a: int = 1
try:
    vars(Slotted())
except TypeError as e:
    print("TypeError:", e)
print(dir(Slotted()).count("a"))                  # dir still shows slots: 1

# Output:
# {'id': 7, 'total': 99.5}
# {'methods': ['pay'], 'data': ['id', 'status', 'total']}
# ['alpha', 'beta']
# ['Any', 'Dynamic', 'Order', 'o']
# 7 {'id': 7, 'total': 99.5}
# TypeError: vars() argument must have __dict__ attribute
# 1
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Own data | `vars(o)` / `o.__dict__` | `Object.keys(o)` / `Object.entries(o)` |
| All reachable names | `dir(o)` | `for...in` (includes inherited enumerable) |
| Own + non-enumerable | n/a | `Object.getOwnPropertyNames(o)` |
| Methods | on the class (`vars(C)`) | on the prototype (`C.prototype`) |

```python
# Python way
class U:
    def __init__(self) -> None: self.name = "Asha"
print(vars(U()))                                # {'name': 'Asha'}
```
```javascript
// JavaScript way
class U { constructor() { this.name = "Asha"; } }
console.log(Object.entries(new U()));           // [ [ 'name', 'Asha' ] ]
```

Key difference: Python's `vars` returns the live dict (changes affect the object). JavaScript's `Object.entries` returns a copy. Python methods are not in the instance data, the same as JS methods on the prototype.

---

## 🟠 FastAPI Connection
For response data prefer `response_model` or `model_dump()`. `vars()` is a quick tool for debug routes and for plain classes (non-Pydantic) that you must return. Remember FastAPI cannot always serialise arbitrary objects, so convert them first.

```python
# FastAPI: debug route using vars() to show app state
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # in-process client


class State:
    def __init__(self) -> None:
        self.requests: int = 0                    # counter
        self.version: str = "1.0"                 # version


state: State = State()                            # shared state object
app: FastAPI = FastAPI()                          # create app


@app.get("/debug/state")                          # internal debug route
def debug() -> dict[str, object]:
    state.requests += 1                           # count calls
    return vars(state)                            # instance data as dict


client: TestClient = TestClient(app)              # test client
client.get("/debug/state")                        # call 1
print(client.get("/debug/state").json())          # {'requests': 2, 'version': '1.0'}

# Output:
# {'requests': 2, 'version': '1.0'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking `vars(obj)` includes methods and class attributes
✅ Correct: it has only instance data; use `dir(obj)` or `vars(type(obj))` for the rest

```python
class A:
    c = 1
    def m(self): ...
a = A(); a.i = 2
print(vars(a))                                  # {'i': 2}
print([n for n in dir(a) if not n.startswith("_")])   # ['c', 'i', 'm']
```

❌ Mistake 2: Mutating the dict you got from `vars(obj)` by accident
✅ Correct: copy first (`dict(vars(obj))`) if you only want a snapshot

❌ Mistake 3: Using `vars()` inside a function to change locals
✅ Correct: `vars()` in a function returns a snapshot of locals; writing to it does not change variables

❌ Mistake 4: Calling `vars()` on an `int`, `str` or `__slots__` object
✅ Correct: catch `TypeError` or use `getattr(obj, "__dict__", {})`

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    a = 1
    def __init__(s): s.b = 2
print('a' in vars(A()), 'a' in dir(A()), len(vars(A())))
print(vars() is globals())
def f():
    z = 1
    return vars()
print(f())
class K:
    q = 5
    print(sorted(k for k in vars() if not k.startswith("__")))
```
Answer (verified on 3.13): `False True 1`, then `True`, then `{'z': 1}`, then `['q']`. `a` is a class attribute, so it is in `dir` but not in the instance `vars`. At module level `vars()` is the globals dict. Inside a function it returns the local variables. Inside a class body it returns the namespace being built, so `q` is visible.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `vars()` and `dir()`?
A1: `vars(obj)` is the object's own `__dict__` (a mapping of name to value). `dir(obj)` is a sorted list of names (no values) including class and inherited attributes.

Q2: Is `vars(obj)` a copy?
A2: No, it is the same dict as `obj.__dict__`. Changing it changes the object (except for `locals()` inside functions).

Q3: How can you customise `dir()`?
A3: Define `__dir__` returning an iterable of names. `dir` will sort it. Libraries use this to advertise dynamic attributes created through `__getattr__`.

Q4: Why does `vars()` fail on an object with `__slots__`?
A4: Slot classes have no instance `__dict__`; values live in fixed slots. Use `{s: getattr(o, s) for s in o.__slots__}`. `dir()` still lists the slot names.

Q5: What does `dir()` with no argument return?
A5: A sorted list of names in the current local scope (module names at top level, local names in a function).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Quick object-to-dict conversion for plain classes
- Exploring unknown libraries in a shell
- Debug endpoints, logging object state

❌ Avoid when:
- Production serialisation (use `dataclasses.asdict`, Pydantic `model_dump`)
- Objects with `__slots__` or properties holding the real data
- Security-sensitive output (you may leak private fields)

---

## 📊 Visual Diagram
```
 class A: a = 1;  def __init__(s): s.b = 2        a = A()

 vars(a)  ─►  {'b': 2}                      only the instance's own dict
 vars(A)  ─►  mappingproxy({'a': 1, ...})   class dict (methods, class attrs)
 dir(a)   ─►  ['__class__', ..., 'a', 'b']  merged: a.__dict__ + A + object
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `vars()` | Object's own attribute dict | object का अपना attribute dict |
| `dir()` | Sorted list of reachable names | पहुँच योग्य नामों की sorted list |
| `__dict__` | Storage dict of attributes | attributes का भंडार dict |
| `__dir__` | Hook that customises `dir()` | `dir()` बदलने वाला hook |
| `locals()` / `globals()` | Current scope namespaces | मौजूदा scope के namespaces |
| `__slots__` | Fixed attributes, no dict | तय attributes, dict नहीं |

---

## ⚡ 3-Line Summary
English: `vars` returns the object's own attribute dict (live), `dir` returns a sorted list of all reachable names. Use `vars` for data, `dir` for discovery. Neither is a replacement for proper serialisation.
Hindi: `vars` object का अपना attribute dict (live) देता है, `dir` सभी पहुँच योग्य नामों की sorted list। Data के लिए `vars`, खोज के लिए `dir`। दोनों proper serialisation का विकल्प नहीं हैं।

---

## ➡️ Next Topic
**170. __dict__ attribute** — how attributes are stored, lookup order, and `__slots__` memory savings.
