---

# Q240. Lifespan Events (Startup/Shutdown)
# Category: FastAPI + Web Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Run code once at app startup (e.g. open a DB pool / load a model) and once at shutdown (close it) using FastAPI's modern `lifespan` — not the deprecated `@app.on_event`. Show the order with `TestClient`.

---

## 💡 Quick Concept (2 lines only)
`lifespan` is an async context manager: code before `yield` runs at startup, code after `yield` runs at shutdown. Share resources via `app.state`.
हिंदी: `yield` से पहले = startup, `yield` के बाद = shutdown — एक ही जगह setup और cleanup।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from contextlib import asynccontextmanager        # Step 1: helper to build async context manager
from fastapi import FastAPI, Request              # app + request type
from fastapi.testclient import TestClient         # in-process client

events: list[str] = []                            # record the order of events

@asynccontextmanager                              # turns the generator into a lifespan
async def lifespan(app: FastAPI):                 # FastAPI passes the app in
    events.append("startup: open pool")           # Step 2: runs BEFORE first request
    app.state.db = {"connected": True}            # store shared resource on app.state
    yield                                         # Step 3: app serves requests here
    app.state.db["connected"] = False             # Step 4: cleanup after last request
    events.append("shutdown: close pool")         # runs when app stops

app = FastAPI(lifespan=lifespan)                  # Step 5: register the lifespan

@app.get("/status")                               # simple route
def status(request: Request) -> dict:             # request gives access to app.state
    return {"db": request.app.state.db["connected"]}  # read the shared resource

# ============================================
# TEST CASES
# ============================================
with TestClient(app) as client:                   # `with` triggers startup + shutdown
    print(events)                                 # Expected: ['startup: open pool']
    print(client.get("/status").json())           # Expected: {'db': True}
print(events)                                     # Expected: ['startup: open pool', 'shutdown: close pool']
print(app.state.db)                               # Expected: {'connected': False}
```

---

## 🔍 Why This Works (3 lines max)
Starlette enters the context manager when the server starts and exits it on shutdown, so setup/cleanup stay paired (like `with`). Without `with TestClient(app)`, lifespan does NOT run in tests.
हिंदी: Server start पर context में enter, बंद होने पर exit — tests में `with TestClient` ज़रूरी है।

---

## ⚡ Alternative Solution
```python
# Deprecated style (still works, but gives DeprecationWarning in new FastAPI)
import warnings                                   # to silence the deprecation noise
from fastapi import FastAPI                       # app class
from fastapi.testclient import TestClient         # in-process client

log: list[str] = []                               # collect events

with warnings.catch_warnings():                   # hide DeprecationWarning for the demo
    warnings.simplefilter("ignore")               # ignore all warnings inside block
    old = FastAPI()                               # app without lifespan

    @old.on_event("startup")                      # old-style startup hook
    async def up() -> None:                       # handler
        log.append("up")                          # record startup

    @old.on_event("shutdown")                     # old-style shutdown hook
    async def down() -> None:                     # handler
        log.append("down")                        # record shutdown

    with TestClient(old):                         # triggers both hooks
        pass                                      # no requests needed

print(log)                                        # Expected: ['up', 'down']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: creating a DB connection at import time (module level)
# db = connect()          # runs on import, even in tests, never closed cleanly

# ❌ Wrong: forgetting `with` in tests, so startup never ran
# client = TestClient(app); client.get("/status")   # app.state.db missing -> AttributeError

# ✅ Correct: create in lifespan, store on app.state, use `with TestClient(app)`
```

---

## 🎯 Interview Tip (1 line)
Say: "I use `lifespan` (async context manager) for pools, ML models and HTTP clients; `on_event` is deprecated and can't share local variables between startup and shutdown."

---

## 🔗 Related Questions
→ Q239 (API versioning) | Q236 (TestClient) | Q237 (async DB session) | Q119 (context manager class)
