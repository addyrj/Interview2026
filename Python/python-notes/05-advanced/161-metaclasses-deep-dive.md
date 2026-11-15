---

# 161. Metaclasses — Deep Dive
# हिंदी में: Metaclasses — गहराई से (class बनाने वाली class)

---

## 🔵 Simple Definition (English)
A metaclass is the class of a class. Just as an object is created by its class, a class is created by its metaclass. The default metaclass is `type`. By writing your own metaclass you can change how classes are built: add attributes, validate the body, or register them.

## 🔵 सरल परिभाषा (Hindi)
Metaclass "class की class" है। जैसे object अपनी class से बनता है, वैसे class अपनी metaclass से बनती है। Default metaclass `type` है। अपनी metaclass लिखकर आप class बनने का तरीका बदल सकते हैं: attributes जोड़ना, body की जाँच करना या class को register करना।

---

## 🔴 Problem it Solves
Sometimes a rule must apply to every class in a family: "each plugin must define `run()`", "every model must be registered by name", "this class must have only one instance". Doing this by hand in each class is easy to forget. A metaclass runs at class-definition time, so the mistake is caught when the module is imported, not in production later. Frameworks (Django models, SQLAlchemy declarative, Pydantic, Enum, ABC) are built on this.

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी एक नियम पूरे class परिवार पर लगाना होता है: "हर plugin में `run()` हो", "हर model name से register हो", "इस class का सिर्फ एक instance हो"। हर class में हाथ से यह करना भूलना आसान है। Metaclass class बनते समय चलती है, इसलिए गलती module import होते ही पकड़ी जाती है, बाद में production में नहीं। Django models, SQLAlchemy declarative, Pydantic, Enum, ABC सब इसी पर बने हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python reads "class A(Base, metaclass=Meta):" and picks the metaclass
Step 2 → Meta.__prepare__(name, bases) returns the namespace dict (rarely changed)
Step 3 → The class body runs and fills that namespace
Step 4 → Meta(name, bases, namespace) is called:
           Meta.__new__ builds the class object, Meta.__init__ finishes it
Step 5 → The result is stored under the name "A"
Step 6 → Later, A() calls Meta.__call__, which calls A.__new__ then A.__init__
```

Rule of thumb: Metaclass `__new__`/`__init__` run once per class definition. Metaclass `__call__` runs on every instance creation.

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python "class A(Base, metaclass=Meta):" पढ़ता है और metaclass चुनता है
Step 2 → Meta.__prepare__(name, bases) namespace dict देता है (कम बदला जाता है)
Step 3 → Class body चलती है और namespace भरती है
Step 4 → Meta(name, bases, namespace) call होता है:
           Meta.__new__ class object बनाता है, Meta.__init__ उसे पूरा करता है
Step 5 → नतीजा "A" नाम से store हो जाता है
Step 6 → बाद में A() लिखने पर Meta.__call__ चलता है, जो A.__new__ फिर A.__init__ बुलाता है
```

सूत्र: Metaclass के `__new__`/`__init__` हर class definition पर एक बार चलते हैं। Metaclass का `__call__` हर instance बनने पर चलता है।

---

## 🟡 Real World Example
A payments service has many gateway plugins (Razorpay, Stripe, PayU). A metaclass registers each plugin by name, so the checkout code can do `registry["razorpay"]()`, and it refuses to import a plugin that forgot to implement `run()`. Django's `Model`, SQLAlchemy's declarative base and Pydantic's `BaseModel` collect field definitions the same way.

## 🟡 Real Example Hindi mein
Payments service में कई gateway plugins हैं (Razorpay, Stripe, PayU)। Metaclass हर plugin को नाम से register करती है, ताकि checkout code `registry["razorpay"]()` लिख सके, और जिस plugin में `run()` नहीं है उसे import ही नहीं होने देती। Django का `Model`, SQLAlchemy का declarative base और Pydantic का `BaseModel` भी fields इसी तरह इकट्ठा करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic metaclass examples
class Meta(type):                                 # a metaclass inherits from type
    def __new__(mcs, name: str, bases: tuple, ns: dict):   # runs when a class is CREATED
        print(f"creating class {name}")           # see creation time
        ns["created_by"] = "Meta"                 # add an attribute to every class
        return super().__new__(mcs, name, bases, ns)   # build the class object


class A(metaclass=Meta):                          # use Meta to build A
    pass                                          # empty body


print(A.created_by)                               # attribute added by the metaclass
print(type(A), type(A()))                         # class of A is Meta, class of A() is A

B = type("B", (), {"x": 1, "hello": lambda self: "hi"})   # type() can build classes dynamically
print(B().hello(), B.x, B.__name__)               # works like a normal class
print(type(type))                                 # type is its own metaclass

# Output:
# creating class A
# Meta
# <class '__main__.Meta'> <class '__main__.A'>
# hi 1 B
# <class 'type'>
```

## 💻 Code Example — Advanced
```python
# Production style: registry, validation, singleton via __call__, __init_subclass__
from typing import Any                            # type for generic kwargs


class PluginMeta(type):
    """Auto-register every concrete plugin and validate the interface."""

    registry: dict[str, type] = {}                # shared plugin registry

    def __new__(mcs, name: str, bases: tuple[type, ...], ns: dict[str, Any]) -> "PluginMeta":
        cls = super().__new__(mcs, name, bases, ns)   # create the class first
        if bases:                                 # skip the abstract Base itself
            if "run" not in ns:                   # enforce the interface
                raise TypeError(f"{name} must define run()")   # fail at class definition time
            mcs.registry[name.lower()] = cls      # register by lowercase name
        return cls                                # return the finished class


class Plugin(metaclass=PluginMeta):               # base class, no run() needed
    pass


class Email(Plugin):                              # concrete plugin
    def run(self) -> str:
        return "sending email"                    # pretend work


class Sms(Plugin):                                # another plugin
    def run(self) -> str:
        return "sending sms"


print(sorted(PluginMeta.registry))                # ['email', 'sms']
print(PluginMeta.registry["sms"]().run())         # build plugin by name

try:                                              # missing run() must fail early
    class Broken(Plugin):                         # no run() here
        pass
except TypeError as e:                            # caught while defining the class
    print("TypeError:", e)


class Singleton(type):
    """Metaclass making each class a singleton by overriding __call__."""

    _instances: dict[type, Any] = {}              # one instance per class

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:   # runs on Settings()
        if cls not in Singleton._instances:       # first call only
            Singleton._instances[cls] = super().__call__(*args, **kwargs)   # build once
        return Singleton._instances[cls]          # always the same object


class Settings(metaclass=Singleton):              # app-wide settings
    def __init__(self) -> None:
        print("loading settings once")            # prints only once


print(Settings() is Settings())                   # True


class Base:                                       # the modern lightweight alternative
    subclasses: list[type] = []                   # list of children

    def __init_subclass__(cls, **kwargs: Any) -> None:   # called for each subclass
        super().__init_subclass__(**kwargs)       # keep the chain working
        Base.subclasses.append(cls)               # record child


class Child1(Base): ...                           # auto recorded
class Child2(Base): ...                           # auto recorded
print([c.__name__ for c in Base.subclasses])      # ['Child1', 'Child2']

class M1(type): ...                               # metaclass 1
class M2(type): ...                               # metaclass 2
class X(metaclass=M1): ...                        # class with M1
class Y(metaclass=M2): ...                        # class with M2
try:                                              # mixing unrelated metaclasses
    class Z(X, Y): ...                            # conflict
except TypeError as e:                            # Python refuses
    print("TypeError:", str(e)[:48])              # metaclass conflict message

# Output:
# ['email', 'sms']
# sending sms
# TypeError: Broken must define run()
# loading settings once
# True
# ['Child1', 'Child2']
# TypeError: metaclass conflict: the metaclass of a derived c
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Class of a class | metaclass (`type`) | `Function` constructor (no real equivalent) |
| Hook at class creation | `__new__` of metaclass, `__init_subclass__` | decorators, `static {}` blocks |
| Build class dynamically | `type("A", (), {...})` | `class` expression, `Object.setPrototypeOf` |
| Intercept instantiation | metaclass `__call__` | `Proxy` with `construct` trap |

```python
# Python way
Dyn = type("Dyn", (), {"x": 1})                 # create a class at runtime
print(Dyn().x)                                  # 1
```
```javascript
// JavaScript way
const Dyn = class { x = 1 };                    // class expression, no metaclass concept
console.log(new Dyn().x);                       // 1
const P = new Proxy(Dyn, { construct(t, a) { console.log("creating"); return new t(...a); } });
new P();                                        // Proxy intercepts construction
```

Key difference: in JavaScript classes are special function objects and you rarely customise how classes themselves are built. In Python classes are normal objects created by `type(...)`, so you can customise that process.

---

## 🟠 FastAPI Connection
FastAPI request and response bodies are Pydantic models. `BaseModel` uses a metaclass (`ModelMetaclass`) that reads annotations when the class is defined and builds validators and a JSON schema. That is why FastAPI can generate OpenAPI docs from a plain class.

```python
# FastAPI/Pydantic: BaseModel itself is built by a metaclass
from fastapi import FastAPI                       # FastAPI app
from fastapi.testclient import TestClient         # in-process client
from pydantic import BaseModel                    # uses ModelMetaclass internally


class User(BaseModel):                            # fields are read at CLASS creation time
    name: str                                     # required string
    age: int = 18                                 # optional int


print(type(User).__name__)                        # the metaclass of every pydantic model
print(list(User.model_fields))                    # metaclass collected the fields

app: FastAPI = FastAPI()                          # create app


@app.post("/users")                               # POST /users
def create(user: User) -> User:                   # body validated by the generated schema
    return user                                   # echo back


client: TestClient = TestClient(app)              # test client
print(client.post("/users", json={"name": "Asha"}).json())   # default age applied

# Output:
# ModelMetaclass
# ['name', 'age']
# {'name': 'Asha', 'age': 18}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a metaclass when a simpler tool works
✅ Correct: try `__init_subclass__` or a class decorator first

```python
# Wrong - heavy
class Meta(type):
    def __init__(cls, n, b, d):
        super().__init__(n, b, d); print("registered", n)
# Right - simple (3.6+)
class Base:
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw); print("registered", cls.__name__)
class A(Base): ...                              # prints: registered A
```

❌ Mistake 2: Forgetting to call `super().__new__` and return the class
✅ Correct: always `return super().__new__(mcs, name, bases, ns)`

```python
class Meta(type):
    def __new__(mcs, name, bases, ns):
        # Wrong - returns None, so the class name becomes None
        # print("hi")
        # Right
        return super().__new__(mcs, name, bases, ns)
```

❌ Mistake 3: Mixing two unrelated metaclasses in multiple inheritance
✅ Correct: make a combined metaclass that inherits both

```python
class M1(type): ...
class M2(type): ...
class Both(M1, M2): ...                         # combined metaclass
class X(metaclass=M1): ...
class Y(metaclass=M2): ...
class Z(X, Y, metaclass=Both): ...              # works now
```

❌ Mistake 4: Overriding `__call__` and forgetting to forward arguments
✅ Correct: `return super().__call__(*args, **kwargs)`

---

## 🧠 Tricky Interview Question

```python
# What will this output? (order matters)
class M(type):
    def __call__(cls, *a, **k):
        print("M.__call__"); return super().__call__(*a, **k)
    def __new__(m, n, b, d):
        print("M.__new__"); return super().__new__(m, n, b, d)
    def __init__(c, n, b, d):
        print("M.__init__"); super().__init__(n, b, d)
class A(metaclass=M):
    def __new__(cls):
        print("A.__new__"); return super().__new__(cls)
    def __init__(self): print("A.__init__")
print("--")
A()
```
Answer (verified on 3.13):
```
M.__new__
M.__init__
--
M.__call__
A.__new__
A.__init__
```
`M.__new__` and `M.__init__` run once when the class `A` is defined (before the `--`). `A()` goes through `M.__call__` first, which then runs `A.__new__` and `A.__init__`.

---

## ⚫ Interview Questions + Answers

Q1: What is the type of a class? What is the type of `type`?
A1: The type of a normal class is `type` (its metaclass). `type(type)` is `type`, so `type` is its own metaclass. Everything is an object, and every class is an instance of `type` or of a subclass of it.

Q2: Metaclass `__new__` vs `__init__`?
A2: `__new__` creates the class object and can change the name, bases or namespace before creation. `__init__` receives the finished class and can only modify it. Use `__new__` when you must alter the namespace.

Q3: When is a metaclass really needed?
A3: When you must change how instances are created at class level (`__call__`), customise the namespace (`__prepare__`, for example ordered or special dicts), or when a framework must read the class body. For registration or validation, `__init_subclass__` is usually enough.

Q4: How does a metaclass singleton work?
A4: Override `__call__` on the metaclass. Check a dict of instances per class, create once with `super().__call__`, and return the stored object afterwards. Unlike the `__new__` singleton, `__init__` is not re-run.

Q5: What is a "metaclass conflict"?
A5: When a class inherits from classes with different, unrelated metaclasses, Python cannot choose one. Fix it with a metaclass that inherits from both.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building a framework (ORM, serializer, plugin system)
- You must intercept instance creation for every class in a family
- Custom namespace is needed through `__prepare__`

❌ Avoid when:
- `__init_subclass__`, a class decorator, a descriptor or a plain function solves it
- The team is not familiar with metaclasses (hard to debug and read)
- You only need validation of one class (use `dataclass` or Pydantic)

---

## 📊 Visual Diagram
```
 instance  a  ──is an instance of──►  class A  ──is an instance of──►  metaclass Meta (or type)
                                                                            │
                                                                            ▼
                                                        type  ──is an instance of──► type (itself)

 class A(metaclass=Meta):
     body runs -> namespace dict
          │
          ▼
 Meta.__new__(Meta, "A", bases, ns) -> class object A
 Meta.__init__(A, "A", bases, ns)
 A()  ->  Meta.__call__(A)  ->  A.__new__  ->  A.__init__
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metaclass | Class whose instances are classes | class की class |
| `type` | Default metaclass | default metaclass |
| `__prepare__` | Returns the namespace used for the class body | class body का namespace देता है |
| `__init_subclass__` | Simple hook run for each subclass | हर subclass पर चलने वाला हल्का hook |
| Registry | Dict of classes by name | नाम से classes की dict |
| Singleton | Only one instance exists | केवल एक instance |

---

## ⚡ 3-Line Summary
English: A metaclass builds classes the way a class builds objects; the default is `type`. Its `__new__`/`__init__` run once per class, its `__call__` runs per instance. Prefer `__init_subclass__` when it is enough.
Hindi: Metaclass classes को वैसे बनाती है जैसे class objects को; default `type` है। इसके `__new__`/`__init__` हर class पर एक बार और `__call__` हर instance पर चलते हैं। जहाँ काफी हो वहाँ `__init_subclass__` को प्राथमिकता दें।

---

## ➡️ Next Topic
**162. __new__ vs __init__** — who creates the object and who fills it, and when to override each.
