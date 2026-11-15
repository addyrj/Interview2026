---

# 253. uvloop — Fast Event Loop
# हिंदी में: uvloop — तेज़ Event Loop

---

## 🔵 Simple Definition (English)
`uvloop` is a drop-in replacement for the default `asyncio` event loop. It is written in Cython on top of `libuv` (the same C library that powers Node.js), so network-heavy async programs usually run noticeably faster, often 2x or more on socket-heavy workloads. Your `async`/`await` code does not change.

## 🔵 सरल परिभाषा (Hindi)
`uvloop` default `asyncio` event loop का drop-in replacement है। यह Cython में `libuv` (वही C library जो Node.js चलाती है) के ऊपर लिखा गया है, इसलिए network-heavy async programs आमतौर पर काफी तेज़ चलते हैं, socket-heavy काम में अक्सर 2 गुना या ज़्यादा। आपका `async`/`await` code बदलता नहीं।

---

## 🔴 Problem it Solves
The default asyncio loop is written in pure Python, so every socket event, callback and timer pays the Python interpreter cost. At thousands of requests per second the loop itself becomes the bottleneck. `uvloop` moves that hot path into compiled C code without forcing you to rewrite your application.

## 🔴 यह क्यों बना? (Hindi)
Default asyncio loop pure Python में लिखा है, इसलिए हर socket event, callback और timer पर Python interpreter की cost लगती है। हज़ारों requests प्रति second पर loop खुद bottleneck बन जाता है। `uvloop` उस hot path को compiled C code में ले जाता है और आपको application दोबारा लिखनी नहीं पड़ती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install uvloop   (Linux and macOS only; no Windows support)
Step 2 → Python's asyncio lets you swap the event loop implementation (loop policy / factory)
Step 3 → uvloop provides its own Loop class built on libuv's C event loop
Step 4 → You start your app with uvloop.run(main())  (or loop_factory=uvloop.new_event_loop)
Step 5 → All asyncio APIs (sleep, gather, streams, create_task) now run on libuv
Step 6 → Uvicorn does this for you: it auto-uses uvloop when installed (--loop auto)

Old way (deprecated in 3.14):  asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
Modern way:  uvloop.run(main())  or  asyncio.run(main(), loop_factory=uvloop.new_event_loop)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install uvloop   (सिर्फ Linux और macOS; Windows support नहीं)
Step 2 → asyncio में event loop implementation बदली जा सकती है (loop policy / factory)
Step 3 → uvloop अपनी Loop class देता है जो libuv के C event loop पर बनी है
Step 4 → App को uvloop.run(main()) से शुरू करो (या loop_factory=uvloop.new_event_loop)
Step 5 → सभी asyncio APIs (sleep, gather, streams, create_task) अब libuv पर चलते हैं
Step 6 → Uvicorn यह खुद कर देता है: uvloop installed हो तो अपने आप use करता है (--loop auto)

पुराना तरीका (3.14 में deprecated):  asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
नया तरीका:  uvloop.run(main())  या  asyncio.run(main(), loop_factory=uvloop.new_event_loop)
```

---

## 🟡 Real World Example
A Razorpay-style webhook receiver gets 5,000 callbacks per second from banks. Each handler only parses JSON and writes to Redis, so the work is tiny and the cost is dominated by socket handling. Running Uvicorn with uvloop (and httptools) reduces CPU use per request, so the same server handles more traffic. Teams usually see the gain just by adding `uvicorn[standard]` to requirements.

## 🟡 Real Example Hindi mein
Razorpay जैसा webhook receiver banks से 5,000 callbacks प्रति second लेता है। हर handler सिर्फ JSON parse करके Redis में लिखता है, इसलिए काम छोटा है और cost ज़्यादातर socket handling की है। Uvicorn को uvloop (और httptools) के साथ चलाने से हर request पर CPU कम लगता है और वही server ज़्यादा traffic संभालता है। Teams को अक्सर सिर्फ `uvicorn[standard]` requirements में जोड़ने से फायदा मिल जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: run the same coroutine on the default loop and on uvloop
import asyncio                                   # standard library event loop
import sys                                       # to check the platform
import uvloop                                    # pip install uvloop (Linux/macOS)


async def main() -> str:                         # an ordinary coroutine, nothing special
    await asyncio.sleep(0.01)                    # pretend to wait for I/O
    loop = asyncio.get_running_loop()            # ask who is running us
    return type(loop).__module__ + "." + type(loop).__name__   # name of the loop class


print("platform :", sys.platform)                # uvloop works on darwin and linux
print("default  :", asyncio.run(main()))         # standard asyncio loop
print("uvloop   :", uvloop.run(main()))          # uvloop.run (uvloop 0.18+)
print("factory  :", asyncio.run(main(), loop_factory=uvloop.new_event_loop))   # Python 3.12+ way

# Output:
# platform : darwin
# default  : asyncio.unix_events._UnixSelectorEventLoop
# uvloop   : uvloop.Loop
# factory  : uvloop.Loop
```

## 💻 Code Example — Advanced
```python
# Production style: use uvloop when available, fall back safely, and measure
import asyncio                                   # event loop
import sys                                       # platform check
import time                                      # timing
from collections.abc import Callable, Coroutine  # type hints
from typing import Any                           # type hints


def pick_runner() -> Callable[[Coroutine[Any, Any, Any]], Any]:
    """Return uvloop.run if usable, else plain asyncio.run."""
    if sys.platform == "win32":                  # uvloop does not support Windows
        return asyncio.run                       # safe fallback
    try:                                         # uvloop is an optional dependency
        import uvloop                            # may raise ImportError
    except ImportError:                          # not installed
        return asyncio.run                       # fallback again
    return uvloop.run                            # fast path


async def echo_roundtrips(n: int) -> int:
    """Open a local TCP echo server and do n round trips (socket-heavy work)."""
    async def handle(r: asyncio.StreamReader, w: asyncio.StreamWriter) -> None:
        while data := await r.readline():        # read until the client closes
            w.write(data)                        # echo the line back
            await w.drain()                      # apply back-pressure
        w.close()                                # close this connection

    server = await asyncio.start_server(handle, "127.0.0.1", 0)   # port 0 = any free port
    port: int = server.sockets[0].getsockname()[1]               # which port we got
    reader, writer = await asyncio.open_connection("127.0.0.1", port)   # client side
    ok: int = 0                                  # successful round trips
    for i in range(n):                           # send n messages
        writer.write(f"msg{i}\n".encode())       # request
        await writer.drain()                     # flush
        if await reader.readline() == f"msg{i}\n".encode():   # reply must match
            ok += 1                              # count success
    writer.close()                               # close client
    server.close()                               # stop server
    await server.wait_closed()                   # wait until it is down
    return ok                                    # number of good replies


def timed(runner: Callable[..., Any], n: int) -> tuple[int, float]:
    start: float = time.perf_counter()           # start the timer
    ok: int = runner(echo_roundtrips(n))         # run on the chosen loop
    return ok, time.perf_counter() - start       # result and seconds


ok_std, t_std = timed(asyncio.run, 2000)         # default loop
ok_fast, t_fast = timed(pick_runner(), 2000)     # uvloop (or fallback)
print("correct replies:", ok_std, ok_fast)       # both must be 2000
print("uvloop faster than default?", t_fast < t_std)   # speed varies by machine, usually True

# Output:
# correct replies: 2000 2000
# uvloop faster than default? True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Default event loop | pure-Python `asyncio` loop | libuv inside Node.js (always) |
| Faster loop | `uvloop` (also libuv) | n/a, already libuv |
| Choose loop | `uvloop.run(main())` | cannot choose |
| Windows | not supported by uvloop | supported |

```python
# Python way — swap the loop, keep the code
import uvloop                                   # libuv-based loop
async def main() -> None:
    print("hello from uvloop")                  # same async code
uvloop.run(main())                              # 1 line change
```
```javascript
// JavaScript way — Node.js already runs on libuv, nothing to swap
async function main() {
  console.log("hello from libuv");              // same async code
}
main();                                         // event loop is built in
```

Key difference: Node.js has libuv built in. In Python, uvloop gives you roughly the same engine, but you must opt in.

---

## 🟠 FastAPI Connection
You almost never call uvloop yourself with FastAPI. Uvicorn picks it automatically: `pip install "uvicorn[standard]"` installs uvloop and httptools, and `uvicorn main:app` uses them (`--loop auto`). You can force it with `--loop uvloop`. Below we start Uvicorn programmatically and check which loop it ran.

```python
# FastAPI example — verify the loop type Uvicorn picked (TestClient uses anyio, so we use uvicorn.Server)
import asyncio                                   # loop control
import httpx                                     # async HTTP client
import uvicorn                                   # ASGI server
from fastapi import FastAPI                      # framework

app: FastAPI = FastAPI()                         # create app


@app.get("/loop")                                # endpoint that reveals the loop
async def loop_name() -> dict[str, str]:
    return {"loop": type(asyncio.get_running_loop()).__module__}   # module of the loop class


async def run_and_call() -> str:
    config = uvicorn.Config(app, host="127.0.0.1", port=34253, log_level="error", loop="uvloop")   # force uvloop
    server = uvicorn.Server(config)              # build the server
    task = asyncio.create_task(server.serve())   # run it in the background
    while not server.started:                    # wait until it is listening
        await asyncio.sleep(0.05)                # small poll
    async with httpx.AsyncClient() as client:    # call our own endpoint
        r = await client.get("http://127.0.0.1:34253/loop")   # GET /loop
    server.should_exit = True                    # ask server to stop
    await task                                   # wait for shutdown
    return r.json()["loop"]                      # which loop did it use?


import uvloop                                    # run our driver on uvloop too
print(uvloop.run(run_and_call()))                # prints the loop module name

# Output:
# uvloop
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the deprecated policy API on new Python
✅ Correct: use `uvloop.run()` or `loop_factory`

```python
import asyncio, uvloop
# Wrong — set_event_loop_policy is deprecated starting Python 3.14 and removed later
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# Right
# uvloop.run(main())
```

❌ Mistake 2: Installing uvloop on Windows
✅ Correct: guard with `sys.platform` and fall back to `asyncio.run`

❌ Mistake 3: Expecting uvloop to speed up blocking or CPU-bound code
✅ Correct: uvloop only speeds up the loop machinery (sockets, callbacks); a slow database query or heavy math stays just as slow

```python
import time
# Wrong — blocking call; uvloop cannot help, it still freezes the loop
async def handler() -> None:
    time.sleep(1)
# Right — await a real async operation
```

---

## 🧠 Tricky Interview Question

```python
# Does this change behaviour when uvloop is enabled? What does it print?
import asyncio, uvloop

async def main() -> None:
    results = await asyncio.gather(*(asyncio.sleep(0.01, i) for i in range(3)))
    print(results)

uvloop.run(main())
asyncio.run(main())

# Output:
# [0, 1, 2]
# [0, 1, 2]
```
Answer: Both print `[0, 1, 2]`. uvloop implements the same asyncio API contract, so program behaviour (ordering of `gather` results, cancellation, exceptions) is identical. Only speed and low-level details change. Code that touches loop internals (private attributes, `loop._selector`) or relies on `ProactorEventLoop` features can break.

---

## ⚫ Interview Questions + Answers

Q1: What is uvloop?
A1: A fast drop-in event loop for asyncio built on libuv and Cython. It implements the `asyncio.AbstractEventLoop` interface, so existing code runs unchanged.

Q2: How much faster is it?
A2: Its authors reported about 2 to 4 times faster than the default loop on echo-server benchmarks. Real apps see less because DB and business logic dominate. Always benchmark your own workload.

Q3: How do you enable it with Uvicorn / FastAPI?
A3: Install `uvicorn[standard]` (it brings uvloop) and run `uvicorn main:app`. Or pass `--loop uvloop` explicitly. Gunicorn deployments use `-k uvicorn.workers.UvicornWorker` (or the `uvicorn-worker` package in newer setups).

Q4: Which platforms support uvloop?
A4: Linux and macOS. It does not support Windows, so developers on Windows use the default loop locally.

Q5: Why is `set_event_loop_policy` discouraged now?
A5: Python 3.14 deprecates the event-loop policy system; `asyncio.run(..., loop_factory=...)` (3.12+) and `uvloop.run()` are the supported, explicit ways.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running production ASGI servers (Uvicorn) on Linux
- Socket-heavy services: proxies, chat, webhooks, WebSockets
- You want a free speedup with one dependency

❌ Avoid when:
- Developing or deploying on Windows
- You depend on loop internals or the `ProactorEventLoop` (subprocess pipes on Windows)
- Your bottleneck is the database or CPU work, not the loop

---

## 📊 Visual Diagram
```
Your code:   async def handler(): await db.fetch(...)       (unchanged)
                          |
                   asyncio API (sleep, gather, streams)
                          |
          +---------------+-----------------+
          |                                 |
  default loop                          uvloop
  (pure Python,                         (Cython + libuv,
   selectors module)                     compiled C)
          |                                 |
          +---------------+-----------------+
                          |
                    OS: epoll / kqueue
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop | Runs coroutines and I/O callbacks | coroutines चलाने वाला loop |
| libuv | C library for async I/O (used by Node.js) | async I/O की C library |
| Cython | Python-like language compiled to C | C में compile होने वाली Python जैसी भाषा |
| Drop-in | Replace without changing other code | बिना बदलाव के बदलना |
| Loop factory | Function that creates the loop | loop बनाने वाला function |
| epoll / kqueue | OS mechanisms to watch many sockets | कई sockets देखने के OS तरीके |

---

## ⚡ 3-Line Summary
English: uvloop replaces the asyncio event loop with a libuv-based one for better speed, with no code changes. Use `uvloop.run()` or let Uvicorn pick it up. It helps socket-heavy work only and is not available on Windows.
Hindi: uvloop asyncio event loop को libuv-आधारित loop से बदलता है, बेहतर speed के लिए और code बदले बिना। `uvloop.run()` use करें या Uvicorn को खुद चुनने दें। यह सिर्फ socket-heavy काम में मदद करता है और Windows पर उपलब्ध नहीं।

---

## ➡️ Next Topic
**254. Async Context Managers** — `async with` and `__aenter__` / `__aexit__`: safely open and close async resources like DB connections and HTTP sessions.
