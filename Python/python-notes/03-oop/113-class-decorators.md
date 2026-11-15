---

# 113. Class Decorators
# हिंदी में: Class Decorators (Class को सजाना / बदलना)

---

## 🔵 Simple Definition (English)
A class decorator is a function that receives a class, may change or wrap it, and returns a class (usually the same one). Writing `@decorator` above `class Foo:` is the same as `Foo = decorator(Foo)`. `@dataclass` is the most famous example.

## 🔵 सरल परिभाषा (Hindi)
Class decorator एक function है जो class लेता है, उसे बदल या wrap कर सकता है, और class लौटाता है (आमतौर पर वही class)। `class Foo:` के ऊपर `@decorator` लिखना `Foo = decorator(Foo)` के बराबर है। `@dataclass` सबसे मशहूर उदाहरण है।

---

## 🔴 Problem it Solves
You want to add the same behavior to many classes: register them, add a `to_json` method, count instances, make them singletons, or log every method call. Copying that code into each class is repetitive, and inheritance forces a shared base class that may not fit. A metaclass is overkill. A class decorator is a short, explicit, reusable function that is applied only to the classes that need it.

## 🔴 यह क्यों बना? (Hindi)
आप कई classes में वही behavior जोड़ना चाहते हो: उन्हें register करना, `to_json` method जोड़ना, instances गिनना, singleton बनाना, या हर method call log करना। हर class में वही code copy करना दोहराव है, और inheritance एक shared base class थोप देती है जो हमेशा fit नहीं होती। Metaclass जरूरत से ज्यादा भारी है। Class decorator छोटा, साफ और reusable function है जो सिर्फ उन्हीं classes पर लगता है जिन्हें चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a function: def deco(cls): ...; return cls
Step 2 → Python builds the class normally (body runs, class object is made)
Step 3 → Then it calls deco(cls) with the finished class
Step 4 → The decorator can: add attributes/methods, wrap methods,
         register the class, or even return a different class
Step 5 → The returned object is bound to the class name
Step 6 → Parameterized form: @deco(option=1) -> deco(option=1) returns the real decorator

@deco
class Foo: ...        ==>     class Foo: ...      Foo = deco(Foo)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → function लिखें: def deco(cls): ...; return cls
Step 2 → Python class को सामान्य तरीके से बनाता है (body चलती है, class object बनता है)
Step 3 → फिर वह तैयार class के साथ deco(cls) call करता है
Step 4 → Decorator attributes/methods जोड़ सकता है, methods wrap कर सकता है,
         class register कर सकता है, या कोई दूसरी class भी लौटा सकता है
Step 5 → जो लौटता है वही class के नाम से bind हो जाता है
Step 6 → Parameter वाला रूप: @deco(option=1) -> deco(option=1) असली decorator लौटाता है

@deco
class Foo: ...        ==>     class Foo: ...      Foo = deco(Foo)
```

---

## 🟡 Real World Example
A payment backend marks each handler class with `@register("upi")` so a router can find it by name. A reporting service adds `@auditable` to models so every `save()` is logged with the user and time. `@dataclass`, `@total_ordering` (from `functools`) and `@final` are class decorators in the standard library. A config class can be turned into a singleton with `@singleton` so the app reads the file only once.

## 🟡 Real Example Hindi mein
Payment backend हर handler class पर `@register("upi")` लगाता है ताकि router उसे नाम से ढूंढ सके। Reporting service models पर `@auditable` लगाती है ताकि हर `save()` user और समय के साथ log हो। `@dataclass`, `@total_ordering` (`functools` से) और `@final` standard library के class decorators हैं। Config class को `@singleton` से singleton बनाया जा सकता है ताकि app file सिर्फ एक बार पढ़े।

---

## 💻 Code Example — Basic
```python
# Basic class decorator examples
from typing import Any, Callable, TypeVar         # type hints

T = TypeVar("T", bound=type)                      # any class type


def add_hello(cls: T) -> T:                       # receives the class
    cls.hello = lambda self: f"Hello from {type(self).__name__}"   # attach a new method
    return cls                                    # return the same class


def register(registry: dict[str, type]) -> Callable[[T], T]:      # decorator WITH arguments
    def wrapper(cls: T) -> T:                     # the real decorator
        registry[cls.__name__.lower()] = cls      # store the class by name
        return cls                                # unchanged class
    return wrapper                                # hand it to Python


plugins: dict[str, type] = {}                     # our registry


@add_hello                                        # same as Greeter = add_hello(Greeter)
class Greeter:
    pass


@register(plugins)                                # decorator factory is called first
class Upi:
    pass


@register(plugins)
class Card:
    pass


print(Greeter().hello())                          # method added by the decorator
print(sorted(plugins))                            # both classes are registered
print(plugins["upi"] is Upi)                      # decorator returned the same class

# Manual form shows there is no magic
class Plain:
    pass


Plain = add_hello(Plain)                          # exactly what @add_hello does
print(Plain().hello())                            # works the same

# Output:
# Hello from Greeter
# ['card', 'upi']
# True
# Hello from Plain
```

## 💻 Code Example — Advanced
```python
# Production style: singleton, auditing wrapper, instance counter, functools.total_ordering
import functools                                  # wraps, total_ordering
import time                                       # for timing
from typing import Any, Callable, TypeVar         # type hints

T = TypeVar("T")                                  # generic class type


def singleton(cls: type[T]) -> Callable[..., T]:
    """Make a class return the same instance every time."""
    instances: dict[type, T] = {}                 # one instance per class

    @functools.wraps(cls, updated=())             # copy __name__, __doc__ onto the wrapper
    def get_instance(*args: Any, **kwargs: Any) -> T:
        if cls not in instances:                  # first call
            instances[cls] = cls(*args, **kwargs) # create and remember
        return instances[cls]                     # always the same object

    return get_instance                           # NOTE: Config is now a function, not a class


def audited(*method_names: str) -> Callable[[type[T]], type[T]]:
    """Wrap the named methods so each call is logged with its duration."""
    def decorate(cls: type[T]) -> type[T]:
        for name in method_names:                 # for each method to wrap
            original = getattr(cls, name)         # get the plain function

            @functools.wraps(original)            # keep the method's metadata
            def wrapper(self: Any, *a: Any, _orig: Callable = original, _n: str = name, **k: Any) -> Any:
                start = time.perf_counter()       # begin timing
                try:
                    return _orig(self, *a, **k)   # call the real method
                finally:                          # always log, even on error
                    ms = (time.perf_counter() - start) * 1000
                    print(f"[audit] {cls.__name__}.{_n} took {ms >= 0}")   # prints True (time varies)

            setattr(cls, name, wrapper)           # replace the method on the class
        return cls                                # same class, upgraded methods
    return decorate


def count_instances(cls: type[T]) -> type[T]:
    """Add a class-level counter incremented on every creation."""
    original_init = cls.__init__                  # remember the real __init__
    cls.created = 0                               # type: ignore[attr-defined]

    @functools.wraps(original_init)
    def new_init(self: Any, *a: Any, **k: Any) -> None:
        type(self).created += 1                   # count first
        original_init(self, *a, **k)              # then run the real __init__

    cls.__init__ = new_init                       # type: ignore[method-assign]
    return cls


@singleton
class Config:
    """App configuration (read once)."""
    def __init__(self, env: str = "dev") -> None:
        print("loading config")                   # proves __init__ runs once
        self.env: str = env


a, b = Config("prod"), Config("dev")              # second call ignores its arguments
print(a is b, a.env)                              # True prod
print(Config.__name__, Config.__doc__)            # metadata copied by wraps


@audited("pay")
@count_instances
class Gateway:
    def __init__(self, name: str) -> None:
        self.name: str = name

    def pay(self, amount: int) -> str:
        return f"{self.name} paid {amount}"


g1, g2 = Gateway("razorpay"), Gateway("paytm")    # two instances
print(g1.pay(100))                                # logged call
print(Gateway.created)                            # 2


@functools.total_ordering                         # stdlib class decorator: fills in <=, >, >=
class Version:
    def __init__(self, n: int) -> None:
        self.n: int = n

    def __eq__(self, other: object) -> bool:      # needed by total_ordering
        return isinstance(other, Version) and self.n == other.n

    def __lt__(self, other: "Version") -> bool:   # the one ordering method we write
        return self.n < other.n


print(Version(2) > Version(1), Version(1) <= Version(1))   # True True

# Output:
# loading config
# True prod
# Config App configuration (read once).
# [audit] Gateway.pay took True
# razorpay paid 100
# 2
# True True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Class decorator | `@deco class A` (stable, built in) | TC39 decorators (new, TS/Babel) |
| Meaning | `A = deco(A)` | `A = deco(A, context)` |
| Function wrapper | very common | higher-order function |
| Use case | register, add methods, singleton | Angular `@Component`, NestJS `@Injectable` |

```python
# Python way
def with_id(cls):
    cls.id = 42                              # add a class attribute
    return cls                               # must return the class

@with_id
class A:
    pass

print(A.id)                                  # 42
```
```javascript
// JavaScript way (works today without decorator syntax)
const withId = (cls) => { cls.id = 42; return cls; };   // plain higher-order function
const A = withId(class A {});                           // manual application
console.log(A.id);                                      // 42
// With TypeScript/NestJS: @Injectable() class UserService {}  (decorator syntax)
```

Key difference: Python has had decorator syntax for classes since 3.0 and uses it everywhere (`@dataclass`). In JavaScript it is newer and mostly seen through Angular/NestJS, but the idea - a function that takes a class and returns a class - is identical.

---

## 🟠 FastAPI Connection
FastAPI itself decorates functions (`@app.get`), but class decorators help around it: registering service classes, turning Pydantic-free data holders into `@dataclass`, and creating settings singletons. Note that `@lru_cache` on a function returning settings is the common FastAPI singleton, and `@dataclass` classes are valid FastAPI models.

```python
# FastAPI example - registry decorator for services, resolved by name
from typing import Callable                       # types
from fastapi import FastAPI, HTTPException        # app and errors
from fastapi.testclient import TestClient         # tests

services: dict[str, type] = {}                    # name -> class


def service(name: str) -> Callable[[type], type]: # class decorator factory
    def deco(cls: type) -> type:
        services[name] = cls                      # register
        return cls                                # unchanged
    return deco


@service("upi")                                   # registered at import time
class UpiService:
    def pay(self, amount: int) -> str:
        return f"UPI paid {amount}"


@service("card")
class CardService:
    def pay(self, amount: int) -> str:
        return f"Card paid {amount}"


app: FastAPI = FastAPI()                          # create app


@app.post("/pay/{method}")                        # POST /pay/upi?amount=100
def pay(method: str, amount: int) -> dict[str, str]:
    cls = services.get(method)                    # find service
    if cls is None:                               # unknown method
        raise HTTPException(404, "unknown payment method")
    return {"message": cls().pay(amount)}         # use it


client: TestClient = TestClient(app)              # client
print(client.post("/pay/upi", params={"amount": 100}).json())
print(client.post("/pay/cash", params={"amount": 100}).status_code)

# Output:
# {'message': 'UPI paid 100'}
# 404
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to return the class
✅ Correct: always `return cls`

```python
def bad(cls):
    cls.x = 1            # Wrong: no return -> name becomes None
@bad
class A: pass
print(A)                 # None
def good(cls):
    cls.x = 1
    return cls           # Right
@good
class B: pass
print(B)                 # <class '__main__.B'>
```

❌ Mistake 2: `@deco` vs `@deco()` confusion for decorators with arguments
✅ Correct: a decorator factory needs the parentheses

```python
def tag(label):
    def deco(cls):
        cls.label = label
        return cls
    return deco
# Wrong - passes the class as `label`, then returns a function
@tag
class A: pass
print(A.__name__)        # deco   (A is now a function!)
# Right
@tag("x")
class B: pass
print(B.label)           # x
```

❌ Mistake 3: Returning a function from the decorator (singleton) and then using `isinstance` or inheritance
✅ Correct: know the trade-off; use a module-level instance, or a metaclass/`__new__` singleton if you need the class

```python
def singleton(cls):
    inst = {}
    def get(*a, **k):
        return inst.setdefault(cls, cls(*a, **k))
    return get
@singleton
class Config: pass
c = Config()
try:
    isinstance(c, Config)        # Wrong: Config is a function now
except TypeError as e:
    print("TypeError")           # TypeError
# Right: keep the class
class Config2: pass
config = Config2()               # one module-level instance
print(isinstance(config, Config2))   # True
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def add_x(cls):
    cls.x = 1
    return cls

def add_y(cls):
    cls.y = cls.x + 1
    return cls

@add_y
@add_x
class A:
    pass

print(A.x, A.y)

@add_x
@add_y
class B:
    pass
```
Answer: `1 2` for the first print, and then defining `B` raises `AttributeError: type object 'B' has no attribute 'x'`. Decorators apply from bottom to top (closest to the class first). For `A`, `add_x` runs first and sets `x`, then `add_y` reads it. For `B`, `add_y` runs first, but `x` does not exist yet, so it fails at class-definition time.

---

## ⚫ Interview Questions + Answers

Q1: What is a class decorator and how is it different from a function decorator?
A1: It takes a class and returns a class (or anything) after the class is created. A function decorator wraps a function. The syntax is identical, `@deco` means `name = deco(name)`.

Q2: Class decorator vs metaclass vs `__init_subclass__`?
A2: A class decorator is explicit and applied class by class, not inherited. `__init_subclass__` runs automatically for every subclass of a base. A metaclass can change the class before it exists and customize instance creation, but is the most complex. Choose the simplest that works.

Q3: Is a class decorator inherited by subclasses?
A3: No. The decorator ran only on the decorated class; a subclass is a new class and is not decorated. Wrapped methods are inherited, but registration or checks do not repeat. Use `__init_subclass__` if you need it for every subclass.

Q4: How do you write a decorator that takes arguments?
A4: Write a factory: `def deco(arg): def real(cls): ...; return cls; return real`. `@deco(5)` calls `deco(5)` first, then applies the result to the class.

Q5: Name class decorators in the standard library.
A5: `@dataclasses.dataclass`, `@functools.total_ordering`, `@typing.final`, `@enum.unique`, and `@typing.runtime_checkable`. These show that class decorators are a normal, idiomatic tool.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Adding the same methods or attributes to several unrelated classes
- Registering classes (plugins, handlers, routes)
- Light wrapping or logging of methods
- You want something simpler than a metaclass

❌ Avoid when:
- You need the behavior inherited by all subclasses automatically (use `__init_subclass__`)
- The decorator changes the class into a function (breaks `isinstance`, subclassing)
- Type checkers must understand added attributes (they usually cannot)
- Plain inheritance or composition is clearer

---

## 📊 Visual Diagram
```
@add_hello
@register(plugins)            order of application: bottom -> top
class Greeter: ...

step 1: class Greeter built                    -> <class Greeter>
step 2: Greeter = register(plugins)(Greeter)   -> same class, now in registry
step 3: Greeter = add_hello(Greeter)           -> same class, new method

decorator(cls) can return:   cls itself (common)  |  a wrapper class  |  a function (careful)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Class decorator | Function that takes and returns a class | class लेकर class लौटाने वाला function |
| Decorator factory | Function that returns a decorator | decorator लौटाने वाला function |
| Registry | Dict of registered classes | registered classes की dict |
| Singleton | Only one instance exists | सिर्फ एक instance |
| `functools.wraps` | Copy metadata to a wrapper | wrapper में metadata copy करना |
| Monkey patching | Changing a class after creation | बनने के बाद class बदलना |

---

## ⚡ 3-Line Summary
English: A class decorator receives a finished class, modifies or wraps it, and returns it. `@deco` is just `Cls = deco(Cls)`; with arguments you need a factory. Use it for registries, added methods and singletons when a metaclass is too much.
Hindi: Class decorator तैयार class लेता है, उसे बदलता या wrap करता है और लौटाता है। `@deco` बस `Cls = deco(Cls)` है; arguments के लिए factory चाहिए। Metaclass भारी लगे तो registries, extra methods और singletons के लिए इसे use करें।

---

## ➡️ Next Topic
**114. Abstract Base Classes** - define interfaces that subclasses must implement, enforced at instantiation time.
