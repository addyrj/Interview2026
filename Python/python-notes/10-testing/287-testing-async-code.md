---

# 287. Testing Async Code
# हिंदी में: Async Code को Test करना

---

## 🔵 Simple Definition (English)
Testing async code means running `async def` functions inside a test with a real event loop. With pytest you install `pytest-asyncio`, mark the test `@pytest.mark.asyncio`, write `async def test_...`, and `await` things directly. Use `AsyncMock` for async dependencies and `httpx.AsyncClient` for FastAPI apps.

## 🔵 सरल परिभाषा (Hindi)
Async code test करने का मतलब है `async def` functions को असली event loop के अंदर test में चलाना। pytest में `pytest-asyncio` install करें, test पर `@pytest.mark.asyncio` लगाएं, `async def test_...` लिखें और सीधे `await` करें। Async dependencies के लिए `AsyncMock` और FastAPI apps के लिए `httpx.AsyncClient` इस्तेमाल करें।

---

## 🔴 Problem it Solves
A normal test function is not a coroutine. If you call `await` in it, you get a syntax error. If you call an `async def` without `await`, you get a coroutine object and the code never runs (only a "coroutine was never awaited" warning). Modern FastAPI apps are async from top to bottom (endpoints, database drivers, HTTP clients), so you need an event loop inside the test, a way to fake awaitables, and a way to test timeouts and concurrency.

## 🔴 यह क्यों बना? (Hindi)
सामान्य test function coroutine नहीं होता। उसमें `await` लिखो तो syntax error। `async def` को बिना `await` call करो तो coroutine object मिलता है और code चलता ही नहीं (सिर्फ "coroutine was never awaited" warning)। आधुनिक FastAPI apps ऊपर से नीचे तक async हैं (endpoints, database drivers, HTTP clients), इसलिए test के अंदर event loop, awaitables के नकली version और timeouts व concurrency test करने का तरीका चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install pytest-asyncio  (plugin that runs coroutines in an event loop)
Step 2 → Mode: "strict" (default; you must mark tests) or "auto" (all async tests handled)
Step 3 → Write:  @pytest.mark.asyncio  async def test_x():  result = await fn()
Step 4 → Async fixtures: use @pytest_asyncio.fixture (strict mode) with async/yield
Step 5 → Fake async calls with AsyncMock: await mock() returns return_value;
         assert_awaited_once_with(...) checks the awaits
Step 6 → FastAPI: httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) calls the app in-process
Step 7 → Timeouts: asyncio.timeout(seconds) around slow code -> TimeoutError (3.11+)

Set explicitly in pytest.ini: asyncio_mode = strict   and   asyncio_default_fixture_loop_scope = function
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install pytest-asyncio  (plugin जो coroutines को event loop में चलाता है)
Step 2 → Mode: "strict" (default; tests पर mark लगाना होगा) या "auto" (सब async tests अपने आप)
Step 3 → लिखो:  @pytest.mark.asyncio  async def test_x():  result = await fn()
Step 4 → Async fixtures: @pytest_asyncio.fixture (strict mode) के साथ async/yield
Step 5 → Async calls को AsyncMock से fake करो: await mock() return_value देता है;
         assert_awaited_once_with(...) awaits जांचता है
Step 6 → FastAPI: httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) app को in-process call करता है
Step 7 → Timeouts: धीमे code के चारों ओर asyncio.timeout(seconds) -> TimeoutError (3.11+)

pytest.ini में साफ लिखो: asyncio_mode = strict   और   asyncio_default_fixture_loop_scope = function
```

---

## 🟡 Real World Example
A Swiggy-style "order tracking" endpoint fetches the order from the database and the rider location from a separate service concurrently with `asyncio.gather`. The test calls the app through `httpx.AsyncClient`, replaces the rider service with an `AsyncMock` that returns a fixed location, and also tests the timeout path: when the rider service hangs, the endpoint must answer in under 2 seconds with the last known location instead of freezing every user.

## 🟡 Real Example Hindi mein
Swiggy जैसे "order tracking" endpoint का काम है database से order और अलग service से rider की location `asyncio.gather` से एक साथ लाना। Test `httpx.AsyncClient` से app को call करता है, rider service की जगह fixed location देने वाला `AsyncMock` लगाता है और timeout वाला रास्ता भी जांचता है: rider service अटक जाए तो endpoint को 2 सेकंड से कम में आखिरी जानी हुई location के साथ जवाब देना चाहिए, सारे users को freeze नहीं करना चाहिए।

---

## 💻 Code Example — Basic
```python
# Basic async tests (verified: pytest 9.2, pytest-asyncio 1.4, Python 3.13)
# pytest.ini:
#   [pytest]
#   asyncio_mode = strict
#   asyncio_default_fixture_loop_scope = function
import asyncio                                    # event loop tools
import pytest                                     # framework


DB: dict[int, str] = {1: "asha"}                  # fake database


async def fetch_user(uid: int) -> str:            # function under test (async)
    await asyncio.sleep(0.01)                     # pretend I/O
    if uid not in DB:                             # missing user
        raise KeyError(uid)                       # error path
    return DB[uid]


@pytest.mark.asyncio                              # needed in strict mode
async def test_fetch_user() -> None:              # test itself is async
    assert await fetch_user(1) == "asha"          # just await inside the test


@pytest.mark.asyncio
async def test_missing() -> None:
    with pytest.raises(KeyError):                 # exceptions work as usual
        await fetch_user(99)


@pytest.mark.asyncio
async def test_concurrency() -> None:
    res = await asyncio.gather(*(fetch_user(1) for _ in range(5)))   # 5 tasks at once
    assert res == ["asha"] * 5                    # gather keeps the input order

# Output: 3 passed
#
# Without the plugin / mark (strict mode), pytest does NOT run the coroutine. Real result:
#   async def test_forgot_mark(): assert False
#   -> FAILED ... "async def functions are not natively supported."
# And calling an async function without await:
#   f()  -> a coroutine object; Python warns "RuntimeWarning: coroutine 'f' was never awaited"
```

## 💻 Code Example — Advanced
```python
# Production style: FastAPI + async client fixture + AsyncMock + timeout (verified: all three tests pass)
import asyncio                                    # gather / timeout
from collections.abc import AsyncIterator         # type of async generator fixtures
from unittest.mock import AsyncMock, patch        # async-aware mock
import httpx                                      # async HTTP client
import pytest                                     # framework
import pytest_asyncio                             # async fixtures in strict mode
from fastapi import FastAPI, HTTPException        # app

app: FastAPI = FastAPI()                          # app under test
DB: dict[int, str] = {1: "asha"}                  # fake db


async def fetch_user(uid: int) -> str:            # async dependency
    await asyncio.sleep(0.01)                     # pretend I/O
    if uid not in DB:
        raise KeyError(uid)
    return DB[uid]


async def slow() -> None:
    await asyncio.sleep(10)                       # something that hangs


@app.get("/users/{uid}")
async def get_user(uid: int) -> dict[str, str]:   # async endpoint
    try:
        return {"name": await fetch_user(uid)}
    except KeyError:
        raise HTTPException(404, "not found")     # clean 404


@pytest_asyncio.fixture                           # async fixture needs this decorator in strict mode
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)      # call the ASGI app directly: no server, no network
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c                                   # teardown happens when the async with exits


@pytest.mark.asyncio
async def test_endpoint(client: httpx.AsyncClient) -> None:
    r = await client.get("/users/1")              # await the request
    assert r.status_code == 200 and r.json() == {"name": "asha"}
    assert (await client.get("/users/5")).status_code == 404


@pytest.mark.asyncio
async def test_asyncmock() -> None:
    with patch(f"{__name__}.fetch_user", new=AsyncMock(return_value="mocked")) as m:   # patch with AsyncMock
        assert await fetch_user(7) == "mocked"    # awaiting the mock returns the value
        m.assert_awaited_once_with(7)             # await-specific assertion


@pytest.mark.asyncio
async def test_timeout() -> None:
    with pytest.raises(TimeoutError):             # asyncio.timeout raises TimeoutError (3.11+)
        async with asyncio.timeout(0.05):         # cancel after 50 ms
            await slow()                          # would take 10 s without the timeout

# Notes:
# - In the verified project the app code lived in app.py and the patch target was "app.fetch_user";
#   when code and tests share one file, patch f"{__name__}.fetch_user" as above.
# - TestClient (sync) is also fine for simple FastAPI tests; AsyncClient is needed when the test itself must await things.
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (pytest-asyncio) | JavaScript (Jest) |
|---------|-------------------------|-------------------|
| Async test | `@pytest.mark.asyncio async def` | `test("x", async () => {...})` |
| Await result | `await fn()` | `await fn()` |
| Expect rejection | `with pytest.raises(E): await fn()` | `await expect(fn()).rejects.toThrow()` |
| Fake async fn | `AsyncMock(return_value=1)` | `jest.fn().mockResolvedValue(1)` |
| Timers | `asyncio.timeout`, `freezegun`-style tools | `jest.useFakeTimers()` |
| Forgetting await | warning "never awaited" | un-awaited promise (test may pass wrongly) |
| Needs a plugin | yes (`pytest-asyncio` / `anyio`) | no, built in |

```python
# Python way
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_call() -> None:
    api = AsyncMock(return_value={"ok": True})    # async fake
    assert await api() == {"ok": True}            # await it
    api.assert_awaited_once()                     # verify the await
```
```javascript
// JavaScript way (Jest)
test("call", async () => {
  const api = jest.fn().mockResolvedValue({ ok: true });   // async fake
  expect(await api()).toEqual({ ok: true });               // await it
  expect(api).toHaveBeenCalledTimes(1);                    // verify the call
});
```

Key difference: Jest understands promises natively. Python test functions are plain functions, so you need a plugin to supply an event loop. Python also gives a loud "never awaited" warning when you forget `await`; in JS a forgotten `await` can make a test pass without checking anything.

---

## 🟠 FastAPI Connection
For simple endpoints, `TestClient` is enough (it runs the async app in a background thread for you) and the test can stay synchronous. Use `httpx.AsyncClient` with `ASGITransport` when the test must `await` other async code (a real async database session, background tasks, or concurrent requests). With `ASGITransport` lifespan events (startup/shutdown) do not run automatically; use a library such as `asgi-lifespan` if your app depends on them.

```python
# FastAPI: concurrent requests in one async test
import asyncio                                            # gather
import httpx                                              # async client
import pytest                                             # pytest
from fastapi import FastAPI                               # app

app: FastAPI = FastAPI()                                  # app
counter: dict[str, int] = {"hits": 0}                     # shared state


@app.post("/hit")
async def hit() -> dict[str, int]:
    await asyncio.sleep(0)                                # yield control to the event loop
    counter["hits"] += 1                                  # safe in one event loop (no threads)
    return counter


@pytest.mark.asyncio
async def test_parallel_hits() -> None:
    transport = httpx.ASGITransport(app=app)              # in-process ASGI
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        results = await asyncio.gather(*(c.post("/hit") for _ in range(10)))   # 10 at once
    assert all(r.status_code == 200 for r in results)     # all succeeded
    assert counter["hits"] == 10                          # no lost updates
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `await` (the test checks a coroutine object, not the result)
✅ Correct: always `await` async calls

```python
# Wrong — "coroutine ... was never awaited"; the assertion below would compare a coroutine
async def test_a() -> None:
    result = fetch_user(1)
    # assert result == "asha"  -> False!
# Right
async def test_b() -> None:
    result = await fetch_user(1)
```

❌ Mistake 2: Using a plain `@pytest.fixture` for an async fixture in strict mode
✅ Correct: `@pytest_asyncio.fixture` (or set `asyncio_mode = "auto"`)

❌ Mistake 3: Using `Mock` / `MagicMock` for an async function
✅ Correct: use `AsyncMock` (and `patch` picks it automatically for `async def` targets)

```python
from unittest.mock import MagicMock, AsyncMock
# Wrong — "await MagicMock()()" -> TypeError: object MagicMock can't be used in 'await' expression
# Right
fake = AsyncMock(return_value=1)    # await fake() -> 1
```

❌ Mistake 4: `time.sleep()` inside async code or tests (blocks the whole event loop)
✅ Correct: `await asyncio.sleep()`; and for slow code use `asyncio.timeout()` so tests cannot hang forever

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import asyncio

async def f() -> int:
    return 1

async def main() -> None:
    c = f()
    print(type(c).__name__)
    print(c == 1)
    print(await c)

asyncio.run(main())
```
Answer: `coroutine`, then `False`, then `1`. Calling an `async def` function does not run its body; it creates a coroutine object. Comparing that object with `1` is `False`. Only `await c` runs it and gives `1`. This is exactly what happens in a test when you forget `await`: the assertion compares a coroutine with a value, and Python only emits a `RuntimeWarning` if the coroutine is never awaited. (A related surprise: `assert coroutine_object` is always truthy, so such a test passes silently.)

---

## ⚫ Interview Questions + Answers

Q1: Why does pytest need a plugin to test async code?
A1: A test function is called like a regular function and returns. For `async def`, calling returns a coroutine object that nobody runs. `pytest-asyncio` (or `anyio`'s pytest plugin) detects async tests and runs them in an event loop.

Q2: Difference between `asyncio_mode = strict` and `auto`?
A2: In strict (default) you mark tests with `@pytest.mark.asyncio` and async fixtures with `@pytest_asyncio.fixture`; plain unmarked async tests are not handled by it. In auto mode all `async def` tests and fixtures are handled automatically, which is simpler for projects using only asyncio.

Q3: How do you mock an async dependency?
A3: `AsyncMock`. `await mock()` returns `return_value`, or raises/produces values via `side_effect`. Check with `assert_awaited`, `assert_awaited_once_with`, `await_count`. `patch` creates an `AsyncMock` automatically if the target is an `async def`.

Q4: How do you test FastAPI async endpoints?
A4: Either the sync `TestClient` (simple, runs the loop for you) or `httpx.AsyncClient(transport=ASGITransport(app=app))` inside an async test when you need to await other things or send concurrent requests. Override dependencies with `app.dependency_overrides`.

Q5: How do you test timeouts without waiting?
A5: Wrap the call in `asyncio.timeout(0.05)` (3.11+) or `asyncio.wait_for(...)` and expect `TimeoutError`; or mock the slow dependency with `AsyncMock(side_effect=TimeoutError())`. Never call a real `sleep(10)` in a test.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Code uses `async def`, `await`, `asyncio.gather`, async DB drivers, `httpx.AsyncClient`
- You need to test concurrency, cancellation, and timeouts
- A test must await another coroutine (async fixtures, async DB session)

❌ Avoid when:
- A synchronous FastAPI test through `TestClient` is enough
- You can test the pure logic as normal sync functions (keep logic outside the async layer)
- You rely on real sleeping/time: use timeouts and mocks instead

---

## 📊 Visual Diagram
```
sync test:   test() ──► runs ──► done

async test:  pytest-asyncio
                 |
                 v
           create event loop
                 |
                 v
      run  async def test():          (await points let other tasks run)
              r = await client.get("/users/1")  ──► ASGITransport ──► FastAPI app (in-process)
              await asyncio.gather(...)         ──► tasks interleave
                 |
                 v
           close loop, clean async fixtures

 Forgot await:   fetch_user(1)  -> <coroutine>  (body never ran)  ⚠
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coroutine | Result of calling an `async def` | `async def` को call करने का नतीजा |
| Event loop | Scheduler that runs coroutines | Coroutines चलाने वाला scheduler |
| pytest-asyncio | Plugin to run async tests | Async tests चलाने वाला plugin |
| AsyncMock | Mock whose calls can be awaited | जिसे await किया जा सके ऐसा mock |
| ASGITransport | Calls an ASGI app without a server | बिना server के ASGI app call करना |
| asyncio.timeout | Cancels slow awaits | धीमे await को रोकना |

---

## ⚡ 3-Line Summary
English: To test async code, use `pytest-asyncio` with `@pytest.mark.asyncio` and `await` inside the test. Fake async dependencies with `AsyncMock`, call FastAPI through `httpx.AsyncClient` with `ASGITransport`, and guard slow code with `asyncio.timeout`. Never forget `await`.
Hindi: Async code test करने के लिए `pytest-asyncio` के साथ `@pytest.mark.asyncio` लगाएं और test के अंदर `await` करें। Async dependencies को `AsyncMock` से fake करें, FastAPI को `ASGITransport` वाले `httpx.AsyncClient` से call करें और धीमे code पर `asyncio.timeout` लगाएं। `await` कभी न भूलें।

---

## ➡️ Next Topic
**288. Coverage.py** — measure which lines and branches your tests actually run, and fail CI when coverage drops.
