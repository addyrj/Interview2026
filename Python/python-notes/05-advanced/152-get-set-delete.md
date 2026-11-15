---

# 152. __get__ __set__ __delete__
# हिंदी में: `__get__`, `__set__`, `__delete__` — Descriptor के तीन Methods

---

## 🔵 Simple Definition (English)
These are the three hook methods of a descriptor. `__get__(self, obj, objtype)` runs when the attribute is read, `__set__(self, obj, value)` runs when it is assigned, and `__delete__(self, obj)` runs on `del`. Defining any of the last two makes it a data descriptor, which beats the instance dictionary.

## 🔵 सरल परिभाषा (Hindi)
ये descriptor के तीन hook methods हैं। `__get__(self, obj, objtype)` attribute पढ़ने पर चलता है, `__set__(self, obj, value)` assign करने पर, और `__delete__(self, obj)` `del` करने पर। आखिरी दो में से कोई भी define करने से वह data descriptor बन जाता है, जो instance dictionary से ऊपर रहता है।

---

## 🔴 Problem it Solves
Python needs a precise way to let a class attribute react to read, write and delete. Knowing exactly what each hook receives (`obj`, `objtype`, `value`) is the difference between a descriptor that works and one that overwrites shared state, recurses forever or breaks when accessed on the class. These three methods are the whole contract.

## 🔴 यह क्यों बना? (Hindi)
Python को class attribute के read, write और delete पर प्रतिक्रिया देने का सटीक तरीका चाहिए था। हर hook को क्या मिलता है (`obj`, `objtype`, `value`) यह जानना ही तय करता है कि descriptor सही चलेगा या shared state overwrite करेगा, अनंत recursion में जाएगा या class पर access करने पर टूट जाएगा। ये तीन methods पूरा contract हैं।

---

## 🟢 How it Works — Step by Step

```
Signature summary
   __get__(self, obj, objtype=None)   obj = the instance (None if accessed on the class)
                                      objtype = the class of the instance (always given)
   __set__(self, obj, value)          obj = the instance, value = right side of "="
   __delete__(self, obj)              obj = the instance

Step 1 → d.x           : Python finds descriptor x on type(d) -> calls x.__get__(d, Demo)
Step 2 → Demo.x        : same lookup, but obj is None -> x.__get__(None, Demo)
Step 3 → d.x = 10      : calls x.__set__(d, 10); the instance dict is NOT updated automatically
Step 4 → del d.x       : calls x.__delete__(d)
Step 5 → Your code must store data itself: obj.__dict__[name] or setattr(obj, "_name", value)
Step 6 → Never store per-instance data on the descriptor (self) — it is shared by all instances
Step 7 → Only __get__ defined -> non-data descriptor; with __set__/__delete__ -> data descriptor
```

## 🟢 कैसे काम करता है? (Hindi)
```
Signature सार
   __get__(self, obj, objtype=None)   obj = instance (class पर access हो तो None)
                                      objtype = instance की class (हमेशा मिलती है)
   __set__(self, obj, value)          obj = instance, value = "=" के दाईं ओर की value
   __delete__(self, obj)              obj = instance

Step 1 → d.x           : Python type(d) पर descriptor x ढूंढकर x.__get__(d, Demo) call करता है
Step 2 → Demo.x        : वही lookup, लेकिन obj None है -> x.__get__(None, Demo)
Step 3 → d.x = 10      : x.__set__(d, 10) call होता है; instance dict अपने आप update नहीं होता
Step 4 → del d.x       : x.__delete__(d) call होता है
Step 5 → Data आपको खुद store करना है: obj.__dict__[name] या setattr(obj, "_name", value)
Step 6 → Per-instance data descriptor (self) पर कभी store न करें — वह सभी instances में shared है
Step 7 → सिर्फ __get__ हो -> non-data descriptor; __set__/__delete__ हो -> data descriptor
```

---

## 🟡 Real World Example
A wallet service wants a `balance` that only accepts integers, logs every change for audit, refuses deletion, and a `currency` that is read-only. `__set__` handles the type check and audit log, `__delete__` blocks removal, and a second descriptor with a `__set__` that always raises makes a constant. Banks and fintech apps need this audit behaviour for compliance.

## 🟡 Real Example Hindi mein
Wallet service चाहती है कि `balance` सिर्फ integer ले, हर बदलाव का audit log बने, delete न हो सके, और `currency` read-only हो। `__set__` type check और audit log संभालता है, `__delete__` हटाने से रोकता है, और ऐसा दूसरा descriptor जिसका `__set__` हमेशा error देता है, constant बना देता है। Banks और fintech apps को compliance के लिए यह audit behaviour चाहिए।

---

## 💻 Code Example — Basic
```python
# The three descriptor methods: what each one receives
from typing import Any                                    # any type


class Verbose:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name: str = name                             # attribute name, e.g. "x"

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        print(f"__get__(obj={'None' if obj is None else 'inst'}, objtype={objtype.__name__})")
        if obj is None:
            return self                                   # class access
        return obj.__dict__.get(self.name, "<unset>")     # instance access

    def __set__(self, obj: Any, value: Any) -> None:
        print(f"__set__(value={value!r})")
        obj.__dict__[self.name] = value                   # store value

    def __delete__(self, obj: Any) -> None:
        print("__delete__()")
        obj.__dict__.pop(self.name, None)                 # remove value


class Demo:
    x = Verbose()                                         # descriptor on the class


d = Demo()
print(d.x)                                                # __get__ with instance
d.x = 10                                                  # __set__
print(d.x)                                                # __get__ again
del d.x                                                   # __delete__
print(d.x)                                                # back to <unset>
print(Demo.x is Demo.__dict__["x"])                       # __get__ with obj=None returns descriptor

# Output:
# __get__(obj=inst, objtype=Demo)
# <unset>
# __set__(value=10)
# __get__(obj=inst, objtype=Demo)
# 10
# __delete__()
# __get__(obj=inst, objtype=Demo)
# <unset>
# __get__(obj=None, objtype=Demo)
# True
```
Why does it work even though the instance dict key and the descriptor share a name? Because the descriptor is a data descriptor, so its `__get__` is called before the instance dict is consulted.

## 💻 Code Example — Advanced
```python
# Production style: typed field with default, read-only field, protected delete, audit trail
from typing import Any, Generic, TypeVar                  # typing helpers

T = TypeVar("T")
AUDIT: list[str] = []                                     # a real app would write to a log/DB


class TypedField(Generic[T]):
    """Type-checked field with a default; logs every change."""

    def __init__(self, kind: type[T], default: T) -> None:
        self.kind: type[T] = kind                         # expected type
        self.default: T = default                         # value when never set

    def __set_name__(self, owner: type, name: str) -> None:
        self.name: str = name                             # public name
        self.storage: str = "_" + name                    # instance dict key

    def __get__(self, obj: Any, objtype: type | None = None) -> T:
        if obj is None:
            return self                                   # type: ignore[return-value]
        return obj.__dict__.get(self.storage, self.default)   # fall back to default

    def __set__(self, obj: Any, value: T) -> None:
        if not isinstance(value, self.kind):              # type check
            raise TypeError(f"{self.name} must be {self.kind.__name__}, got {type(value).__name__}")
        old: T = self.__get__(obj)                        # previous value
        obj.__dict__[self.storage] = value                # store
        AUDIT.append(f"{self.name}: {old!r} -> {value!r}")   # audit trail

    def __delete__(self, obj: Any) -> None:
        raise AttributeError(f"cannot delete {self.name}")   # protect important fields


class ReadOnly:
    """Data descriptor with __set__ that always refuses: makes a true read-only attribute."""

    def __init__(self, value: Any) -> None:
        self.value = value

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        return self.value

    def __set__(self, obj: Any, value: Any) -> None:
        raise AttributeError(f"{self.name} is read-only")


class Wallet:
    balance = TypedField(int, 0)                          # int only, default 0
    currency = ReadOnly("INR")                            # constant per class


w = Wallet()
print(w.balance, w.currency)                              # 0 INR
w.balance = 500
w.balance = 450
print(w.balance, AUDIT)
for action in ("w.balance = 'lots'", "w.currency = 'USD'", "del w.balance"):
    try:
        exec(action)                                      # demo only: run each failing statement
    except (TypeError, AttributeError) as e:
        print(type(e).__name__ + ":", e)

# Output:
# 0 INR
# 450 ['balance: 0 -> 500', 'balance: 500 -> 450']
# TypeError: balance must be int, got str
# AttributeError: currency is read-only
# AttributeError: cannot delete balance
```
Both blocks were run on Python 3.13.3 and the printed output is real. (`exec` is used only to keep the demo short; do not use it in production code.)

---

## 🟠 JavaScript vs Python Comparison

| Hook | Python descriptor | JavaScript equivalent |
|------|-------------------|-----------------------|
| Read | `__get__(self, obj, objtype)` | getter `get x()` / `Proxy` `get` trap |
| Write | `__set__(self, obj, value)` | setter `set x(v)` / `Proxy` `set` trap |
| Delete | `__delete__(self, obj)` | `Proxy` `deleteProperty` trap |
| Class-level access | `obj is None` in `__get__` | static members are separate |

```python
# Python way — all three hooks in one reusable class
class Tracked:
    def __set_name__(self, owner, name): self.n = name           # learn the name
    def __get__(self, o, t=None): return self if o is None else o.__dict__.get(self.n)
    def __set__(self, o, v): o.__dict__[self.n] = v              # write
    def __delete__(self, o): del o.__dict__[self.n]              # delete

class User:
    email = Tracked()
u = User(); u.email = "a@b.com"; del u.email
```
```javascript
// JavaScript way — Proxy traps give the same three hooks (per object, not per class field)
const u = new Proxy({}, {
  get: (t, k) => t[k],                       // read
  set: (t, k, v) => { t[k] = v; return true; },   // write
  deleteProperty: (t, k) => delete t[k],     // delete
});
u.email = "a@b.com"; delete u.email;
```

Key difference: a JavaScript Proxy wraps a whole object and intercepts every key. A Python descriptor is attached to one named class attribute and is shared by all instances, so per-instance data must be stored on the instance.

---

## 🟠 FastAPI Connection
Descriptors are handy for guarding application-level configuration or domain objects used inside routes. A read-only `__set__` raises `AttributeError`, which a route can translate into an HTTP `409 Conflict`.

```python
# FastAPI example — read-only config exposed by an API
from typing import Any                                      # any type
from fastapi import FastAPI, HTTPException                  # FastAPI parts
from fastapi.testclient import TestClient                   # in-process client


class ReadOnly:
    def __init__(self, value: Any) -> None:
        self.value = value                                  # constant value

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name                                    # attribute name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        return self.value                                   # always the constant

    def __set__(self, obj: Any, value: Any) -> None:
        raise AttributeError(f"{self.name} is read-only")   # forbid writes


class Config:
    api_version = ReadOnly("v1")                            # cannot be changed at runtime


cfg: Config = Config()
app: FastAPI = FastAPI()


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": cfg.api_version}                     # uses __get__


@app.put("/version/{v}")
def change(v: str) -> dict[str, str]:
    try:
        cfg.api_version = v                                 # triggers __set__ -> raises
    except AttributeError as e:
        raise HTTPException(status_code=409, detail=str(e))  # map to HTTP 409
    return {"version": cfg.api_version}


client = TestClient(app)
print(client.get("/version").json())                        # {'version': 'v1'}
r = client.put("/version/v2")
print(r.status_code, r.json())                              # 409 {'detail': 'api_version is read-only'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `__set__` storing with the same name -> infinite recursion
✅ Correct: store under a different key (`_x`) or use `obj.__dict__`

```python
class Rec:
    def __set__(self, o, v): setattr(o, "x", v)    # Wrong: setattr calls __set__ again
class A:
    x = Rec()
# A().x = 1   # RecursionError
# Right: o.__dict__["x"] = v   or   setattr(o, "_x", v)
```

❌ Mistake 2: Forgetting `if obj is None: return self` in `__get__`
✅ Correct: handle class-level access

```python
class NoneRet:
    def __get__(self, o, t=None): return 42     # Wrong: ignores o, so Class.attr also gives 42
class C:
    z = NoneRet()
print(C.z)                                      # 42  <- tools can no longer reach the descriptor
# Right: if o is None: return self
```

❌ Mistake 3: Defining `__set__` but no `__get__` and expecting the descriptor to return values
✅ Correct: implement `__get__` too, or the instance dict is read directly

```python
class OnlySet:
    def __set__(self, o, v): o.__dict__["y"] = v
class B:
    y = OnlySet()
b = B(); b.y = 5
print(type(b.y).__name__)       # int  <- read falls through to the instance dict
# Right: define __get__ so reads go through your logic (validation, defaults)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class Counter:
    def __init__(self):
        self.n = 0
    def __get__(self, o, t=None):
        self.n += 1
        return self.n

class M:
    c = Counter()

m = M()
print(m.c, m.c, M().c)
```
Answer: `1 2 3`. The descriptor object is created once and lives on the class, so it is shared by all instances. Every attribute read calls `__get__`, which increments the same `self.n`. Even a brand new `M()` instance continues the count. This shows why per-instance data must never be stored on `self` of the descriptor.

---

## ⚫ Interview Questions + Answers

Q1: What arguments does `__get__` receive and why is `obj` sometimes None?
A1: `(self, obj, objtype)`. `obj` is the instance, or `None` when the attribute is accessed on the class. `objtype` is the class. Return `self` for the class case.

Q2: Is the instance dict updated automatically by `__set__`?
A2: No. Python only calls your `__set__`. You must store the value yourself, usually in `obj.__dict__` or under a private name.

Q3: What happens if a data descriptor defines only `__set__`?
A3: Writes go through your logic, but reads are not intercepted: Python falls back to the instance dictionary (and then class attribute). Define `__get__` as well for predictable behaviour.

Q4: Why does a data descriptor beat the instance dictionary?
A4: The attribute lookup algorithm checks the class for a data descriptor first, before the instance `__dict__`. That is what makes validated fields and properties impossible to bypass by normal assignment.

Q5: How do I make an attribute truly read-only with descriptors?
A5: Implement `__get__` and a `__set__` that raises `AttributeError`. A descriptor with only `__get__` can still be shadowed by the instance dict.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need control over read, write and delete of an attribute
- The same rule is reused on many fields
- You are building a framework, ORM or validation layer

❌ Avoid when:
- A simple `@property` is enough for one attribute
- Pydantic or dataclass validators already cover the need
- You store state on the descriptor itself (a shared-state bug)

---

## 📊 Visual Diagram
```
d.x            ─►  type(d).x.__get__(d, Demo)         read
d.x = 10       ─►  type(d).x.__set__(d, 10)           write
del d.x        ─►  type(d).x.__delete__(d)            delete
Demo.x         ─►  type(d).x.__get__(None, Demo)      class access

 ┌────────── Demo (class) ──────────┐
 │ x = Verbose()  ◄── ONE object,   │   shared by every instance
 └──────────────────────────────────┘
   d1.__dict__ {"x": 10}   d2.__dict__ {"x": 99}      per-instance data lives here
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__get__` | Called on read | पढ़ने पर call होता है |
| `__set__` | Called on assignment | assign करने पर call होता है |
| `__delete__` | Called on `del` | `del` पर call होता है |
| `objtype` | The class of the instance | Instance की class |
| Read-only attribute | Descriptor whose `__set__` raises | जिसका `__set__` error देता है |
| Shared state | Data on the descriptor, common to all instances | Descriptor पर रखा data जो सब में common है |

---

## ⚡ 3-Line Summary
English: `__get__(obj, objtype)`, `__set__(obj, value)` and `__delete__(obj)` are the three hooks; `obj` is None for class access. Store per-instance data on the instance, never on the descriptor. A descriptor with `__set__` or `__delete__` beats the instance dictionary.
Hindi: `__get__(obj, objtype)`, `__set__(obj, value)` और `__delete__(obj)` तीन hooks हैं; class access में `obj` None होता है। Per-instance data instance पर रखें, descriptor पर कभी नहीं। `__set__` या `__delete__` वाला descriptor instance dictionary से ऊपर रहता है।

---

## ➡️ Next Topic
**153. Property vs Descriptor** — when the built-in `property` is enough and when to write your own descriptor.
