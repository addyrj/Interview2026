---

# 083. __init__ Method
# हिंदी में: __init__ Method (Constructor / शुरुआती setup)

---

## 🔵 Simple Definition (English)
`__init__` is a special method that Python calls automatically right after a new object is created. You use it to set the starting values (attributes) of the object. It must return `None`.

## 🔵 सरल परिभाषा (Hindi)
`__init__` एक special method है जिसे Python नया object बनते ही अपने आप call करता है। इससे object की शुरुआती values (attributes) set की जाती हैं। यह `None` return करना चाहिए।

---

## 🔴 Problem it Solves
Without a constructor you would create an empty object and then set every attribute by hand: `u = User(); u.name = ...; u.email = ...`. It is easy to forget one, and the object can exist in a half-ready state. `__init__` forces the caller to give required values and lets you validate them once, so every object starts in a valid state.

## 🔴 यह क्यों बना? (Hindi)
Constructor के बिना आप खाली object बनाते और हर attribute हाथ से set करते: `u = User(); u.name = ...; u.email = ...`। कोई एक भूल जाना आसान है और object अधूरी हालत में रह सकता है। `__init__` caller से ज़रूरी values मंगवाता है और उन्हें एक ही जगह validate करता है, ताकि हर object सही state में शुरू हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write `User('Asha', 'a@b.com')`
Step 2 → Python calls `User.__new__(User, ...)` which allocates an empty object
Step 3 → Python calls `__init__(obj, 'Asha', 'a@b.com')` on that object
Step 4 → Inside, `self.name = name` stores data on the object
Step 5 → `__init__` returns None (returning anything else raises TypeError)
Step 6 → The ready object is returned to the caller
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप `User('Asha', 'a@b.com')` लिखते हैं
Step 2 → Python `User.__new__(User, ...)` call करता है जो खाली object बनाता है
Step 3 → Python उस object पर `__init__(obj, 'Asha', 'a@b.com')` call करता है
Step 4 → अंदर `self.name = name` object में data रखता है
Step 5 → `__init__` None return करता है (कुछ और return करने पर TypeError)
Step 6 → तैयार object caller को मिल जाता है
```

---

## 🟡 Real World Example
A signup service builds a `User` object from the request: `__init__` lowercases the email, rejects empty names and sets `created_at`. An AI app creates an `LLMClient(api_key, model, timeout=30)` once at startup; `__init__` stores the settings and creates the HTTP session.

## 🟡 Real Example Hindi mein
Signup service request से `User` object बनाती है: `__init__` email को lowercase करता है, खाली name reject करता है और `created_at` set करता है। AI app startup पर एक बार `LLMClient(api_key, model, timeout=30)` बनाती है; `__init__` settings रखता है और HTTP session बनाता है।

---

## 💻 Code Example — Basic
```python
# Basic: __init__ initialises a new object
class User:                                       # simple class
    def __init__(self, name: str, email: str, age: int = 18) -> None:   # self + parameters
        self.name: str = name                     # store name on the object
        self.email: str = email.lower()           # normalise before storing
        self.age: int = age                       # default value used if not passed
        print(f"init called for {self.name}")     # proves __init__ runs automatically


u1: User = User("Asha", "ASHA@Mail.com")          # age uses default 18
u2: User = User(name="Raj", email="raj@x.com", age=30)   # keyword arguments
print(u1.email, u1.age, u2.age)                   # asha@mail.com 18 30
print(User.__init__(u1, "Zed", "z@z.com"))        # __init__ is a normal method and returns None
print(u1.name)                                    # calling it again re-initialised u1

try:                                              # missing required argument
    User("OnlyName")                              # email missing
except TypeError as e:                            # Python raises TypeError
    print("Error:", e)


class Real:                                       # shows __new__ then __init__
    def __new__(cls, *args: object) -> "Real":    # __new__ CREATES the object
        print("new")                              # runs first
        return super().__new__(cls)               # allocate memory

    def __init__(self, x: int) -> None:           # __init__ INITIALISES it
        print("init")                             # runs second
        self.x: int = x


Real(1)                                           # new then init

# Output:
# init called for Asha
# init called for Raj
# asha@mail.com 18 30
# init called for Zed
# None
# Zed
# Error: User.__init__() missing 1 required positional argument: 'email'
# new
# init
```

## 💻 Code Example — Advanced
```python
# Advanced: validation, defaults without mutable bugs, alternate constructors
from __future__ import annotations
import re                                         # simple email check
from datetime import datetime, timezone           # timestamps


class Order:                                      # an e-commerce order
    _EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")   # tiny email pattern

    def __init__(self, customer_email: str, items: list[str] | None = None) -> None:
        if not self._EMAIL.match(customer_email):         # validate input
            raise ValueError(f"invalid email: {customer_email!r}")
        self.customer_email: str = customer_email         # store valid email
        self.items: list[str] = list(items) if items else []   # NEW list per object, copy input
        self.created_at: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)   # fixed so output is stable
        self.status: str = "pending"                      # start state

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Order: # alternate constructor (JSON -> object)
        return cls(str(data["email"]), list(data.get("items", [])))   # type: ignore[arg-type]

    def __repr__(self) -> str:
        return f"Order({self.customer_email!r}, items={self.items}, status={self.status!r})"


o1: Order = Order.from_dict({"email": "a@b.com", "items": ["pen"]})
o2: Order = Order("c@d.com")
o1.items.append("book")                           # modifies only o1
print(o1, o2, sep="\n")
src: list[str] = ["x"]                            # caller's list
o3: Order = Order("e@f.com", src)
src.append("y")                                   # caller mutates later
print(o3.items)                                   # o3 is safe because we copied
try:
    Order("not-an-email")
except ValueError as e:
    print("Error:", e)


class Bad:                                        # the classic bug
    def __init__(self, tags: list[str] = []) -> None:    # one list shared forever
        self.tags = tags


a, b = Bad(), Bad()
a.tags.append("oops")
print(b.tags)                                     # b is polluted

# Output:
# Order('a@b.com', items=['pen', 'book'], status='pending')
# Order('c@d.com', items=[], status='pending')
# ['x']
# Error: invalid email: 'not-an-email'
# ['oops']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Constructor name | `__init__` | `constructor` |
| Needs `self`/`this` | `self` first parameter | `this` implicit |
| Default values | `age: int = 18` | `age = 18` |
| Overloading | not supported; use defaults or classmethods | not supported |
| Parent constructor | `super().__init__(...)` | `super(...)` |
| Return value | must be None | ignored for primitives |

```python
# Python way
class User:
    def __init__(self, name: str, age: int = 18) -> None:
        self.name: str = name
        self.age: int = age

u = User("Asha")           # age defaults to 18
```
```javascript
// JavaScript way
class User {
  constructor(name, age = 18) {
    this.name = name;
    this.age = age;
  }
}
const u = new User("Asha"); // age defaults to 18
```

Key difference: in JS a derived class must call `super()` before touching `this`; in Python calling `super().__init__()` is a convention you can forget, and Python will not warn you. Python also splits creation (`__new__`) from initialisation (`__init__`).

---

## 🟠 FastAPI Connection
Dependency classes are initialised once with their configuration, then injected into routes. FastAPI also calls `__init__` of your Pydantic models for every request body, which is where validation happens.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


class Settings:                                   # __init__ reads config once
    def __init__(self, env: str = "dev", debug: bool = True) -> None:
        self.env: str = env
        self.debug: bool = debug


settings = Settings(env="prod", debug=False)      # built once at startup


@app.get("/env")
def env() -> dict[str, object]:
    return {"env": settings.env, "debug": settings.debug}


print(TestClient(app).get("/env").json())

# Output:
# {'env': 'prod', 'debug': False}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a mutable default argument
✅ Correct: use `None` and create the list inside

```python
class Bad:
    def __init__(self, tags: list[str] = []) -> None:
        self.tags = tags
a, b = Bad(), Bad()
a.tags.append("x")
print(b.tags)          # Wrong: ['x'] shared

class Good:
    def __init__(self, tags: list[str] | None = None) -> None:
        self.tags = list(tags) if tags else []
print(Good().tags)     # Right: []
```

❌ Mistake 2: Returning a value from `__init__`
✅ Correct: return nothing; use a classmethod for alternate construction

```python
class A:
    def __init__(self):
        return 5
try:
    A()
except TypeError as e:
    print("Error:", e)
```

❌ Mistake 3: Forgetting to call `super().__init__()` in a child
✅ Correct: call the parent init first

```python
class P:
    def __init__(self) -> None:
        self.ready = True

class C(P):
    def __init__(self) -> None:
        pass                      # Wrong: self.ready never set

class C2(P):
    def __init__(self) -> None:
        super().__init__()        # Right
print(hasattr(C(), "ready"), C2().ready)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def __init__(self):
        print("A init")
        return None
    def __new__(cls):
        print("A new")
        return super().__new__(cls)
class B:
    def __new__(cls):
        return 42
    def __init__(self):
        print("B init")
a = A()
b = B()
print(type(b))
```

Output:
```
A new
A init
<class 'int'>
```

Answer: `__new__` always runs first and creates the object, then `__init__` runs, so A prints `A new` then `A init`. For B, `__new__` returns `42`, which is not an instance of B, so Python skips `__init__` and `B init` is never printed. `b` is therefore the integer 42 and `type(b)` is `int`. `__init__` only runs when `__new__` returns an instance of the class.

---

## ⚫ Interview Questions + Answers

Q1: Is `__init__` a constructor?
A1: Almost. It is the initialiser. The real constructor is `__new__`, which creates the object. `__init__` fills it. In everyday code people call `__init__` the constructor.

Q2: Can a class have two `__init__` methods?
A2: No. The second definition replaces the first. Use default arguments, `*args`, or alternate constructors with `@classmethod` such as `from_dict`.

Q3: What is wrong with `def __init__(self, items=[])`?
A3: The default list is created once when the function is defined and reused by every call, so objects share it. Use `None` and create a new list inside.

Q4: What happens if `__init__` raises an exception?
A4: Object creation fails and the exception reaches the caller; no object is returned. This is how you enforce validation, for example raising `ValueError` for bad input.

Q5: When does `__init__` not run?
A5: When `__new__` returns something that is not an instance of the class, or when objects are created without calling it, such as `pickle`/`copy` restoring state or `object.__new__(cls)` used directly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Setting required attributes of every object
- Validating and normalising input once
- Opening resources the object needs (client, session)
- Injecting dependencies (config, repository)

❌ Avoid when:
- Heavy work like network calls or reading big files; use a factory or lazy property
- Business actions with side effects; keep init predictable
- Many optional parameters; use a dataclass or builder instead

---

## 📊 Visual Diagram
```
User("Asha", "A@B.com")
      |
      v
 __new__(cls)     -> empty object  (obj)
      |
      v
 __init__(obj, "Asha", "A@B.com")
      |   self.name  = "Asha"
      |   self.email = "a@b.com"
      v
 ready object returned to caller
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Constructor | Code that builds an object | Object बनाने वाला code |
| Initialiser | `__init__`, sets starting data | शुरुआती data set करने वाला |
| `__new__` | Creates the empty object | खाली object बनाता है |
| Default argument | Value used if none passed | न देने पर इस्तेमाल होने वाली value |
| Alternate constructor | Classmethod that builds objects | Object बनाने का दूसरा तरीका |
| Validation | Checking input is correct | Input सही है या नहीं जाँचना |

---

## ⚡ 3-Line Summary
English: `__init__` runs automatically after the object is created and sets its starting data. It must return None and should validate input. Avoid mutable defaults and remember `super().__init__()` in child classes.
Hindi: `__init__` object बनने के बाद अपने आप चलता है और शुरुआती data set करता है। यह None return करता है और input validate करना चाहिए। Mutable defaults से बचें और child class में `super().__init__()` याद रखें।

---

## ➡️ Next Topic
**084. Instance vs Class Variables** — which data belongs to each object and which is shared by all, and the bugs shared data causes.
