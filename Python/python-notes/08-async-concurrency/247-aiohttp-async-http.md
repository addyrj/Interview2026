---

# 247. aiohttp — Async HTTP
# हिंदी में: aiohttp — Async HTTP Client और Server

---

## 🔵 Simple Definition (English)
`aiohttp` is a library for making HTTP requests (client) and building HTTP servers using `async`/`await`. While one request waits for the network, the event loop runs other requests. So one thread can handle hundreds of calls at once.

## 🔵 सरल परिभाषा (Hindi)
`aiohttp` एक library है जिससे `async`/`await` में HTTP requests (client) भेजी जाती हैं और HTTP server बनाए जाते हैं। जब एक request network का इंतजार करती है, तब event loop दूसरी requests चलाता है। इसलिए एक thread सैकड़ों calls एक साथ संभाल सकता है।

---

## 🔴 Problem it Solves
`requests.get()` is blocking. If you call 100 APIs one by one and each takes 200 ms, you wait 20 seconds. Inside an async app (FastAPI), a blocking call even freezes the whole event loop, so every other user waits too. `aiohttp` gives non-blocking HTTP so 100 calls can finish in about 200 ms total.

## 🔴 यह क्यों बना? (Hindi)
`requests.get()` blocking है। अगर आप 100 APIs एक-एक करके बुलाएं और हर एक 200 ms ले, तो 20 सेकंड लगते हैं। Async app (FastAPI) के अंदर blocking call पूरे event loop को रोक देती है, यानी बाकी सारे users भी इंतजार करते हैं। `aiohttp` non-blocking HTTP देता है, जिससे 100 calls कुल लगभग 200 ms में हो जाती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create ONE ClientSession (it owns a connection pool)
Step 2 → session.get(url) sends the request and yields control (await)
Step 3 → Event loop runs other coroutines while the network is busy
Step 4 → Response headers arrive -> you get a ClientResponse object
Step 5 → await resp.json() / resp.text() reads the body
Step 6 → Leaving "async with" releases the connection back to the pool
Step 7 → asyncio.gather() runs many such requests concurrently
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक ही ClientSession बनाओ (इसके पास connection pool होता है)
Step 2 → session.get(url) request भेजकर control छोड़ देता है (await)
Step 3 → Network busy होने पर event loop दूसरे coroutines चलाता है
Step 4 → Response headers आते हैं -> ClientResponse object मिलता है
Step 5 → await resp.json() / resp.text() से body पढ़ते हैं
Step 6 → "async with" से बाहर आने पर connection pool में वापस जाता है
Step 7 → asyncio.gather() से ऐसी कई requests एक साथ चलती हैं
```

---

## 🟡 Real World Example
An aggregator app (like a Razorpay dashboard) needs payment status from 5 services: payments, refunds, settlements, disputes and customers. With `aiohttp` and `gather` it calls all 5 together, so the dashboard loads in the time of the slowest call instead of the sum of all. A web crawler or price-comparison bot (Flipkart vs Amazon) also uses `aiohttp` to fetch thousands of pages quickly.

## 🟡 Real Example Hindi mein
Aggregator app (जैसे Razorpay dashboard) को 5 services से payment status चाहिए: payments, refunds, settlements, disputes और customers। `aiohttp` और `gather` से पांचों एक साथ बुलाए जाते हैं, इसलिए dashboard सबसे धीमी call के समय में खुलता है, सबके जोड़ में नहीं। Web crawler या price-comparison bot (Flipkart vs Amazon) भी हजारों pages जल्दी लाने के लिए `aiohttp` इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic aiohttp: a tiny local server + a client calling it (runs standalone)
# pip install aiohttp
import asyncio                                           # event loop
from aiohttp import web, ClientSession                   # server + client classes


async def hello(request: web.Request) -> web.Response:   # a route handler
    await asyncio.sleep(0.1)                             # pretend to do I/O
    return web.json_response({"id": request.match_info["id"]})   # JSON reply


async def serve() -> web.AppRunner:                      # start the server in background
    app: web.Application = web.Application()             # create the app
    app.add_routes([web.get("/item/{id}", hello)])       # register a route
    runner: web.AppRunner = web.AppRunner(app)           # runner manages lifecycle
    await runner.setup()                                 # prepare it
    await web.TCPSite(runner, "127.0.0.1", 34147).start()  # listen on a port
    return runner                                        # caller will clean up


async def main() -> None:
    runner: web.AppRunner = await serve()                # start server
    async with ClientSession() as s:                     # one session = connection pool
        async with s.get("http://127.0.0.1:34147/item/1") as r:   # send GET
            print(r.status, await r.json())              # status and parsed JSON
    await runner.cleanup()                               # stop the server


asyncio.run(main())                                      # run everything

# Output:
# 200 {'id': '1'}
```

## 💻 Code Example — Advanced
```python
# Production style: shared session, timeout, concurrency, error handling
import asyncio                                           # gather
import time                                              # measure speed
from typing import Any                                   # type hints
from aiohttp import web, ClientSession, ClientTimeout, ClientError   # aiohttp parts


async def item(request: web.Request) -> web.Response:   # slow-ish endpoint
    await asyncio.sleep(0.1)                             # 100 ms of "work"
    return web.json_response({"id": request.match_info["id"]})   # reply


async def boom(request: web.Request) -> web.Response:   # always fails
    return web.Response(status=500, text="fail")         # HTTP 500


async def fetch(session: ClientSession, i: int) -> dict[str, Any]:
    async with session.get(f"http://127.0.0.1:34147/item/{i}") as resp:   # GET one item
        resp.raise_for_status()                          # raise on 4xx/5xx
        return await resp.json()                         # parsed body


async def main() -> None:
    app: web.Application = web.Application()             # build server
    app.add_routes([web.get("/item/{id}", item), web.get("/boom", boom)])   # routes
    runner: web.AppRunner = web.AppRunner(app)           # runner
    await runner.setup()                                 # prepare
    await web.TCPSite(runner, "127.0.0.1", 34147).start()   # listen

    start: float = time.perf_counter()                   # start timer
    async with ClientSession(timeout=ClientTimeout(total=5)) as s:   # 5 s total timeout
        results = await asyncio.gather(*(fetch(s, i) for i in range(10)))   # 10 calls at once
        print(len(results), results[0])                  # how many, first one
        try:                                             # error handling
            async with s.get("http://127.0.0.1:34147/boom") as r:   # failing endpoint
                r.raise_for_status()                     # turns 500 into an exception
        except ClientError as e:                         # base class of all client errors
            print(type(e).__name__, getattr(e, "status", None))   # name + HTTP status
    print("fast:", time.perf_counter() - start < 0.5)    # 10 calls took ~0.1 s, not 1 s
    await runner.cleanup()                               # shutdown


asyncio.run(main())                                      # run

# Output:
# 10 {'id': '0'}
# ClientResponseError 500
# fast: True
# (verified with aiohttp 3.14, Python 3.13; timings vary by machine)
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (aiohttp) | JavaScript |
|---------|------------------|-----------|
| HTTP client | `ClientSession.get()` | `fetch()` / axios |
| Reuse connections | one `ClientSession` | keep-alive agent |
| Parallel calls | `asyncio.gather` | `Promise.all` |
| Timeout | `ClientTimeout(total=5)` | `AbortSignal.timeout(5000)` |
| Error on 4xx/5xx | `raise_for_status()` | check `res.ok` (fetch does not throw) |
| Read body | `await resp.json()` | `await res.json()` |

```python
# Python way
import asyncio, aiohttp                                  # imports

async def main() -> None:
    async with aiohttp.ClientSession() as s:             # session
        urls = ["https://a.com", "https://b.com"]        # two URLs
        rs = await asyncio.gather(*(s.get(u) for u in urls))   # parallel (shown for shape)
```
```javascript
// JavaScript way
const urls = ["https://a.com", "https://b.com"];          // two URLs
const rs = await Promise.all(urls.map(u => fetch(u)));    // parallel
const data = await Promise.all(rs.map(r => r.json()));    // read bodies
```

Key difference: in JS the response body is read with the same `await res.json()`, but in aiohttp you must close the response (use `async with`) or the connection leaks. Also `fetch` is global; aiohttp needs a session object you manage yourself.

---

## 🟠 FastAPI Connection
Inside a FastAPI `async def` endpoint, never call `requests`. Use `aiohttp` (or `httpx.AsyncClient`). Create ONE session at startup using lifespan and reuse it for every request.

```python
# FastAPI example — shared aiohttp session via lifespan
from contextlib import asynccontextmanager               # lifespan helper
from collections.abc import AsyncIterator                # type for lifespan
import aiohttp                                           # HTTP client
from fastapi import FastAPI, Request                     # FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))   # startup
    yield                                                # app runs here
    await app.state.http.close()                         # shutdown: close the pool


app: FastAPI = FastAPI(lifespan=lifespan)                # attach lifespan


@app.get("/proxy")                                       # GET /proxy?url=...
async def proxy(request: Request, url: str) -> dict[str, int]:
    async with request.app.state.http.get(url) as r:     # reuse the shared session
        body: bytes = await r.read()                     # read the body
        return {"status": r.status, "bytes": len(body)}  # small summary
```
(Pattern only; the shared-session idea was verified, this endpoint was not called against the internet.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating a new `ClientSession` for every request
✅ Correct: create one session and reuse it

```python
import aiohttp

# Wrong — new pool + new TCP/TLS handshake each time (slow, warns on leaks)
async def bad(url: str) -> int:
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            return r.status

# Right — session passed in, created once by the caller
async def good(s: aiohttp.ClientSession, url: str) -> int:
    async with s.get(url) as r:
        return r.status
```

❌ Mistake 2: Not closing the response / session
✅ Correct: always use `async with`, or you get "Unclosed client session" warnings and leaked sockets

```python
# Wrong
# r = await session.get(url)      # connection stays open until garbage-collected
# Right
# async with session.get(url) as r: ...
```

❌ Mistake 3: Forgetting that 4xx/5xx do not raise by default
✅ Correct: call `resp.raise_for_status()` (or check `resp.status`)

```python
# Wrong — a 500 page is silently parsed or fails later
# data = await resp.json()
# Right
# resp.raise_for_status(); data = await resp.json()
```

---

## 🧠 Tricky Interview Question

```python
# What does this print? Is it concurrent?
import asyncio, aiohttp

async def get(s: aiohttp.ClientSession, u: str) -> int:
    async with s.get(u) as r:
        return r.status

async def main() -> None:
    async with aiohttp.ClientSession() as s:
        for u in ["http://x/1", "http://x/2", "http://x/3"]:
            print(await get(s, u))
```
Answer: It is NOT concurrent. `await` inside a plain `for` loop waits for each call to finish before starting the next, so three 200 ms calls take 600 ms. `async` does not mean parallel by itself. Use `await asyncio.gather(*(get(s, u) for u in urls))` (or `asyncio.TaskGroup`) to start all three together.

---

## ⚫ Interview Questions + Answers

Q1: Why use aiohttp instead of requests in async code?
A1: `requests` blocks the thread, which blocks the event loop and freezes all other coroutines. `aiohttp` awaits network I/O, so the loop keeps serving others.

Q2: What does `ClientSession` do?
A2: It holds a connection pool, cookies and default headers/timeouts. Reusing one session keeps TCP/TLS connections alive (keep-alive), which is much faster than a new connection per request.

Q3: How do you limit concurrency to avoid hammering a server?
A3: Use `asyncio.Semaphore(n)` around each request, or `aiohttp.TCPConnector(limit=n)` (default limit is 100 connections, `limit_per_host` default is unlimited).

Q4: aiohttp vs httpx?
A4: httpx has both sync and async APIs, HTTP/2 support and a `requests`-like API, plus easy testing with ASGI transports. aiohttp is async-only, also gives a server and WebSocket support, and is very mature and fast. For FastAPI projects httpx is common; for crawlers aiohttp is common.

Q5: How do you set a timeout?
A5: `ClientSession(timeout=ClientTimeout(total=10, connect=3))`, or per request with `timeout=`. Default total timeout is 5 minutes, which is too long for most APIs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Calling many external APIs concurrently
- Web scraping / crawling at scale
- You need an async HTTP client plus WebSocket support
- You want a lightweight async server without a big framework

❌ Avoid when:
- A simple script calls one URL once (use `requests` or `urllib`)
- You need HTTP/2 (use httpx)
- Your code is CPU-heavy (async does not speed up computation)

---

## 📊 Visual Diagram
```
Sequential (requests):  |--A--||--B--||--C--|        = 3 x 200ms = 600ms

Concurrent (aiohttp):   |--A--|
                        |--B--|                      = ~200ms
                        |--C--|

ClientSession
 ├── connection pool (keep-alive sockets)
 ├── cookies, default headers
 └── timeout settings
        │
   session.get() ──> ClientResponse ──> await .json()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ClientSession | Object holding connection pool | Connection pool रखने वाला object |
| Connector | Manages sockets and limits | Sockets और limits संभालने वाला |
| raise_for_status | Raise exception on 4xx/5xx | 4xx/5xx पर exception उठाना |
| gather | Run coroutines concurrently | Coroutines एक साथ चलाना |
| Keep-alive | Reuse the same TCP connection | उसी TCP connection को दोबारा इस्तेमाल करना |
| Semaphore | Limit how many run at once | एक साथ चलने वालों की सीमा |

---

## ⚡ 3-Line Summary
English: `aiohttp` is an async HTTP client and server. Use one shared `ClientSession`, wrap calls in `async with`, and use `gather` plus a semaphore for safe concurrency. It speeds up I/O-bound work only.
Hindi: `aiohttp` एक async HTTP client और server है। एक shared `ClientSession` रखें, calls को `async with` में लपेटें, और सुरक्षित concurrency के लिए `gather` के साथ semaphore लगाएं। यह सिर्फ I/O-bound काम को तेज करता है।

---

## ➡️ Next Topic
**248. asyncpg — Async PostgreSQL** — a fast async driver for PostgreSQL: connection pools, queries and transactions.
