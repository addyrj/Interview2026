---

# Q220. Stream large data with async generators
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Stream 1,000,000 bytes in 64 KB chunks without ever holding all of it in memory. Write an async generator `read_chunks` and consume it with `async for`.

```python
async for chunk in read_chunks(1_000_000, 64_000):
    process(chunk)
```

---

## 💡 Quick Concept (2 lines only)
An `async def` with `yield` is an async generator: it produces one item at a time and can `await` between items.
हिंदी: async def + yield = async generator; एक बार में एक chunk memory में, बाकी lazily आते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio                                    # asyncio library
from collections.abc import AsyncIterator         # type hint


async def read_chunks(total: int, size: int) -> AsyncIterator[bytes]:
    sent = 0                                      # bytes produced so far
    while sent < total:                           # until all data is streamed
        n = min(size, total - sent)               # last chunk may be smaller
        await asyncio.sleep(0)                    # simulated network read (yields to loop)
        yield b"x" * n                            # produce ONE chunk, then pause
        sent += n                                 # advance


async def main() -> None:
    size = 0                                      # running total
    chunks = 0                                    # chunk counter
    async for chunk in read_chunks(1_000_000, 64_000):  # pull chunks lazily
        size += len(chunk)                        # process chunk (only 64 KB in memory at once)
        chunks += 1                               # count it
    print(size, chunks)                           # 1000000 bytes in 16 chunks

    gen = read_chunks(10, 4)                      # manual iteration
    print(await anext(gen), await anext(gen))     # first two chunks (3.10+ anext)
    await gen.aclose()                            # stop early, run generator cleanup


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# 1000000 16
# b'xxxx' b'xxxx'
```

---

## 🔍 Why This Works (3 lines max)
The generator pauses at each `yield`, so memory stays at one chunk (64 KB) regardless of total size. Use `async for` (or `anext()`), and `aclose()` / `contextlib.aclosing` so cleanup in `finally` runs if you stop early.
हिंदी: हर yield पर generator रुकता है; जल्दी रुकना हो तो aclose()/aclosing से cleanup पक्का करो।

---

## ⚡ Alternative Solution
```python
import asyncio                                    # asyncio library
from collections.abc import AsyncIterator         # type hint
from contextlib import aclosing                   # guarantees aclose()


async def lines() -> AsyncIterator[str]:
    try:
        for i in range(1, 1_000_000):             # pretend this is a huge file/stream
            await asyncio.sleep(0)                # yield control
            yield f"line {i}"                     # one line at a time
    finally:
        print("source closed")                    # cleanup runs on early exit


async def only_even(src: AsyncIterator[str]) -> AsyncIterator[str]:
    async for line in src:                        # pipeline stage 1: filter
        if int(line.split()[1]) % 2 == 0:         # keep even-numbered lines
            yield line                            # pass downstream


async def main() -> None:
    async with aclosing(lines()) as src:          # close source even if we break
        async for line in only_even(src):         # pipeline stage 2: consume
            print(line)                           # line 2, 4, 6
            if line == "line 6":                  # enough data
                break                             # stop early
    print([x async for x in only_even(_take(5))]) # async comprehension on a small stream


async def _take(n: int) -> AsyncIterator[str]:
    for i in range(1, n + 1):                     # small finite stream
        yield f"line {i}"                         # emit lines 1..n


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# line 2
# line 4
# line 6
# source closed
# ['line 2', 'line 4']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: building the whole list first - defeats streaming (1 GB in RAM)
chunks = [c async for c in read_chunks(10**9, 64_000)]

# ❌ Wrong: plain `for` over an async generator -> TypeError: 'async_generator' object is not iterable
# ✅ Correct: async for + process each chunk immediately
```

---

## 🎯 Interview Tip (1 line)
Say: "Async generators stream with constant memory; mention aclosing() for cleanup and FastAPI StreamingResponse as the web use."

---

## 🔗 Related Questions
→ Q165 (generators) | Q234 (streaming response) | Q235 (SSE) | Q213 (polling)
