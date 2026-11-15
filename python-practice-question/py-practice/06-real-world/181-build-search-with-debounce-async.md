---

# Q181. Build Search with Debounce (async)
# Category: Real World Problems
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Build an async debouncer for a search box: when `search(query)` is called repeatedly, only the LAST call (after `delay` seconds of silence) should hit the API; earlier pending calls are cancelled. Use `asyncio` with simulated I/O.

---

## 💡 Quick Concept (2 lines only)
Each call cancels the previous pending task and schedules a new one that first `await asyncio.sleep(delay)` then calls the API. Only a call left alone for `delay` survives.
हिंदी: हर नई call पिछला pending task cancel करती है — सिर्फ आखिरी call `delay` के बाद API तक पहुँचती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                           # Step 1: imports
from collections.abc import Awaitable, Callable
from typing import Any

class AsyncDebouncer:
    def __init__(self, fn: Callable[..., Awaitable[Any]], delay: float) -> None:
        self.fn = fn                                     # async function to protect
        self.delay = delay                               # quiet period in seconds
        self._task: asyncio.Task[Any] | None = None     # latest pending task

    def __call__(self, *args: Any) -> asyncio.Task[Any]:
        if self._task and not self._task.done():         # Step 2: a call is still waiting?
            self._task.cancel()                          # cancel it (the debounce)
        self._task = asyncio.create_task(self._run(*args))  # Step 3: schedule the new one
        return self._task                                # caller may await it

    async def _run(self, *args: Any) -> Any:
        await asyncio.sleep(self.delay)                  # Step 4: wait; cancellation lands here
        return await self.fn(*args)                      # quiet long enough -> real call

    def cancel(self) -> None:
        if self._task and not self._task.done():         # drop any pending call
            self._task.cancel()

# ============================================
# TEST CASES
# ============================================
calls: list[str] = []                                    # records real API hits

async def search_api(query: str) -> list[str]:
    await asyncio.sleep(0.01)                            # simulated network I/O
    calls.append(query)                                  # record the hit
    return [f"{query}-result-{i}" for i in range(2)]     # fake results

async def main() -> None:
    search = AsyncDebouncer(search_api, delay=0.05)      # 50ms debounce
    t1 = search("p")                                     # typed "p"
    await asyncio.sleep(0.01)                            # 10ms later (< 50ms)
    t2 = search("py")                                    # cancels t1
    await asyncio.sleep(0.01)
    t3 = search("pyt")                                   # cancels t2
    print(await t3)                                      # Expected: ['pyt-result-0', 'pyt-result-1']
    print(calls)                                         # Expected: ['pyt']
    print(t1.cancelled(), t2.cancelled(), t3.cancelled())  # Expected: True True False
    try:
        await t1                                         # awaiting a cancelled task raises
    except asyncio.CancelledError:
        print("t1 cancelled")                            # Expected: t1 cancelled
    search("later")                                      # a lone call goes through
    await asyncio.sleep(0.1)
    print(calls)                                         # Expected: ['pyt', 'later']
    search("x"); search.cancel()                         # explicit cancel
    await asyncio.sleep(0.1)
    print(calls)                                         # Expected: ['pyt', 'later']

asyncio.run(main())                                      # run the demo
```

---

## 🔍 Why This Works (3 lines max)
`task.cancel()` injects `CancelledError` at the task's current `await`, so a call still sleeping never reaches the API. Because the sleep comes before the API call, cancelled queries cost nothing.
हिंदी: `cancel()` task के `await` पर `CancelledError` डालता है, इसलिए sleep में फँसी पुरानी calls API तक जाती ही नहीं।

---

## ⚡ Alternative Solution
```python
import asyncio, functools                                # modules

def debounce(delay: float):                              # decorator version
    def deco(fn):
        task: asyncio.Task | None = None                 # shared state in closure
        @functools.wraps(fn)                             # keep fn's metadata
        def wrapper(*a, **k):
            nonlocal task
            if task and not task.done():
                task.cancel()                            # cancel previous
            async def run():
                await asyncio.sleep(delay)               # quiet period
                return await fn(*a, **k)                 # real call
            task = asyncio.create_task(run())            # schedule
            return task
        return wrapper
    return deco

out: list[str] = []                                      # captured saves
@debounce(0.03)
async def save(text: str) -> None:
    out.append(text)                                     # pretend to save

async def main2() -> None:
    for ch in ["a", "ab", "abc"]:                        # fast typing
        save(ch)
        await asyncio.sleep(0.005)
    await asyncio.sleep(0.1)                             # let debounce fire
    print(out)                                           # Expected: ['abc']
asyncio.run(main2())
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: firing every query with no cancellation -> all 3 hit the API
async def main3() -> None:
    results: list[str] = []
    async def search(q: str) -> None:
        await asyncio.sleep(0.01)
        results.append(q)
    tasks = [asyncio.create_task(search(q)) for q in ["p", "py", "pyt"]]
    await asyncio.gather(*tasks)
    print(results)                                   # Output: ['p', 'py', 'pyt']  (wasted calls, stale results can arrive out of order)

# ✅ Correct: debounce + cancel the older tasks (see solution)
```

---

## 🎯 Interview Tip (1 line)
Say: "Debounce in asyncio = cancel the previous task and restart a sleep-then-call task; cancel also protects against stale responses overwriting newer ones."

---

## 🔗 Related Questions
→ Q081 (implement debounce) | Q141 (complete debounce) | Q206 (cancel a task) | Q214 (debounce an async function)
