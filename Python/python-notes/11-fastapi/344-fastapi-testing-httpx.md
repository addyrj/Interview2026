---

# 344. FastAPI Testing (httpx)
# हिंदी में: FastAPI Testing (httpx से async टेस्ट)

---

## 🔵 Simple Definition (English)
`httpx.AsyncClient` with `ASGITransport` lets you test your FastAPI app with `async`/`await`, inside the same event loop as your test. Use it when your test must `await` things itself (async database fixtures, concurrent requests). `httpx` can also mock outgoing HTTP calls with `MockTransport`.

## 🔵 सरल परिभाषा (Hindi)
`httpx.AsyncClient` को `ASGITransport` के साथ इस्तेमाल करके आप FastAPI app को `async`/`await` से test करते हैं, वह भी test वाले ही event loop में। जब test को खुद कुछ `await` करना हो (async database fixtures, एक साथ कई requests) तब यह काम आता है। `httpx` का `MockTransport` बाहर जाने वाली HTTP calls को mock भी कर सकता है।

---

## 🔴 Problem it Solves
`TestClient` is synchronous and runs the app in another thread/loop. If your async DB engine, fixtures or background tasks are bound to the test's event loop, that mismatch causes "attached to a different loop" errors. `AsyncClient` runs everything in one loop and lets you fire many requests concurrently with `asyncio.gather`.

## 🔴 यह क्यों बना? (Hindi)
`TestClient` synchronous है और app को दूसरे thread/loop में चलाता है। अगर आपका async DB engine, fixtures या background tasks test के event loop से बंधे हैं, तो "attached to a different loop" जैसी errors आती हैं। `AsyncClient` सब कुछ एक ही loop में चलाता है और `asyncio.gather` से कई requests एक साथ भेजने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → transport = ASGITransport(app=app)  (talks to app directly, no socket)
Step 2 → async with AsyncClient(transport=transport, base_url="http://test") as c
Step 3 → response = await c.get("/path")
Step 4 → assert on response.status_code / response.json()
Step 5 → Mark the test async (pytest-asyncio or anyio) so pytest can await
Step 6 → ASGITransport does NOT run lifespan; use asgi-lifespan's LifespanManager if you need it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → transport = ASGITransport(app=app)  (socket नहीं, सीधे app से बात)
Step 2 → async with AsyncClient(transport=transport, base_url="http://test") as c
Step 3 → response = await c.get("/path")
Step 4 → response.status_code / response.json() पर assert
Step 5 → test को async mark करें (pytest-asyncio या anyio) ताकि pytest await कर सके
Step 6 → ASGITransport lifespan नहीं चलाता; ज़रूरत हो तो asgi-lifespan का LifespanManager लें
```

---

## 🟡 Real World Example
A Swiggy-like order service has an async SQLAlchemy engine. The test fixture creates tables with `await conn.run_sync(...)`, then the test calls `await client.post("/orders")` and finally checks the database with `await session.scalar(...)`, all in one loop. Another test sends 20 simultaneous "place order" requests with `asyncio.gather` to prove there is no race in stock deduction.

## 🟡 Real Example Hindi mein
Swiggy जैसी order service में async SQLAlchemy engine है। Test fixture `await conn.run_sync(...)` से tables बनाता है, test `await client.post("/orders")` बुलाता है और आखिर में `await session.scalar(...)` से database जाँचता है, सब एक ही loop में। दूसरा test 20 "order place करो" requests एक साथ `asyncio.gather` से भेजकर साबित करता है कि stock घटाने में race नहीं है।

---

## 💻 Code Example — Basic
```python
# Basic AsyncClient test, run with: python file.py (pip install fastapi httpx)
import asyncio  # event loop and gather
from typing import Dict  # type hints

from fastapi import FastAPI  # the framework
from httpx import ASGITransport, AsyncClient  # async client + in-process transport

app: FastAPI = FastAPI()  # create app


@app.get("/slow")  # an async endpoint
async def slow() -> Dict[str, str]:
    await asyncio.sleep(0.1)  # pretend we wait on a database
    return {"ok": "yes"}  # JSON body


async def main() -> None:
    transport: ASGITransport = ASGITransport(app=app)  # no network, direct to app
    async with AsyncClient(transport=transport, base_url="http://test") as c:  # open client
        r = await c.get("/slow")  # await one request
        print(r.status_code, r.json())  # show result
        # Output: 200 {'ok': 'yes'}
        results = await asyncio.gather(*[c.get("/slow") for _ in range(5)])  # 5 at once
        print([x.status_code for x in results])  # all statuses
        # Output: [200, 200, 200, 200, 200]


asyncio.run(main())  # start the event loop
```

## 💻 Code Example — Advanced
```python
# Production style: pytest-asyncio fixture + mock an outgoing HTTP API
# pip install fastapi httpx pytest pytest-asyncio   (verified: 1 passed)
from typing import AsyncIterator, Dict  # type hints

import httpx  # for MockTransport
import pytest  # test runner
import pytest_asyncio  # async fixtures
from fastapi import FastAPI, HTTPException  # app + errors
from httpx import ASGITransport, AsyncClient  # test client

app: FastAPI = FastAPI()  # app under test


async def fetch_payment(payment_id: str, http: httpx.AsyncClient) -> Dict[str, str]:
    r = await http.get(f"https://api.razorpay.com/v1/payments/{payment_id}")  # call 3rd party
    if r.status_code != 200:  # upstream failed
        raise HTTPException(status_code=502, detail="Gateway error")  # map to 502
    return r.json()  # parsed body


def mock_gateway(request: httpx.Request) -> httpx.Response:  # fake third party
    if request.url.path.endswith("pay_1"):  # known id
        return httpx.Response(200, json={"id": "pay_1", "status": "captured"})  # success
    return httpx.Response(404, json={"error": "not found"})  # everything else


@app.get("/payments/{payment_id}")  # our API route
async def payment(payment_id: str) -> Dict[str, str]:
    transport = httpx.MockTransport(mock_gateway)  # in tests only; prod injects real client
    async with httpx.AsyncClient(transport=transport) as http:  # fake outgoing client
        return await fetch_payment(payment_id, http)  # call helper


@pytest_asyncio.fixture  # async fixture
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c  # give client to tests; closed automatically


@pytest.mark.asyncio  # tell pytest this test is async
async def test_ok(client: AsyncClient) -> None:
    r = await client.get("/payments/pay_1")  # call our API
    assert r.status_code == 200 and r.json()["status"] == "captured"  # mocked success


@pytest.mark.asyncio  # async test
async def test_gateway_down(client: AsyncClient) -> None:
    r = await client.get("/payments/pay_x")  # upstream returns 404
    assert r.status_code == 502  # we convert to 502
```
Verified by running: a standalone `MockTransport` handler returned `{'url': 'https://api.razorpay.com/v1/payments', 'method': 'GET'}`, and a pytest-asyncio test using the fixture passed (`1 passed`). pytest-asyncio 1.x prints a deprecation warning unless you set `asyncio_default_fixture_loop_scope` in `pytest.ini`. Version-dependent: httpx 0.28 removed the old `AsyncClient(app=app)` shortcut.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: async test with httpx
@pytest.mark.asyncio  # mark async test
async def test_x(client: AsyncClient) -> None:
    r = await client.get("/x")  # await the call
    assert r.status_code == 200  # assert
```
```javascript
// JavaScript: async test with supertest / fetch mock (nock)
test("x", async () => {                 // async test function
  const res = await request(app).get("/x");  // await the call
  expect(res.status).toBe(200);         // expect matcher
});
// Outgoing calls mocked with nock / msw, Python uses httpx.MockTransport
```

Key differences: JS tests are async by default; Python needs a plugin (`pytest-asyncio` or `anyio`) to run `async def` tests. `MockTransport` is the Python equivalent of `nock`/`msw`.

---

## 🟠 FastAPI Connection
Async routes + async DB means the test should be async too. The pattern: create an async client fixture, override the DB dependency with a test session, and assert.

```python
# Async test with dependency override
from typing import Dict  # types
from fastapi import Depends, FastAPI  # app + DI
from httpx import ASGITransport, AsyncClient  # client

app: FastAPI = FastAPI()  # app


async def get_db() -> Dict[str, int]:  # pretend async session
    return {"users": 100}  # real value


@app.get("/count")  # route
async def count(db: Dict[str, int] = Depends(get_db)) -> Dict[str, int]:
    return {"n": db["users"]}  # read


async def fake_db() -> Dict[str, int]:  # test double
    return {"users": 1}  # tiny dataset


app.dependency_overrides[get_db] = fake_db  # swap for tests
# In a test: r = await client.get("/count")  ->  {'n': 1}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the removed `app=` argument
```python
# Wrong (httpx >= 0.28):
client = AsyncClient(app=app, base_url="http://test")
# TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'

# Right:
client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
```

❌ Mistake 2: Forgetting to mark the test async
```python
# Wrong: pytest sees a coroutine that is never awaited
async def test_x(client): ...   # skipped/warned without a plugin

# Right: @pytest.mark.asyncio (or asyncio_mode = auto in pytest.ini)
```

❌ Mistake 3: Expecting lifespan to run
```python
# Wrong: ASGITransport does not send lifespan events; app.state.pool is missing
# Right: wrap with asgi_lifespan.LifespanManager(app), or create resources in a fixture
```

---

## 🧠 Tricky Interview Question

**Q**: What happens?

```python
import httpx
from fastapi import FastAPI
app = FastAPI()
try:
    httpx.AsyncClient(app=app)
except TypeError as e:
    print("TypeError", e)
```

**Answer**:
```
TypeError AsyncClient.__init__() got an unexpected keyword argument 'app'
```
`httpx` 0.28 removed the `app=` shortcut (deprecated since 0.27). Use `transport=ASGITransport(app=app)`. (Verified with httpx 0.28.1.)

---

## ⚫ Interview Questions + Answers

Q1: When do you choose `AsyncClient` over `TestClient`?
A1: When the test itself is async: async DB fixtures, shared event loop objects, or concurrency tests with `asyncio.gather`.

Q2: Does `AsyncClient` start a real server?
A2: No. `ASGITransport` calls the ASGI app directly in memory.

Q3: How do you mock a third-party API?
A3: Pass `httpx.MockTransport(handler)` to the client your code uses (inject the client with `Depends`), or use `respx`.

Q4: How do you run lifespan in async tests?
A4: Use `asgi-lifespan`'s `LifespanManager(app)` around the client, because `ASGITransport` ignores lifespan.

Q5: Can I test concurrency with it?
A5: Yes. `await asyncio.gather(*[c.get("/x") for _ in range(20)])` fires 20 overlapping requests, useful for race-condition tests.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Fixtures or DB engines are async
- You need concurrent requests in a test
- You want to mock outgoing HTTP with `MockTransport`

❌ Avoid when:
- A simple synchronous test works: `TestClient` is less setup
- You need websockets: `TestClient.websocket_connect` is easier

---

## 📊 Visual Diagram

```
 async test (event loop L)
     |
     |  await client.get("/x")
     v
 AsyncClient --ASGITransport--> FastAPI app   (same loop L)
     ^                              |
     |<------ Response -------------+
 async DB session also lives in loop L  -> no loop mismatch
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AsyncClient | httpx client with `await` | await वाला httpx client |
| ASGITransport | Sends requests straight to ASGI app | app को सीधे request भेजने वाला transport |
| MockTransport | Fake network for outgoing calls | नकली network |
| pytest-asyncio | Plugin to run async tests | async tests चलाने वाला plugin |
| Event loop | Scheduler of async tasks | async कामों का scheduler |
| gather | Run awaitables together | कई कामों को साथ चलाना |

---

## ⚡ 3-Line Summary
English: Use `AsyncClient(transport=ASGITransport(app=app))` for async tests that share the event loop with fixtures. Mark tests with pytest-asyncio, mock outgoing calls with `MockTransport`, and remember lifespan is not run.
Hindi: जब fixtures के साथ एक ही event loop चाहिए तो `AsyncClient(transport=ASGITransport(app=app))` इस्तेमाल करें। Tests को pytest-asyncio से mark करें, बाहर की calls `MockTransport` से mock करें, और याद रखें कि lifespan नहीं चलता।

---

## ➡️ Next Topic
**345. FastAPI Best Practices** — the habits that keep a FastAPI codebase clean in production.
