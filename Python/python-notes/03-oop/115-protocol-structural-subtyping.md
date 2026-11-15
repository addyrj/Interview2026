---

# 115. Protocol (Structural Subtyping)
# हिंदी में: Protocol (Structure से Type — Duck Typing का Type-safe रूप)

---

## 🔵 Simple Definition (English)
A `Protocol` (from `typing`, Python 3.8+) describes the methods and attributes an object must have. Any class that has them counts as a match, even if it never inherits from the Protocol. This is "static duck typing": "if it walks like a duck and quacks like a duck, the type checker accepts it as a duck".

## 🔵 सरल परिभाषा (Hindi)
`Protocol` (`typing` से, Python 3.8+) बताता है कि किसी object में कौन से methods और attributes होने चाहिए। जिस class में वे हों वह match मानी जाती है, भले ही वह Protocol से कभी inherit न करे। यह "static duck typing" है: "जो बत्तख की तरह चले और बोले, type checker उसे बत्तख मान लेता है"।

---

## 🔴 Problem it Solves
Python is duck-typed, but type hints need a name for "anything with a `.read()` method". Before Protocols you had two bad options: annotate with a concrete class (too strict, rejects valid objects), or inherit everything from an ABC (forces third-party classes to change, creates coupling). Protocols let a function say "I need something with `.send(msg)`" and any matching class works, including classes from libraries you cannot edit, while mypy/pyright still check your code.

## 🔴 यह क्यों बना? (Hindi)
Python duck-typed है, लेकिन type hints को "ऐसी कोई भी चीज़ जिसमें `.read()` method हो" के लिए नाम चाहिए। Protocol से पहले दो बुरे विकल्प थे: concrete class annotate करना (बहुत सख्त, सही objects reject), या हर चीज़ ABC से inherit कराना (third-party classes बदलनी पड़ें, coupling बढ़े)। Protocol से function कह सकता है "मुझे `.send(msg)` वाली चीज़ चाहिए" और कोई भी matching class चलती है, उन libraries की भी जिन्हें आप edit नहीं कर सकते, और mypy/pyright फिर भी आपका code check करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → class Sender(Protocol): def send(self, msg: str) -> None: ...
Step 2 → Functions annotate parameters as Sender
Step 3 → Any class with a compatible send(msg: str) -> None matches
         (no inheritance, no registration)
Step 4 → The TYPE CHECKER (mypy/pyright) verifies this before you run the code
Step 5 → At runtime, nothing is checked by default (hints are ignored)
Step 6 → Add @runtime_checkable to allow isinstance(x, Sender)
         (checks only that the method names exist, not their signatures)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → class Sender(Protocol): def send(self, msg: str) -> None: ...
Step 2 → Functions अपने parameters को Sender annotate करते हैं
Step 3 → compatible send(msg: str) -> None वाली कोई भी class match होती है
         (न inheritance, न registration)
Step 4 → TYPE CHECKER (mypy/pyright) code चलाने से पहले यह जांचता है
Step 5 → Runtime पर default रूप से कुछ check नहीं होता (hints ignore होते हैं)
Step 6 → isinstance(x, Sender) के लिए @runtime_checkable जोड़ें
         (सिर्फ method names का होना जांचता है, signatures नहीं)
```

---

## 🟡 Real World Example
A notification service needs "something that can send a message". `EmailClient` (your class), `TwilioClient` (third-party SDK) and `FakeSender` (test double) all have `send(msg)`. A `Notifier` Protocol lets the same function accept all three, with no wrapper classes. Standard-library examples: `typing.SupportsInt`, `Iterable`, `Sized`, file-like objects with `.read()`. In AI apps, an `Embedder` Protocol lets you swap OpenAI, a local model or a fake in tests.

## 🟡 Real Example Hindi mein
Notification service को "कोई भी चीज़ जो message भेज सके" चाहिए। `EmailClient` (आपकी class), `TwilioClient` (third-party SDK) और `FakeSender` (test double) सबमें `send(msg)` है। `Notifier` Protocol से एक ही function तीनों को लेता है, बिना wrapper classes के। Standard library के उदाहरण: `typing.SupportsInt`, `Iterable`, `Sized`, `.read()` वाले file-like objects। AI apps में `Embedder` Protocol से OpenAI, local model या tests का fake आसानी से बदल सकते हैं।

---

## 💻 Code Example — Basic
```python
# Basic Protocol examples
from typing import Protocol, runtime_checkable   # the tools


class Quacker(Protocol):                          # describes a shape, not a family tree
    def quack(self) -> str: ...                   # required method


class Duck:                                       # does NOT inherit from Quacker
    def quack(self) -> str:
        return "Quack!"


class Robot:                                      # unrelated class, same method
    def quack(self) -> str:
        return "Beep-quack"


class Cat:                                        # no quack method
    def meow(self) -> str:
        return "meow"


def make_noise(q: Quacker) -> str:                # accepts ANY object with quack()
    return q.quack()


print(make_noise(Duck()))                         # fine
print(make_noise(Robot()))                        # fine, no inheritance needed
# make_noise(Cat())                               # mypy/pyright error: "Cat" is incompatible with "Quacker"


@runtime_checkable                                # allows isinstance() checks
class Closable(Protocol):
    def close(self) -> None: ...


class Conn:
    def close(self) -> None:
        print("closed")


print(isinstance(Conn(), Closable), isinstance(Cat(), Closable))   # checks method names only
try:                                              # without the decorator, isinstance is refused
    isinstance(Duck(), Quacker)                   # Quacker is not runtime_checkable
except TypeError as e:
    print("TypeError:", e)

# Output:
# Quack!
# Beep-quack
# True False
# TypeError: Instance and class checks can only be used with @runtime_checkable protocols
```

## 💻 Code Example — Advanced
```python
# Production style: swappable dependencies, attribute protocol, generics, callable protocol
from dataclasses import dataclass, field         # simple classes
from typing import Callable, Iterable, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")                                  # generic item type
T_co = TypeVar("T_co", covariant=True)            # covariant: read-only producers


class Notifier(Protocol):
    """Anything that can deliver a message."""
    def send(self, to: str, message: str) -> bool: ...


class HasId(Protocol):
    """Protocols can require attributes, not only methods."""
    id: int                                       # attribute requirement


class Repository(Protocol[T_co]):                 # generic protocol (read side)
    def get(self, item_id: int) -> T_co | None: ...
    def list_all(self) -> Iterable[T_co]: ...


class Validator(Protocol):                        # protocol with __call__ = "callable type"
    def __call__(self, value: str) -> bool: ...


@dataclass
class EmailNotifier:                              # no base class
    sent: list[str] = field(default_factory=list)

    def send(self, to: str, message: str) -> bool:
        self.sent.append(f"email:{to}:{message}")
        return True


class FakeNotifier:                               # test double, same shape
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def send(self, to: str, message: str) -> bool:
        self.calls.append((to, message))
        return False                              # simulate a delivery failure


def alert_all(users: Iterable[str], notifier: Notifier) -> int:
    """Send to everyone; return how many deliveries succeeded."""
    ok: int = 0
    for u in users:
        if notifier.send(u, "Your order has shipped"):
            ok += 1
    return ok


email = EmailNotifier()
fake = FakeNotifier()
print(alert_all(["amit", "neha"], email))         # 2
print(alert_all(["amit", "neha"], fake))          # 0
print(fake.calls[0])                              # ('amit', 'Your order has shipped')


@dataclass
class User:
    id: int
    name: str


@dataclass
class Order:
    id: int
    total: float


def ids_of(items: Iterable[HasId]) -> list[int]:  # works for User, Order, anything with .id
    return [i.id for i in items]


print(ids_of([User(1, "a"), Order(7, 9.5)]))      # [1, 7]


class UserRepo:                                   # satisfies Repository[User] by shape
    def __init__(self) -> None:
        self._data: dict[int, User] = {1: User(1, "Amit")}

    def get(self, item_id: int) -> User | None:
        return self._data.get(item_id)

    def list_all(self) -> Iterable[User]:
        return self._data.values()


def first_name(repo: Repository[User], uid: int) -> str:
    user = repo.get(uid)                          # typed as User | None
    return user.name if user else "unknown"


print(first_name(UserRepo(), 1), first_name(UserRepo(), 99))   # Amit unknown

not_empty: Validator = lambda v: bool(v.strip())  # a lambda matches the __call__ protocol
print(not_empty("hi"), not_empty("  "))           # True False


@runtime_checkable
class SupportsClose(Protocol):
    def close(self) -> None: ...


resources: list[object] = [open(__file__), EmailNotifier()]
for r in resources:
    print(type(r).__name__, isinstance(r, SupportsClose))   # runtime check by method name
resources[0].close()                              # type: ignore[attr-defined]

# Output:
# 2
# 0
# ('amit', 'Your order has shipped')
# [1, 7]
# Amit unknown
# True False
# TextIOWrapper True
# EmailNotifier False
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript / TypeScript |
|---------|--------|------------------------|
| Structural typing | `typing.Protocol` | TypeScript `interface` (structural by default) |
| Nominal typing | ABC / normal inheritance | TS `class implements` (still structural) |
| Runtime check | `@runtime_checkable` + `isinstance` | none (types erased); use `"send" in obj` |
| Plain JS | duck typing, no types | duck typing, no types |

```python
# Python way
from typing import Protocol

class Sender(Protocol):
    def send(self, msg: str) -> None: ...     # required shape

class Sms:
    def send(self, msg: str) -> None:
        print("sms:", msg)

def notify(s: Sender) -> None:
    s.send("hi")                              # any matching object works

notify(Sms())                                 # sms: hi
```
```typescript
// TypeScript way - interfaces are structural, same idea
interface Sender { send(msg: string): void }
class Sms { send(msg: string) { console.log("sms:", msg); } }
function notify(s: Sender) { s.send("hi"); }
notify(new Sms());                            // sms: hi - no "implements" needed
```

Key difference: if you know TypeScript interfaces, you already understand Protocols: both are structural. In plain JavaScript there are no types, so everything is duck typing without checks. Python's Protocol is only enforced by external tools (mypy, pyright) and optionally by `isinstance` for method names.

---

## 🟠 FastAPI Connection
Protocols are great for FastAPI dependency injection: the endpoint depends on a small interface (`Mailer`, `Cache`, `Embedder`), production code passes the real client, and tests pass a fake without any inheritance. Because FastAPI does not validate Protocol types at runtime, use Protocols for services, and Pydantic models for request/response data.

```python
# FastAPI example - inject a Mailer protocol, override in tests
from typing import Protocol                       # Protocol
from fastapi import Depends, FastAPI              # FastAPI pieces
from fastapi.testclient import TestClient         # tests


class Mailer(Protocol):                           # what the endpoint needs
    def send(self, to: str, body: str) -> str: ...


class SmtpMailer:                                 # "real" implementation (no base class)
    def send(self, to: str, body: str) -> str:
        return f"smtp -> {to}"


class FakeMailer:                                 # test implementation
    def __init__(self) -> None:
        self.outbox: list[str] = []

    def send(self, to: str, body: str) -> str:
        self.outbox.append(to)
        return "fake"


def get_mailer() -> Mailer:                       # dependency provider
    return SmtpMailer()


app: FastAPI = FastAPI()                          # create app


@app.post("/welcome")                             # POST /welcome?email=a@b.com
def welcome(email: str, mailer: Mailer = Depends(get_mailer)) -> dict[str, str]:
    return {"status": mailer.send(email, "Welcome!")}


client: TestClient = TestClient(app)              # client
print(client.post("/welcome", params={"email": "a@b.com"}).json())
fake: FakeMailer = FakeMailer()                   # keep a reference to inspect later
app.dependency_overrides[get_mailer] = lambda: fake   # swap in the fake
print(client.post("/welcome", params={"email": "x@y.com"}).json(), fake.outbox)

# Output:
# {'status': 'smtp -> a@b.com'}
# {'status': 'fake'} ['x@y.com']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `isinstance` on a Protocol without `@runtime_checkable`
✅ Correct: decorate it, and remember it only checks that names exist

```python
from typing import Protocol, runtime_checkable
class P(Protocol):
    def f(self) -> int: ...
# Wrong
try:
    isinstance(object(), P)
except TypeError:
    print("TypeError")        # TypeError
# Right
@runtime_checkable
class Q(Protocol):
    def f(self) -> int: ...
class Impl:
    def f(self) -> str:       # wrong return type, still passes the runtime check!
        return "x"
print(isinstance(Impl(), Q))  # True (signatures are NOT checked at runtime)
```

❌ Mistake 2: Expecting Python to raise an error when a class does not match
✅ Correct: run mypy/pyright in CI; runtime does not enforce Protocols

```python
from typing import Protocol
class P(Protocol):
    def f(self) -> int: ...
def use(p: P) -> int:
    return p.f()
class Bad:
    pass
# Wrong assumption: "Python will refuse Bad()"
try:
    use(Bad())                # type checker flags this line, Python only fails inside
except AttributeError as e:
    print("runtime AttributeError")   # runtime AttributeError
# Right: run `mypy .` or `pyright` in CI
```

❌ Mistake 3: Subclassing a Protocol and forgetting that it is then a normal (nominal) class
✅ Correct: inherit only when you want default method bodies; instantiation of the Protocol itself is blocked

```python
from typing import Protocol
class P(Protocol):
    def f(self) -> int: ...
try:
    P()                       # Wrong: cannot instantiate a protocol
except TypeError as e:
    print(e)                  # Protocols cannot be instantiated
class Impl(P):                # explicit subclass is allowed (and checked by the type checker)
    def f(self) -> int:
        return 1
print(Impl().f())             # 1
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from typing import Protocol, runtime_checkable

@runtime_checkable
class HasName(Protocol):
    name: str

class A:
    name = "a"

class B:
    def __init__(self):
        self.name = "b"

class C:
    pass

print(isinstance(A(), HasName), isinstance(B(), HasName), isinstance(C(), HasName))
def f(x: HasName) -> str:
    return x.name
print(f(C()) if False else "skipped")
```
Answer: `True True False` then `skipped`. A runtime-checkable Protocol with a data attribute checks with `hasattr`-style logic: `A` has `name` as a class attribute, `B` has it as an instance attribute, `C` has none. Python checks only that the name exists, never its type (`name` could be an int and still pass). The type checker (mypy) would reject `f(C())`, but Python itself would only fail at the `x.name` line, raising `AttributeError`. Also note: Protocols with non-method members cannot be used with `issubclass`.

---

## ⚫ Interview Questions + Answers

Q1: What is a Protocol and how does it differ from an ABC?
A1: A Protocol is structural: any class with matching members is accepted by the type checker, no inheritance needed. An ABC is nominal: a class must inherit (or be registered) and Python enforces abstract methods at instantiation. Protocols give flexibility, ABCs give runtime enforcement and shared code.

Q2: Does Python enforce Protocols at runtime?
A2: No. They are for static type checkers. `@runtime_checkable` makes `isinstance`/`issubclass` work, but it only checks that attributes or methods exist, not their signatures or types, and it is slower than normal `isinstance`.

Q3: When should I prefer Protocol?
A3: When you want to depend on a small behavior (`.read()`, `.send()`), when the implementing classes come from other libraries, or when you want test doubles without inheritance. It follows the "program to an interface, not an implementation" idea with low coupling.

Q4: Can a Protocol have attributes and default implementations?
A4: Yes. You can declare attributes (`id: int`) and methods with bodies. Explicit subclasses inherit the default bodies; structurally matching classes do not receive them. Use `ClassVar` and `@property` in Protocols to be precise about read-only vs writable members.

Q5: What are examples in the standard library?
A5: `typing.Iterable`, `Sized`, `Hashable`, `SupportsInt`, `SupportsFloat`, `SupportsAbs`, `typing.SupportsIndex`, and `os.PathLike` are Protocol-like interfaces: `collections.abc.Iterable` matches any class with `__iter__`, with no inheritance.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want type-safe duck typing without forcing inheritance
- Dependencies come from third-party code you cannot change
- You write test doubles and swappable services (DI)
- You describe callbacks via a `__call__` protocol

❌ Avoid when:
- You need runtime enforcement of required methods (use ABC)
- You want to share implementation code across classes (use a base class or mixin)
- You do not run a type checker (you gain little)
- You rely on `isinstance` with signature checks

---

## 📊 Visual Diagram
```
 Nominal (ABC):                    Structural (Protocol):

 Base <-- inherits --- Child       Sender (Protocol)  (just a shape)
 must say "I am a Base"               send(msg) -> None
                                           ^
                                           | "has send(msg)? then it fits"
                          +----------------+----------------+
                          |                |                |
                     EmailClient     TwilioClient       FakeSender
                     (yours)         (3rd party)        (tests)
                     no inheritance anywhere

 Checked by:  mypy / pyright (before running)   -- Python itself ignores it
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Protocol | Interface defined by shape | shape से बना interface |
| Structural typing | Match by members, not by inheritance | members से match, inheritance से नहीं |
| Nominal typing | Match by declared inheritance | declared inheritance से match |
| Duck typing | Use an object if it has the needed methods | जरूरी methods हों तो object चलाओ |
| `@runtime_checkable` | Allows `isinstance` with Protocol | Protocol के साथ `isinstance` की अनुमति |
| Type checker | Tool like mypy/pyright that checks hints | hints जांचने वाला tool |

---

## ⚡ 3-Line Summary
English: A `Protocol` describes the shape (methods/attributes) an object needs, and any class with that shape matches without inheriting. It is checked by mypy/pyright, not by Python at runtime. Use it for swappable services and test doubles; use ABC when you need runtime enforcement.
Hindi: `Protocol` उस shape (methods/attributes) को बताता है जो object में चाहिए, और वह shape रखने वाली कोई भी class बिना inherit किए match हो जाती है। इसे mypy/pyright जांचते हैं, Python runtime पर नहीं। Swappable services और test doubles के लिए इसे use करें; runtime enforcement चाहिए तो ABC।

---

## ➡️ Next Topic
**116. Functional Programming in Python** (already covered) - then continue with **117. map() Function**: apply a function to every item of an iterable lazily.
