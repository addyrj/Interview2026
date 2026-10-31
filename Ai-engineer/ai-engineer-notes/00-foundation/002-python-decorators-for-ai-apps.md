---

# 002. Python Decorators for AI Apps
# हिंदी में: AI Apps के लिए Python Decorators

---

## 🔵 Simple Definition (English)
A decorator is a function that takes another function and returns an improved version of it. You write `@retry` above a function and it gets retry logic without changing its body. In AI apps, decorators add retry, timing, caching, logging and token counting around LLM calls.

## 🔵 सरल परिभाषा (Hindi)
Decorator एक function है जो दूसरे function को लेकर उसका बेहतर version return करता है। Function के ऊपर `@retry` लिखने से उसकी body बदले बिना retry logic जुड़ जाता है। AI apps में LLM calls के चारों ओर retry, timing, caching, logging और token counting के लिए decorators use होते हैं।

---

## 🔴 Problem it Solves
Every LLM function needs the same extras: retry on 429, timing, logging, caching. Copy-pasting `try/except` and `time.time()` into 30 functions creates bugs and noise. Decorators keep this cross-cutting code in one place, so business code stays clean.

## 🔴 यह क्यों बना? (Hindi)
हर LLM function को वही extras चाहिए: 429 पर retry, timing, logging, caching। 30 functions में `try/except` copy-paste करने से bugs और गंदा code बनता है। Decorators यह common code एक जगह रखते हैं, business logic साफ़ रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a function `timed(func)` that defines an inner `wrapper(*args, **kwargs)`
Step 2 → Inside wrapper: do "before" work, call func(*args, **kwargs), do "after" work
Step 3 → `timed` returns wrapper
Step 4 → `@timed` above `def ask()` means: ask = timed(ask)
Step 5 → Use functools.wraps so the name and docstring are kept
Step 6 → For async functions the wrapper must be `async def` and use `await func(...)`
Step 7 → For arguments (`@retry(times=3)`) add one more outer layer (decorator factory)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → `timed(func)` function लिखो जिसके अंदर `wrapper(*args, **kwargs)` हो
Step 2 → wrapper में पहले "before" काम, फिर func call, फिर "after" काम
Step 3 → `timed` wrapper return करता है
Step 4 → `def ask()` के ऊपर `@timed` का मतलब: ask = timed(ask)
Step 5 → `functools.wraps` से नाम और docstring बने रहते हैं
Step 6 → async function के लिए wrapper भी `async def` हो और `await func(...)` करे
Step 7 → Arguments (`@retry(times=3)`) के लिए एक और बाहरी layer (decorator factory)
```

---

## 🟡 Real World Example
**Tariff Classification System**: `classify_product()` calls an LLM. We decorate it with `@retry(times=3)` for rate-limit errors, `@timed` to log latency, and `@cache` so the same product description is never paid for twice. A repeated "iPhone 15" query costs 0 tokens on the second call.

**Amazon AI**: Product-title generation functions use a `@track_tokens` decorator to charge token usage to each seller account.

## 🟡 Real Example Hindi mein
**Tariff System**: `classify_product()` LLM call करता है। उस पर `@retry(times=3)` (rate-limit के लिए), `@timed` (latency log) और `@cache` (एक ही description दोबारा pay न करना) लगाते हैं। "iPhone 15" दूसरी बार पूछने पर 0 tokens।

**Amazon AI**: Title generation functions पर `@track_tokens` लगता है ताकि हर seller account पर token usage का हिसाब रहे।

---

## 💻 Code Example — Basic
```python
# Basic decorator - pure Python, runs directly
import functools  # for functools.wraps
import time  # for timing


def timed(func):  # decorator: receives the original function
    @functools.wraps(func)  # keep original name and docstring
    def wrapper(*args, **kwargs):  # accepts any arguments
        start = time.perf_counter()  # start the clock
        result = func(*args, **kwargs)  # call the real function
        elapsed = time.perf_counter() - start  # compute elapsed seconds
        print(f"{func.__name__} took {elapsed:.3f}s")  # log the timing
        return result  # return the original result unchanged
    return wrapper  # hand back the new function


@timed  # same as classify = timed(classify)
def classify(product: str) -> str:  # a fake LLM call
    time.sleep(0.2)  # simulate latency
    return f"{product}: 8517"  # fake HS code


print(classify("phone"))  # prints timing line, then the result
print(classify.__name__)  # "classify" thanks to functools.wraps
```

## 💻 Code Example — Advanced
```python
# Production decorators: async retry with backoff + in-memory TTL cache + token tracking
import asyncio  # async sleep
import functools  # wraps
import logging  # structured logs
import time  # monotonic clock
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar  # typing helpers

P = ParamSpec("P")  # captures the wrapped function's parameters
R = TypeVar("R")  # captures the wrapped function's return type
log = logging.getLogger("ai")  # module logger


def async_retry(times: int = 3, base_delay: float = 0.5,
                exceptions: tuple[type[BaseException], ...] = (ConnectionError, TimeoutError)
                ) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Retry an async function with exponential backoff on given exceptions."""
    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:  # real decorator
        @functools.wraps(func)  # keep metadata
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # async wrapper
            for attempt in range(1, times + 1):  # attempts 1..times
                try:  # protect the call
                    return await func(*args, **kwargs)  # success: return immediately
                except exceptions as exc:  # only retry known transient errors
                    if attempt == times:  # last attempt failed
                        raise  # re-raise the original error
                    delay = base_delay * 2 ** (attempt - 1)  # 0.5, 1, 2 ...
                    log.warning("retry %s/%s after %s: %s", attempt, times, delay, exc)  # log it
                    await asyncio.sleep(delay)  # non-blocking wait
            raise RuntimeError("unreachable")  # keeps type checkers happy
        return wrapper  # return decorated function
    return decorator  # return the decorator (factory pattern)


def ttl_cache(seconds: float = 60.0) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Cache async results by arguments for a limited time (saves tokens)."""
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:  # decorator
        store: dict[tuple, tuple[float, Any]] = {}  # key -> (expiry, value)

        @functools.wraps(func)  # keep metadata
        async def wrapper(*args: Any, **kwargs: Any) -> Any:  # async wrapper
            key = (args, tuple(sorted(kwargs.items())))  # hashable cache key
            hit = store.get(key)  # look up
            if hit and hit[0] > time.monotonic():  # still fresh
                return hit[1]  # cache hit: zero tokens spent
            value = await func(*args, **kwargs)  # miss: call the real function
            store[key] = (time.monotonic() + seconds, value)  # save with expiry
            return value  # return fresh value
        return wrapper  # decorated function
    return decorator  # factory result


calls = {"n": 0}  # counts real calls for the demo


@ttl_cache(seconds=30)  # outer: cache first
@async_retry(times=3, base_delay=0.1)  # inner: retry real calls
async def classify(product: str) -> str:  # fake LLM call
    calls["n"] += 1  # count the call
    if calls["n"] == 1:  # fail once to show retry
        raise ConnectionError("503")  # transient error
    return f"{product}: 8517.13"  # fake result


async def main() -> None:  # demo
    print(await classify("phone"))  # retried once, then success
    print(await classify("phone"))  # served from cache
    print("real calls:", calls["n"])  # 2 (1 failed + 1 success), not 3


if __name__ == "__main__":  # entry
    asyncio.run(main())  # run demo
```

---

## 🟠 FastAPI Integration
FastAPI itself is built on decorators (`@app.get`). You can stack your own decorators under the route decorator. Keep the order: `@app.post(...)` must be the top one, and your wrapper must use `functools.wraps` so FastAPI still sees the correct type hints for validation.

```python
# FastAPI + custom decorator (log latency of each route)
import functools  # wraps
import time  # timer
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # request model

app = FastAPI()  # app


def log_latency(func):  # decorator for async routes
    @functools.wraps(func)  # critical: preserves signature for FastAPI
    async def wrapper(*args, **kwargs):  # async wrapper
        start = time.perf_counter()  # start
        try:  # make sure we log even on error
            return await func(*args, **kwargs)  # call route
        finally:  # always runs
            print(f"{func.__name__}: {time.perf_counter() - start:.3f}s")  # log
    return wrapper  # decorated route


class Q(BaseModel):  # body
    text: str  # product text


@app.post("/classify")  # route decorator on top
@log_latency  # custom decorator below
async def classify(q: Q) -> dict[str, str]:  # handler
    return {"code": "8517", "input": q.text}  # fake answer
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `@tool` decorator turns a Python function into a tool the LLM can call; the docstring and type hints become the tool schema. This is why good type hints and docstrings matter. LangGraph and LangChain also use `.with_retry()` and `.with_fallbacks()` on Runnables, which is the same idea as retry decorators.

```python
# LangChain @tool decorator (langchain-core)
from langchain_core.tools import tool  # decorator that builds a tool


@tool  # converts function into a Tool with a JSON schema
def lookup_duty(hs_code: str) -> str:  # type hint becomes the schema type
    """Return the import duty percent for an HS code."""  # docstring is the tool description
    return {"8517": "0%", "6403": "20%"}.get(hs_code, "unknown")  # tiny fake table


print(lookup_duty.name)  # "lookup_duty"
print(lookup_duty.invoke({"hs_code": "8517"}))  # "0%"
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `functools.wraps`
✅ Correct: always add it, or names, docstrings and FastAPI signatures break.

```python
# Wrong: wrapper replaces the name, func.__name__ becomes "wrapper"
def deco(f):
    def wrapper(*a, **k):
        return f(*a, **k)
    return wrapper

# Right: metadata is preserved
import functools
def deco(f):
    @functools.wraps(f)
    def wrapper(*a, **k):
        return f(*a, **k)
    return wrapper
```

❌ Mistake 2: Using a sync wrapper on an async function
✅ Correct: make the wrapper `async def` and `await` the call.

```python
# Wrong: returns a coroutine un-awaited, retry/try-except never catches the error
def retry(f):
    def wrapper(*a, **k):
        try:
            return f(*a, **k)  # coroutine is created but not awaited here
        except Exception:
            pass
    return wrapper

# Right: async wrapper, awaits inside the try
def retry(f):
    async def wrapper(*a, **k):
        try:
            return await f(*a, **k)
        except Exception:
            raise
    return wrapper
```

❌ Mistake 3: Caching with a mutable or huge key (e.g. whole documents) or without expiry, so memory grows and stale answers live forever. Use TTL and hash the key.

---

## 🧠 Tricky Interview Question

**Q**: "Your `@cache` decorator on an LLM function returns the same answer for different users, and one user saw another user's data. What happened?"

**Answer**: The cache key ignored something that changes the answer, such as user id, tenant, system prompt or model name (or the user context was passed through a global, not an argument). Cache keys must include every input that affects the output. Also never cache personal data in a shared in-process dict. Fix: include `tenant_id`, `model`, `prompt_version` in the key, hash it, scope the cache per tenant, and set a TTL.

---

## ⚫ Interview Questions + Answers

Q1: What does `@decorator` mean in Python? (Easy)
A1: It is shorthand for `func = decorator(func)`. The decorator runs once at definition time and the returned wrapper replaces the original function.

Q2: Why use `functools.wraps`? (Easy)
A2: It copies `__name__`, `__doc__`, and `__wrapped__` from the original to the wrapper. Without it, debugging, logging, and tools that read signatures (FastAPI, LangChain `@tool`) see the wrapper instead.

Q3: How do you write a decorator that takes arguments? (Medium)
A3: Add an outer function (a factory) that takes the arguments and returns the real decorator, which returns the wrapper. `@retry(times=3)` calls `retry(3)` first, then applies the result to the function.

Q4: How do you decorate both sync and async functions with one decorator? (Medium)
A4: Check `inspect.iscoroutinefunction(func)` and return an async wrapper for async functions and a sync wrapper for sync ones. A sync wrapper on an async function breaks `await` and error handling.

Q5: Design a decorator that enforces a per-user token budget on LLM calls. (Hard)
A5: The decorator reads `user_id` from arguments, checks a counter in Redis (atomic `INCRBY` with a daily key and TTL), estimates input tokens before the call and rejects with a 429 if the budget is exceeded, then after the call adds the real `usage.total_tokens`. It must be async, use atomic Redis ops to avoid races under concurrency, and fail open or closed by policy if Redis is down.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The same cross-cutting logic (retry, log, cache, auth, metrics) applies to many functions
- You want business code to stay clean
- You build reusable tools for LLM apps

❌ Avoid when:
- The logic is used once (a plain function call is clearer)
- The behaviour is hidden and surprising for teammates (e.g. a decorator that silently swallows errors)
- Deep stacks of 5+ decorators make debugging hard

---

## 📊 Visual Diagram
```
 caller ──> [ @ttl_cache ] ──> [ @async_retry ] ──> classify() ──> LLM API
              │ hit? return              │ fail? wait + retry
              └─ miss ───────────────────┘

 @timed:   start ─> func() ─> stop ─> log   (wrapper surrounds the function)
```

---

## 💰 Cost Impact
Decorators themselves cost no tokens, but they control spending. A TTL cache can remove 20-60 percent of repeated calls in FAQ-like traffic. Retry decorators can waste tokens if they retry on non-transient errors (e.g. a 400 caused by a too-long prompt), so retry only on 429/5xx/timeouts and cap attempts. A token-tracking decorator gives per-user spend data. Example: 100K daily queries at 600 tokens on gpt-4o-mini cost about $9/day at input pricing; a 40 percent cache hit rate saves about $3.6/day.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Decorator | Function that wraps another function | दूसरे function को wrap करने वाला function |
| Wrapper | Inner function that adds behaviour | अंदर वाला function जो behaviour जोड़ता है |
| functools.wraps | Keeps original metadata | original नाम/docstring बचाता है |
| Decorator factory | Decorator that takes arguments | arguments लेने वाला decorator |
| Backoff | Increasing wait between retries | retries के बीच बढ़ता इंतज़ार |
| TTL | Time before cache entry expires | cache कब तक valid |
| ParamSpec | Typing tool to keep signatures | signature typing के लिए |

---

## ⚡ 3-Line Summary
English: A decorator wraps a function to add retry, timing, caching or logging without touching its body. Use `functools.wraps` and async-aware wrappers. Good caching and retry decorators cut tokens and failures.
Hindi: Decorator function की body बदले बिना उसमें retry, timing, caching या logging जोड़ता है। `functools.wraps` और async wrappers use करो। अच्छे cache और retry decorators tokens और failures कम करते हैं।

---

## ➡️ Next Topic
**003. Python Classes + OOP for LangChain** — LangChain components (retrievers, tools, callbacks) are classes, so you need OOP to build and extend them.
