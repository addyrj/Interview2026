---

# 112. Metaclasses Basics
# हिंदी में: Metaclasses की बुनियाद (Class की Class)

---

## 🔵 Simple Definition (English)
A metaclass is the "class of a class". Just as an object is created by a class, a class is created by a metaclass. The default metaclass is `type`. By writing your own metaclass you can inspect or change a class at the moment it is created, for example to register it, validate it or add methods.

## 🔵 सरल परिभाषा (Hindi)
Metaclass "class की class" है। जैसे object class से बनता है, वैसे class metaclass से बनती है। Default metaclass `type` है। अपना metaclass लिखकर आप class के बनते ही उसे जांच या बदल सकते हो, जैसे register करना, validate करना या methods जोड़ना।

---

## 🔴 Problem it Solves
Sometimes you want a rule to apply to every class in a family: "every plugin class must be registered automatically", "every model must define a `table_name`", "no class may define a method called `save` twice". Doing this by hand means every developer must remember to call `register(MyPlugin)`, and they will forget. A metaclass runs automatically when a class statement finishes, so the rule cannot be skipped. (Today, `__init_subclass__` solves 90% of these cases more simply; metaclasses are for the rest.)

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी एक family की हर class पर rule लागू करना होता है: "हर plugin class अपने-आप register हो", "हर model में `table_name` हो", "कोई class `save` method दो बार define न करे"। हाथ से करने पर हर developer को `register(MyPlugin)` याद रखना पड़ेगा, और वे भूलेंगे। Metaclass class statement खत्म होते ही अपने-आप चलता है, इसलिए rule skip नहीं हो सकता। (आज `__init_subclass__` ऐसे 90% cases ज्यादा आसानी से हल करता है; बाकी के लिए metaclass है।)

---

## 🟢 How it Works — Step by Step

```
Step 1 → Everything is an object; a class is an object too
Step 2 → type(obj) is its class; type(Class) is its metaclass (default: type)
Step 3 → When Python runs "class Foo(Base): ..." it:
           a) runs the body into a namespace dict
           b) calls Meta(name, bases, namespace)   (Meta = type by default)
Step 4 → Meta.__new__ builds the class object, Meta.__init__ finishes it
Step 5 → Your metaclass overrides __new__/__init__ to inspect or edit the class
Step 6 → Syntax: class Foo(metaclass=MyMeta): ...  (subclasses inherit it)

type("Foo", (), {"x": 1})  ==  class Foo: x = 1
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर चीज़ object है; class भी object है
Step 2 → type(obj) उसकी class है; type(Class) उसका metaclass है (default: type)
Step 3 → जब Python "class Foo(Base): ..." चलाता है तो:
           a) body को namespace dict में चलाता है
           b) Meta(name, bases, namespace) call करता है   (default में Meta = type)
Step 4 → Meta.__new__ class object बनाता है, Meta.__init__ उसे पूरा करता है
Step 5 → आपका metaclass __new__/__init__ override करके class को देखता या बदलता है
Step 6 → Syntax: class Foo(metaclass=MyMeta): ...  (subclasses इसे inherit करती हैं)

type("Foo", (), {"x": 1})  ==  class Foo: x = 1
```

---

## 🟡 Real World Example
Django's `Model` uses a metaclass: when you write `class User(models.Model): name = CharField()`, the metaclass collects the fields, builds the table mapping and registers the model. SQLAlchemy's declarative base, Pydantic v1's `BaseModel` and `enum.Enum` also use metaclasses. A plugin system (payment gateways: `RazorpayPlugin`, `PaytmPlugin`) registers each subclass automatically so the checkout code can look them up by name.

## 🟡 Real Example Hindi mein
Django का `Model` metaclass use करता है: जब आप `class User(models.Model): name = CharField()` लिखते हो, तो metaclass fields जमा करता है, table mapping बनाता है और model register करता है। SQLAlchemy का declarative base, Pydantic v1 का `BaseModel` और `enum.Enum` भी metaclass use करते हैं। Plugin system (payment gateways: `RazorpayPlugin`, `PaytmPlugin`) हर subclass को अपने-आप register करता है ताकि checkout code उन्हें नाम से ढूंढ सके।

---

## 💻 Code Example — Basic
```python
# Basic metaclass examples
class Foo:                                        # an ordinary class
    pass


f: Foo = Foo()                                    # an instance
print(type(f))                                    # the class of the instance
print(type(Foo))                                  # the class of the class = metaclass
print(type(type))                                 # type is its own metaclass

Dynamic = type("Dynamic", (), {"x": 10, "hello": lambda self: "hi"})   # build a class by hand
print(Dynamic().x, Dynamic().hello())             # works like a normal class
print(Dynamic.__name__)                           # Dynamic


class LoudMeta(type):                             # a metaclass inherits from type
    def __new__(mcs, name: str, bases: tuple, namespace: dict):   # called to CREATE the class
        print(f"creating class {name}")           # runs at class-definition time
        return super().__new__(mcs, name, bases, namespace)       # let type do the real work


class Demo(metaclass=LoudMeta):                   # message prints right here, no instance needed
    pass


print("after class definition")                   # proves ordering
print(type(Demo))                                 # the metaclass is LoudMeta now

# Output:
# <class '__main__.Foo'>
# <class 'type'>
# <class 'type'>
# 10 hi
# Dynamic
# creating class Demo
# after class definition
# <class '__main__.LoudMeta'>
```

## 💻 Code Example — Advanced
```python
# Production style: auto-registry + validation metaclass, and the modern __init_subclass__ alternative
from typing import Any, ClassVar                  # type hints


class PluginMeta(type):
    """Registers every concrete plugin and enforces a required attribute."""

    registry: dict[str, type] = {}                # name -> class, shared by all plugins

    def __new__(mcs, name: str, bases: tuple[type, ...], ns: dict[str, Any]) -> "PluginMeta":
        cls = super().__new__(mcs, name, bases, ns)       # build the class first
        if bases:                                 # skip the abstract base itself
            key = ns.get("plugin_name")           # each plugin must declare a name
            if not isinstance(key, str) or not key:       # validate at definition time
                raise TypeError(f"{name} must define a non-empty 'plugin_name'")
            if key in mcs.registry:               # avoid silent overrides
                raise TypeError(f"duplicate plugin_name {key!r}")
            mcs.registry[key] = cls               # auto-register
        return cls                                # return the finished class

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:   # customise INSTANCE creation too
        instance = super().__call__(*args, **kwargs)       # normal __new__ + __init__
        print(f"created {cls.__name__}")          # simple audit hook
        return instance


class PaymentPlugin(metaclass=PluginMeta):        # base class: users inherit from this
    plugin_name: ClassVar[str]                    # annotation only, no value

    def pay(self, amount: int) -> str:            # interface method
        raise NotImplementedError


class Razorpay(PaymentPlugin):                    # auto-registered as "razorpay"
    plugin_name = "razorpay"

    def pay(self, amount: int) -> str:
        return f"razorpay charged {amount}"


class Paytm(PaymentPlugin):                       # auto-registered as "paytm"
    plugin_name = "paytm"

    def pay(self, amount: int) -> str:
        return f"paytm charged {amount}"


print(sorted(PluginMeta.registry))                # ['paytm', 'razorpay']
gateway = PluginMeta.registry["razorpay"]()       # look up by name, then create
print(gateway.pay(499))                           # razorpay charged 499

try:                                              # missing attribute is caught early
    class Broken(PaymentPlugin):                  # no plugin_name
        pass
except TypeError as e:                            # error happens when class is defined
    print("Error:", e)

try:                                              # duplicate names are caught too
    class Razorpay2(PaymentPlugin):
        plugin_name = "razorpay"
except TypeError as e:
    print("Error:", e)


# The simpler modern way: __init_subclass__ (no metaclass needed)
class Handler:
    handlers: ClassVar[dict[str, type]] = {}      # registry

    def __init_subclass__(cls, /, key: str = "", **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)       # cooperate with other bases
        if key:                                   # register when a key is given
            Handler.handlers[key] = cls


class EmailHandler(Handler, key="email"):         # class keyword argument
    pass


print(Handler.handlers)                           # {'email': <class '__main__.EmailHandler'>}

# Output:
# ['paytm', 'razorpay']
# created Razorpay
# razorpay charged 499
# Error: Broken must define a non-empty 'plugin_name'
# Error: duplicate plugin_name 'razorpay'
# {'email': <class '__main__.EmailHandler'>}
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Class is an object | yes, instance of `type` | yes, instance of `Function` |
| Customize class creation | metaclass / `__init_subclass__` | no direct equivalent; decorators or `Proxy` |
| Create class dynamically | `type(name, bases, dict)` | `class extends` in a function / `Object.setPrototypeOf` |
| Auto-register subclasses | `__init_subclass__` | static code in constructor, `new.target` |

```python
# Python way - class creation hook
class Base:
    registry: list[str] = []                  # shared list

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)   # keep chain intact
        Base.registry.append(cls.__name__)    # runs when a subclass is defined

class A(Base): pass
class B(Base): pass
print(Base.registry)                          # ['A', 'B']
```
```javascript
// JavaScript way - no class-definition hook; register in the constructor via new.target
class Base {
  static registry = [];
  constructor() { Base.registry.push(new.target.name); }   // runs per INSTANCE, not per class
}
class A extends Base {}
class B extends Base {}
new A(); new B();
console.log(Base.registry);                  // [ 'A', 'B' ] only after instances exist
```

Key difference: Python can run code at class-definition time (metaclass or `__init_subclass__`), JavaScript cannot, so JS frameworks rely on decorators/registries called by hand.

---

## 🟠 FastAPI Connection
You rarely write metaclasses in a FastAPI app, but you use them constantly: Pydantic's `BaseModel` (its metaclass reads field annotations and builds validators), `Enum` (members created by `EnumMeta`), SQLAlchemy's declarative base (maps classes to tables), and `abc.ABC` (`ABCMeta`). The plugin/registry pattern is useful for choosing a payment gateway or storage backend by name from a config value.

```python
# FastAPI example - choose a backend from a registry (built with __init_subclass__)
from typing import ClassVar                       # type hint
from fastapi import FastAPI, HTTPException        # app and errors
from fastapi.testclient import TestClient         # tests


class Notifier:
    registry: ClassVar[dict[str, type["Notifier"]]] = {}   # name -> class

    def __init_subclass__(cls, /, name: str = "", **kw) -> None:
        super().__init_subclass__(**kw)           # cooperate
        if name:                                  # register named subclasses
            Notifier.registry[name] = cls

    def send(self, to: str) -> str:               # interface
        raise NotImplementedError


class Email(Notifier, name="email"):
    def send(self, to: str) -> str:
        return f"email sent to {to}"


class Sms(Notifier, name="sms"):
    def send(self, to: str) -> str:
        return f"sms sent to {to}"


app: FastAPI = FastAPI()                          # create app


@app.post("/notify/{channel}")                    # POST /notify/email?to=amit
def notify(channel: str, to: str) -> dict[str, str]:
    cls = Notifier.registry.get(channel)          # look up the class by name
    if cls is None:                               # unknown channel
        raise HTTPException(404, f"no notifier {channel!r}")
    return {"result": cls().send(to)}             # instantiate and use


client: TestClient = TestClient(app)              # client
print(client.post("/notify/sms", params={"to": "amit"}).json())
print(client.post("/notify/fax", params={"to": "amit"}).status_code)

# Output:
# {'result': 'sms sent to amit'}
# 404
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a metaclass when `__init_subclass__` or a decorator is enough
✅ Correct: prefer the simpler tool first

```python
# Wrong - heavy for a simple registry
class Meta(type):
    reg: list = []
    def __init__(cls, name, bases, ns):
        super().__init__(name, bases, ns)
        Meta.reg.append(name)
# Right - 4 lines, no metaclass conflicts
class Base:
    reg: list = []
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        Base.reg.append(cls.__name__)
class X(Base): pass
print(Base.reg)           # ['X']
```

❌ Mistake 2: Metaclass conflict when mixing two bases with different metaclasses
✅ Correct: make a combined metaclass that inherits from both

```python
from abc import ABC, ABCMeta
class M(type): pass
class A(metaclass=M): pass
# Wrong
try:
    class B(A, ABC): pass
except TypeError as e:
    print("conflict")      # conflict
# Right
class M2(M, ABCMeta): pass
class C(A, ABC, metaclass=M2): pass
print(type(C).__name__)    # M2
```

❌ Mistake 3: Forgetting to call `super().__new__` and return the class
✅ Correct: always build via `super()` and return the result

```python
class Bad(type):
    def __new__(mcs, name, bases, ns):
        print("making", name)        # Wrong: returns None
class Good(type):
    def __new__(mcs, name, bases, ns):
        return super().__new__(mcs, name, bases, ns)    # Right
class Z(metaclass=Good): pass
print(Z)                              # <class '__main__.Z'>
try:
    class Y(metaclass=Bad): pass
    print(Y)                          # Wrong result: None
except Exception as e:
    print(e)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class Meta(type):
    def __new__(mcs, name, bases, ns):
        print("Meta.__new__", name)
        return super().__new__(mcs, name, bases, ns)
    def __call__(cls, *a, **k):
        print("Meta.__call__", cls.__name__)
        return super().__call__(*a, **k)

class A(metaclass=Meta):
    def __new__(cls):
        print("A.__new__")
        return super().__new__(cls)
    def __init__(self):
        print("A.__init__")

print("--- defined")
A()
class B(A):
    pass
print(type(B).__name__)
```
Answer: `Meta.__new__ A`, `--- defined`, `Meta.__call__ A`, `A.__new__`, `A.__init__`, then (defining B) `Meta.__new__ B`, then `Meta`. The metaclass `__new__` runs when the class statement executes, not when an instance is made. Creating an instance first goes through `Meta.__call__`, which calls `A.__new__` then `A.__init__`. A subclass inherits the metaclass, so defining `B` runs `Meta.__new__` again and `type(B)` is `Meta`.

---

## ⚫ Interview Questions + Answers

Q1: What is a metaclass?
A1: The class of a class. `type` is the default metaclass. A class statement calls `metaclass(name, bases, namespace)` to build the class object, so a custom metaclass can validate, register or modify classes at definition time.

Q2: What is the difference between `__new__` and `__init__` in a metaclass?
A2: `Meta.__new__` creates the class object (can change name, bases, namespace before creation). `Meta.__init__` receives the already created class and can only configure it. Use `__new__` when you must alter the namespace, `__init__` otherwise.

Q3: When should you avoid metaclasses?
A3: Almost always. Prefer class decorators, `__init_subclass__`, `__set_name__` or plain inheritance. Metaclasses are harder to read, cause conflicts with other metaclasses and surprise teammates. "If you wonder whether you need one, you do not."

Q4: How does `type(name, bases, dict)` work?
A4: It is the three-argument form of `type` that builds a class dynamically. `class A(B): x = 1` is equivalent to `A = type("A", (B,), {"x": 1})`. Useful for generating classes from a schema at runtime.

Q5: Which standard-library or popular tools use metaclasses?
A5: `abc.ABCMeta` (abstract classes), `enum.EnumMeta`, `typing.Protocol` internals, Django models, SQLAlchemy declarative base, and Pydantic v1 models. In v2 Pydantic still uses a metaclass (`ModelMetaclass`) to collect fields.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You build a framework that must hook class creation (ORMs, plugin systems)
- You need to change the class namespace before the class exists
- You need to customize how instances are created for all subclasses (`__call__`), e.g. singletons

❌ Avoid when:
- A decorator, `__init_subclass__`, `__set_name__` or a function can do the job
- You mix many libraries that already use metaclasses (conflicts)
- The team is not familiar with the pattern
- You only need runtime checks on instances (use normal methods)

---

## 📊 Visual Diagram
```
instance  ---- type() ---->  class  ---- type() ---->  metaclass
  f                           Foo                       type
  |__ created by Foo(...)     |__ created by type(name, bases, ns)
                                  or by your Meta(name, bases, ns)

class Foo(Base, metaclass=Meta):          timeline
    body...                               1. body runs -> namespace dict
                                          2. Meta.__new__(name, bases, ns)  -> class object
                                          3. Meta.__init__(cls, ...)
                                          4. __init_subclass__ of Base is called
Foo(...)  -> Meta.__call__ -> Foo.__new__ -> Foo.__init__ -> instance
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metaclass | Class that creates classes | classes बनाने वाली class |
| `type` | Default metaclass | default metaclass |
| Namespace | Dict of names defined in class body | class body में defined नामों की dict |
| `__init_subclass__` | Hook run when a subclass is defined | subclass बनने पर चलने वाला hook |
| Registry | Dict of known classes by name | नाम से classes की dict |
| Class-definition time | When the `class` statement runs | जब `class` statement चलता है |

---

## ⚡ 3-Line Summary
English: A metaclass creates classes the way a class creates objects; the default is `type`. Custom metaclasses run code when a class is defined, which frameworks use for registries and validation. Prefer `__init_subclass__` or decorators unless you truly need a metaclass.
Hindi: Metaclass classes को वैसे बनाता है जैसे class objects को बनाती है; default `type` है। Custom metaclass class define होते ही code चलाता है, जिसे frameworks registries और validation के लिए use करते हैं। जब तक सच में जरूरी न हो, `__init_subclass__` या decorators को चुनें।

---

## ➡️ Next Topic
**113. Class Decorators** - a lighter way to modify or register a class after it is created, using a decorator on the class itself.
