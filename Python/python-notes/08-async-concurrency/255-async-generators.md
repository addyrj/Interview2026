---

# 255. Async Generators
# हिंदी में: Async Generators (`async def` + `yield`)

---

## 🔵 Simple Definition (English)
An async generator is an `async def` function that uses `yield`. It produces values one at a time and can `await` between them. You read it with `async for`. It is perfect for streaming data that arrives slowly, like pages from an API or rows from a database.

## 🔵 सरल परिभाषा (Hindi)
Async generator ऐसा `async def` function है जिसमें `yield` होता है। यह values एक-एक करके बनाता है और बीच में `await` कर सकता है। इसे `async for` से पढ़ते हैं। धीरे-धीरे आने वाले data को stream करने के लिए यह एकदम सही है, जैसे API के pages या database की rows।

---

## 🔴 Problem it Solves
Without it you must load ALL results into a list first (`await fetch_all()`), which wastes memory and delays the first result. A normal generator cannot `await`. An async generator lets you yield each item as soon as it is ready while the event loop serves other tasks in between.

## 🔴 यह क्यों बना? (Hindi)
इसके बिना आपको पहले सारे results एक list में लोड करने पड़ते हैं (`await fetch_all()`), जिससे memory बर्बाद होती है और पहला result देर से मिलता है। सामान्य generator `await` नहीं कर सकता। Async generator हर item तैयार होते ही yield करने देता है, और बीच में event loop दूसरे tasks चलाता रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write "async def f(): ... yield x ..."  (note: no return value with yield)
Step 2 → Calling f() does NOT run any code; it returns an async_generator object
Step 3 → "async for v in f():" calls __anext__() each loop turn
Step 4 → The function runs until the next yield, then pauses and hands you v
Step 5 → Between yields the function may await (sleep, network, DB)
Step 6 → When the function ends, StopAsyncIteration stops the loop
Step 7 → await agen.aclose() stops early and runs the finally block
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → "async def f(): ... yield x ..." लिखो  (yield के साथ return value नहीं)
Step 2 → f() बुलाने पर code नहीं चलता; async_generator object मिलता है
Step 3 → "async for v in f():" हर चक्कर में __anext__() बुलाता है
Step 4 → Function अगले yield तक चलती है, रुकती है और v देती है
Step 5 → Yields के बीच function await कर सकती है (sleep, network, DB)
Step 6 → Function खत्म होने पर StopAsyncIteration से loop रुकता है
Step 7 → await agen.aclose() जल्दी रोकता है और finally block चलाता है
```

---

## 🟡 Real World Example
An LLM chat backend streams tokens: the model returns tokens one by one, and the async generator yields each token to the client (Server-Sent Events). A reporting endpoint exports 5 million orders as CSV: an async generator reads 1000 rows at a time from the DB and yields lines, so memory stays small. A scraper yields each page as it is downloaded instead of waiting for all pages.

## 🟡 Real Example Hindi mein
LLM chat backend tokens stream करता है: model tokens एक-एक करके देता है और async generator हर token client को yield करता है (Server-Sent Events)। Reporting endpoint 50 लाख orders CSV में export करता है: async generator DB से 1000 rows एक बार में पढ़कर lines yield करता है, इसलिए memory कम रहती है। Scraper सारे pages के download का इंतजार किए बिना हर page तैयार होते ही yield करता है।

---

## 💻 Code Example — Basic
```python
# Basic async generators (verified on Python 3.13)
import asyncio                                           # event loop
from collections.abc import AsyncIterator, AsyncGenerator   # type hints


async def ticker(n: int) -> AsyncIterator[int]:          # async generator: async def + yield
    for i in range(n):                                   # count up
        await asyncio.sleep(0.01)                        # await is allowed between yields
        yield i                                          # hand one value to the caller


async def pages(total: int, size: int) -> AsyncGenerator[list[int], None]:
    try:
        for s in range(0, total, size):                  # step through in chunks
            await asyncio.sleep(0)                       # let other tasks run
            yield list(range(s, min(s + size, total)))   # yield one chunk (page)
    finally:
        print("generator cleanup")                       # runs on finish OR aclose()


async def main() -> None:
    async for x in ticker(3):                            # consume with async for
        print(x)                                         # 0, 1, 2
    print([x async for x in ticker(4) if x % 2 == 0])    # async comprehension with filter
    async for p in pages(7, 3):                          # page by page
        print(p)                                         # [0,1,2] [3,4,5] [6]
    g = pages(10, 5)                                     # create, nothing runs yet
    print(await anext(g))                                # 3.10+: get just the first page
    await g.aclose()                                     # stop early -> finally runs


asyncio.run(main())                                      # run

# Output:
# 0
# 1
# 2
# [0, 2]
# [0, 1, 2]
# [3, 4, 5]
# [6]
# generator cleanup
# [0, 1, 2, 3, 4]
# generator cleanup
```

## 💻 Code Example — Advanced
```python
# Production style: paginated "API" streamed lazily, with a limit and safe cleanup
import asyncio                                           # event loop
from collections.abc import AsyncIterator                # type hints
from typing import Any                                   # any JSON-like dict

FAKE_DB: list[dict[str, Any]] = [{"id": i, "amount": i * 10} for i in range(1, 8)]   # 7 rows


async def fetch_page(offset: int, limit: int) -> list[dict[str, Any]]:
    await asyncio.sleep(0.01)                            # pretend network call
    return FAKE_DB[offset: offset + limit]               # one page of rows


async def stream_orders(page_size: int = 3) -> AsyncIterator[dict[str, Any]]:
    offset: int = 0                                      # where the next page starts
    try:
        while True:                                      # keep paging
            rows = await fetch_page(offset, page_size)   # fetch ONE page only
            if not rows:                                 # empty page = no more data
                return                                   # ends the generator
            for row in rows:                             # yield rows one by one
                yield row                                # consumer gets it immediately
            offset += page_size                          # move to the next page
    finally:
        print("stream closed")                           # always runs (even on break)


async def total_amount(limit: int | None = None) -> int:
    total: int = 0                                       # running sum
    async for row in stream_orders():                    # lazy iteration, tiny memory
        total += row["amount"]                           # use each row
        if limit is not None and row["id"] >= limit:     # stop early if asked
            break                                        # leaves the loop (see tricky section!)
    return total                                         # final sum


async def main() -> None:
    print(await total_amount())                          # sum of all 7 rows = 280
    print(await total_amount(limit=2))                   # first two rows = 30
    first = [r async for r in stream_orders()]           # collect all as a list
    print(len(first), first[0])                          # 7 rows, first row


asyncio.run(main())                                      # run

# Output (verified). Note the break case: "stream closed" for the limit=2 run
# is printed LATE (after "30"), because cleanup after break is deferred:
# stream closed
# 280
# 30
# stream closed
# stream closed
# 7 {'id': 1, 'amount': 10}
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Async generator | `async def` + `yield` | `async function*` |
| Consume | `async for x in gen()` | `for await (const x of gen())` |
| Early stop | `aclose()` / `break` | `return()` / `break` |
| Next value manually | `await anext(g)` | `await g.next()` |
| Result of `next` | the value | `{ value, done }` object |

```python
# Python way
async def count(n: int):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async for i in count(3):
    print(i)
```
```javascript
// JavaScript way
async function* count(n) {
  for (let i = 0; i < n; i++) {
    await new Promise(r => setTimeout(r, 100));
    yield i;
  }
}
for await (const i of count(3)) console.log(i);
```

Key difference: almost one-to-one. JS needs `for await` while Python uses `async for`. In Python an `async def` with `yield` cannot `return value` (only a bare `return`), and `anext(g)` returns the value directly instead of `{value, done}`; the end is signalled by `StopAsyncIteration`.

---

## 🟠 FastAPI Connection
`StreamingResponse` accepts an async generator, so you can stream big files, CSV exports, or LLM tokens without holding everything in memory.

```python
# FastAPI example — streaming with an async generator
import asyncio                                           # sleep
from collections.abc import AsyncIterator                # type
from fastapi import FastAPI                              # FastAPI
from fastapi.responses import StreamingResponse          # streaming reply

app: FastAPI = FastAPI()                                 # app


async def token_stream(prompt: str) -> AsyncIterator[str]:
    for word in f"Answer to {prompt}".split():           # pretend the LLM emits words
        await asyncio.sleep(0.05)                        # model latency
        yield word + " "                                 # send one token


@app.get("/chat")                                        # GET /chat?q=hello
async def chat(q: str) -> StreamingResponse:
    return StreamingResponse(token_stream(q), media_type="text/plain")   # sent chunk by chunk
```
(Pattern; the generator logic was run, the HTTP endpoint was not called here.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using normal `for` on an async generator
✅ Correct: use `async for`

```python
# Wrong
for x in ticker(2):        # TypeError: 'async_generator' object is not iterable
    ...
# Right
async for x in ticker(2):
    ...
```

❌ Mistake 2: Trying to `await` the generator object (or `return` a value)
✅ Correct: iterate it, or `await anext(g)` for one item

```python
# Wrong
g = gen()
await g                     # TypeError: object async_generator can't be used in 'await' expression
# Right
first = await anext(g)
```

❌ Mistake 3: Breaking out early without closing the generator
✅ Correct: wrap in `contextlib.aclosing()` so cleanup runs immediately

```python
from contextlib import aclosing

# Wrong — finally block runs "later" (when garbage collected / loop shuts down)
async for x in stream_orders():
    break
# Right — cleanup runs right at the end of the with-block
async with aclosing(stream_orders()) as s:
    async for x in s:
        break
```

---

## 🧠 Tricky Interview Question

```python
# What is printed?
import asyncio

async def gen():
    yield 1
    yield 2

async def main() -> None:
    g = gen()
    print(type(g).__name__)
    print(await anext(g), await anext(g))
    try:
        await anext(g)
    except StopAsyncIteration:
        print("exhausted")
    g2 = gen()
    print([x async for x in g2], [x async for x in g2])

asyncio.run(main())
```
Answer: `async_generator`, then `1 2`, then `exhausted`, then `[1, 2] []`. Calling `gen()` returns an async generator object (no code runs yet). `anext` pulls one value at a time; after the last `yield` the next call raises `StopAsyncIteration`. An async generator is a one-shot iterator: the second comprehension over the same `g2` gets an empty list because it is already exhausted. Create a new generator by calling `gen()` again.

---

## ⚫ Interview Questions + Answers

Q1: What makes a function an async generator?
A1: It is defined with `async def` and contains `yield`. Calling it returns an `async_generator` object (without running the body).

Q2: Async generator vs returning a list from a coroutine?
A2: A list requires all items to be ready first (memory heavy, slow first byte). An async generator yields lazily, so memory is constant and the consumer starts working at once.

Q3: How do `asend`, `athrow` and `aclose` work?
A3: They mirror generator `send/throw/close`: `asend(v)` resumes the generator and the `yield` expression evaluates to `v`; `athrow(exc)` raises inside; `aclose()` raises `GeneratorExit` at the paused `yield` so `finally` blocks run.

Q4: Why use `contextlib.aclosing`?
A4: When you `break` out of `async for`, the generator is not closed immediately; cleanup is deferred to the event loop's asyncgen hooks. `aclosing` guarantees deterministic cleanup.

Q5: Can an async generator be used with `asyncio.gather`?
A5: Not directly, since it is not awaitable. Wrap consumption in a coroutine (e.g. `async def collect(g): return [x async for x in g]`) and gather those.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Streaming responses (LLM tokens, CSV exports, SSE)
- Paginated APIs / DB cursors with large result sets
- Event feeds, polling loops, websockets

❌ Avoid when:
- You need all results at once anyway (return a list)
- The work is purely CPU (a normal generator is enough)
- You need random access or length (use a list)

---

## 📊 Visual Diagram
```
caller:  async for row in stream():          generator body
            │ __anext__() ───────────────►   runs until yield
            │ ◄──────── row 1 ────────────   pauses here
         (process row 1)
            │ __anext__() ───────────────►   resumes after yield
            │                                await fetch(...)   <- loop serves other tasks
            │ ◄──────── row 2 ────────────
            │ __anext__() ───────────────►   function ends
            │ ◄── StopAsyncIteration ─────   loop stops

break / aclose()  ->  GeneratorExit at the yield  ->  finally runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Async generator | `async def` containing `yield` | `yield` वाला `async def` |
| `async for` | Loop over async iterable | Async iterable पर loop |
| `anext()` | Get next item (3.10+) | अगला item लेना |
| `aclose()` | Stop generator early | Generator को जल्दी बंद करना |
| StopAsyncIteration | Signal: no more items | "और items नहीं" का संकेत |
| Streaming | Send data piece by piece | Data टुकड़ों में भेजना |

---

## ⚡ 3-Line Summary
English: An async generator (`async def` + `yield`) produces values lazily and can await between them. Consume it with `async for`, close it with `aclose()` or `aclosing()`, and remember it can be used only once.
Hindi: Async generator (`async def` + `yield`) values lazily बनाता है और बीच में await कर सकता है। इसे `async for` से पढ़ें, `aclose()` या `aclosing()` से बंद करें, और याद रखें कि यह सिर्फ एक बार इस्तेमाल होता है।

---

## ➡️ Next Topic
**256. Async Iterators** — the class-based protocol (`__aiter__` and `__anext__`) behind `async for`.
