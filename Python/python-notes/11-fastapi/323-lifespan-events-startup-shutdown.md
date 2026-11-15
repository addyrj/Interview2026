---

# 323. Lifespan Events (startup + shutdown)
# हिंदी में: Lifespan Events (startup और shutdown)

---

## 🔵 Simple Definition (English)
A lifespan function runs setup code once before the app serves its first request and cleanup code once after the last one. You write it as an async context manager and pass it as `FastAPI(lifespan=...)`.

## 🔵 सरल परिभाषा (Hindi)
Lifespan function app की पहली request से पहले setup code एक बार और आखिरी request के बाद cleanup code एक बार चलाता है। इसे async context manager की तरह लिखकर `FastAPI(lifespan=...)` में देते हैं।

---

## 🔴 Problem it Solves
Expensive resources (DB pool, Redis client, ML model, HTTP client) should be created once, not per request, and closed cleanly on shutdown. Older `@app.on_event('startup')` handlers split setup and teardown across two functions and are deprecated. Lifespan keeps both in one place, so shared variables and `try/finally` work naturally.

## 🔴 यह क्यों बना? (Hindi)
महँगे resources (DB pool, Redis client, ML model, HTTP client) एक बार बनाने चाहिए, हर request पर नहीं, और shutdown पर ठीक से बंद करने चाहिए। पुराने `@app.on_event('startup')` handlers setup और teardown को दो functions में बाँटते हैं और अब deprecated हैं। Lifespan दोनों एक जगह रखता है, इसलिए shared variables और `try/finally` आसानी से चलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Uvicorn starts and sends 'lifespan.startup' to the app
Step 2 → FastAPI enters your context manager and runs code before `yield`
Step 3 → If startup raises, the app fails to start (good: fail fast)
Step 4 → After `yield` begins, requests are served
Step 5 → On SIGTERM/Ctrl+C, Uvicorn sends 'lifespan.shutdown'
Step 6 → Code after `yield` (or in `finally`) closes pools and flushes data
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Uvicorn शुरू होकर app को 'lifespan.startup' भेजता है
Step 2 → FastAPI आपके context manager में जाकर `yield` से पहले का code चलाता है
Step 3 → Startup में error आए तो app शुरू नहीं होता (fail fast, अच्छा है)
Step 4 → `yield` के बाद requests serve होती हैं
Step 5 → SIGTERM/Ctrl+C पर Uvicorn 'lifespan.shutdown' भेजता है
Step 6 → `yield` के बाद (या `finally` में) का code pools बंद करता है और data flush करता है
```

---

## 🟡 Real World Example
A Razorpay-style service opens an asyncpg pool and a Redis client at startup and closes them on shutdown. An AI app loads a 500 MB embedding model once at startup (not per request). A Kubernetes rolling deploy sends SIGTERM and shutdown code drains connections gracefully.

## 🟡 Real Example Hindi mein
Razorpay जैसी service startup पर asyncpg pool और Redis client खोलती है और shutdown पर बंद करती है। AI app 500 MB का embedding model startup पर एक बार load करता है (हर request पर नहीं)। Kubernetes rolling deploy SIGTERM भेजता है और shutdown code connections को gracefully बंद करता है।

---

## 💻 Code Example — Basic
Record startup and shutdown. Note that `TestClient` must be used with `with` to trigger lifespan.

```python
# Basic lifespan - every line commented
from contextlib import asynccontextmanager  # build an async context manager
from collections.abc import AsyncIterator  # type hint
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # test client

STATE: list[str] = []  # record what happens


@asynccontextmanager  # turn the generator into a context manager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # FastAPI passes the app
    STATE.append("startup")  # runs once BEFORE the first request
    yield  # the app serves requests here
    STATE.append("shutdown")  # runs once AFTER the last request


app: FastAPI = FastAPI(lifespan=lifespan)  # pass lifespan to the app


@app.get("/")  # route
def root() -> dict[str, list[str]]:  # handler
    return {"state": STATE}  # show state


with TestClient(app) as client:  # "with" is REQUIRED to run lifespan in tests
    print(client.get("/").json())  # startup already ran
    # Output: {'state': ['startup']}
print(STATE)  # after leaving "with", shutdown ran
# Output: ['startup', 'shutdown']
```

## 💻 Code Example — Advanced
Shared resource yielded as state, cleanup in `finally`, read via `request.state`.

```python
# Production style: shared resources on app.state, cleanup in finally
from contextlib import asynccontextmanager  # context manager helper
from collections.abc import AsyncIterator  # type hint
from fastapi import FastAPI, Request  # app and request
from fastapi.testclient import TestClient  # test client


class FakeDB:  # stand-in for an async DB pool
    def __init__(self) -> None:  # constructor
        self.open: bool = False  # connection state

    async def connect(self) -> None:  # open pool
        self.open = True  # now usable

    async def close(self) -> None:  # close pool
        self.open = False  # released


@asynccontextmanager  # lifespan factory
async def lifespan(app: FastAPI) -> AsyncIterator[dict[str, FakeDB]]:  # may yield a state dict
    db: FakeDB = FakeDB()  # create resource
    await db.connect()  # startup work: connect
    try:  # make sure cleanup always runs
        yield {"db": db}  # yielded dict becomes request.state (Starlette lifespan state)
    finally:  # shutdown work
        await db.close()  # close pool even if app crashed
        print("db closed:", not db.open)  # prove it


app: FastAPI = FastAPI(lifespan=lifespan)  # attach


@app.get("/health")  # health route
async def health(request: Request) -> dict[str, bool]:  # read shared resource
    db: FakeDB = request.state.db  # from the lifespan state
    return {"db_open": db.open}  # report


with TestClient(app) as client:  # run lifespan
    print(client.get("/health").json())  # DB is open while serving
    # Output: {'db_open': True}
# Output: db closed: True
```

---

## 🟠 JavaScript vs Python Comparison

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool()   # startup
    yield
    await app.state.pool.close()           # shutdown

app = FastAPI(lifespan=lifespan)
```

```javascript
// Express: manual wiring
const pool = await createPool();                 // startup
const server = app.listen(3000);
process.on('SIGTERM', async () => {              // shutdown
  server.close();
  await pool.end();
});
```

Express has no framework hook: you create resources before `listen` and handle `SIGTERM` yourself. FastAPI gives one structured place with guaranteed ordering. A Python `yield` inside a context manager is the divider between startup and shutdown.

---

## 🟠 FastAPI Connection
Use lifespan for anything shared across requests. Store objects on `app.state` or yield a dict (becomes `request.state`). Do not combine `lifespan=` with `on_event` handlers: when lifespan is set, the old event handlers are ignored. Sub-applications and routers do not run their own lifespan the way the main app does, so keep it on the main app.

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import httpx
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http = httpx.AsyncClient(timeout=5.0)  # one client for all requests
    try:
        yield
    finally:
        await app.state.http.aclose()  # close sockets on shutdown


app: FastAPI = FastAPI(lifespan=lifespan)


@app.get("/proxy")
async def proxy(request: Request) -> dict[str, int]:
    client: httpx.AsyncClient = request.app.state.http  # reuse it
    r = await client.get("https://example.com")
    return {"status": r.status_code}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using deprecated `on_event`
```python
@app.on_event('startup')
async def start(): ...  # deprecated
```
✅ Correct:
```python
@asynccontextmanager
async def lifespan(app): yield
app = FastAPI(lifespan=lifespan)
```

❌ Mistake 2: Skipping `finally` for cleanup
```python
async def lifespan(app):
    pool = await make()
    yield
    await pool.close()  # skipped if the app crashed
```
✅ Correct:
```python
async def lifespan(app):
    pool = await make()
    try:
        yield
    finally:
        await pool.close()
```

❌ Mistake 3: Creating a connection per request
```python
@app.get('/')
async def r():
    client = httpx.AsyncClient()  # new pool every time
```
✅ Correct:
```python
# create once in lifespan, reuse via app.state
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient

state = {}

@asynccontextmanager
async def lifespan(app):
    state["db"] = "connected"
    yield
    state.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return state

c = TestClient(app)
print(c.get("/").json())
with TestClient(app) as c2:
    print(c2.get("/").json())
print(state)
```

**Answer**:
```
{}
{'db': 'connected'}
{}
```
`TestClient(app)` without `with` never runs lifespan, so the first call sees an empty dict. Inside `with TestClient(app)`, startup ran (`db` set). On leaving the block, shutdown ran and `state.clear()` emptied it. With a real server (uvicorn) lifespan always runs.

---

## ⚫ Interview Questions + Answers

Q1: What replaced `on_event('startup')`?
A1: The `lifespan` async context manager. Code before `yield` is startup, code after is shutdown.

Q2: When does lifespan run under multiple workers?
A2: Once per worker process. If you run 4 Uvicorn workers you get 4 startups, so each opens its own pool.

Q3: Why does my test not trigger startup?
A3: `TestClient` only runs lifespan inside a `with` block (or use `async with LifespanManager` for httpx).

Q4: Where do I keep the shared objects?
A4: On `app.state` or by yielding a dict, which becomes `request.state` for each request.

Q5: What if startup raises?
A5: The server exits with the error, so a broken DB config is caught at deploy time instead of on the first user request.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- DB pools, Redis, HTTP clients
- Loading ML models once
- Graceful shutdown (flush queues, close sockets)

❌ Avoid when:
- Per-request setup (use dependencies)
- Very slow startup without health/readiness probes
- Mixing with deprecated on_event

---

## 📊 Visual Diagram

```
uvicorn start
   |-> lifespan.startup  -> [code BEFORE yield]  open pool / load model
   |-> serve requests ........ (app.state / request.state available)
   |-> SIGTERM
   |-> lifespan.shutdown -> [code AFTER yield]   close pool / flush
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| lifespan | Startup/shutdown hook | शुरू/बंद होने का hook |
| asynccontextmanager | Turns generator into async with | generator को async with बनाता है |
| app.state | Shared app storage | app का साझा भंडार |
| Graceful shutdown | Finish work, close cleanly | काम पूरा करके ठीक से बंद करना |
| Connection pool | Reusable DB connections | दोबारा इस्तेमाल होने वाले connections |
| Fail fast | Crash early on bad setup | गलत setup पर तुरंत रुकना |

---

## ⚡ 3-Line Summary
English: `lifespan` is one async context manager: code before `yield` runs at startup, after it at shutdown. Create shared resources there and clean up in `finally`. It replaces deprecated `on_event`.
Hindi: `lifespan` एक async context manager है: `yield` से पहले का code startup पर, बाद का shutdown पर चलता है। Shared resources वहीं बनाएँ और `finally` में बंद करें। यह deprecated `on_event` की जगह है।

---

## ➡️ Next Topic
**324. Exception Handlers** — turn errors into clean, consistent JSON responses.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output. The `fa_code` httpx proxy snippet needs internet and was not run.
