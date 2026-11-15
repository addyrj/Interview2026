---

# 166. Introspection in Python
# हिंदी में: Introspection (चलते समय object को जाँचना)

---

## 🔵 Simple Definition (English)
Introspection means a program can examine itself while running: ask an object its type, its attributes, its methods, its docstring or its parent classes. Python makes everything an object, so almost everything can be inspected with tools like `type`, `dir`, `isinstance`, `hasattr`, `callable` and the `inspect` module.

## 🔵 सरल परिभाषा (Hindi)
Introspection का मतलब है कि program चलते समय खुद को जाँच सकता है: किसी object से उसका type, attributes, methods, docstring या parent classes पूछना। Python में सब कुछ object है, इसलिए `type`, `dir`, `isinstance`, `hasattr`, `callable` और `inspect` module से लगभग सब कुछ जाँचा जा सकता है।

---

## 🔴 Problem it Solves
Code often receives objects whose shape it does not know in advance: plugins, JSON models, function arguments, library classes. Without introspection you would hard-code every case. With it you can write generic code: serialisers, validators, dependency injection, auto-documentation, debuggers, REPL helpers. It also helps you explore unknown libraries quickly (`dir(obj)`, `help(obj)`).

## 🔴 यह क्यों बना? (Hindi)
Code को अक्सर ऐसे objects मिलते हैं जिनकी बनावट पहले से पता नहीं होती: plugins, JSON models, function arguments, library classes। Introspection के बिना हर case hard-code करना पड़ता। इससे आप generic code लिख सकते हैं: serialisers, validators, dependency injection, auto-documentation, debuggers, REPL helpers। अनजान libraries को जल्दी समझने में भी मदद मिलती है (`dir(obj)`, `help(obj)`)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Every object stores metadata: __class__, __dict__, __doc__, __module__
Step 2 → Every class stores: __name__, __mro__ (parent order), __bases__
Step 3 → Every function stores: __name__, __code__, __defaults__, __annotations__
Step 4 → Builtins read this data:
           type(x)          -> class of x
           isinstance(x, C) -> is x an instance of C (or a subclass)?
           dir(x)           -> names reachable on x
           hasattr/getattr  -> look up an attribute by string name
           callable(x)      -> can x be called?
Step 5 → inspect module combines these into friendly tools (signature, getmembers)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर object metadata रखता है: __class__, __dict__, __doc__, __module__
Step 2 → हर class रखती है: __name__, __mro__ (parent क्रम), __bases__
Step 3 → हर function रखता है: __name__, __code__, __defaults__, __annotations__
Step 4 → Builtins यही data पढ़ते हैं:
           type(x)          -> x की class
           isinstance(x, C) -> क्या x, C (या उसकी subclass) का instance है?
           dir(x)           -> x पर पहुँचने लायक नाम
           hasattr/getattr  -> string नाम से attribute ढूँढना
           callable(x)      -> क्या x को call किया जा सकता है?
Step 5 → inspect module इन्हें आसान tools में जोड़ता है (signature, getmembers)
```

---

## 🟡 Real World Example
An admin dashboard auto-generates a form for any SQLAlchemy model by inspecting its columns and type hints. A plugin loader scans a folder, imports each module, and uses `hasattr(mod, "run")` plus `callable` to decide if it is a valid plugin. A debugging helper prints the class, parent classes and public methods of any object when a production bug appears.

## 🟡 Real Example Hindi mein
Admin dashboard किसी भी SQLAlchemy model का form अपने आप बनाता है, उसके columns और type hints को जाँचकर। Plugin loader folder scan करता है, हर module import करता है और `hasattr(mod, "run")` व `callable` से तय करता है कि वह valid plugin है या नहीं। Production में bug आने पर debugging helper किसी भी object की class, parent classes और public methods print कर देता है।

---

## 💻 Code Example — Basic
```python
# Basic introspection
class User:
    """A user."""                                 # docstring is introspectable

    def __init__(self, name: str) -> None:
        self.name: str = name                     # instance attribute

    def greet(self) -> str:
        return f"hi {self.name}"                  # method


u: User = User("Asha")                            # object
print(type(u).__name__, u.__class__ is User)      # User True
print(User.__doc__, User.__module__)              # A user. __main__
print(isinstance(u, User), issubclass(User, object))   # True True
print(callable(u.greet), callable(u))             # True False
print([a for a in dir(u) if not a.startswith("_")])    # ['greet', 'name']
print(hasattr(u, "name"), getattr(u, "age", "n/a"))    # True n/a
print(u.greet.__name__, u.greet.__self__ is u)    # greet True
print(User.__mro__)                               # method resolution order

# Output:
# User True
# A user. __main__
# True True
# True False
# ['greet', 'name']
# True n/a
# greet True
# (<class '__main__.User'>, <class 'object'>)
```

## 💻 Code Example — Advanced
```python
# Production style: auto-generated "describe" for any object
import inspect                                    # deeper introspection
from typing import Any, get_type_hints            # annotations


class Payment:
    """Charge a customer."""

    gateway: str = "razorpay"                     # class attribute

    def __init__(self, amount: int, currency: str = "INR") -> None:
        self.amount: int = amount                 # instance attribute
        self.currency: str = currency

    def charge(self, retries: int = 3) -> bool:   # public method
        """Try to charge."""
        return True

    def _audit(self) -> None: ...                 # private helper


def describe(obj: Any) -> dict[str, Any]:
    """Return a structured description of obj."""
    cls: type = obj if inspect.isclass(obj) else type(obj)   # accept class or instance
    methods: dict[str, str] = {
        n: str(inspect.signature(m))              # signature as text
        for n, m in inspect.getmembers(cls, inspect.isfunction)
        if not n.startswith("_")                  # public only
    }
    return {
        "name": cls.__name__,                     # class name
        "doc": inspect.getdoc(cls),               # cleaned docstring
        "bases": [b.__name__ for b in cls.__mro__[1:-1]],   # parents except object
        "methods": methods,                       # name -> signature
        "hints": get_type_hints(cls.__init__),    # constructor annotations
        "fields": vars(obj) if not inspect.isclass(obj) else {},   # instance data
    }


info = describe(Payment(500))                     # describe an instance
for k, v in info.items():                         # print neatly
    print(k, "=", v)

print(hasattr(Payment, "refund"))                 # False -> feature detection
print(getattr(Payment(1), "gateway"))             # razorpay (class attr via instance)


def tracer(frame_depth: int = 1) -> str:
    """Return the name of the calling function."""
    return inspect.stack()[frame_depth].function  # who called me?


def checkout() -> str:
    return tracer()                               # asks: who is my caller


print(checkout())                                 # checkout

# Output:
# name = Payment
# doc = Charge a customer.
# bases = []
# methods = {'charge': '(self, retries: int = 3) -> bool'}
# hints = {'amount': <class 'int'>, 'currency': <class 'str'>, 'return': <class 'NoneType'>}
# fields = {'amount': 500, 'currency': 'INR'}
# False
# razorpay
# checkout
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Type of value | `type(x)` | `typeof x` / `x.constructor` |
| Is instance? | `isinstance(x, C)` | `x instanceof C` |
| List attributes | `dir(x)` / `vars(x)` | `Object.keys(x)` / `Object.getOwnPropertyNames(x)` |
| Has attribute? | `hasattr(x, "a")` | `"a" in x` / `x.hasOwnProperty("a")` |
| Function parameters | `inspect.signature(f)` | `f.length` / parse `f.toString()` |
| Parent chain | `C.__mro__` | `Object.getPrototypeOf(x)` |

```python
# Python way
class A:
    x = 1
print(type(A()).__name__, hasattr(A, "x"), callable(A))    # A True True
```
```javascript
// JavaScript way
class A { x = 1 }
const a = new A();
console.log(a.constructor.name, "x" in a, typeof A === "function");   // A true true
```

Key difference: Python can describe a function's full parameter list with names, defaults and annotations (`inspect.signature`). In JavaScript, `f.length` only gives a count and you cannot read parameter names without parsing the source.

---

## 🟠 FastAPI Connection
FastAPI is introspection-heavy: it reads each route function's signature and type hints to decide which parameters come from the path, query, body or `Depends`. That is how `item_id: int` becomes a validated path parameter without extra code.

```python
# FastAPI: /schema endpoint built purely from introspection
import inspect                                    # signature
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # in-process client

app: FastAPI = FastAPI()                          # create app


@app.get("/items/{item_id}")                      # route with a path param
def read_item(item_id: int, q: str | None = None) -> dict[str, object]:
    return {"item_id": item_id, "q": q}


@app.get("/introspect")                           # lists parameter info of every route
def introspect() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}                # route -> params
    for route in app.routes:                      # every registered route
        endpoint = getattr(route, "endpoint", None)   # the Python function
        if endpoint is read_item:                 # only our demo route
            out[route.path] = list(inspect.signature(endpoint).parameters)   # parameter names
    return out


client: TestClient = TestClient(app)              # test client
print(client.get("/introspect").json())           # {'/items/{item_id}': ['item_id', 'q']}
print(client.get("/items/7", params={"q": "x"}).json())   # FastAPI read the same signature

# Output:
# {'/items/{item_id}': ['item_id', 'q']}
# {'item_id': 7, 'q': 'x'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Checking types with `type(x) == C`
✅ Correct: use `isinstance(x, C)` so subclasses work

```python
class A: ...
class B(A): ...
b = B()
print(type(b) == A, isinstance(b, A))           # False True
```

❌ Mistake 2: Using `hasattr` with a property that has side effects
✅ Correct: `hasattr` actually runs the property; check the class (`hasattr(type(x), "name")`) or use `inspect.getattr_static`

❌ Mistake 3: Relying on `dir()` to be complete
✅ Correct: it is a convenience listing; classes may define `__dir__` or `__getattr__` that creates names dynamically

❌ Mistake 4: Using introspection in hot loops
✅ Correct: cache the result (e.g. compute `inspect.signature` once at startup)

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    x = 1
a = A(); a.y = 2
print(hasattr(A, 'y'), hasattr(a, 'x'), 'x' in vars(a),
      isinstance(A, type), isinstance(type, type),
      isinstance(object, type), isinstance(type, object))
```
Answer (verified on 3.13): `False True False True True True True`. `y` is on the instance only. `x` lives on the class but is reachable through the instance, so `hasattr(a, "x")` is True while `vars(a)` shows only `y`. A class is an instance of `type`, `type` is an instance of itself, and `object` is an instance of `type`, while `type` is also a subclass of `object`, so both circular statements hold.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `type()` and `isinstance()`?
A1: `type(x)` returns the exact class. `isinstance(x, C)` is true for `C` and all its subclasses, and accepts a tuple of classes. Prefer `isinstance`.

Q2: How do you list all methods of an object?
A2: `[n for n in dir(obj) if callable(getattr(obj, n))]`, or `inspect.getmembers(obj, inspect.isroutine)`.

Q3: What does `callable()` check?
A3: Whether the object can be called with `()`: functions, classes, lambdas and instances whose class defines `__call__`.

Q4: What is duck typing and how does introspection relate?
A4: Python cares about behaviour, not declared type. `hasattr(x, "read")` or try/except is the duck-typing check. For static contracts use `typing.Protocol`.

Q5: What is the MRO and how can you see it?
A5: The method resolution order is the list of classes Python searches for attributes, computed by C3 linearisation. See it with `C.__mro__` or `C.mro()`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing frameworks, plugins, serialisers and DI containers
- Debugging or exploring unknown objects (`dir`, `help`)
- Feature detection (`hasattr`) instead of version checks

❌ Avoid when:
- Normal business logic where types are known
- Hot code paths (introspection is slower than direct access)
- Static typing (Protocol, TypedDict) expresses the same contract better

---

## 📊 Visual Diagram
```
 object u ──► type(u) -> User ──► User.__mro__ -> (User, object)
   │              │
   │              ├─ User.__name__, User.__doc__, User.__module__
   │              └─ User.__dict__ : methods, class attributes
   ├─ u.__dict__  : instance attributes
   └─ dir(u)      : instance + class + parents (merged, sorted)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Introspection | Examining objects at runtime | चलते समय object जाँचना |
| `type()` | Exact class of an object | object की सटीक class |
| `isinstance()` | Class or subclass check | class या subclass जाँच |
| `dir()` | Lists reachable names | पहुँच योग्य नामों की सूची |
| MRO | Attribute search order | attribute खोजने का क्रम |
| Duck typing | Judge by behaviour | व्यवहार से पहचानना |

---

## ⚡ 3-Line Summary
English: Introspection lets code examine objects at runtime with `type`, `isinstance`, `dir`, `hasattr` and `callable`. It powers frameworks like FastAPI. Prefer `isinstance` over `type ==`, and cache results.
Hindi: Introspection से code चलते समय `type`, `isinstance`, `dir`, `hasattr` और `callable` से objects जाँच सकता है। FastAPI जैसे frameworks इसी पर चलते हैं। `type ==` की जगह `isinstance` चुनें और नतीजे cache करें।

---

## ➡️ Next Topic
**167. inspect Module** — signatures, source code, frames and members in one toolbox.
