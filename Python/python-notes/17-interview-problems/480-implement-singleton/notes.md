---

# 480. Implement Singleton
# हिंदी में: Singleton बनाना (सिर्फ एक Instance)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13).

---

## 🔵 Simple Definition (English)
A singleton is a class that only ever has one instance. Every time you "create" it, you get the same object. It is used for shared resources like configuration, a logger, or a connection pool.

## 🔵 सरल परिभाषा (Hindi)
Singleton ऐसी class है जिसका हमेशा सिर्फ एक ही instance होता है। जब भी आप उसे "बनाते" हैं, वही एक object मिलता है। Configuration, logger या connection pool जैसे साझा resources के लिए इस्तेमाल होता है।

---

## 🔴 Problem it Solves
Creating many copies of something that should be shared causes bugs and waste: five different settings objects that disagree, ten connection pools opening 500 connections, multiple loggers writing to the same file. Singleton guarantees one shared instance and one global access point.

## 🔴 यह क्यों बना? (Hindi)
जो चीज़ साझा होनी चाहिए उसकी कई copies बनाने से bugs और बर्बादी होती है: पाँच अलग settings objects जो आपस में अलग मान रखें, दस connection pools जो 500 connections खोल दें, कई loggers जो एक ही file में लिखें। Singleton एक साझा instance और एक global access point की गारंटी देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep a place to store the one instance (class attribute / dict / module)
Step 2 → On creation, check: does an instance already exist?
Step 3 → No -> create it and store it. Yes -> return the stored one
Step 4 → Threads: protect the check-and-create with a Lock (double-checked locking)
Step 5 → Ways: module-level object, __new__, decorator, metaclass, cached factory
Step 6 → Simplest Pythonic way: a module (imported once) or functools.lru_cache factory
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक instance रखने की जगह तय करो (class attribute / dict / module)
Step 2 → बनाते समय जाँचो: instance पहले से है क्या?
Step 3 → नहीं -> बनाकर रख लो। हाँ -> रखा हुआ लौटा दो
Step 4 → Threads: check-और-create को Lock से बचाओ (double-checked locking)
Step 5 → तरीके: module-level object, __new__, decorator, metaclass, cached factory
Step 6 → सबसे Pythonic तरीका: module (एक बार import होता है) या functools.lru_cache factory
```

---

## 🟡 Real World Example
An app `Settings` object read from environment variables once; a shared logger; a Redis/DB connection pool; an ML model loaded into memory once (loading a 2 GB model per request would kill the server); a feature-flag client. In FastAPI the usual pattern is `@lru_cache def get_settings()`.

## 🟡 Real Example Hindi mein
Environment variables से एक बार पढ़ा गया `Settings` object; साझा logger; Redis/DB connection pool; memory में एक बार लोड हुआ ML model (हर request पर 2 GB model लोड करना server को मार देगा); feature-flag client। FastAPI में सामान्य तरीका `@lru_cache def get_settings()` है।

---

## 💻 Code Example — Basic
```python
# Basic singleton with __new__
class Config:
    _instance: "Config | None" = None          # holds the one instance

    def __new__(cls) -> "Config":
        if cls._instance is None:              # first time?
            cls._instance = super().__new__(cls)   # create the object
            cls._instance.debug = True         # initialise once here
        return cls._instance                   # always the same object

a = Config()                                   # first call creates it
b = Config()                                   # second call reuses it
print(a is b)                                  # same object?
b.debug = False                                # change via one name...
print(a.debug)                                 # ...visible through the other

# Output:
# True
# False
```

## 💻 Code Example — Advanced
```python
# Production style: thread-safe metaclass singleton + cached factory (more in main.py)
import functools
import threading
from typing import Any


class SingletonMeta(type):
    _instances: dict[type, Any] = {}           # class -> its one instance
    _lock = threading.Lock()                   # guards creation across threads

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with cls._lock:                        # one thread creates at a time
            if cls not in cls._instances:      # still missing?
                cls._instances[cls] = super().__call__(*args, **kwargs)   # build once
        return cls._instances[cls]             # same object for everyone


class Settings(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.env: str = "prod"                 # runs only once


seen: list[int] = []                           # ids observed by workers

def worker() -> None:
    seen.append(id(Settings()))                # each thread asks for the singleton

threads = [threading.Thread(target=worker) for _ in range(20)]
for t in threads: t.start()                    # race to create it
for t in threads: t.join()                     # wait for all
print(len(set(seen)))                          # one unique id

@functools.lru_cache(maxsize=None)             # the FastAPI-style singleton
def get_settings() -> dict[str, str]:
    return {"env": "prod"}                     # built once, reused after

print(get_settings() is get_settings())        # same object

# Output:
# 1
# True
```

---

## 🟠 JavaScript vs Python Comparison
In JS an ES module is evaluated once, so `export const config = new Config()` is already a singleton. The same is true for Python modules: importing the module gives every importer the same object.

```python
# Python way: config.py
class _Config: ...
config = _Config()          # every `from config import config` gets this same object
```
```javascript
// JavaScript way: config.js
class Config {}
export const config = new Config();   // module cache makes it a singleton
```

---

## 🟠 FastAPI Connection
FastAPI's recommended singleton is a cached dependency: `get_settings()` with `@lru_cache`, injected via `Depends`. This keeps it testable: tests override it with `app.dependency_overrides` instead of fighting a hard-coded global. Heavy objects (ML model, HTTP client) are created in `lifespan` and stored on `app.state`.

```python
from functools import lru_cache
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

@lru_cache                                     # built once per process
def get_settings() -> dict[str, str]:
    return {"env": "prod"}

app = FastAPI()

@app.get("/env")
def env(s: Annotated[dict[str, str], Depends(get_settings)]) -> dict[str, str]:
    return s                                   # same object on every request

c = TestClient(app)
print(c.get("/env").json())                    # {'env': 'prod'}
app.dependency_overrides[get_settings] = lambda: {"env": "test"}   # easy to replace in tests
print(c.get("/env").json())                    # {'env': 'test'}

# Output:
# {'env': 'prod'}
# {'env': 'test'}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: not thread-safe: two threads both see `None` and create two instances.
✅ Correct: use a `Lock` (double-checked) or create at import time.

```python
# Wrong
if cls._instance is None:
    cls._instance = super().__new__(cls)   # race window
# Right
with cls._lock:
    if cls._instance is None:
        cls._instance = super().__new__(cls)
```

❌ Mistake 2: `__init__` re-runs on every `Config()` call with the `__new__` approach, resetting state.
✅ Correct: initialise in `__new__` once, guard `__init__`, or use the metaclass approach.

❌ Mistake 3: using a singleton as a hidden global that makes tests share state (and multi-worker servers still get one instance PER PROCESS).
✅ Correct: prefer dependency injection; use Redis/DB for state shared across processes.

---

## 🧠 Tricky Interview Question
```python
class S:
    _inst = None
    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst
    def __init__(self):
        print("init")
        self.count = 0

a = S(); a.count = 5
b = S()
print(a is b, b.count)
```
Answer: prints `init` twice, then `True 0`. It IS a singleton, but `__init__` runs on every `S()` call and resets `count` to 0, even for `a`. Fix by initialising only once (flag) or using a metaclass.

---

## ⚫ Interview Questions + Answers

Q1: Easiest singleton in Python?
A1: A module-level instance (modules are cached in `sys.modules`), or `@lru_cache` on a factory function.

Q2: Metaclass vs `__new__` vs decorator?
A2: Metaclass: real class, works with subclasses, `__init__` runs once. `__new__`: simple but `__init__` re-runs. Decorator: replaces the class with a function, so `isinstance` and subclassing break.

Q3: Is a singleton thread-safe by default?
A3: No. Use a lock with double-checked locking, or create the instance eagerly at import.

Q4: Why is singleton considered an anti-pattern by some?
A4: Hidden global state, hard to test, tight coupling. Dependency injection gives the same sharing with explicit wiring.

Q5: Does gunicorn with 4 workers share the singleton?
A5: No. Each worker process has its own copy. For shared state use Redis, a database, or a message broker.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Exactly one shared resource is required (config, pool, loaded model)
- Creating the object is expensive
- You need a single coordination point (logger, registry)

❌ Avoid when:
- It is just a convenient global (use DI)
- You need different instances in tests or per tenant
- State must be shared across processes or machines

---

## 📊 Visual Diagram
```
  Settings()  Settings()  Settings()        (3 callers)
      |           |           |
      +-----------+-----------+
                  v
        +---------------------+
        |  _instances dict    |   exists? -- no --> create, store
        |  Settings -> obj#1  |            -- yes -> return obj#1
        +---------------------+
                  |
                  v
             the one object
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Singleton | One instance per class | एक ही instance |
| Metaclass | Class of a class | class की class |
| `__new__` | Creates the object before `__init__` | object बनाने वाला method |
| Double-checked locking | Check, lock, check again | दो बार जाँच के साथ lock |
| Dependency injection | Passing dependencies in explicitly | dependencies बाहर से देना |
| Global state | Shared mutable data | साझा बदलने वाला data |

---

## ⚡ 3-Line Summary
English: A singleton makes sure a class has exactly one shared instance.
English: In Python use a module, `@lru_cache` factory, or a thread-safe metaclass.
English: Prefer dependency injection in FastAPI, and remember each worker process has its own instance.

Hindi: Singleton यह तय करता है कि class का सिर्फ एक साझा instance हो।
Hindi: Python में module, `@lru_cache` factory या thread-safe metaclass इस्तेमाल करो।
Hindi: FastAPI में dependency injection चुनो, और याद रखो कि हर worker process का अपना instance होता है।

---

## ➡️ Next Topic
**481. Build REST API (FastAPI)** — put the patterns together in a real CRUD service.

---
