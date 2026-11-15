---

# 094. super() Function
# हिंदी में: super() Function (Parent Class को Call करना)

---

## 🔵 Simple Definition (English)
`super()` gives you a proxy to the next class in the Method Resolution Order (MRO). You use it inside a child class to call a parent's method (usually `__init__`) without hard-coding the parent's name. It is the base of cooperative multiple inheritance in Python.

## 🔵 सरल परिभाषा (Hindi)
`super()` Method Resolution Order (MRO) में अगली class का proxy देता है। Child class के अंदर इसे parent का method (अक्सर `__init__`) call करने के लिए इस्तेमाल करते हैं, parent का नाम hard-code किए बिना। Python में cooperative multiple inheritance इसी पर टिका है।

---

## 🔴 Problem it Solves
When a child overrides a method, the parent's version is lost. Developers used `Parent.__init__(self, ...)` to bring it back, but that hard-codes the parent name (rename the parent and everything breaks) and, with multiple inheritance, can call the same grandparent twice (the "diamond problem"). `super()` follows the MRO, so each class in the chain runs exactly once, in the correct order.

## 🔴 यह क्यों बना? (Hindi)
Child जब method override करता है तो parent वाला version खो जाता है। पहले `Parent.__init__(self, ...)` लिखते थे, लेकिन इसमें parent का नाम hard-code हो जाता है (parent का नाम बदला तो सब टूटा) और multiple inheritance में एक ही grandparent दो बार call हो सकता है ("diamond problem")। `super()` MRO को follow करता है, इसलिए chain की हर class सही क्रम में सिर्फ एक बार चलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python builds the MRO of a class (C3 linearization): class.__mro__
Step 2 → Inside a method, super() (zero-arg form) finds two things automatically:
         the current class (from the hidden __class__ cell) and `self`
Step 3 → super() returns a proxy that starts searching AFTER the current class in type(self).__mro__
Step 4 → super().method(...) calls that next class's method with the same self
Step 5 → That method may call super() again, passing control down the chain
Step 6 → Result: every class in the MRO runs once (cooperative inheritance)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python class का MRO बनाता है (C3 linearization): class.__mro__
Step 2 → Method के अंदर super() (बिना arguments वाला रूप) दो चीजें खुद ढूंढता है:
         मौजूदा class (hidden __class__ cell से) और `self`
Step 3 → super() ऐसा proxy देता है जो type(self).__mro__ में मौजूदा class के बाद से search शुरू करता है
Step 4 → super().method(...) अगली class के method को वही self देकर call करता है
Step 5 → वह method फिर super() call करके control आगे बढ़ा सकता है
Step 6 → नतीजा: MRO की हर class एक बार चलती है (cooperative inheritance)
```

---

## 🟡 Real World Example
A payments service has a base `Notifier` with `__init__(self, user_id)`. `SMSNotifier` and `EmailNotifier` extend it and add phone/email. A Razorpay-style `PaymentError` extends `Exception`: its `__init__` calls `super().__init__(message)` so that `str(error)` and tracebacks work. SQLAlchemy models, Django models and Pydantic models all rely on `super().__init__` to run framework setup.

## 🟡 Real Example Hindi mein
Payments service में base `Notifier` है जिसका `__init__(self, user_id)` है। `SMSNotifier` और `EmailNotifier` उसे extend करके phone/email जोड़ते हैं। Razorpay जैसा `PaymentError`, `Exception` को extend करता है: उसका `__init__` `super().__init__(message)` call करता है ताकि `str(error)` और traceback सही चलें। SQLAlchemy, Django और Pydantic models framework का setup चलाने के लिए `super().__init__` पर निर्भर हैं।

---

## 💻 Code Example — Basic
```python
# Basic super() example
class Animal:                                       # parent class
    def __init__(self, name: str) -> None:          # parent constructor
        self.name: str = name                       # store the name

    def speak(self) -> str:                         # parent method
        return f"{self.name} makes a sound"         # generic sound


class Dog(Animal):                                  # child class
    def __init__(self, name: str, breed: str) -> None:   # child constructor
        super().__init__(name)                      # run the parent constructor first
        self.breed: str = breed                     # then add child-only data

    def speak(self) -> str:                         # override parent method
        base: str = super().speak()                 # reuse the parent's result
        return f"{base} - Woof!"                    # extend it


d: Dog = Dog("Bruno", "Labrador")                   # create a dog
print(d.name, d.breed)                              # both attributes exist
print(d.speak())                                    # parent text + child text
print(Dog.__mro__)                                  # the lookup order super() uses

# Output:
# Bruno Labrador
# Bruno makes a sound - Woof!
# (<class '__main__.Dog'>, <class '__main__.Animal'>, <class 'object'>)
```

## 💻 Code Example — Advanced
```python
# Production style: cooperative multiple inheritance with **kwargs
from datetime import datetime, timezone             # timestamps


class Base:                                         # end of the chain
    def __init__(self, **kwargs: object) -> None:   # accept leftovers
        if kwargs:                                  # nobody consumed these keywords
            raise TypeError(f"Unexpected arguments: {sorted(kwargs)}")   # fail loudly
        self.log: list[str] = []                    # shared log list


class TimestampMixin(Base):                         # adds created_at
    def __init__(self, *, created_at: datetime | None = None, **kwargs: object) -> None:
        super().__init__(**kwargs)                  # pass the rest down the MRO
        self.created_at: datetime = created_at or datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.log.append("TimestampMixin")           # record that we ran


class AuditMixin(Base):                             # adds actor
    def __init__(self, *, actor: str = "system", **kwargs: object) -> None:
        super().__init__(**kwargs)                  # pass the rest down
        self.actor: str = actor                     # who did it
        self.log.append("AuditMixin")               # record that we ran


class Order(TimestampMixin, AuditMixin):            # two parents -> diamond with Base
    def __init__(self, order_id: int, **kwargs: object) -> None:
        super().__init__(**kwargs)                  # starts the whole chain
        self.order_id: int = order_id               # own data
        self.log.append("Order")                    # record that we ran


o: Order = Order(7, actor="admin")                  # kwargs are routed to the right class
print([c.__name__ for c in Order.__mro__])          # MRO: Order, Timestamp, Audit, Base, object
print(o.log)                                        # Base ran ONCE; order is deepest first
print(o.actor, o.created_at.year)                   # values set by different classes

try:                                                # typo in keyword name
    Order(8, actr="x")                              # nobody accepts "actr"
except TypeError as e:                              # Base raises it
    print("Error:", e)                              # clear message

# Output:
# ['Order', 'TimestampMixin', 'AuditMixin', 'Base', 'object']
# ['AuditMixin', 'TimestampMixin', 'Order']
# admin 2026
# Error: Unexpected arguments: ['actr']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Call parent constructor | `super().__init__(...)` | `super(...)` |
| Call parent method | `super().method()` | `super.method()` |
| Must call before using `self`/`this` | Not enforced (but do it first) | Required before `this` in constructor |
| Multiple inheritance | Yes, resolved by MRO | No (single `extends`) |
| Needs explicit class name | No (zero-arg form) | No |

```python
# Python way
class A:
    def hi(self) -> str:
        return "A"          # parent method

class B(A):
    def hi(self) -> str:
        return super().hi() + "B"   # call parent, add own part

print(B().hi())             # AB
```
```javascript
// JavaScript way
class A { hi() { return "A"; } }              // parent method
class B extends A {
  hi() { return super.hi() + "B"; }           // super.hi() — no parentheses after super
}
console.log(new B().hi());                    // AB
```

Key difference: in JS, `super(...)` is a call only in the constructor, while Python's `super()` is an object you can use anywhere. Python's `super()` follows the MRO, so with multiple inheritance it may call a *sibling* class, not only the direct parent.

---

## 🟠 FastAPI Connection
Pydantic models (the heart of FastAPI request/response validation) support custom `__init__`/validators, and custom exceptions in FastAPI apps always call `super().__init__`. `HTTPException` itself is a subclass, and your own error classes should extend it correctly.

```python
# FastAPI example — custom exception built with super()
from fastapi import FastAPI, HTTPException          # app and base exception
from fastapi.testclient import TestClient           # test without a server


class InsufficientBalance(HTTPException):           # our domain error
    def __init__(self, needed: int, available: int) -> None:
        super().__init__(                           # let HTTPException do the real work
            status_code=402,                        # Payment Required
            detail=f"Need {needed}, have {available}",   # message for the client
        )


app: FastAPI = FastAPI()                            # create app


@app.get("/pay")                                    # GET /pay?amount=500
def pay(amount: int) -> dict[str, int]:
    balance: int = 100                              # fake wallet
    if amount > balance:                            # not enough money
        raise InsufficientBalance(amount, balance)  # FastAPI turns it into a 402 response
    return {"paid": amount}                         # success


client: TestClient = TestClient(app)                # in-process client
r = client.get("/pay", params={"amount": 500})      # trigger the error
print(r.status_code, r.json())                      # status and body

# Output:
# 402 {'detail': 'Need 500, have 100'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to call `super().__init__()` in the child
✅ Correct: call it so the parent's setup runs

```python
class P:
    def __init__(self) -> None:
        self.ready = True       # parent setup

class Wrong(P):
    def __init__(self) -> None:
        self.x = 1              # parent __init__ never runs -> no self.ready

class Right(P):
    def __init__(self) -> None:
        super().__init__()      # parent setup runs
        self.x = 1

print(hasattr(Wrong(), "ready"), hasattr(Right(), "ready"))   # False True
```

❌ Mistake 2: Hard-coding the parent in multiple inheritance (double call)
✅ Correct: use `super()` everywhere in the chain

```python
class Root:
    def __init__(self) -> None:
        print("Root init")

class L(Root):
    def __init__(self) -> None:
        Root.__init__(self)      # Wrong: hard-coded
        print("L init")

class R(Root):
    def __init__(self) -> None:
        Root.__init__(self)      # Wrong: hard-coded
        print("R init")

class Bad(L, R):
    def __init__(self) -> None:
        L.__init__(self)         # Root runs here...
        R.__init__(self)         # ...and AGAIN here

Bad()                            # Root init, L init, Root init, R init
```

❌ Mistake 3: Using zero-arg `super()` outside a class body or in a `@staticmethod`
✅ Correct: use it only in instance/class methods (or pass arguments explicitly)

```python
class A:
    @staticmethod
    def make() -> str:
        try:
            return super().__str__()      # Wrong: no self / no class to bind to
        except RuntimeError as e:
            return f"RuntimeError: {e}"

print(A.make())   # RuntimeError: super(): no arguments
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def go(self) -> None:
        print("A")

class B(A):
    def go(self) -> None:
        print("B start")
        super().go()
        print("B end")

class C(A):
    def go(self) -> None:
        print("C start")
        super().go()
        print("C end")

class D(B, C):
    def go(self) -> None:
        print("D start")
        super().go()
        print("D end")

D().go()
```
Answer: The MRO of `D` is `D, B, C, A, object`. So `super()` inside `B` does NOT go to `A`; it goes to `C` (the next class after B in D's MRO). Output: `D start`, `B start`, `C start`, `A`, `C end`, `B end`, `D end`. `A` runs only once. That is why `super()` means "next in MRO", not "parent".

---

## ⚫ Interview Questions + Answers

Q1: What does `super()` actually return?
A1: A proxy object (type `super`) bound to the instance. Attribute lookups on it start searching `type(self).__mro__` after the class where `super()` was written. It is not simply "the parent class".

Q2: Why does zero-argument `super()` work in Python 3 but needed `super(Child, self)` in Python 2?
A2: The compiler creates a hidden `__class__` cell for any method that uses the name `super`. At runtime `super()` reads `__class__` and the first argument of the method (`self`). In Python 3 you can still write `super(Child, self)` explicitly, which is rarely needed.

Q3: What is MRO and how do you see it?
A3: MRO is the order Python searches classes for an attribute. It is computed by C3 linearization, which keeps children before parents and respects the order of bases. See it with `Cls.__mro__` or `Cls.mro()`.

Q4: How should `__init__` signatures look in cooperative multiple inheritance?
A4: Each class takes the arguments it needs (keyword-only is safest), takes `**kwargs`, and forwards them with `super().__init__(**kwargs)`. The last class (usually a base that rejects unknown kwargs) ends the chain.

Q5: Is calling `super().__init__()` always required?
A5: No, but almost always wise. If the parent does setup (attributes, registration, validation), skipping it leaves the object half-built. Skip it only when you deliberately replace the parent's whole initialization.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Extending a parent's `__init__` or any overridden method
- Subclassing built-ins or framework classes (`Exception`, `dict`, `HTTPException`, Pydantic `BaseModel`)
- Mixins and multiple inheritance (always use `super()`)
- You want code that survives renaming the parent class

❌ Avoid when:
- The class has no parent besides `object` and nothing to extend
- You want to completely replace the parent's behavior
- A simple composition (a `has-a` attribute) is clearer than a deep inheritance chain

---

## 📊 Visual Diagram
```
class D(B, C)      MRO: D -> B -> C -> A -> object

          A
         / \
        B   C
         \ /
          D

D().go()
  D.go  --super()-->  B.go  --super()-->  C.go  --super()-->  A.go
 "D start"           "B start"           "C start"           "A"
  ...unwinds back:   "C end"  ->  "B end"  ->  "D end"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| super() | Proxy to the next class in MRO | MRO में अगली class का proxy |
| MRO | Method Resolution Order | Method ढूंढने का क्रम |
| C3 linearization | Algorithm that builds the MRO | MRO बनाने वाला algorithm |
| Diamond problem | Two parents share one grandparent | दो parents का एक ही grandparent |
| Cooperative inheritance | Every class calls super() so all run once | सब classes super() से chain बनाती हैं |
| Override | Child replaces a parent's method | Child द्वारा parent method बदलना |

---

## ⚡ 3-Line Summary
English: `super()` calls the next class in the MRO, not just the direct parent. Use it in `__init__` and overridden methods so setup runs once and in order. In multiple inheritance, every class should use `super()` and forward `**kwargs`.
Hindi: `super()` MRO की अगली class को call करता है, सिर्फ सीधे parent को नहीं। `__init__` और overridden methods में इसे इस्तेमाल करें ताकि setup सही क्रम में एक बार चले। Multiple inheritance में हर class `super()` इस्तेमाल करे और `**kwargs` आगे भेजे।

---

## ➡️ Next Topic
**095. Abstract Classes (ABC)** — force child classes to implement required methods, so a base class defines a contract that cannot be skipped.
