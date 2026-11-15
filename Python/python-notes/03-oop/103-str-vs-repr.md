---

# 103. __str__ vs __repr__
# हिंदी में: __str__ बनाम __repr__ (User के लिए text बनाम Developer के लिए text)

---

## 🔵 Simple Definition (English)
`__str__` returns a friendly, readable text of an object for end users (used by `print()` and `str()`). `__repr__` returns an unambiguous text for developers (used in the REPL, logs, debuggers, and inside containers). Rule of thumb: `__repr__` should ideally look like the code that recreates the object.

## 🔵 सरल परिभाषा (Hindi)
`__str__` object का सरल, पढ़ने लायक text end users के लिए लौटाता है (`print()` और `str()` इस्तेमाल करते हैं)। `__repr__` developers के लिए साफ, अस्पष्ट न होने वाला text लौटाता है (REPL, logs, debugger और containers के अंदर इस्तेमाल होता है)। नियम: `__repr__` ऐसा दिखे जैसे object दोबारा बनाने वाला code।

---

## 🔴 Problem it Solves
By default, printing an object gives `<__main__.User object at 0x7f3a...>`, which tells you nothing in a log at 3 AM. You need two kinds of text: a nice one for the UI ("Asha (asha@x.com)") and a precise one for debugging (`User(id=7, email='asha@x.com')`). Python separates these two jobs into `__str__` and `__repr__`.

## 🔴 यह क्यों बना? (Hindi)
Default में object print करने पर `<__main__.User object at 0x7f3a...>` आता है, जो रात 3 बजे log में कुछ नहीं बताता। दो तरह का text चाहिए: UI के लिए सुंदर ("Asha (asha@x.com)") और debugging के लिए सटीक (`User(id=7, email='asha@x.com')`). Python इन दो कामों को `__str__` और `__repr__` में बांटता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → print(obj) or str(obj) or f"{obj}"  -> calls obj.__str__()
Step 2 → If __str__ is missing -> Python falls back to __repr__
Step 3 → repr(obj), REPL echo, debugger, logging "%r", and items inside list/dict -> obj.__repr__()
Step 4 → If __repr__ is missing -> default <Class object at 0x...>
Step 5 → f"{obj!r}" forces repr; f"{obj!s}" forces str
Step 6 → Both must return a str (otherwise TypeError)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → print(obj) या str(obj) या f"{obj}"  -> obj.__str__() call होता है
Step 2 → __str__ न हो तो Python __repr__ पर आ जाता है
Step 3 → repr(obj), REPL echo, debugger, logging "%r", और list/dict के अंदर के items -> obj.__repr__()
Step 4 → __repr__ भी न हो तो default <Class object at 0x...>
Step 5 → f"{obj!r}" repr को और f"{obj!s}" str को force करता है
Step 6 → दोनों को str ही लौटाना होता है (वरना TypeError)
```

---

## 🟡 Real World Example
A Razorpay-style `Payment` object: `str(p)` -> "Rs 499.00 paid by Asha" (shown in an email), `repr(p)` -> `Payment(id='pay_8F2', amount=49900, status='captured')` (shown in a Sentry error or log line). When an exception is logged with `logger.error("failed: %r", payment)`, the repr tells engineers exactly which object failed.

## 🟡 Real Example Hindi mein
Razorpay जैसा `Payment` object: `str(p)` -> "Rs 499.00 paid by Asha" (email में दिखता है), `repr(p)` -> `Payment(id='pay_8F2', amount=49900, status='captured')` (Sentry error या log में दिखता है)। जब `logger.error("failed: %r", payment)` लिखते हैं तो repr बताता है कि कौन सा object fail हुआ।

---

## 💻 Code Example — Basic
```python
# Basic __str__ vs __repr__
class User:                                     # simple class
    def __init__(self, name: str, email: str) -> None:    # constructor
        self.name: str = name                   # name
        self.email: str = email                 # email

    def __str__(self) -> str:                   # for end users
        return f"{self.name} <{self.email}>"    # friendly text

    def __repr__(self) -> str:                  # for developers
        return f"User(name={self.name!r}, email={self.email!r})"    # !r adds quotes


u: User = User("Asha", "a@x.com")               # create object
print(u)                                        # print uses __str__
print(repr(u))                                  # explicit repr
print([u])                                      # containers show items with __repr__
print(f"{u} | {u!r}")                          # f-string: default str, !r forces repr


class OnlyRepr:                                 # no __str__ defined
    def __repr__(self) -> str:
        return "OnlyRepr()"


print(OnlyRepr())                               # str falls back to repr
print(str("hi"), repr("hi"))                    # built-in str: repr adds quotes

# Output:
# Asha <a@x.com>
# User(name='Asha', email='a@x.com')
# [User(name='Asha', email='a@x.com')]
# Asha <a@x.com> | User(name='Asha', email='a@x.com')
# OnlyRepr()
# hi 'hi'
```

## 💻 Code Example — Advanced
```python
# Production style: safe repr (no secrets), eval-able repr, dataclass, __format__
from dataclasses import dataclass, field        # dataclass tools
from decimal import Decimal                     # exact money


@dataclass
class Payment:
    id: str                                     # gateway id
    amount: Decimal                             # money amount
    card_number: str = field(repr=False)        # NEVER put secrets in repr / logs
    status: str = "created"

    def __str__(self) -> str:                   # human text
        return f"Rs {self.amount:.2f} ({self.status})"

    def __format__(self, spec: str) -> str:     # custom f"{p:short}"
        if spec == "short":                     # custom format spec
            return self.id                      # just the id
        return str(self)                        # default


p: Payment = Payment("pay_1", Decimal("499"), "4111111111111111")
print(p)                                        # str: friendly
print(repr(p))                                  # repr: auto-generated, card hidden
print(f"{p:short} / {p}")                       # __format__ in action
assert "4111" not in repr(p)                    # secret never appears


class Point:                                    # eval-able repr
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x!r}, {self.y!r})"   # subclass-friendly

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Point) and (self.x, self.y) == (o.x, o.y)


pt: Point = Point(1, 2)                         # create
clone = eval(repr(pt), {"Point": Point})        # demo only: round-trip (never eval untrusted text)
print(repr(pt), clone == pt)                    # repr recreates an equal object


class Broken:                                   # bad repr must not crash logging
    def __repr__(self) -> str:
        raise RuntimeError("oops")              # a buggy repr


try:                                            # str() on broken repr
    str(Broken())                               # falls back to repr -> raises
except RuntimeError as e:
    print("Error:", e)

# Output:
# Rs 499.00 (created)
# Payment(id='pay_1', amount=Decimal('499'), status='created')
# pay_1 / Rs 499.00 (created)
# Point(1, 2) True
# Error: oops
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| User-facing text | `__str__` | `toString()` |
| Developer-facing text | `__repr__` | `util.inspect.custom` (Node) / `[Symbol.for('nodejs.util.inspect.custom')]` |
| `print` / `console.log` | `print` -> `__str__` | `console.log` -> inspect view (not toString) |
| Template strings | f"{obj}" -> `__str__` | `${obj}` -> `toString()` |
| Fallback | `__str__` -> `__repr__` | `toString()` -> `[object Object]` |

```python
# Python way
class P:
    def __str__(self) -> str:
        return "friendly"
    def __repr__(self) -> str:
        return "P()"

print(P(), [P()])       # friendly [P()]
```
```javascript
// JavaScript way
class P {
  toString() { return "friendly"; }
}
console.log(`${new P()}`);     // friendly   (template string uses toString)
console.log(String(new P()));  // friendly
console.log([new P()]);        // [ P {} ]   (console.log uses inspect, not toString)
```

Key difference: JavaScript has only one text hook (`toString`) and a separate inspect mechanism in Node. Python has two clear hooks, and `repr` is what you see in lists, logs and the REPL.

---

## 🟠 FastAPI Connection
Good `__repr__` methods make FastAPI logs and exception reports readable. Pydantic models already generate a repr, and you hide secrets with `Field(repr=False)` so passwords never appear in error logs.

```python
# FastAPI example — Pydantic repr hides secrets
from fastapi import FastAPI                    # app
from fastapi.testclient import TestClient      # test client
from pydantic import BaseModel, Field          # schema and field options


class Signup(BaseModel):
    email: str
    password: str = Field(repr=False)          # excluded from repr/logs


app: FastAPI = FastAPI()                       # create app
log: list[str] = []                            # stand-in for a logger


@app.post("/signup")                           # POST /signup
def signup(data: Signup) -> dict[str, str]:
    log.append(f"signup request: {data!r}")    # repr in the log line
    return {"ok": data.email}


client: TestClient = TestClient(app)           # test client
client.post("/signup", json={"email": "a@x.com", "password": "pw123"})
print(log[0])                                  # password is not present

# Output:
# signup request: Signup(email='a@x.com')
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Defining only `__str__` and expecting good debug output
✅ Correct: always define `__repr__` first; `__str__` is optional

```python
class Wrong:
    def __str__(self) -> str:
        return "pretty"

class Right:
    def __repr__(self) -> str:
        return "Right()"

print([Wrong()])           # [<__main__.Wrong object at 0x...>]  (address varies)
print([Right()])           # [Right()]
```

❌ Mistake 2: Returning a non-string
✅ Correct: always return `str`

```python
class Wrong:
    def __str__(self):
        return 42                       # not a string

try:
    str(Wrong())
except TypeError as e:
    print("Error:", e)                  # __str__ returned non-string (type int)
```

❌ Mistake 3: Putting secrets or huge data into `__repr__`
✅ Correct: exclude passwords/tokens; truncate big payloads

```python
class Wrong:
    def __init__(self) -> None:
        self.token = "sk_live_abc"
    def __repr__(self) -> str:
        return f"Wrong(token={self.token!r})"      # leaks into logs

class Right(Wrong):
    def __repr__(self) -> str:
        return "Right(token='***')"                # masked

print(repr(Right()))                               # Right(token='***')
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def __repr__(self) -> str:
        return "repr-A"

class B(A):
    def __str__(self) -> str:
        return "str-B"

b = B()
print(b)
print([b])
print(f"{b!r} {b!s}")
print("%s %r" % (b, b))
```
Answer: `str-B`, then `[repr-A]`, then `repr-A str-B`, then `str-B repr-A`. `print(b)` uses `__str__` (defined in B). Lists always use `repr` of their items, and B inherits `__repr__` from A. `!r` forces repr and `!s` forces str; `%s` and `%r` do the same in old-style formatting.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `__str__` and `__repr__`?
A1: `__str__` is readable output for users (`print`, `str`). `__repr__` is unambiguous output for developers (`repr`, REPL, logs, containers). If only one is defined, define `__repr__`, because `str()` falls back to it.

Q2: What should a good `__repr__` look like?
A2: Ideally valid Python that recreates the object: `Point(1, 2)`. If that is impossible, use `<Point x=1 y=2>`. Use `{self.x!r}` so strings get quotes, and `type(self).__name__` so subclasses show correctly.

Q3: Which is used inside a list or dict?
A3: `repr`. `print([obj])` shows `repr(obj)` for each element even if `__str__` exists.

Q4: What does `@dataclass` give you?
A4: An auto-generated `__repr__` such as `Payment(id='pay_1', ...)`. It does not generate `__str__`, so `str()` falls back to the repr. Use `field(repr=False)` to hide fields.

Q5: What is `__format__`?
A5: It controls `format(obj, spec)` and `f"{obj:spec}"`. By default it calls `str(obj)` when the spec is empty and raises `TypeError` for non-empty specs, so implement it if you want custom specs (like `datetime` does for `%Y-%m-%d`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always define `__repr__` for classes that appear in logs or debugging
- Define `__str__` for user-visible text (emails, UI, reports)
- Hiding sensitive fields from logs

❌ Avoid when:
- Doing slow work (database calls) inside them - logging calls them often
- Putting secrets or very large data in the output
- Using `__str__` to return JSON for APIs (use `model_dump()` / `json.dumps`)

---

## 📊 Visual Diagram
```
                 obj
        +---------+----------+
        |                    |
  print(obj)           repr(obj)
  str(obj)             REPL echo
  f"{obj}"             logs  %r
        |              [obj] inside list
        v                    v
    __str__  --missing-->  __repr__  --missing--> <Class object at 0x..>
   (for users)           (for developers)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__str__` | Friendly text for users | Users के लिए सरल text |
| `__repr__` | Precise text for developers | Developers के लिए सटीक text |
| `!r` / `!s` | f-string flags forcing repr / str | f-string में repr / str चुनने वाले flags |
| `__format__` | Controls `format()` and f-string specs | f-string specs का नियंत्रण |
| REPL | Interactive Python shell | Interactive Python shell |
| Fallback | Use another method if missing | न मिलने पर दूसरा method |

---

## ⚡ 3-Line Summary
English: `__str__` is for readable output (`print`), `__repr__` is for precise developer output (logs, REPL, containers). Always write `__repr__`; add `__str__` only when users need a different text. Never leak secrets in either.
Hindi: `__str__` पढ़ने लायक output (`print`) के लिए है, `__repr__` developers के सटीक output (logs, REPL, containers) के लिए। हमेशा `__repr__` लिखें; `__str__` तभी जब users को अलग text चाहिए। किसी में भी secrets leak न करें।

---

## ➡️ Next Topic
**104. `__len__`, `__getitem__`, `__setitem__`** — make your class behave like a list or dict: `len(x)`, `x[0]`, `x[0] = 5`.
