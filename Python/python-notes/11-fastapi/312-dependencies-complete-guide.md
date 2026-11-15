---

# 312. Dependencies — Complete Guide
# हिंदी में: Dependencies — पूरी गाइड (Depends के सभी रूप)

---

## 🔵 Simple Definition (English)
A dependency is a function (or class) that FastAPI runs before your endpoint and whose result it injects as a parameter via `Depends(...)`. It is how you share logic like pagination, authentication and DB sessions across many routes. This note covers every place and form dependencies can take.

## 🔵 सरल परिभाषा (Hindi)
Dependency एक function (या class) है जिसे FastAPI आपके endpoint से पहले चलाता है और उसका नतीजा `Depends(...)` के ज़रिए parameter में डाल देता है। Pagination, authentication और DB session जैसी साझा logic कई routes में इसी से बँटती है। इस note में dependency के सभी रूप और जगहें हैं।

---

## 🔴 Problem it Solves
Without dependencies you copy the same code (read token, check user, parse `skip/limit`) into every route. A bug fix means editing 50 places, and tests cannot swap the real DB or auth for a fake. Dependencies give one reusable, testable, documented unit that FastAPI wires for you.

## 🔴 यह क्यों बना? (Hindi)
Dependencies के बिना वही code (token पढ़ना, user जाँचना, `skip/limit` parse करना) हर route में copy करना पड़ता है। एक bug सुधारने के लिए 50 जगह बदलना पड़ता है और tests में असली DB या auth की जगह नकली नहीं लगा सकते। Dependencies एक reusable, testable और documented इकाई देती हैं जिसे FastAPI खुद जोड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write a normal function: def pagination(skip: int = 0, limit: int = 10)
Step 2 → Endpoint declares: params = Depends(pagination)
Step 3 → On each request FastAPI reads the dependency's own parameters (query, header...)
Step 4 → It calls the dependency and passes the result into the endpoint
Step 5 → Same dependency used twice in one request is called ONCE (cached per request)
Step 6 → Tests can replace it with app.dependency_overrides[pagination] = fake
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप सामान्य function लिखते हैं: def pagination(skip: int = 0, limit: int = 10)
Step 2 → Endpoint में लिखते हैं: params = Depends(pagination)
Step 3 → हर request पर FastAPI dependency के अपने parameters (query, header...) पढ़ता है
Step 4 → वह dependency चलाता है और नतीजा endpoint को देता है
Step 5 → एक request में वही dependency दो बार आए तो वह सिर्फ़ एक बार चलती है (cache)
Step 6 → Tests में app.dependency_overrides[pagination] = fake से बदल सकते हैं
```

---

## 🟡 Real World Example
A Zomato-like service: every route needs the logged-in user, a DB session and pagination. `get_current_user`, `get_db` and `Pagination` are dependencies. Admin routes add `require_admin`. In tests, `get_db` is overridden to use SQLite, and `get_current_user` returns a fake user, with no real login needed.

## 🟡 Real Example Hindi mein
Zomato जैसी service में हर route को logged-in user, DB session और pagination चाहिए। `get_current_user`, `get_db` और `Pagination` dependencies हैं। Admin routes में `require_admin` जुड़ता है। Tests में `get_db` को SQLite से बदल देते हैं और `get_current_user` नकली user लौटाता है, असली login की ज़रूरत नहीं।

---

## 💻 Code Example — Basic
```python
# Basic dependencies - run directly (pip install fastapi httpx)
from typing import Annotated, Optional  # type tools
from fastapi import Depends, FastAPI, Header, HTTPException  # core
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # create app


def pagination(skip: int = 0, limit: int = 10) -> dict:  # function dependency, params come from query
    return {"skip": skip, "limit": min(limit, 50)}  # cap limit so nobody asks for a million rows


class Filters:  # class dependency: FastAPI calls Filters(...) to build an object
    def __init__(self, q: Optional[str] = None, active: bool = True) -> None:  # query params
        self.q = q  # search text
        self.active = active  # only active items?


Page = Annotated[dict, Depends(pagination)]  # reusable alias, keeps signatures short


@app.get("/items")  # uses a function and a class dependency
def items(page: Page, f: Annotated[Filters, Depends()]) -> dict:  # Depends() with no arg = use the type itself
    return {"page": page, "q": f.q, "active": f.active}  # echo


def api_key_guard(x_api_key: Annotated[Optional[str], Header()] = None) -> None:  # runs only for its side effect
    if x_api_key != "secret":  # wrong or missing key
        raise HTTPException(status_code=401, detail="Bad API key")  # stop the request here


@app.get("/private", dependencies=[Depends(api_key_guard)])  # decorator-level: no value needed in the function
def private() -> dict:  # function does not receive anything
    return {"data": "top secret"}  # reached only if guard passed


c: TestClient = TestClient(app)  # demo client
print(c.get("/items?skip=5&limit=999&q=pizza").json())  # limit is capped at 50
# Output: {'page': {'skip': 5, 'limit': 50}, 'q': 'pizza', 'active': True}
print(c.get("/private").status_code)  # no key
# Output: 401
print(c.get("/private", headers={"X-API-Key": "secret"}).json())  # with key
# Output: {'data': 'top secret'}
```

## 💻 Code Example — Advanced
```python
# Production style: router-level, app-level, caching, async deps, overrides for tests
import asyncio  # to run async dependency in the demo
from typing import Annotated  # metadata
from fastapi import APIRouter, Depends, FastAPI, Request  # core
from fastapi.testclient import TestClient  # demo client

CALLS: list[str] = []  # records which dependencies ran


def audit(request: Request) -> None:  # app-level dependency: runs for EVERY route
    CALLS.append(f"audit {request.url.path}")  # log the call


app: FastAPI = FastAPI(dependencies=[Depends(audit)])  # global dependency


async def get_config() -> dict:  # async dependency (e.g. fetch config from Redis)
    await asyncio.sleep(0)  # pretend I/O
    CALLS.append("get_config")  # record that it ran
    return {"env": "prod"}  # value


def get_user(cfg: Annotated[dict, Depends(get_config)]) -> str:  # depends on get_config (see next topic)
    return f"user-in-{cfg['env']}"  # build from config


def get_greeting(cfg: Annotated[dict, Depends(get_config)]) -> str:  # ALSO depends on get_config
    return f"hello from {cfg['env']}"  # second consumer


router: APIRouter = APIRouter(prefix="/v1", dependencies=[Depends(get_config)])  # router-level dependency


@router.get("/me")  # endpoint
def me(user: Annotated[str, Depends(get_user)], greet: Annotated[str, Depends(get_greeting)]) -> dict:  # two deps share one
    return {"user": user, "greet": greet}  # response


@router.get("/fresh")  # endpoint that disables caching
def fresh(a: Annotated[dict, Depends(get_config)], b: Annotated[dict, Depends(get_config, use_cache=False)]) -> dict:
    return {"same": a is b}  # different objects because use_cache=False


app.include_router(router)  # attach the router
c: TestClient = TestClient(app)  # demo client

CALLS.clear()  # reset log
print(c.get("/v1/me").json())  # normal call
# Output: {'user': 'user-in-prod', 'greet': 'hello from prod'}
print(CALLS)  # get_config ran ONCE even though 3 places need it (cache per request)
# Output: ['audit /v1/me', 'get_config']

CALLS.clear()  # reset log
print(c.get("/v1/fresh").json(), CALLS.count("get_config"))  # use_cache=False runs it again
# Output: {'same': False} 2

app.dependency_overrides[get_config] = lambda: {"env": "test"}  # replace in tests, no code change in routes
print(c.get("/v1/me").json())  # now uses the fake
# Output: {'user': 'user-in-test', 'greet': 'hello from test'}
app.dependency_overrides.clear()  # always clean up
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI): injected by the framework, based on the signature
def get_user(token: str = Header()) -> User: ...

@app.get("/me")
def me(user: User = Depends(get_user)): ...
```
```javascript
// JavaScript (Express): middleware mutates req, you read it later
const getUser = (req, res, next) => { req.user = decode(req.headers.token); next(); };
app.get("/me", getUser, (req, res) => res.json(req.user));
// NestJS has real dependency injection: constructor(private users: UsersService) {}
```

Key difference: Express middleware passes data by mutating `req` (untyped, order-dependent). FastAPI dependencies return typed values, appear in OpenAPI docs, are cached per request and can be overridden in tests. It is closer to NestJS providers/guards than to Express middleware.

---

## 🟠 FastAPI Connection
Dependencies are the backbone of a production FastAPI project: DB sessions, current user, permissions, pagination, rate limits, settings. Levels: per-parameter, `dependencies=[...]` in the decorator, per-router, or the whole app. The overrides feature makes tests fast.

```python
# FastAPI: role-checking dependency factory (a dependency that returns a dependency)
from typing import Annotated  # metadata
from fastapi import Depends, FastAPI, Header, HTTPException  # core
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
USERS: dict[str, str] = {"t1": "admin", "t2": "viewer"}  # token -> role


def role_required(role: str):  # factory: configure the dependency with an argument
    def checker(x_token: Annotated[str, Header()]) -> str:  # the real dependency
        actual: str | None = USERS.get(x_token)  # look up role
        if actual != role:  # not allowed
            raise HTTPException(status_code=403, detail=f"{role} only")  # forbidden
        return actual  # allowed
    return checker  # give FastAPI the inner function


@app.delete("/users/1")  # admin-only route
def delete_user(role: Annotated[str, Depends(role_required("admin"))]) -> dict:  # reuse with "admin"
    return {"deleted_by": role}  # response


c: TestClient = TestClient(app)  # client
print(c.delete("/users/1", headers={"X-Token": "t1"}).json())  # admin
# Output: {'deleted_by': 'admin'}
print(c.delete("/users/1", headers={"X-Token": "t2"}).status_code)  # viewer
# Output: 403
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling the dependency yourself
```python
# Wrong - runs it immediately at import time, FastAPI sees a value not a callable
def me(page = Depends(pagination())): ...

# Correct - pass the function itself
def me(page = Depends(pagination)): ...
```

❌ Mistake 2: Forgetting `Depends` (it becomes a query parameter)
```python
# Wrong - FastAPI treats "page" as a body/query field of type dict
def me(page: dict = pagination): ...

# Correct
def me(page: dict = Depends(pagination)): ...
```

❌ Mistake 3: Creating a global state in a dependency without thinking about caching
```python
# Wrong - assuming it runs on every use; with caching it runs once per request
# Correct - use Depends(fn, use_cache=False) if you need a fresh value each time
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print?

```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
count = {"n": 0}

def counter():
    count["n"] += 1
    return count["n"]

@app.get("/x")
def x(a: int = Depends(counter), b: int = Depends(counter)):
    return [a, b]

c = TestClient(app)
print(c.get("/x").json(), c.get("/x").json())
```

**Answer**:
```
[1, 1] [2, 2]
```
Within one request the same dependency is cached, so `a` and `b` are both 1. A new request starts with a fresh cache, so the function runs again and returns 2 for both.

---

## ⚫ Interview Questions + Answers

Q1: What is a dependency in FastAPI?
A1: Any callable (function, class, async function, generator) used with `Depends()`. FastAPI resolves its parameters, calls it and injects the result.

Q2: Function vs class dependency?
A2: A function is simple. A class groups related query params into an object (`Depends()` with no argument uses the class itself) and can keep helper methods. Both are just callables.

Q3: Where can dependencies be declared?
A3: As a parameter, in the decorator `dependencies=[...]`, on an `APIRouter(dependencies=[...])`, and on `FastAPI(dependencies=[...])`.

Q4: How do dependencies help testing?
A4: `app.dependency_overrides[real] = fake` swaps any dependency (DB, auth, clock) with a fake, with no changes to route code.

Q5: Sync vs async dependencies?
A5: Both work. Sync ones run in a thread pool, async ones run on the event loop. Do not block the loop inside `async def`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Logic is shared by many routes (auth, DB session, pagination, settings)
- You want typed, documented, overridable building blocks
- You need setup/teardown per request (see next topics)

❌ Avoid when:
- A plain helper function call is enough (no request data, no wiring needed)
- Heavy business logic (keep it in a service layer, the dependency only wires it)
- Global mutable state hidden behind a dependency

---

## 📊 Visual Diagram

```
 Request ─► FastAPI resolves graph
              │
   app deps ─►│ audit
 router deps ►│ get_config ─────────┐ (cached, runs once)
 param deps ─►│ get_user ◄──────────┤
              │ get_greeting ◄──────┘
              ▼
         endpoint(user, greet)
              │
 tests: app.dependency_overrides[get_config] = fake
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dependency | Callable run before the endpoint | endpoint से पहले चलने वाला callable |
| Depends | Marker that requests injection | injection माँगने वाला निशान |
| Injection | Framework passes the value in | framework द्वारा value देना |
| use_cache | Reuse result within a request | एक request में नतीजा दोबारा इस्तेमाल |
| dependency_overrides | Replace a dependency (tests) | tests में dependency बदलना |
| Dependency factory | Function returning a dependency | dependency लौटाने वाला function |

---

## ⚡ 3-Line Summary
English: `Depends` injects reusable logic into routes. Declare it per parameter, per decorator, per router or app-wide. Results are cached per request and can be overridden for tests.
Hindi: `Depends` reusable logic को routes में डालता है। इसे parameter, decorator, router या पूरे app पर लगाया जा सकता है। नतीजा हर request में cache होता है और tests के लिए बदला जा सकता है।

---

## ➡️ Next Topic
**313. Sub-dependencies** — dependencies that depend on other dependencies (chains and graphs).
