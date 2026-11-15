---

# 343. FastAPI Testing (TestClient)
# हिंदी में: FastAPI Testing (TestClient से API टेस्ट करना)

---

## 🔵 Simple Definition (English)
`TestClient` lets you call your FastAPI app like a real client (`client.get(...)`, `client.post(...)`) without starting a server or opening a port. It runs your app in-process and returns a normal response object. You write plain `def test_...` functions and run them with `pytest`.

## 🔵 सरल परिभाषा (Hindi)
`TestClient` से आप अपने FastAPI app को असली client की तरह call करते हैं (`client.get(...)`, `client.post(...)`), बिना server चालू किए और बिना port खोले। App उसी process में चलता है और आपको सामान्य response object मिलता है। आप साधारण `def test_...` functions लिखते हैं और `pytest` से चलाते हैं।

---

## 🔴 Problem it Solves
Testing an API by hand (Postman, curl) is slow and cannot run in CI. Starting a real server on a port for each test is flaky (port clashes, timing). `TestClient` removes the server: the request goes straight into the ASGI app, so tests are fast, deterministic and easy to automate.

## 🔴 यह क्यों बना? (Hindi)
API को हाथ से test करना (Postman, curl) धीमा है और CI में नहीं चल सकता। हर test के लिए असली server और port चालू करना भरोसेमंद नहीं होता (port टकराना, timing)। `TestClient` server हटा देता है: request सीधे ASGI app में जाती है, इसलिए tests तेज़, predictable और automate करने में आसान होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → client = TestClient(app) wraps your FastAPI app
Step 2 → client.post("/items", json={...}) builds an HTTP request in memory
Step 3 → The request goes through middleware, routing, validation, your function
Step 4 → The response comes back as a normal Response (status_code, json(), headers)
Step 5 → assert on status code and body; validation errors give 422
Step 6 → `with TestClient(app)` also runs startup/shutdown (lifespan) events
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → client = TestClient(app) आपके app को लपेट लेता है
Step 2 → client.post(...) memory में ही HTTP request बनाता है
Step 3 → Request middleware, routing, validation और आपके function से गुज़रती है
Step 4 → Response वापस आता है (status_code, json(), headers)
Step 5 → status code और body पर assert करें; validation error पर 422 आता है
Step 6 → `with TestClient(app)` लिखने पर startup/shutdown (lifespan) भी चलते हैं
```

---

## 🟡 Real World Example
A Razorpay-style payments service has `POST /payments`. The team tests: valid payment returns 201, missing `amount` returns 422, unknown payment id returns 404, and a non-logged-in user gets 401. These run on every pull request in GitHub Actions in under a second, with the real database replaced by a fake via `dependency_overrides`.

## 🟡 Real Example Hindi mein
Razorpay जैसी payments service में `POST /payments` है। Team test करती है: सही payment पर 201, `amount` गायब हो तो 422, अनजान payment id पर 404, और login के बिना 401। ये tests हर pull request पर GitHub Actions में एक सेकंड से कम में चलते हैं, और असली database की जगह `dependency_overrides` से fake लगाया जाता है।

---

## 💻 Code Example — Basic
```python
# Basic TestClient example (pip install fastapi httpx pytest)
from typing import Dict  # type hints for return values
from fastapi import FastAPI, HTTPException  # app class and error class
from fastapi.testclient import TestClient  # the in-process client
from pydantic import BaseModel  # request body validation


class Item(BaseModel):  # body schema
    name: str  # required text
    price: float  # required number


app: FastAPI = FastAPI()  # create the app
DB: Dict[int, Item] = {}  # fake in-memory "database"


@app.post("/items", status_code=201)  # create route returns 201
def create(item: Item) -> Dict[str, int]:  # FastAPI validates body into Item
    new_id: int = len(DB) + 1  # next id
    DB[new_id] = item  # store item
    return {"id": new_id}  # JSON response


@app.get("/items/{item_id}")  # read route
def get(item_id: int) -> Item:  # item_id is converted to int
    if item_id not in DB:  # missing id
        raise HTTPException(status_code=404, detail="Item not found")  # 404
    return DB[item_id]  # response_model is inferred from return type


client: TestClient = TestClient(app)  # build the client

r = client.post("/items", json={"name": "Pen", "price": 10.5})  # call POST
print(r.status_code, r.json())  # status and body
# Output: 201 {'id': 1}

r = client.get("/items/1")  # call GET
print(r.status_code, r.json())  # status and body
# Output: 200 {'name': 'Pen', 'price': 10.5}

r = client.get("/items/99")  # unknown id
print(r.status_code, r.json())  # 404 with detail
# Output: 404 {'detail': 'Item not found'}

r = client.post("/items", json={"name": "Pen"})  # price missing
print(r.status_code, r.json()["detail"][0]["type"], r.json()["detail"][0]["loc"])  # 422 info
# Output: 422 missing ['body', 'price']

r = client.get("/items/abc")  # wrong type in path
print(r.status_code, r.json()["detail"][0]["msg"])  # pydantic message
# Output: 422 Input should be a valid integer, unable to parse string as an integer
```

## 💻 Code Example — Advanced
```python
# Production style: pytest file with fixtures, dependency override, lifespan, errors
# Save as test_api.py and run: pytest -q   (verified with pytest 9, FastAPI 0.162)
from contextlib import asynccontextmanager  # build lifespan handler
from typing import AsyncIterator, Dict, Iterator, List  # type hints

import pytest  # test framework
from fastapi import Depends, FastAPI, WebSocket  # app, DI, websocket
from fastapi.testclient import TestClient  # in-process client


events: List[str] = []  # record lifecycle events


@asynccontextmanager  # lifespan = startup + shutdown in one function
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    events.append("start")  # runs at startup (open DB pool here)
    yield  # app serves requests here
    events.append("stop")  # runs at shutdown (close pool here)


app: FastAPI = FastAPI(lifespan=lifespan)  # app with lifespan


def get_user() -> str:  # a dependency (imagine: JWT decoding)
    return "real-user"  # production value


@app.get("/me")  # route that uses the dependency
def me(user: str = Depends(get_user)) -> Dict[str, str]:
    return {"user": user}  # echo user


@app.get("/boom")  # route that crashes
def boom() -> None:
    raise RuntimeError("x")  # unhandled bug


@app.websocket("/ws")  # websocket route
async def ws(sock: WebSocket) -> None:
    await sock.accept()  # accept connection
    data: str = await sock.receive_text()  # read message
    await sock.send_text("echo:" + data)  # reply
    await sock.close()  # close


@pytest.fixture()  # fixture creates a fresh client per test
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:  # `with` runs lifespan startup/shutdown
        yield c  # give client to the test
    app.dependency_overrides.clear()  # always undo overrides


def test_override(client: TestClient) -> None:
    app.dependency_overrides[get_user] = lambda: "fake"  # replace dependency
    assert client.get("/me").json() == {"user": "fake"}  # fake is used
    app.dependency_overrides.clear()  # remove override
    assert client.get("/me").json() == {"user": "real-user"}  # real is back


def test_lifespan(client: TestClient) -> None:
    assert "start" in events  # startup ran because of `with`


def test_server_error_visible() -> None:
    with pytest.raises(RuntimeError):  # TestClient re-raises server bugs
        TestClient(app).get("/boom")
    quiet = TestClient(app, raise_server_exceptions=False)  # act like a real server
    assert quiet.get("/boom").status_code == 500  # we get a 500 response


def test_websocket(client: TestClient) -> None:
    with client.websocket_connect("/ws") as sock:  # open websocket
        sock.send_text("hi")  # send
        assert sock.receive_text() == "echo:hi"  # receive
```
Verified by running: override gives `fake` then `real`; lifespan events were `['start', 'inside', 'stop']`; the `/boom` route raised `RuntimeError` by default and returned `500` with `raise_server_exceptions=False`; websocket echoed `echo:hi`. Note: with Starlette 1.x, importing `TestClient` prints a `StarletteDeprecationWarning` suggesting `httpx2`. It still works; this is version-dependent (FastAPI 0.162, Starlette 1.10 at time of writing).

---

## 🟠 JavaScript vs Python Comparison
In Node you use `supertest` with Jest. In Python, `TestClient` plays the same role.

```python
# Python: pytest + TestClient
from fastapi.testclient import TestClient  # in-process client
client = TestClient(app)  # no server, no port
def test_health() -> None:
    r = client.get("/health")  # sync call, even though app may be async
    assert r.status_code == 200  # plain assert
```
```javascript
// JavaScript: Jest + supertest
const request = require("supertest");   // in-process HTTP testing
test("health", async () => {            // test must be async
  const res = await request(app).get("/health");  // await needed
  expect(res.status).toBe(200);         // expect(...) matcher
});
```

Key differences: `TestClient` is synchronous (no `await`, even for `async def` routes), pytest uses plain `assert`, and `dependency_overrides` replaces `jest.mock`.

---

## 🟠 FastAPI Connection
FastAPI's dependency injection is the main hook for tests. Replace the database or auth dependency with a fake; no monkeypatching needed.

```python
# Fake the DB dependency in tests
from typing import Dict, Iterator  # types
from fastapi import Depends, FastAPI  # app and DI
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI()  # app


def get_db() -> Iterator[Dict[str, int]]:  # real dependency would open a session
    yield {"users": 100}  # pretend real DB


@app.get("/count")  # route
def count(db: Dict[str, int] = Depends(get_db)) -> Dict[str, int]:
    return {"n": db["users"]}  # read from db


app.dependency_overrides[get_db] = lambda: {"users": 3}  # fake DB for tests
print(TestClient(app).get("/count").json())  # uses the fake
# Output: {'n': 3}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `with TestClient(app)` when your app needs lifespan/startup
```python
# Wrong: lifespan is NOT run, app.state.pool does not exist
client = TestClient(app)
client.get("/orders")  # AttributeError / missing pool

# Right: use the context manager so startup/shutdown run
with TestClient(app) as client:
    client.get("/orders")
```

❌ Mistake 2: Leaving `dependency_overrides` set after a test
```python
# Wrong: override leaks into the next test, causing mystery failures
app.dependency_overrides[get_db] = fake_db

# Right: clear it in a fixture teardown
yield client
app.dependency_overrides.clear()
```

❌ Mistake 3: Testing against the real production database
```python
# Wrong: tests delete real data
client = TestClient(app)  # app points at DATABASE_URL=prod

# Right: override get_db with a SQLite/test-Postgres session, or set env to a test DB
```

---

## 🧠 Tricky Interview Question

**Q**: What is printed?

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient

events = []

@asynccontextmanager
async def lifespan(app):
    events.append("start"); yield; events.append("stop")

app = FastAPI(lifespan=lifespan)

@app.get("/x")
def x(): return {}

c = TestClient(app); c.get("/x"); print(events)
with TestClient(app) as c: c.get("/x")
print(events)
```

**Answer**:
```
[]
['start', 'stop']
```
Without `with`, `TestClient` never runs the lifespan, so nothing is recorded. With `with`, startup runs on enter and shutdown on exit. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: Why is `TestClient` synchronous even for `async def` endpoints?
A1: It runs the ASGI app in a background event-loop thread (via anyio) and gives you a blocking API. For truly async tests, use `httpx.AsyncClient` with `ASGITransport` (topic 344).

Q2: How do you replace a dependency in a test?
A2: `app.dependency_overrides[original_dep] = fake_dep`, then clear it afterwards.

Q3: Why do I get a 422 in my test?
A3: Request data failed validation. Print `r.json()["detail"]`; each item shows `loc`, `msg` and `type` of the bad field.

Q4: How do you test file upload or auth headers?
A4: `client.post("/up", files={"file": ("a.txt", b"data")})` and `client.get("/me", headers={"Authorization": "Bearer token"})`.

Q5: What does `raise_server_exceptions=False` do?
A5: By default unhandled exceptions in your route are re-raised inside the test. With `False` you receive a real 500 response, like production.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You want fast unit/integration tests of routes, validation, auth and error handling
- You run tests in CI without any server
- You want to test websockets (`websocket_connect`)

❌ Avoid when:
- Your test itself must be `async` (awaiting DB fixtures) — use `httpx.AsyncClient`
- You must test real network behaviour (TLS, proxies, nginx) — use an end-to-end test against a running container

---

## 📊 Visual Diagram

```
 pytest test function
        |
        v
  TestClient(app)  --in-memory request-->  Middleware
                                              |
                                           Router
                                              |
                                  Dependencies (can be overridden)
                                              |
                                        Your endpoint
                                              |
  assert r.status_code  <--response--  Pydantic response model
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TestClient | In-process client for ASGI apps | App को सीधे call करने वाला client |
| Fixture | Reusable test setup | test की पहले से तैयारी |
| dependency_overrides | Dict to replace dependencies | dependency बदलने वाला dict |
| Lifespan | Startup/shutdown handler | app शुरू/बंद होने का code |
| 422 | Validation error status | validation में गलती |
| CI | Automatic test run on each push | हर push पर अपने-आप test |

---

## ⚡ 3-Line Summary
English: `TestClient(app)` calls your FastAPI app in memory with no server. Use `with` to run lifespan, `dependency_overrides` to fake DB/auth, and plain `assert` in pytest. It is synchronous; use `httpx.AsyncClient` for async tests.
Hindi: `TestClient(app)` बिना server के आपके app को memory में call करता है। Lifespan के लिए `with`, DB/auth fake करने के लिए `dependency_overrides` और pytest में सामान्य `assert` इस्तेमाल करें। यह synchronous है; async tests के लिए `httpx.AsyncClient` लें।

---

## ➡️ Next Topic
**344. FastAPI Testing (httpx)** — async tests with `httpx.AsyncClient` and `ASGITransport`.
