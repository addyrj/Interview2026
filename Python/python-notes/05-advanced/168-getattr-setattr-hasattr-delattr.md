---

# 168. getattr/setattr/hasattr/delattr
# हिंदी में: getattr / setattr / hasattr / delattr (नाम की string से attribute पढ़ना-लिखना)

---

## 🔵 Simple Definition (English)
These four builtins read, write, check and delete an attribute using its name as a string. `getattr(o, "x")` is `o.x`, `setattr(o, "x", 1)` is `o.x = 1`, `hasattr(o, "x")` asks if it exists, and `delattr(o, "x")` is `del o.x`. They are useful when the name is only known at runtime.

## 🔵 सरल परिभाषा (Hindi)
ये चार builtins attribute का नाम string में देकर उसे पढ़ते, लिखते, जाँचते और हटाते हैं। `getattr(o, "x")` मतलब `o.x`, `setattr(o, "x", 1)` मतलब `o.x = 1`, `hasattr(o, "x")` पूछता है कि वह है या नहीं, और `delattr(o, "x")` मतलब `del o.x`। जब नाम सिर्फ runtime पर पता हो तब ये काम आते हैं।

---

## 🔴 Problem it Solves
With the dot syntax, the attribute name is fixed in your code. But event handlers (`on_create`, `on_delete`), config loaders, PATCH APIs and serialisers decide the name from data: a string from JSON, a database column or a URL. Without these builtins you would write a long `if/elif` chain for every possible name. They also give a clean default when something is missing: `getattr(o, "x", default)`.

## 🔴 यह क्यों बना? (Hindi)
Dot syntax में attribute का नाम code में तय होता है। लेकिन event handlers (`on_create`, `on_delete`), config loaders, PATCH APIs और serialisers नाम को data से तय करते हैं: JSON की string, database column या URL। इन builtins के बिना हर संभव नाम के लिए लंबी `if/elif` chain लिखनी पड़ती। ये कुछ न मिलने पर साफ default भी देते हैं: `getattr(o, "x", default)`।

---

## 🟢 How it Works — Step by Step

```
Step 1 → getattr(o, "x")      runs the same lookup as o.x
           (instance __dict__ -> class -> parents; descriptors and properties run)
Step 2 → If not found: AttributeError, or the default if you passed a third argument
Step 3 → setattr(o, "x", v)   same as o.x = v (calls __setattr__ and descriptors)
Step 4 → hasattr(o, "x")      calls getattr and returns False only on AttributeError
Step 5 → delattr(o, "x")      same as del o.x, AttributeError if missing
Step 6 → If a class defines __getattr__, it is the fallback used when normal lookup fails
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → getattr(o, "x")      वही lookup चलाता है जो o.x चलाता है
           (instance __dict__ -> class -> parents; descriptors और properties चलते हैं)
Step 2 → न मिले तो AttributeError, या तीसरा argument दिया हो तो default
Step 3 → setattr(o, "x", v)   o.x = v जैसा (__setattr__ और descriptors बुलाता है)
Step 4 → hasattr(o, "x")      getattr चलाता है और सिर्फ AttributeError पर False देता है
Step 5 → delattr(o, "x")      del o.x जैसा, न हो तो AttributeError
Step 6 → अगर class में __getattr__ है तो normal lookup fail होने पर वही fallback है
```

---

## 🟡 Real World Example
A webhook receiver gets events named `create`, `delete`, `refund` and routes them to methods `on_create`, `on_delete`, `on_refund` with `getattr(handler, f"on_{event}")`. A PATCH `/profile` endpoint applies only the fields the client sent using `setattr`. A settings loader copies environment values into a settings object but ignores unknown keys using `hasattr`.

## 🟡 Real Example Hindi mein
Webhook receiver को `create`, `delete`, `refund` नाम के events मिलते हैं और वह `getattr(handler, f"on_{event}")` से उन्हें `on_create`, `on_delete`, `on_refund` methods तक पहुँचाता है। PATCH `/profile` endpoint client के भेजे fields को ही `setattr` से लागू करता है। Settings loader environment values को settings object में कॉपी करता है और `hasattr` से अनजान keys छोड़ देता है।

---

## 💻 Code Example — Basic
```python
# Basic getattr/setattr/hasattr/delattr
class User:
    role: str = "guest"                           # class attribute


u: User = User()                                  # object
setattr(u, "name", "Asha")                        # same as u.name = "Asha"
print(getattr(u, "name"))                         # Asha
print(getattr(u, "age", 18))                      # default 18 when missing (no error)
print(hasattr(u, "name"), hasattr(u, "email"))    # True False
print(getattr(u, "role"))                         # guest (found on the class)
delattr(u, "name")                                # same as del u.name
print(hasattr(u, "name"))                         # False

try:                                              # missing without default
    getattr(u, "email")
except AttributeError as e:
    print("AttributeError:", e)

try:                                              # delete a missing attribute
    delattr(u, "ghost")
except AttributeError as e:
    print("AttributeError:", e)

# Output:
# Asha
# 18
# True False
# guest
# False
# AttributeError: 'User' object has no attribute 'email'
# AttributeError: 'User' object has no attribute 'ghost'
```

## 💻 Code Example — Advanced
```python
# Production style: dispatch by name, config loader, safe updates, lazy proxy
from dataclasses import dataclass                 # simple model
from typing import Any                            # typing


class Handlers:
    def on_create(self, p: dict[str, Any]) -> str:   # handler 1
        return f"created {p['id']}"

    def on_delete(self, p: dict[str, Any]) -> str:   # handler 2
        return f"deleted {p['id']}"


def dispatch(h: Handlers, event: str, payload: dict[str, Any]) -> str:
    fn = getattr(h, f"on_{event}", None)          # look up a method by name
    if not callable(fn):                          # unknown event
        raise ValueError(f"unknown event: {event}")   # explicit error
    return fn(payload)                            # call it


print(dispatch(Handlers(), "create", {"id": 1}))  # created 1
try:
    dispatch(Handlers(), "explode", {})
except ValueError as e:
    print("Error:", e)


@dataclass
class Settings:
    debug: bool = False                           # setting 1
    workers: int = 1                              # setting 2


def apply(s: Settings, data: dict[str, Any]) -> list[str]:
    """Update only known fields. Return rejected keys."""
    rejected: list[str] = []                      # unknown keys
    for k, v in data.items():                     # each incoming key
        if hasattr(s, k) and not k.startswith("_"):   # known and public
            setattr(s, k, v)                      # update
        else:
            rejected.append(k)                    # never set unknown attributes blindly
    return rejected


s: Settings = Settings()
print(apply(s, {"debug": True, "workers": 4, "__class__": "x"}), s)   # ['__class__'] Settings(...)


class Lazy:
    """Computes an attribute on first access using __getattr__."""

    def __getattr__(self, name: str) -> str:      # only called when normal lookup FAILS
        if name.startswith("_"):                  # protect dunder lookups
            raise AttributeError(name)
        value: str = f"computed-{name}"           # expensive work here
        setattr(self, name, value)                # cache on the instance
        return value


l: Lazy = Lazy()
print(l.report, l.__dict__)                       # computed-report {'report': 'computed-report'}


class Locked:
    def __setattr__(self, name: str, value: Any) -> None:   # intercept every assignment
        if name != "x":                           # allow only x
            raise AttributeError(f"cannot set {name}")
        super().__setattr__(name, value)          # real assignment


k: Locked = Locked()
k.x = 1
try:
    k.y = 2
except AttributeError as e:
    print("AttributeError:", e)
print(getattr(k, "x"))

# Output:
# created 1
# Error: unknown event: explode
# ['__class__'] Settings(debug=True, workers=4)
# computed-report {'report': 'computed-report'}
# AttributeError: cannot set y
# 1
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Read by name | `getattr(o, "x", default)` | `o["x"] ?? default` |
| Write by name | `setattr(o, "x", v)` | `o["x"] = v` |
| Exists? | `hasattr(o, "x")` | `"x" in o` |
| Delete | `delattr(o, "x")` | `delete o["x"]` |
| Call by name | `getattr(o, name)(*args)` | `o[name](...args)` |

```python
# Python way
class H:
    def on_ping(self) -> str: return "pong"
print(getattr(H(), "on_" + "ping")())          # pong
```
```javascript
// JavaScript way
class H { on_ping() { return "pong"; } }
console.log(new H()["on_" + "ping"]());         // pong - bracket notation is built in
```

Key difference: JavaScript objects allow bracket access with a string, so no helper is needed. Python uses the dot for attributes and `[]` for items, so you need the four builtins for dynamic attribute access.

---

## 🟠 FastAPI Connection
PATCH endpoints apply only the fields the client sent. `model_dump(exclude_unset=True)` gives those fields and `setattr` writes them to the stored object. Keep the allowed fields in a Pydantic model so clients cannot set arbitrary attributes such as `is_admin`.

```python
# FastAPI: PATCH endpoint that applies only allowed fields with setattr
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # in-process client
from pydantic import BaseModel                    # models

app: FastAPI = FastAPI()                          # create app


class Profile(BaseModel):                         # stored object
    name: str = "Asha"
    city: str = "Pune"


class ProfilePatch(BaseModel):                    # allowed update fields (all optional)
    name: str | None = None
    city: str | None = None


db: Profile = Profile()                           # fake database row


@app.patch("/profile")                            # PATCH /profile
def patch(body: ProfilePatch) -> Profile:
    for field, value in body.model_dump(exclude_unset=True).items():   # only fields sent
        setattr(db, field, value)                 # update by name
    return db


client: TestClient = TestClient(app)              # test client
print(client.patch("/profile", json={"city": "Delhi"}).json())   # {'name': 'Asha', 'city': 'Delhi'}

# Output:
# {'name': 'Asha', 'city': 'Delhi'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `setattr` with names straight from user input
✅ Correct: whitelist the names (a Pydantic model or a set of allowed fields)

```python
# Wrong - client can overwrite anything: {"is_admin": true, "__class__": ...}
# for k, v in request_json.items(): setattr(user, k, v)
# Right
ALLOWED = {"name", "city"}
# for k, v in request_json.items():
#     if k in ALLOWED: setattr(user, k, v)
```

❌ Mistake 2: Expecting the default in `getattr(o, "x", default)` to be lazy
✅ Correct: it is evaluated first, always; use `if hasattr` or try/except for costly defaults

```python
def expensive():
    print("called"); return 0
class O: x = 1
print(getattr(O, "x", expensive()))             # prints "called" and then 1
```

❌ Mistake 3: Using `hasattr` on properties that raise other exceptions
✅ Correct: in Python 3 `hasattr` only catches `AttributeError`; a `KeyError` inside a property propagates

❌ Mistake 4: Thinking `hasattr` is free
✅ Correct: it runs the property getter (side effects, slow I/O) — use `inspect.getattr_static` to check without running

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def expensive():
    print("called"); return 0
class O: x = 1
print(getattr(O, 'x', expensive()))
class P:
    @property
    def boom(self): raise KeyError("k")
try: print(hasattr(P(), 'boom'))
except KeyError as e: print("KeyError propagates", e)
class Q:
    @property
    def boom(self): raise AttributeError("a")
print(hasattr(Q(), 'boom'))
o = O(); setattr(o, "1x", 5); print(o.__dict__, getattr(o, "1x"))
```
Answer (verified on 3.13):
```
called
1
KeyError propagates 'k'
False
{'1x': 5} 5
```
The default argument is computed before the call, so "called" prints although `x` exists. `hasattr` converts only `AttributeError` into `False`; a `KeyError` escapes; an `AttributeError` raised inside a property makes `hasattr` say False even though the property exists. `setattr` accepts any string, even names that are not valid identifiers (`"1x"`), reachable only through `getattr`/`__dict__`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `getattr(o, "x")` and `o.__dict__["x"]`?
A1: `getattr` follows the full lookup (class, parents, descriptors, properties, `__getattr__`). `__dict__["x"]` reads only that object's own dict and raises `KeyError` for class attributes or methods.

Q2: How do `__getattr__` and `__getattribute__` differ?
A2: `__getattribute__` runs for every attribute access. `__getattr__` runs only when normal lookup raised `AttributeError`. Override `__getattr__` for fallbacks (lazy loading, proxies).

Q3: How do you call a method by name?
A3: `getattr(obj, name)(*args)`. Validate the name or use a dispatch dict to avoid exposing internals.

Q4: Why is `setattr` with user-controlled names risky?
A4: It allows overwriting internals or security flags (mass assignment). Always whitelist fields.

Q5: What does `setattr` do on a class using `__slots__`?
A5: It works only for names declared in `__slots__`; other names raise `AttributeError`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dispatching events by name
- Applying PATCH/partial updates
- Loading config into objects, plugin discovery
- Providing safe defaults (`getattr(settings, "DEBUG", False)`)

❌ Avoid when:
- The name is known at write time (use `o.x`)
- A dict or dispatch table is clearer
- Name comes from untrusted input without a whitelist

---

## 📊 Visual Diagram
```
 getattr(o, "x") lookup path
   1. type(o).__mro__ data descriptors (property with setter)
   2. o.__dict__["x"]
   3. class attribute / non-data descriptor / method
   4. __getattr__(self, "x")        (only if 1-3 failed)
   5. default given?  yes -> return default
                      no  -> raise AttributeError
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `getattr` | Read attribute by name | नाम से attribute पढ़ना |
| `setattr` | Write attribute by name | नाम से attribute लिखना |
| `hasattr` | Check attribute exists | attribute है या नहीं |
| `delattr` | Delete attribute | attribute हटाना |
| Dispatch | Choose a function from a name | नाम से function चुनना |
| Mass assignment | Client sets fields it should not | client का मना किए fields बदलना |

---

## ⚡ 3-Line Summary
English: The four builtins access attributes by string name, so code can be driven by data. `getattr` supports a default, `hasattr` only treats `AttributeError` as missing. Whitelist names that come from users.
Hindi: चारों builtins attribute को string नाम से access करते हैं, इसलिए code data से चल सकता है। `getattr` में default मिलता है, `hasattr` सिर्फ `AttributeError` को "नहीं है" मानता है। User से आए नामों को whitelist करें।

---

## ➡️ Next Topic
**169. vars() + dir()** — list an object's data and everything reachable on it.
