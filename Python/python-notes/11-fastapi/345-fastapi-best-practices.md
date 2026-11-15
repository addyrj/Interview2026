---

# 345. FastAPI Best Practices
# हिंदी में: FastAPI Best Practices (अच्छी आदतें)

---

## 🔵 Simple Definition (English)
FastAPI best practices are proven habits that keep an API fast, safe and easy to change: separate input and output schemas, use dependency injection, never block the event loop, load config from environment variables, and return clear errors. These are not rules of the framework; they are lessons from real production systems.

## 🔵 सरल परिभाषा (Hindi)
FastAPI best practices वे आज़माई हुई आदतें हैं जिनसे API तेज़, सुरक्षित और बदलने में आसान रहती है: input और output के अलग schemas, dependency injection, event loop को block न करना, config को environment variables से लेना और साफ़ errors लौटाना। ये framework के नियम नहीं हैं; असली production systems के सबक हैं।

---

## 🔴 Problem it Solves
Beginner FastAPI code often works on day 1 and hurts on day 100: one giant `main.py`, passwords leaking in responses, `time.sleep` freezing every user, secrets hard-coded, database sessions never closed. Best practices prevent these problems before they reach production.

## 🔴 यह क्यों बना? (Hindi)
शुरुआती FastAPI code पहले दिन चलता है पर सौवें दिन तकलीफ देता है: एक विशाल `main.py`, response में password लीक होना, `time.sleep` से सब users का रुक जाना, hard-coded secrets, database sessions का बंद न होना। Best practices ये समस्याएँ production से पहले ही रोक देती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Use an app factory + lifespan (startup/shutdown) instead of globals
Step 2 → Settings from env vars via pydantic-settings (never hard-code secrets)
Step 3 → Separate schemas: UserCreate (input), UserOut (output, no password)
Step 4 → Use response_model so only safe fields leave the API
Step 5 → Inject DB/auth with Depends + Annotated; override them in tests
Step 6 → async def only with await-able libraries; plain def for blocking code
Step 7 → Central exception handlers and consistent error JSON
Step 8 → Version URLs (/api/v1), tag routers, add /health, write tests
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Globals की जगह app factory + lifespan (startup/shutdown) इस्तेमाल करें
Step 2 → Settings pydantic-settings से env vars में से लें (secrets hard-code न करें)
Step 3 → अलग schemas: UserCreate (input), UserOut (output, password नहीं)
Step 4 → response_model लगाएँ ताकि सिर्फ़ सुरक्षित fields बाहर जाएँ
Step 5 → DB/auth को Depends + Annotated से inject करें; tests में override करें
Step 6 → async def सिर्फ़ await वाली libraries के साथ; blocking code के लिए सादा def
Step 7 → Central exception handlers और एक जैसा error JSON
Step 8 → URLs version करें (/api/v1), routers tag करें, /health जोड़ें, tests लिखें
```

---

## 🟡 Real World Example
A Zomato-style restaurant API: `POST /api/v1/users` accepts `UserCreate` (with password) but returns `UserOut` (without it). Database sessions come from `Depends(get_db)` so they always close. The payment-status endpoint is plain `def` because it uses a blocking SDK, so FastAPI runs it in a thread pool, and `/health` is used by Kubernetes for liveness checks.

## 🟡 Real Example Hindi mein
Zomato जैसी restaurant API: `POST /api/v1/users` में `UserCreate` (password के साथ) आता है पर response में `UserOut` (password के बिना) जाता है। Database sessions `Depends(get_db)` से आते हैं इसलिए हमेशा बंद होते हैं। Payment-status endpoint सादा `def` है क्योंकि वह blocking SDK इस्तेमाल करता है, इसलिए FastAPI उसे thread pool में चलाता है, और `/health` को Kubernetes liveness check के लिए इस्तेमाल करता है।

---

## 💻 Code Example — Basic
```python
# Basic: separate schemas + response_model hides the password
from typing import Dict  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # to run the demo here
from pydantic import BaseModel  # schemas


class UserIn(BaseModel):  # what the client SENDS
    name: str  # display name
    password: str  # secret, must never be returned


class UserOut(BaseModel):  # what the server RETURNS
    name: str  # only safe fields


app: FastAPI = FastAPI()  # create app


@app.post("/u", response_model=UserOut)  # response is filtered through UserOut
def create_user(data: UserIn) -> UserIn:  # we even return the full object
    return data  # FastAPI strips `password` using response_model


client: TestClient = TestClient(app)  # test client
print(client.post("/u", json={"name": "A", "password": "p"}).json())  # call it
# Output: {'name': 'A'}
```

## 💻 Code Example — Advanced
```python
# Production style: factory, lifespan, settings, DI, error handler, health check
# pip install fastapi httpx pydantic-settings
from contextlib import asynccontextmanager  # lifespan helper
from functools import lru_cache  # cache settings
from typing import Annotated, AsyncIterator, Dict, List  # type hints

from fastapi import APIRouter, Depends, FastAPI, Request, status  # core pieces
from fastapi.responses import JSONResponse  # custom error body
from fastapi.testclient import TestClient  # demo runner
from pydantic import BaseModel, Field  # schemas with rules
from pydantic_settings import BaseSettings  # env-based config


class Settings(BaseSettings):  # reads env vars like APP_NAME
    app_name: str = "Shop API"  # default if env var missing
    max_items: int = 3  # business limit


@lru_cache  # build Settings once per process
def get_settings() -> Settings:
    return Settings()  # read env now


class DomainError(Exception):  # our own business error
    def __init__(self, code: str, message: str) -> None:
        self.code = code  # machine-readable code
        self.message = message  # human message


class ItemIn(BaseModel):  # input schema with validation
    name: str = Field(min_length=2, max_length=30)  # 2..30 chars


class ItemOut(ItemIn):  # output schema
    id: int  # server-generated id


class Repo:  # stand-in for a DB repository
    def __init__(self) -> None:
        self.rows: Dict[int, ItemOut] = {}  # in-memory store

    def add(self, data: ItemIn) -> ItemOut:
        item = ItemOut(id=len(self.rows) + 1, **data.model_dump())  # new row
        self.rows[item.id] = item  # save
        return item  # return saved row


@asynccontextmanager  # startup + shutdown in one place
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.repo = Repo()  # open resources at startup
    yield  # app runs
    app.state.repo = None  # close resources at shutdown


def get_repo(request: Request) -> Repo:  # dependency: gets the repo
    return request.app.state.repo  # from app state


RepoDep = Annotated[Repo, Depends(get_repo)]  # reusable alias
SettingsDep = Annotated[Settings, Depends(get_settings)]  # reusable alias

router: APIRouter = APIRouter(prefix="/items", tags=["items"])  # versionable group


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def add_item(data: ItemIn, repo: RepoDep, cfg: SettingsDep) -> ItemOut:
    if len(repo.rows) >= cfg.max_items:  # business rule
        raise DomainError("LIMIT", "Too many items")  # handled centrally below
    return repo.add(data)  # plain def: safe for blocking DB drivers


@router.get("", response_model=List[ItemOut])
def list_items(repo: RepoDep) -> List[ItemOut]:
    return list(repo.rows.values())  # all rows


def create_app() -> FastAPI:  # app factory = easy to test
    app = FastAPI(title=get_settings().app_name, lifespan=lifespan)  # build app
    app.include_router(router, prefix="/api/v1")  # version the API

    @app.exception_handler(DomainError)  # one place for domain errors
    async def domain_handler(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"code": exc.code, "message": exc.message})

    @app.get("/health")  # liveness probe
    def health() -> Dict[str, str]:
        return {"status": "ok"}  # tiny and fast

    return app  # hand back the app


app: FastAPI = create_app()  # module-level app for uvicorn

if __name__ == "__main__":  # demo run
    with TestClient(app) as c:  # `with` runs lifespan
        for n in ("pen", "ink", "pad", "bag"):  # 4th exceeds the limit
            r = c.post("/api/v1/items", json={"name": n})  # create
            print(r.status_code, r.json())  # show result
        print(c.post("/api/v1/items", json={"name": "x"}).status_code)  # too short name
        print(c.get("/health").json())  # health
# Output:
# 201 {'name': 'pen', 'id': 1}
# 201 {'name': 'ink', 'id': 2}
# 201 {'name': 'pad', 'id': 3}
# 409 {'code': 'LIMIT', 'message': 'Too many items'}
# 422
# {'status': 'ok'}
```
This app was run; the 4th request returns the 409 domain error and the 1-character name returns 422. In a separate timing test with 5 simultaneous requests (each doing a 0.2 s wait) the results were: `async def` + `time.sleep` = about 1.0 s (blocked), plain `def` + `time.sleep` = about 0.2 s (thread pool), `async def` + `await asyncio.sleep` = about 0.2 s. Exact times vary per machine.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: validated input, filtered output, DI
@app.post("/users", response_model=UserOut)  # output filter
def create(data: UserIn, db: DbDep) -> User:  # validated body + injected DB
    return repo.create(db, data)  # return ORM object
```
```javascript
// JavaScript (Express): validation, filtering and DI are manual
app.post("/users", validate(userSchema), async (req, res) => {  // zod/joi middleware
  const user = await repo.create(req.db, req.body);   // db comes from middleware
  const { password, ...safe } = user;                  // manually strip secrets
  res.status(201).json(safe);                          // send safe fields
});
```

Key differences: FastAPI generates validation, docs and output filtering from type hints; Express needs libraries (zod, joi) and manual stripping of secrets. Express handlers are always async; FastAPI lets you pick `def` (thread pool) or `async def` (event loop).

---

## 🟠 FastAPI Connection
This whole topic is FastAPI. The three habits with the biggest payoff: (1) `response_model` on every route, (2) `Depends` for DB/auth, (3) never call blocking code inside `async def`.

```python
# Blocking code: choose def, or move it to a thread from async def
import time  # blocking sleep (stand-in for a blocking SDK)
from fastapi import FastAPI  # app
from starlette.concurrency import run_in_threadpool  # run blocking code in a thread

app: FastAPI = FastAPI()  # app


@app.get("/a")  # BAD: blocks the event loop for everybody
async def bad() -> int:
    time.sleep(1)  # blocks all other requests
    return 1


@app.get("/b")  # GOOD: plain def runs in the thread pool
def good() -> int:
    time.sleep(1)  # only this thread waits
    return 1


@app.get("/c")  # GOOD: async route that offloads blocking work
async def good_async() -> int:
    await run_in_threadpool(time.sleep, 1)  # thread, loop stays free
    return 1
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning the DB model with the password
```python
# Wrong: no response_model, password_hash is sent to the client
@app.get("/users/{id}")
def get_user(id: int): return db_user

# Right: response_model=UserOut hides internal fields
@app.get("/users/{id}", response_model=UserOut)
def get_user(id: int): return db_user
```

❌ Mistake 2: Blocking inside `async def`
```python
# Wrong: requests.get / time.sleep / sync DB call in async def freezes the server
async def handler(): return requests.get(url).json()

# Right: use httpx.AsyncClient with await, or declare the route as plain def
async def handler(): return (await client.get(url)).json()
```

❌ Mistake 3: Hard-coded secrets and global DB sessions
```python
# Wrong:
SECRET = "abc123"; db = SessionLocal()   # one shared session for all requests

# Right: Settings from env + a per-request session dependency that closes it
```

❌ Mistake 4: One giant file and unversioned URLs
```python
# Right: routers per feature (users.py, orders.py), include_router(prefix="/api/v1")
```

---

## 🧠 Tricky Interview Question

**Q**: Five clients call each route at once. Each route waits 0.2 s. About how long does the batch take?

```python
@app.get("/blocking")
async def bad():
    time.sleep(0.2)
    return 1

@app.get("/sync")
def good():
    time.sleep(0.2)
    return 1

@app.get("/nb")
async def nb():
    await asyncio.sleep(0.2)
    return 1
```

**Answer**:
```
/blocking 1.0   (5 x 0.2 s, one after another, loop is blocked)
/sync     0.2   (thread pool, runs in parallel)
/nb       0.2   (event loop switches between tasks)
```
`async def` does not mean fast. If you block inside it, you block every request on that worker. (Measured by running; numbers are approximate.)

---

## ⚫ Interview Questions + Answers

Q1: Why separate `UserIn` and `UserOut` schemas?
A1: Input has fields the client may set (password), output has fields you want to expose (id, name). Using one model leaks secrets or lets clients set read-only fields like `id`.

Q2: `def` or `async def` for a route?
A2: `async def` when everything inside is awaitable (httpx, asyncpg, async SQLAlchemy). Plain `def` when you use blocking libraries; FastAPI runs it in a thread pool.

Q3: Why use `lifespan` instead of `@app.on_event("startup")`?
A3: `on_event` is deprecated. `lifespan` keeps startup and shutdown together, so resources opened are guaranteed to be closed.

Q4: How do you manage config safely?
A4: `pydantic-settings` reads env vars and `.env`, validates types, and `lru_cache` builds it once. Secrets come from the platform (Docker/Kubernetes secrets), never from git.

Q5: How do you keep a big project maintainable?
A5: Feature routers, a service layer for business logic, repositories for DB access, dependencies for shared things, tests with `dependency_overrides` (see 346).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- The API will live longer than a demo and have several developers
- You handle user data, payments or anything sensitive
- You want predictable, testable code

❌ Avoid when:
- A throwaway 20-line script: layers and factories are overkill
- You copy "best practices" blindly: a 3-endpoint service does not need a repository layer

---

## 📊 Visual Diagram

```
 Request
    |
 Middleware (CORS, logging, request id)
    |
 Router /api/v1/items  --validate--> ItemIn (422 on bad input)
    |
 Depends: settings, repo, current_user
    |
 Service/business logic  --raises--> DomainError ---> exception handler ---> 409 JSON
    |
 Repository (DB)
    |
 response_model=ItemOut  (filters fields)  ---> 201 JSON
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| response_model | Output filter/schema | output को छानने वाला schema |
| Lifespan | Startup/shutdown handler | शुरू/बंद होने का handler |
| Dependency Injection | Framework supplies helpers | ज़रूरी चीज़ें framework देता है |
| App factory | Function that builds the app | app बनाने वाला function |
| Thread pool | Threads for blocking code | blocking code के लिए threads |
| Domain error | Business rule failure | business नियम की विफलता |

---

## ⚡ 3-Line Summary
English: Separate input/output schemas, inject dependencies, load settings from env, and never block the event loop. Use lifespan, routers, versioned URLs, central error handlers and tests.
Hindi: Input/output schemas अलग रखें, dependencies inject करें, settings env से लें और event loop को कभी block न करें। Lifespan, routers, versioned URLs, central error handlers और tests इस्तेमाल करें।

---

## ➡️ Next Topic
**346. FastAPI Project Structure** — how to lay out folders for a growing FastAPI codebase.
