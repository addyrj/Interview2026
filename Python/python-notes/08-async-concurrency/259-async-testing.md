---

# 259. Async Testing
# हिंदी में: Async Code की Testing (pytest-asyncio, anyio, httpx)

---

## 🔵 Simple Definition (English)
Async testing means writing tests for `async def` functions and async web endpoints. Plain pytest cannot run coroutines, so you add a plugin (`pytest-asyncio` or `anyio`) that starts an event loop for each test. For FastAPI you call the app in-process with `httpx.AsyncClient` and `ASGITransport`.

## 🔵 सरल परिभाषा (Hindi)
Async testing का मतलब `async def` functions और async web endpoints के tests लिखना है। सादा pytest coroutines नहीं चला सकता, इसलिए एक plugin (`pytest-asyncio` या `anyio`) जोड़ते हैं जो हर test के लिए event loop चलाता है। FastAPI के लिए आप `httpx.AsyncClient` और `ASGITransport` से app को उसी process में बुलाते हैं।

---

## 🔴 Problem it Solves
If you write `async def test_x(): assert await f() == 1` and run plain pytest, the coroutine is created but never awaited, so the test does not really run (modern pytest fails it with "async def functions are not natively supported"). Async tests also need async fixtures (DB connections, HTTP clients), mocking of awaitables, and timeouts. The plugins solve all of this.

## 🔴 यह क्यों बना? (Hindi)
अगर आप `async def test_x(): assert await f() == 1` लिखकर सादा pytest चलाएं, तो coroutine बनता है पर await नहीं होता, यानी test असल में चलता नहीं (नया pytest उसे "async def functions are not natively supported" से fail करता है)। Async tests को async fixtures (DB connections, HTTP clients), awaitables की mocking और timeouts भी चाहिए। Plugins यह सब हल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install pytest pytest-asyncio httpx   (or use anyio's built-in pytest plugin)
Step 2 → Mark the test:  @pytest.mark.asyncio  (strict mode) or set asyncio_mode = auto
Step 3 → The plugin creates an event loop and runs your coroutine to the end
Step 4 → Async fixtures use @pytest_asyncio.fixture (strict mode) and can yield
Step 5 → For FastAPI: httpx.AsyncClient(transport=ASGITransport(app=app))
Step 6 → Mock async functions with unittest.mock.AsyncMock
Step 7 → Use asyncio.wait_for / anyio.fail_after to make tests fail instead of hanging
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install pytest pytest-asyncio httpx   (या anyio का built-in pytest plugin)
Step 2 → Test पर mark लगाओ:  @pytest.mark.asyncio  (strict mode) या asyncio_mode = auto
Step 3 → Plugin event loop बनाता है और आपके coroutine को पूरा चलाता है
Step 4 → Async fixtures में @pytest_asyncio.fixture (strict mode) लगता है, yield भी हो सकता है
Step 5 → FastAPI के लिए: httpx.AsyncClient(transport=ASGITransport(app=app))
Step 6 → Async functions को unittest.mock.AsyncMock से mock करो
Step 7 → Test अटकने की जगह fail हो, इसके लिए asyncio.wait_for / anyio.fail_after इस्तेमाल करो
```

---

## 🟡 Real World Example
A stock-price API (Zerodha-style) has an endpoint `/price/{symbol}` that calls an external quote service. The CI pipeline runs tests that (1) call the endpoint through `AsyncClient` without starting a real server, (2) replace the external call with `AsyncMock` so tests are fast and do not depend on the internet, and (3) check the 404 path. These tests run in milliseconds on every pull request.

## 🟡 Real Example Hindi mein
Stock-price API (Zerodha जैसी) में `/price/{symbol}` endpoint बाहरी quote service को बुलाता है। CI pipeline ऐसे tests चलाती है जो (1) असली server शुरू किए बिना `AsyncClient` से endpoint बुलाते हैं, (2) बाहरी call को `AsyncMock` से बदलते हैं ताकि tests तेज़ रहें और internet पर निर्भर न हों, और (3) 404 वाला रास्ता जांचते हैं। ये tests हर pull request पर मिलीसेकंड में चलते हैं।

---

## 💻 Code Example — Basic
```python
# Basic async tests (verified: pytest 9.2, pytest-asyncio 1.4, Python 3.13)
# Files:  app.py  (the code under test)  +  test_basic.py  +  pytest.ini
#
# pytest.ini
#   [pytest]
#   asyncio_mode = strict
#   asyncio_default_fixture_loop_scope = function

# ---------- app.py ----------
import asyncio                                           # sleep
from fastapi import FastAPI, HTTPException               # web framework

app: FastAPI = FastAPI()                                 # the application


async def fetch_price(sym: str) -> float:                # pretend external API call
    await asyncio.sleep(0.01)                            # network delay
    return {"INFY": 1500.5}.get(sym, -1.0)               # -1.0 means unknown symbol


@app.get("/price/{sym}")                                 # GET /price/INFY
async def price(sym: str) -> dict[str, float]:
    p: float = await fetch_price(sym)                    # call the "API"
    if p < 0:                                            # unknown symbol
        raise HTTPException(404, "unknown symbol")       # 404 reply
    return {"price": p}                                  # JSON reply


# ---------- test_basic.py ----------
import asyncio                                           # for wait_for
import pytest                                            # test framework
from app import fetch_price                              # function under test


@pytest.mark.asyncio                                     # tells pytest-asyncio to run it in a loop
async def test_fetch_price() -> None:
    assert await fetch_price("INFY") == 1500.5           # await works inside the test


@pytest.mark.asyncio                                     # another async test
async def test_timeout() -> None:
    with pytest.raises(asyncio.TimeoutError):            # expect a timeout error
        await asyncio.wait_for(asyncio.sleep(1), timeout=0.05)   # 0.05 s limit on a 1 s sleep

# Run:  pytest -q
# Output (both tests pass):
# ..                                            [100%]
```

## 💻 Code Example — Advanced
```python
# Advanced: FastAPI endpoint tests, async fixture, AsyncMock, parametrize
# test_app.py  (uses app.py from the basic example)  -- verified together with the other examples: 9 passed
import httpx                                             # HTTP client with ASGI support
import pytest                                            # test framework
import pytest_asyncio                                    # async fixture decorator
from unittest.mock import AsyncMock, patch               # mock awaitables
from app import app                                      # the FastAPI app


@pytest_asyncio.fixture                                  # async fixture (strict mode needs this decorator)
async def client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)             # call the app directly, no network/port
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c                                          # tests receive the client; closed afterwards


@pytest.mark.asyncio
async def test_ok(client: httpx.AsyncClient) -> None:
    r: httpx.Response = await client.get("/price/INFY")  # call the endpoint
    assert r.status_code == 200                          # success
    assert r.json() == {"price": 1500.5}                 # exact body


@pytest.mark.asyncio
async def test_mocked_dependency(client: httpx.AsyncClient) -> None:
    with patch("app.fetch_price", new=AsyncMock(return_value=9.0)) as m:   # replace the slow call
        r: httpx.Response = await client.get("/price/ANY")   # any symbol now works
    assert r.json() == {"price": 9.0}                    # served the mocked value
    m.assert_awaited_once_with("ANY")                    # it was awaited once with that argument


@pytest.mark.parametrize("sym,code", [("INFY", 200), ("NOPE", 404)])   # two cases, one test
@pytest.mark.asyncio
async def test_status(client: httpx.AsyncClient, sym: str, code: int) -> None:
    assert (await client.get(f"/price/{sym}")).status_code == code   # check each status


# ---- anyio alternative (also verified): no pytest-asyncio needed ----
import anyio                                             # anyio ships a pytest plugin


@pytest.mark.anyio                                       # run on the backends from `anyio_backend`
async def test_anyio_style() -> None:
    with anyio.fail_after(1):                            # fail (not hang) after 1 s
        await anyio.sleep(0.01)                          # code under test

# Run:  pytest -q          (anyio test is run twice: [asyncio] and [trio], needs trio installed)
# Output (this file): 6 passed  (test_ok, test_mocked_dependency, 2 x test_status, 2 x anyio test)
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (pytest) | JavaScript (Jest/Vitest) |
|---------|-----------------|-------------------------|
| Async test | `@pytest.mark.asyncio` + `async def` | `test("x", async () => {...})` (built in) |
| Mock async fn | `AsyncMock` | `jest.fn().mockResolvedValue(...)` |
| HTTP test client | `httpx.AsyncClient(ASGITransport)` | `supertest` |
| Fixtures | `@pytest_asyncio.fixture` | `beforeEach(async () => ...)` |
| Timeout | `asyncio.wait_for` / pytest-timeout | `jest.setTimeout` |
| Needs plugin? | YES | NO |

```python
# Python way
@pytest.mark.asyncio
async def test_x() -> None:
    assert await f() == 1
```
```javascript
// JavaScript way
test("x", async () => {
  expect(await f()).toBe(1);
});
```

Key difference: Jest/Vitest understand promises natively, but pytest needs a plugin and a marker (or `asyncio_mode = auto`). Also in Python an async fixture needs its own decorator in strict mode.

---

## 🟠 FastAPI Connection
FastAPI's docs recommend `httpx.AsyncClient` with `ASGITransport` for async tests (and `TestClient` for simple sync tests). For dependency overrides, set `app.dependency_overrides[get_db] = fake_db` and clear it after each test. Note: `AsyncClient` with `ASGITransport` does NOT run lifespan events; use `asgi-lifespan`'s `LifespanManager` (or `TestClient` as a context manager) if you need startup/shutdown code to run.

```python
# FastAPI example — override a dependency in tests
import httpx                                             # client
import pytest                                            # tests
from fastapi import Depends, FastAPI                     # FastAPI

app: FastAPI = FastAPI()                                 # app


async def get_db() -> str:                               # real dependency (imagine a DB)
    return "real-db"                                     # real value


@app.get("/where")                                       # endpoint
async def where(db: str = Depends(get_db)) -> dict[str, str]:
    return {"db": db}                                    # shows which db was used


@pytest.mark.asyncio
async def test_override() -> None:
    async def fake_db() -> str:                          # test double
        return "fake-db"                                 # fake value

    app.dependency_overrides[get_db] = fake_db           # swap the dependency
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            assert (await c.get("/where")).json() == {"db": "fake-db"}   # fake used
    finally:
        app.dependency_overrides.clear()                 # always restore
```
(Pattern; same technique as the verified tests above.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the marker (strict mode)
✅ Correct: add `@pytest.mark.asyncio` (or set `asyncio_mode = auto`)

```python
# Wrong — fails: "async def functions are not natively supported"
async def test_x() -> None:
    await asyncio.sleep(0)
# Right
@pytest.mark.asyncio
async def test_x() -> None:
    await asyncio.sleep(0)
```

❌ Mistake 2: Using `@pytest.fixture` for an async fixture in strict mode
✅ Correct: `@pytest_asyncio.fixture`

```python
# Wrong — ERROR: 'test_x' requested an async fixture 'f', with no plugin or hook that handled it
@pytest.fixture
async def f(): return 1
# Right
@pytest_asyncio.fixture
async def f(): return 1
```

❌ Mistake 3: Using `MagicMock` for an async function
✅ Correct: use `AsyncMock` (or `patch(..., new_callable=AsyncMock)`)

```python
# Wrong — a plain MagicMock returns a float; awaiting it gives
# TypeError: object float can't be used in 'await' expression
with patch("app.fetch_price", new=MagicMock(return_value=9.0)): ...
# Right
with patch("app.fetch_price", new=AsyncMock(return_value=9.0)): ...
```

---

## 🧠 Tricky Interview Question

```python
# pytest.ini has: asyncio_mode = strict   -- what happens?
import asyncio
import pytest

async def test_unmarked() -> None:
    await asyncio.sleep(0)

@pytest.fixture
async def f() -> int:
    return 1

@pytest.mark.asyncio
async def test_fx(f: int) -> None:
    assert f == 1
```
Answer: Both fail, in different ways (verified with pytest 9 and pytest-asyncio 1.4). `test_unmarked` FAILS with "async def functions are not natively supported", since strict mode only handles tests marked `asyncio`. `test_fx` ERRORS at setup with "requested an async fixture 'f', with no plugin or hook that handled it", because the fixture was declared with plain `@pytest.fixture`. Fix: mark the first test, and use `@pytest_asyncio.fixture` for the second (or switch to `asyncio_mode = auto`, where both would work without markers).

---

## ⚫ Interview Questions + Answers

Q1: Strict vs auto mode in pytest-asyncio?
A1: In `strict` (default) only tests marked `@pytest.mark.asyncio` and fixtures from `@pytest_asyncio.fixture` are handled, so it coexists with other async plugins. In `auto` all async tests/fixtures are handled automatically, with no markers.

Q2: How do you test a FastAPI async endpoint without running a server?
A2: `httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")`. Requests go straight into the ASGI app in memory.

Q3: How do you mock an async function?
A3: `unittest.mock.AsyncMock`. `patch()` uses `AsyncMock` automatically when the target is an `async def`. Assert with `assert_awaited_once()` / `assert_awaited_with()`.

Q4: What is the event loop scope?
A4: By default each test gets its own new loop (`function` scope). A session-scoped async fixture (e.g. a DB pool) needs a matching loop scope, e.g. `@pytest.mark.asyncio(loop_scope="session")` and `@pytest_asyncio.fixture(loop_scope="session")` (pytest-asyncio 0.24+).

Q5: How do you avoid a hanging async test?
A5: Wrap awaits in `asyncio.timeout()` (3.11+) / `asyncio.wait_for` / `anyio.fail_after`, or use the `pytest-timeout` plugin.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Testing coroutines, async DB/HTTP code and FastAPI endpoints
- You need to await inside fixtures (connections, clients)
- You want fast tests with `AsyncMock` instead of real network calls

❌ Avoid when:
- Code is sync (plain pytest or `TestClient` is simpler)
- You need real end-to-end behaviour (run a real server in a separate integration suite)
- You rely on lifespan events with only `ASGITransport` (it will not run them)

---

## 📊 Visual Diagram
```
pytest collects:  async def test_x(client)
        │
        ▼
 pytest-asyncio plugin
   1. creates event loop
   2. runs async fixtures (client)      <- @pytest_asyncio.fixture
   3. await test_x(...)
   4. runs fixture teardown, closes loop

 AsyncClient ──(in-memory ASGI call, no socket)──> FastAPI app
                                                       │
                                            AsyncMock replaces slow externals
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pytest-asyncio | Plugin to run async tests | Async tests चलाने वाला plugin |
| strict / auto mode | Marker required / not required | Marker जरूरी / गैर-जरूरी |
| AsyncMock | Mock whose calls are awaitable | Awaitable calls वाला mock |
| ASGITransport | Calls an ASGI app in memory | App को memory में बुलाना |
| Fixture | Reusable test setup | दोबारा इस्तेमाल होने वाला test setup |
| dependency_overrides | Swap FastAPI dependencies in tests | Tests में dependencies बदलना |

---

## ⚡ 3-Line Summary
English: Async tests need a plugin: `pytest-asyncio` (marker + `@pytest_asyncio.fixture`) or anyio's `@pytest.mark.anyio`. Test FastAPI in memory with `AsyncClient(ASGITransport)`, mock awaitables with `AsyncMock`, and always add timeouts.
Hindi: Async tests को plugin चाहिए: `pytest-asyncio` (marker + `@pytest_asyncio.fixture`) या anyio का `@pytest.mark.anyio`। FastAPI को memory में `AsyncClient(ASGITransport)` से test करें, awaitables को `AsyncMock` से mock करें, और हमेशा timeouts लगाएं।

---

## ➡️ Next Topic
**260. Performance Comparison** — measuring sequential vs asyncio vs threads vs processes with real numbers.
