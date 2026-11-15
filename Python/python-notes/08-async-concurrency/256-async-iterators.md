---

# 256. Async Iterators
# हिंदी में: Async Iterators (`__aiter__` और `__anext__`)

---

## 🔵 Simple Definition (English)
An async iterator is an object that can be used in `async for`. It has two methods: `__aiter__()` returns the iterator, and `async def __anext__()` returns the next value (or raises `StopAsyncIteration`). It is the class-based version of an async generator, used when you need to keep state or resources.

## 🔵 सरल परिभाषा (Hindi)
Async iterator ऐसा object है जिसे `async for` में इस्तेमाल किया जा सकता है। इसके दो methods होते हैं: `__aiter__()` iterator लौटाता है, और `async def __anext__()` अगली value देता है (या `StopAsyncIteration` उठाता है)। यह async generator का class वाला रूप है, जब आपको state या resources संभालने हों।

---

## 🔴 Problem it Solves
Sometimes an async generator is not enough: you want an object with its own attributes (cursor id, connection, retry counter), extra methods (`close()`, `stats()`), or you are writing a library class like a database cursor. Normal iterators cannot `await` inside `__next__`. The async iterator protocol allows `await` inside `__anext__`.

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी async generator काफी नहीं होता: आपको ऐसा object चाहिए जिसके अपने attributes हों (cursor id, connection, retry counter), अतिरिक्त methods हों (`close()`, `stats()`), या आप database cursor जैसी library class लिख रहे हों। सामान्य iterators `__next__` में `await` नहीं कर सकते। Async iterator protocol `__anext__` में `await` की अनुमति देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → "async for x in obj:" calls obj.__aiter__()   (a normal, NOT async, method)
Step 2 → __aiter__ returns an object with __anext__ (often self)
Step 3 → Each loop turn does:  x = await iterator.__anext__()
Step 4 → __anext__ may await (network, DB, sleep) before returning a value
Step 5 → When there is nothing left, __anext__ raises StopAsyncIteration
Step 6 → The loop catches it and ends quietly
Step 7 → Builtins: aiter(obj) and anext(it[, default])  (Python 3.10+)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → "async for x in obj:" obj.__aiter__() बुलाता है   (सामान्य method, async नहीं)
Step 2 → __aiter__ ऐसा object लौटाता है जिसमें __anext__ हो (अक्सर self)
Step 3 → हर चक्कर में:  x = await iterator.__anext__()
Step 4 → __anext__ value लौटाने से पहले await कर सकता है (network, DB, sleep)
Step 5 → कुछ बचा न हो तो __anext__ StopAsyncIteration उठाता है
Step 6 → Loop उसे पकड़कर चुपचाप खत्म हो जाता है
Step 7 → Builtins: aiter(obj) और anext(it[, default])  (Python 3.10+)
```

---

## 🟡 Real World Example
A database client library (like `asyncpg` or `motor`) returns a cursor object. You write `async for row in cursor`, and under the hood the cursor class fetches the next batch of 100 rows over the network when its buffer is empty. A Kafka or Redis-stream consumer is also an async iterator: each `__anext__` waits for the next message. A paginated Razorpay-style API wrapper exposes `async for payment in client.payments()` and hides the page logic.

## 🟡 Real Example Hindi mein
Database client library (जैसे `asyncpg` या `motor`) cursor object लौटाती है। आप `async for row in cursor` लिखते हैं, और अंदर cursor class buffer खाली होने पर network से अगली 100 rows लाती है। Kafka या Redis-stream consumer भी async iterator है: हर `__anext__` अगले message का इंतजार करता है। Razorpay जैसे paginated API का wrapper `async for payment in client.payments()` देता है और page का logic छिपा लेता है।

---

## 💻 Code Example — Basic
```python
# Basic async iterators (verified on Python 3.13)
import asyncio                                           # event loop


class Countdown:
    """Async iterator that counts down from n to 1."""

    def __init__(self, n: int) -> None:
        self.n: int = n                                  # current number (state)

    def __aiter__(self) -> "Countdown":                  # plain def, returns the iterator
        return self                                      # the object is its own iterator

    async def __anext__(self) -> int:                    # async def: may await
        if self.n <= 0:                                  # nothing left
            raise StopAsyncIteration                     # tells async for to stop
        await asyncio.sleep(0.01)                        # pretend to wait for data
        self.n -= 1                                      # move the state
        return self.n + 1                                # give back the old value


async def main() -> None:
    async for n in Countdown(3):                         # use it like any iterable
        print(n)                                         # 3, 2, 1
    it: Countdown = Countdown(2)                         # drive it by hand
    print(await anext(it), await anext(it))              # 2 1
    try:
        await anext(it)                                  # one too many
    except StopAsyncIteration:                           # the "end" signal
        print("done")                                    # we reached the end
    print(await anext(Countdown(0), "default"))          # anext() with a default value
    print([x async for x in Countdown(3)])               # async list comprehension


asyncio.run(main())                                      # run

# Output:
# 3
# 2
# 1
# 2 1
# done
# default
# [3, 2, 1]
```

## 💻 Code Example — Advanced
```python
# Production style: a paged reader with state, close() and an async context manager
import asyncio                                           # event loop
from types import TracebackType                          # for __aexit__ typing


class Paged:
    """Reads `total` items in chunks of `size`; fetches lazily."""

    def __init__(self, total: int, size: int) -> None:
        self.total: int = total                          # how many items exist
        self.size: int = size                            # chunk size
        self.pos: int = 0                                # where we are
        self.closed: bool = False                        # lifecycle flag

    def __aiter__(self) -> "Paged":                      # iterator is the object itself
        return self                                      # (single pass)

    async def __anext__(self) -> list[int]:
        if self.closed or self.pos >= self.total:        # finished or closed
            raise StopAsyncIteration                     # end of data
        await asyncio.sleep(0)                           # a real class would do I/O here
        end: int = min(self.pos + self.size, self.total) # end of this chunk
        chunk: list[int] = list(range(self.pos, end))    # build the chunk
        self.pos = end                                   # advance
        return chunk                                     # one page

    async def aclose(self) -> None:                      # extra method generators do not have
        self.closed = True                               # release resources here
        print("closed at", self.pos)                     # show where we stopped

    async def __aenter__(self) -> "Paged":               # also usable with async with
        return self                                      # nothing to open

    async def __aexit__(self, et: type[BaseException] | None,
                        ev: BaseException | None, tb: TracebackType | None) -> None:
        await self.aclose()                              # guaranteed cleanup


async def main() -> None:
    async for c in Paged(5, 2):                          # plain use
        print(c)                                         # [0, 1] [2, 3] [4]
    async with Paged(10, 3) as p:                        # with cleanup
        async for c in p:                                # read until we have enough
            print("got", c)                              # first chunk
            break                                        # stop early
    print(await asyncio.gather(*[anext(Paged(3, 3)) for _ in range(2)]))   # independent iterators


asyncio.run(main())                                      # run

# Output:
# [0, 1]
# [2, 3]
# [4]
# got [0, 1, 2]
# closed at 3
# [[0, 1, 2], [0, 1, 2]]
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Protocol methods | `__aiter__`, `__anext__` | `[Symbol.asyncIterator]()`, `next()` |
| End signal | raise `StopAsyncIteration` | return `{ done: true }` |
| Loop | `async for` | `for await ... of` |
| Next value | returns the value | returns `Promise<{ value, done }>` |
| `__aiter__` async? | NO (plain def) | n/a |

```python
# Python way
class Count:
    def __init__(self, n): self.i, self.n = 0, n
    def __aiter__(self): return self
    async def __anext__(self):
        if self.i >= self.n: raise StopAsyncIteration
        self.i += 1
        return self.i
```
```javascript
// JavaScript way
class Count {
  constructor(n) { this.i = 0; this.n = n; }
  [Symbol.asyncIterator]() { return this; }
  async next() {
    return this.i >= this.n ? { done: true } : { value: ++this.i, done: false };
  }
}
for await (const x of new Count(3)) console.log(x);
```

Key difference: JavaScript signals the end with `{ done: true }`, Python with an exception (`StopAsyncIteration`). Also, Python requires `__aiter__` to be a regular method; in JS the protocol method returns an object directly.

---

## 🟠 FastAPI Connection
Database cursors, Redis streams and WebSocket receivers are all async iterators. FastAPI's WebSocket even has `iter_text()`, an async generator built on this idea. You can also wrap your own class as the source for `StreamingResponse`.

```python
# FastAPI example — a class-based async iterator streamed to the client
import asyncio                                           # sleep
from fastapi import FastAPI                              # FastAPI
from fastapi.responses import StreamingResponse          # streaming reply

app: FastAPI = FastAPI()                                 # app


class Ticks:
    def __init__(self, n: int) -> None:
        self.n, self.i = n, 0                            # total and current

    def __aiter__(self) -> "Ticks":
        return self                                      # single-pass iterator

    async def __anext__(self) -> str:
        if self.i >= self.n:                             # done
            raise StopAsyncIteration                     # end the stream
        self.i += 1                                      # next tick
        await asyncio.sleep(0.1)                         # wait for "data"
        return f"tick {self.i}\n"                        # one chunk


@app.get("/ticks/{n}")                                   # GET /ticks/3
async def ticks(n: int) -> StreamingResponse:
    return StreamingResponse(Ticks(n), media_type="text/plain")   # any async iterable works
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Making `__aiter__` an `async def`
✅ Correct: `__aiter__` must be a plain `def` returning the iterator

```python
# Wrong
class Bad:
    async def __aiter__(self): return self
# async for -> TypeError: 'async for' received an object from __aiter__
#              that does not implement __anext__: coroutine
# Right
class Good:
    def __aiter__(self): return self
```

❌ Mistake 2: Raising `StopIteration` instead of `StopAsyncIteration`
✅ Correct: raise `StopAsyncIteration` to end

```python
# Wrong — RuntimeError: coroutine raised StopIteration
async def __anext__(self): raise StopIteration
# Right
async def __anext__(self): raise StopAsyncIteration
```

❌ Mistake 3: Returning `self` from `__aiter__` and expecting to loop twice
✅ Correct: return a NEW iterator object from `__aiter__` if the data must be re-readable

```python
# Wrong — the second loop sees nothing (state already consumed)
c = Countdown(2)
[x async for x in c]; [x async for x in c]      # second list is []
# Right
class Reusable:
    def __init__(self, n): self.n = n
    def __aiter__(self): return Countdown(self.n)   # fresh iterator each loop
```

---

## 🧠 Tricky Interview Question

```python
# What happens?
import asyncio

class Bad:
    async def __aiter__(self):
        return self
    async def __anext__(self):
        raise StopAsyncIteration

async def main() -> None:
    async for _ in Bad():
        pass

asyncio.run(main())
```
Answer: `TypeError: 'async for' received an object from __aiter__ that does not implement __anext__: coroutine` (plus a RuntimeWarning "coroutine 'Bad.__aiter__' was never awaited"). Because `__aiter__` was declared `async def`, calling it returns a coroutine object, not the iterator. Since Python 3.7 `__aiter__` must be a normal function; only `__anext__` is async. Fix by removing `async` from `__aiter__`.

---

## ⚫ Interview Questions + Answers

Q1: Async iterable vs async iterator?
A1: An async iterable has `__aiter__`. An async iterator has both `__aiter__` and `__anext__` (and `__aiter__` returns self). `async for` needs an iterable; it calls `__aiter__` to get the iterator.

Q2: Async generator vs class-based async iterator?
A2: A generator is shorter and handles state automatically. A class is better when you need extra methods, public attributes, restart logic or async context-manager support. Both work with `async for`.

Q3: What do `aiter()` and `anext()` do?
A3: `aiter(x)` = `x.__aiter__()`; `anext(it)` = `await it.__anext__()`; `anext(it, default)` returns the default instead of raising `StopAsyncIteration`. Both were added in Python 3.10.

Q4: How can you run many async iterators at once?
A4: Drain each in its own coroutine and `asyncio.gather` them, or merge into one with a queue. For example use `asyncio.TaskGroup` with one task per iterator.

Q5: How do you stop an async iterator early?
A5: `break` out of the loop; if the class owns resources, give it an `aclose()` method (like async generators) and use `async with` or `contextlib.aclosing` for cleanup.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing a library cursor / stream / consumer class
- You need state, attributes and methods beside iteration
- You want one object to be both iterable and a context manager

❌ Avoid when:
- A simple async generator does the job (less code)
- Data is already in memory (use a plain list)
- You need random access

---

## 📊 Visual Diagram
```
async for item in obj:
      │
      ├── it = obj.__aiter__()         (sync call, returns iterator)
      │
      └── loop:
            item = await it.__anext__()    <- may do network I/O
            ... your body ...
            (repeat)
          StopAsyncIteration raised  ->  loop ends

class Paged:   state: pos, size, closed
               __aiter__ -> self
               __anext__ -> next chunk | StopAsyncIteration
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Async iterable | Has `__aiter__` | जिसमें `__aiter__` हो |
| Async iterator | Has `__aiter__` and `__anext__` | जिसमें दोनों हों |
| `StopAsyncIteration` | Signals the end | अंत का संकेत |
| `aiter()` / `anext()` | Builtins for manual stepping | हाथ से कदम बढ़ाने वाले builtins |
| Cursor | Object that streams DB rows | DB rows stream करने वाला object |
| Single-pass | Can be consumed only once | सिर्फ एक बार पढ़ा जा सकता है |

---

## ⚡ 3-Line Summary
English: An async iterator implements a normal `__aiter__` and an `async def __anext__` that raises `StopAsyncIteration` at the end. It is the class-based sibling of async generators, best when you need state and extra methods.
Hindi: Async iterator में सामान्य `__aiter__` और `async def __anext__` होता है जो अंत में `StopAsyncIteration` उठाता है। यह async generators का class वाला रूप है, जब state और अतिरिक्त methods चाहिए हों तब सबसे अच्छा।

---

## ➡️ Next Topic
**257. anyio Library** — one async API that works on both asyncio and trio, with task groups and cancel scopes.
