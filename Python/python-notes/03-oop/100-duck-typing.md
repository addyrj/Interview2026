---

# 100. Duck Typing
# हिंदी में: Duck Typing (क्लास नहीं, क्षमता देखो)

---

## 🔵 Simple Definition (English)
Duck typing means Python cares about what an object can DO (which methods it has), not what class it IS. "If it walks like a duck and quacks like a duck, it is a duck." You just call the method; if it exists, it works.

## 🔵 सरल परिभाषा (Hindi)
Duck typing का मतलब है कि Python यह देखता है कि object क्या कर सकता है (कौन से methods हैं), यह नहीं कि वह किस class का है। "जो बत्तख की तरह चलता और बोलता है, वह बत्तख है।" आप बस method call करते हैं; मौजूद है तो चलता है।

---

## 🔴 Problem it Solves
Strict type checks (`if isinstance(x, File)`) make code rigid: a `StringIO`, a network socket wrapper or a test fake cannot be used even if it behaves like a file. Duck typing removes the inheritance requirement, so any compatible object can be plugged in. This is why `json.load(f)` works with files, `StringIO`, `tempfile` objects, and your own reader class.

## 🔴 यह क्यों बना? (Hindi)
सख्त type checks (`if isinstance(x, File)`) code को कठोर बना देते हैं: `StringIO`, network socket wrapper या test fake file जैसा व्यवहार करे तब भी इस्तेमाल नहीं हो सकता। Duck typing से inheritance की ज़रूरत हट जाती है, इसलिए कोई भी compatible object लग सकता है। इसीलिए `json.load(f)` files, `StringIO`, `tempfile` objects और आपकी अपनी reader class के साथ चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Function receives an object, any object: def save(out): out.write("data")
Step 2 → It does NOT check the type; it just uses the method it needs
Step 3 → At runtime Python looks up "write" on that object (attribute lookup)
Step 4 → Found -> it runs. Not found -> AttributeError (or TypeError)
Step 5 → EAFP style: try it, handle the failure  (Easier to Ask Forgiveness than Permission)
Step 6 → LBYL style: hasattr()/isinstance() first - used less in Python
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Function को कोई भी object मिलता है: def save(out): out.write("data")
Step 2 → वह type check नहीं करता; बस जिस method की ज़रूरत है उसे use करता है
Step 3 → Runtime पर Python उस object पर "write" ढूंढता है (attribute lookup)
Step 4 → मिला -> चलता है। नहीं मिला -> AttributeError (या TypeError)
Step 5 → EAFP style: कोशिश करो, fail हो तो संभालो  (माफ़ी मांगना, इजाज़त लेने से आसान)
Step 6 → LBYL style: पहले hasattr()/isinstance() - Python में कम इस्तेमाल होता है
```

---

## 🟡 Real World Example
A logging helper writes to "anything with `.write()`": a real file in production, `sys.stdout` in dev, `io.StringIO` in unit tests. A data loader accepts anything iterable: a list, a generator reading a huge CSV, or a database cursor. Libraries like `requests` accept any "file-like" object for uploads.

## 🟡 Real Example Hindi mein
Logging helper "`.write()` वाली किसी भी चीज़" में लिखता है: production में असली file, dev में `sys.stdout`, unit tests में `io.StringIO`। Data loader कोई भी iterable लेता है: list, बड़ी CSV पढ़ने वाला generator, या database cursor। `requests` जैसी libraries uploads के लिए कोई भी "file-like" object लेती हैं।

---

## 💻 Code Example — Basic
```python
# Basic duck typing example
class Duck:                                     # a real duck
    def quack(self) -> str:                     # the behavior we care about
        return "Quack!"


class Person:                                   # not a duck, no common parent
    def quack(self) -> str:                     # but can quack
        return "I can imitate: Quack!"


class Stone:                                    # cannot quack
    pass


def make_it_quack(thing: object) -> str:        # accepts anything
    return thing.quack()                        # type: ignore[attr-defined]  - just call it


print(make_it_quack(Duck()))                    # works
print(make_it_quack(Person()))                  # works: no inheritance needed
try:                                            # EAFP: try first
    make_it_quack(Stone())                      # no quack method
except AttributeError as e:                     # handle the failure
    print("Error:", e)                          # clear message

print(len("abc"), len([1, 2, 3]), len({"a": 1}))    # len() works on any object with __len__
for ch in "hi":                                 # for works on anything iterable
    print(ch, end=" ")                          # h i
print()                                         # newline

# Output:
# Quack!
# I can imitate: Quack!
# Error: 'Stone' object has no attribute 'quack'
# 3 3 1
# h i
```

## 💻 Code Example — Advanced
```python
# Production style: file-like duck typing, EAFP, Protocol for static checking
import io                                       # in-memory file
import sys                                      # stdout
from typing import Protocol                     # structural typing for type checkers


class Writable(Protocol):                       # documents the "duck" we need
    def write(self, s: str, /) -> int: ...      # only the method we actually use


class ListWriter:                               # our own file-like class
    def __init__(self) -> None:
        self.lines: list[str] = []              # captured text

    def write(self, s: str, /) -> int:          # matches the protocol
        self.lines.append(s)                    # store instead of printing
        return len(s)


def write_report(out: Writable, rows: list[tuple[str, int]]) -> int:
    """Write a report to ANY writable object."""
    total: int = 0                              # characters written
    for name, amount in rows:                   # each row
        total += out.write(f"{name}: {amount}\n")    # same call for every target
    return total


def safe_close(resource: object) -> bool:       # EAFP style
    try:
        resource.close()                        # type: ignore[attr-defined]
        return True                             # it had close()
    except AttributeError:                      # not closable
        return False                            # ignore quietly


data: list[tuple[str, int]] = [("Asha", 500), ("Ravi", 300)]    # sample rows
buf: io.StringIO = io.StringIO()                # in-memory file
lw: ListWriter = ListWriter()                   # custom writer

write_report(sys.stdout, data)                  # real stdout
write_report(buf, data)                         # StringIO
write_report(lw, data)                          # our class
print(repr(buf.getvalue()))                     # captured text
print(lw.lines)                                 # captured list
print(safe_close(buf), safe_close(lw), safe_close(42))   # True False False

# Output:
# Asha: 500
# Ravi: 300
# 'Asha: 500\nRavi: 300\n'
# ['Asha: 500\n', 'Ravi: 300\n']
# True False False
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Duck typing | Yes (runtime) | Yes (runtime) |
| Missing method error | `AttributeError` | `TypeError: x.quack is not a function` |
| Check capability | `hasattr(x, "quack")` | `typeof x.quack === "function"` |
| Static duck typing | `typing.Protocol` | TypeScript structural interfaces |
| Philosophy | EAFP (try/except) | Mostly the same |

```python
# Python way
class A:
    def run(self) -> str:
        return "A"

def go(x) -> str:
    return x.run()          # no type check

print(go(A()))              # A
print(hasattr(5, "run"))    # False
```
```javascript
// JavaScript way
class A { run() { return "A"; } }
function go(x) { return x.run(); }              // no type check either
console.log(go(new A()));                       // A
console.log(typeof (5).run === "function");     // false
```

Key difference: the idea is identical in both languages. The difference is tooling: Python offers `Protocol` and mypy for optional static checks, TypeScript gives the same with interfaces. Python's EAFP style prefers `try/except` over feature checks.

---

## 🟠 FastAPI Connection
FastAPI itself leans on duck typing: `UploadFile.file` is file-like, response bodies accept any iterable for `StreamingResponse`, and dependencies can be any callable (function, class, object with `__call__`).

```python
# FastAPI example — dependency is "any callable", including an object with __call__
from fastapi import FastAPI, Depends           # app and DI
from fastapi.testclient import TestClient      # test client


class RateLimiter:                             # not a function, but callable
    def __init__(self, limit: int) -> None:
        self.limit: int = limit                # allowed calls

    def __call__(self, user: str = "guest") -> str:    # makes the instance callable
        return f"{user} limited to {self.limit}/min"   # pretend check


def plain_dep() -> str:                        # a normal function dependency
    return "plain"


app: FastAPI = FastAPI()                       # create app


@app.get("/a")
def route_a(info: str = Depends(RateLimiter(10))) -> dict[str, str]:   # object as dependency
    return {"info": info}


@app.get("/b")
def route_b(info: str = Depends(plain_dep)) -> dict[str, str]:         # function as dependency
    return {"info": info}


client: TestClient = TestClient(app)           # test client
print(client.get("/a").json(), client.get("/b").json())

# Output:
# {'info': 'guest limited to 10/min'} {'info': 'plain'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Checking `isinstance(x, list)` when any iterable would work
✅ Correct: accept the behavior you need (iteration)

```python
def total_wrong(x: object) -> int:
    if not isinstance(x, list):          # rejects tuples, sets, generators
        raise TypeError("list only")
    return sum(x)

def total_right(x) -> int:
    return sum(x)                        # any iterable of numbers

print(total_right((1, 2, 3)), total_right(i for i in range(4)))   # 6 6
```

❌ Mistake 2: Catching too broad an exception around the duck call
✅ Correct: keep the `try` small, or you hide real bugs

```python
class Thing:
    def go(self) -> None:
        raise AttributeError("bug inside go()")   # real bug, same exception type

t = Thing()
try:
    t.go()                                # Wrong: cannot tell missing method from inner bug
except AttributeError:
    print("treated as 'no go method'")    # misleading

# Right: check, then call outside the try
if hasattr(t, "go"):
    try:
        t.go()
    except AttributeError as e:
        print("real bug:", e)             # real bug: bug inside go()
```

❌ Mistake 3: Assuming a method exists with the same meaning
✅ Correct: document the expected behavior (use a `Protocol`)

```python
class Reader:
    def read(self) -> str:                # returns whole text
        return "abc"

class Stream:
    def read(self, n: int) -> str:        # needs a size argument
        return "ab"[:n]

def load(src) -> str:
    return src.read()                     # works for Reader only

print(load(Reader()))                     # abc
try:
    load(Stream())
except TypeError as e:
    print("Error:", e)                    # read() missing 1 required positional argument: 'n'
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class Wallet:
    def __len__(self) -> int:
        return 0

w = Wallet()
print(bool(w))
print(len(w))
if w:
    print("has money")
else:
    print("empty")
```
Answer: `False`, `0`, `empty`. A class with no `__bool__` is truth-tested using `__len__`: a length of 0 means falsy. The object "quacks" like an empty container, so Python treats it as empty even though it is not a built-in. Lesson: duck typing also covers truthiness; define `__bool__` if you want explicit control.

---

## ⚫ Interview Questions + Answers

Q1: What is duck typing?
A1: Behavior-based typing: an object is usable if it has the needed methods/attributes, regardless of its class or inheritance. Python checks at call time.

Q2: EAFP vs LBYL?
A2: EAFP: "try it and catch the exception" (Pythonic, avoids race conditions, fewer lookups when success is common). LBYL: "look before you leap" with `hasattr`/`isinstance` checks. Use LBYL when failing has side effects.

Q3: How do you get type safety with duck typing?
A3: Use `typing.Protocol` and a checker like mypy/pyright: structural checks before runtime, with no inheritance. For runtime guards, `@runtime_checkable` or `collections.abc` classes (`Iterable`, `Sized`).

Q4: What are the downsides of duck typing?
A4: Errors show up late (at call time), IDE help is weaker, and "same method name, different meaning" mistakes are possible. Mitigate with type hints, tests and Protocols.

Q5: Name built-in duck-typed protocols.
A5: Iteration (`__iter__`/`__next__`), sizing (`__len__`), containers (`__getitem__`, `__contains__`), context managers (`__enter__`/`__exit__`), callables (`__call__`), file-like (`read`/`write`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Accepting file-like, iterable or callable inputs
- Writing testable code with simple fakes
- Libraries that should work with user-defined types

❌ Avoid when:
- Failing late is dangerous (add validation or Protocols)
- Public APIs need clear, documented contracts (use type hints/ABC)
- The same method name could mean different things

---

## 📊 Visual Diagram
```
 write_report(out, rows)       needs only:  out.write(str)

   sys.stdout   -- has write() -->  OK
   StringIO     -- has write() -->  OK
   ListWriter   -- has write() -->  OK
   42           -- no write()  -->  AttributeError

 Class names do not matter. Only the behavior matters.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Duck typing | Judge by behavior, not class | Behavior से पहचान, class से नहीं |
| EAFP | Try first, handle errors | पहले करो, error संभालो |
| LBYL | Check first, then act | पहले जांचो, फिर करो |
| File-like object | Object with read/write | read/write वाला object |
| Protocol | Static description of required methods | ज़रूरी methods का static विवरण |
| Callable | Anything with `__call__` | `__call__` वाली कोई भी चीज़ |

---

## ⚡ 3-Line Summary
English: Duck typing means using an object by its methods, not its class. It makes code flexible (files, `StringIO`, fakes all work) and favors try/except (EAFP). Use `Protocol` and type hints to document and statically check the expected behavior.
Hindi: Duck typing में object को उसके methods से इस्तेमाल करते हैं, उसकी class से नहीं। इससे code flexible रहता है (files, `StringIO`, fakes सब चलते हैं) और try/except (EAFP) पसंद किया जाता है। अपेक्षित behavior को document और static check करने के लिए `Protocol` और type hints इस्तेमाल करें।

---

## ➡️ Next Topic
**101. Operator Overloading** — make `+`, `-`, `==` and `*` work on your own objects like `Money` or `Vector`.
