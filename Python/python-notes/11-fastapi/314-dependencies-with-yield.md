---

# 314. Dependencies with yield
# हिंदी में: yield वाली Dependencies (setup और cleanup)

---

## 🔵 Simple Definition (English)
A dependency with `yield` is a generator: code before `yield` is setup, the yielded value is injected into the endpoint, and code after `yield` is cleanup that runs once the endpoint has finished. It works like a context manager for each request. The classic use is opening and closing a DB session.

## 🔵 सरल परिभाषा (Hindi)
`yield` वाली dependency एक generator है: `yield` से पहले का code setup है, yield की गई value endpoint को मिलती है, और `yield` के बाद का code cleanup है जो endpoint खत्म होने के बाद चलता है। यह हर request के लिए context manager जैसा काम करता है। सबसे आम उपयोग DB session खोलना और बंद करना है।

---

## 🔴 Problem it Solves
A normal `return` dependency cannot clean up: nobody closes the DB connection, file or lock after the request, causing connection leaks until the database refuses new clients. Writing `try/finally` in every route is repetitive. `yield` puts open and close logic in one reusable place and guarantees cleanup, even when the endpoint raises an error.

## 🔴 यह क्यों बना? (Hindi)
सामान्य `return` वाली dependency cleanup नहीं कर सकती: request के बाद DB connection, file या lock कोई बंद नहीं करता और connections leak होते रहते हैं जब तक database नए clients लेना बंद न कर दे। हर route में `try/finally` लिखना दोहराव है। `yield` open और close की logic एक reusable जगह रखता है और endpoint में error आने पर भी cleanup की गारंटी देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives, FastAPI calls the generator dependency
Step 2 → Code runs up to `yield db` (SETUP)
Step 3 → The yielded value is injected into your endpoint
Step 4 → Endpoint runs and returns (or raises)
Step 5 → FastAPI resumes the generator after yield (CLEANUP: finally block)
Step 6 → If the endpoint raised, that exception is thrown INTO the generator at the yield line
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request आती है, FastAPI generator dependency को चलाता है
Step 2 → Code `yield db` तक चलता है (SETUP)
Step 3 → Yield की गई value endpoint में आ जाती है
Step 4 → Endpoint चलता है और return (या raise) करता है
Step 5 → FastAPI generator को yield के बाद से दोबारा चलाता है (CLEANUP: finally block)
Step 6 → Endpoint ने exception दिया हो तो वह yield वाली line पर generator के अंदर फेंका जाता है
```

---

## 🟡 Real World Example
Swiggy order service: `get_db` opens a SQLAlchemy session per request, yields it, then commits or rolls back and closes it. An AI app opens an HTTP client or a Redis lock per request and releases it after. A rate limiter takes a semaphore slot and releases it afterwards.

## 🟡 Real Example Hindi mein
Swiggy order service में `get_db` हर request पर SQLAlchemy session खोलता है, yield करता है, फिर commit या rollback करके बंद करता है। AI app हर request के लिए HTTP client या Redis lock खोलता है और बाद में छोड़ देता है। Rate limiter semaphore का slot लेता है और बाद में लौटा देता है।

---

## 💻 Code Example — Basic
```python
# Basic yield dependency - run directly (pip install fastapi httpx)
from typing import Annotated, Iterator  # type tools
from fastapi import Depends, FastAPI, HTTPException  # core
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # create app
EVENTS: list[str] = []  # records what happened and when


class FakeSession:  # pretend DB session
    def __init__(self) -> None:  # on creation
        self.closed: bool = False  # not closed yet

    def close(self) -> None:  # cleanup action
        self.closed = True  # mark closed
        EVENTS.append("session closed")  # log it


def get_db() -> Iterator[FakeSession]:  # generator dependency
    db: FakeSession = FakeSession()  # SETUP: open the session
    EVENTS.append("session opened")  # log
    try:  # protect the cleanup
        yield db  # value injected into the endpoint
    finally:  # CLEANUP: always runs, success or error
        db.close()  # close the session


@app.get("/ok")  # normal endpoint
def ok(db: Annotated[FakeSession, Depends(get_db)]) -> dict:  # receives the session
    EVENTS.append("endpoint running")  # log
    return {"closed_inside": db.closed}  # session is open here


@app.get("/boom")  # endpoint that fails
def boom(db: Annotated[FakeSession, Depends(get_db)]) -> dict:  # receives the session
    raise HTTPException(status_code=404, detail="nope")  # error inside the endpoint


c: TestClient = TestClient(app)  # demo client
print(c.get("/ok").json(), EVENTS)  # opened -> endpoint -> closed
# Output: {'closed_inside': False} ['session opened', 'endpoint running', 'session closed']
EVENTS.clear()  # reset
print(c.get("/boom").status_code, EVENTS)  # cleanup still ran on error
# Output: 404 ['session opened', 'session closed']
```

## 💻 Code Example — Advanced
```python
# Production style: commit/rollback, async yield, contextmanager, sub-dependency order, exception visibility
from contextlib import contextmanager  # turn a generator into a context manager
from typing import Annotated, AsyncIterator, Iterator  # type tools
from fastapi import Depends, FastAPI, HTTPException  # core
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
LOG: list[str] = []  # event log


class Session:  # fake transactional session
    def commit(self) -> None:  # save
        LOG.append("commit")  # log

    def rollback(self) -> None:  # undo
        LOG.append("rollback")  # log

    def close(self) -> None:  # release
        LOG.append("close")  # log


def get_session() -> Iterator[Session]:  # transaction-per-request pattern
    s: Session = Session()  # open
    try:  # wrap
        yield s  # hand over
        s.commit()  # endpoint finished without error: save
    except Exception:  # endpoint raised
        s.rollback()  # undo changes
        raise  # IMPORTANT: re-raise so FastAPI still returns the error
    finally:  # always
        s.close()  # release the connection


async def get_http_client() -> AsyncIterator[str]:  # async generator dependency
    LOG.append("client open")  # setup
    try:  # protect
        yield "client"  # value
    finally:  # cleanup
        LOG.append("client closed")  # teardown


@contextmanager  # a context manager can be reused outside FastAPI too
def locked(name: str) -> Iterator[str]:  # lock helper
    LOG.append(f"lock {name}")  # acquire
    try:  # protect
        yield name  # inside the lock
    finally:  # release
        LOG.append(f"unlock {name}")  # release


def get_lock() -> Iterator[str]:  # use the context manager as a dependency
    with locked("orders") as name:  # with-block wraps the yield
        yield name  # endpoint runs while the lock is held


@app.post("/orders")  # endpoint with three yield dependencies
async def create(
    s: Annotated[Session, Depends(get_session)],  # opened first
    h: Annotated[str, Depends(get_http_client)],  # opened second
    lk: Annotated[str, Depends(get_lock)],  # opened third
    fail: bool = False,  # query flag to simulate an error
) -> dict:  # response
    if fail:  # simulate failure
        raise HTTPException(status_code=409, detail="conflict")  # raise
    return {"ok": True}  # success


c: TestClient = TestClient(app)  # demo client
print(c.post("/orders").json())  # success path
# Output: {'ok': True}
print(LOG)  # cleanup runs in REVERSE order of setup
# Output: ['client open', 'lock orders', 'unlock orders', 'client closed', 'commit', 'close']
LOG.clear()  # reset
print(c.post("/orders", params={"fail": True}).status_code)  # failure path
# Output: 409
print(LOG)  # rollback instead of commit; every resource still released
# Output: ['client open', 'lock orders', 'unlock orders', 'client closed', 'rollback', 'close']
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI): setup/teardown in one function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
```javascript
// JavaScript (Express): you hook into response events or use try/finally in each handler
app.use(async (req, res, next) => {
  req.db = await pool.connect();             // setup
  res.on("finish", () => req.db.release());   // cleanup after response (also needs "close" for aborted requests)
  next();
});
// Or per handler:
// const db = await pool.connect(); try { ... } finally { db.release(); }
```

Key difference: Express splits setup and cleanup across event listeners and relies on you remembering aborted requests. FastAPI keeps both in one generator and always runs the cleanup, like `using` in C# or a `with` block.

---

## 🟠 FastAPI Connection
The standard SQLAlchemy pattern in FastAPI is exactly this: `SessionLocal()` -> `yield db` -> `db.close()`. Yield dependencies also work in routers and with `dependencies=[Depends(...)]` (the yielded value is discarded but cleanup still runs).

```python
# FastAPI: yield dependency used only for its side effect (no value in the endpoint)
from typing import Iterator  # type
from fastapi import Depends, FastAPI  # core
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
IN_FLIGHT: list[int] = [0]  # gauge of concurrent requests


def track() -> Iterator[None]:  # side-effect dependency
    IN_FLIGHT[0] += 1  # request started
    try:  # protect
        yield  # nothing to inject
    finally:  # cleanup
        IN_FLIGHT[0] -= 1  # request finished


@app.get("/work", dependencies=[Depends(track)])  # attach without a parameter
def work() -> dict:  # endpoint
    return {"in_flight_now": IN_FLIGHT[0]}  # counter is 1 while running


c: TestClient = TestClient(app)  # client
print(c.get("/work").json(), IN_FLIGHT[0])  # 1 during, 0 after
# Output: {'in_flight_now': 1} 0
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `return` instead of `yield` and cleaning up never
```python
# Wrong - the connection is never closed
def get_db():
    db = SessionLocal()
    return db

# Correct
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

❌ Mistake 2: Catching the exception and not re-raising
```python
# Wrong - swallows the error; the client may get a broken/200 response
try:
    yield s
except Exception:
    s.rollback()

# Correct - re-raise after cleanup
try:
    yield s
except Exception:
    s.rollback()
    raise
```

❌ Mistake 3: Yielding more than once
```python
# Wrong - FastAPI expects exactly one yield, a second yield raises RuntimeError
# Correct - one yield per dependency
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
log = []

def a():
    log.append("a start")
    yield 1
    log.append("a end")

def b(x: int = Depends(a)):
    log.append("b start")
    yield x + 1
    log.append("b end")

@app.get("/")
def route(y: int = Depends(b)):
    log.append("route")
    return y

c = TestClient(app)
print(c.get("/").json())
print(log)
```

**Answer**:
```
2
['a start', 'b start', 'route', 'b end', 'a end']
```
Setup runs from the root outward (a, then b), then the endpoint, then cleanup runs in reverse (b, then a), like nested `with` blocks, because `b` depends on `a` and must finish with `a` still alive.

---

## ⚫ Interview Questions + Answers

Q1: When does the code after `yield` run?
A1: After the endpoint function has finished (success or error). In current FastAPI versions (0.118+) the exit code runs after the response has been sent to the client, so slow cleanup does not delay the response. In 0.106 to 0.117 it ran before the response was sent. Check the docs for your version.

Q2: Can I raise `HTTPException` in the cleanup part?
A2: Do not rely on it. After the response is sent the status is already decided. Raise HTTP errors in the setup part or the endpoint, and keep cleanup quiet (log errors instead).

Q3: What happens if the endpoint raises?
A3: The exception is thrown into the generator at the `yield` line, so `try/except/finally` around it sees it. Re-raise after rollback so the error still reaches the client.

Q4: Sync or async generator?
A4: Both are supported. Sync generators run in a thread pool; async ones run on the event loop, so use async for async drivers (asyncpg, httpx.AsyncClient).

Q5: Is `yield` dependency the same as `contextmanager`?
A5: FastAPI wraps your generator in a context manager internally. You can also write a `@contextmanager` and use it inside the generator with a `with` block, as in the Advanced example.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- DB sessions, transactions, HTTP clients, locks, temporary files
- Anything with open and close that must be paired per request
- Tracking metrics (start/end of work)

❌ Avoid when:
- The resource is global and long-lived (create it once in `lifespan`)
- Cleanup is slow and must finish before responding (do it explicitly in the endpoint)
- Work must outlive the request (use background tasks or a queue)

---

## 📊 Visual Diagram

```
 request ─►  get_session():  open  ── yield ───────────────┐
             get_client():   open  ── yield ───────────┐   │
             get_lock():     lock  ── yield ────────┐  │   │
                                                    ▼  ▼   ▼
                                              endpoint runs
                                                    │
 cleanup (reverse):   unlock ◄─ close client ◄─ commit/rollback + close
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| yield dependency | Generator with setup + cleanup | setup और cleanup वाला generator |
| Setup | Code before yield | yield से पहले का code |
| Teardown / cleanup | Code after yield | yield के बाद का code |
| Context manager | Object with enter/exit | enter/exit वाला object |
| Rollback | Undo DB changes | DB बदलाव वापस लेना |
| Connection leak | Opened but never closed | खुला रह गया connection |
| Lifespan | App-wide startup/shutdown | पूरे app का start/stop |

---

## ⚡ 3-Line Summary
English: A `yield` dependency does setup, hands the value to the endpoint, then runs cleanup in a `finally` block. Cleanup runs in reverse order and sees errors raised by the endpoint. Re-raise after rollback and use `lifespan` for app-wide resources.
Hindi: `yield` dependency setup करती है, value endpoint को देती है और फिर `finally` में cleanup चलाती है। Cleanup उल्टे क्रम में चलता है और endpoint के error देख सकता है। Rollback के बाद error दोबारा raise करें और app-wide resources के लिए `lifespan` इस्तेमाल करें।

---

## ➡️ Next Topic
**315. OAuth2 in FastAPI** — the password flow, `OAuth2PasswordBearer` and the Authorize button.
