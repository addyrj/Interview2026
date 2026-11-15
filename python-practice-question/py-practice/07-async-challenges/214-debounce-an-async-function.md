---

# Q214. Debounce an async function
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `@debounce(delay)` for an `async def`. If it is called several times within `delay` seconds, only the LAST call should actually run, and every caller should get that result.

```python
@debounce(0.3)
async def search(q): ...
```

---

## 💡 Quick Concept (2 lines only)
Each call cancels the previous pending timer task and starts a new one; callers in the same window share one Future that holds the final result.
हिंदी: हर call पिछला pending task cancel करती है; सिर्फ last call चलती है और सब callers को वही result मिलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio                                    # asyncio library
import functools                                  # wraps
from collections.abc import Awaitable, Callable   # type hints
from typing import Any                            # generic


def debounce(delay: float) -> Callable:
    def decorator(fn: Callable[..., Awaitable[Any]]) -> Callable[..., asyncio.Future]:
        timer: asyncio.Task | None = None         # pending delayed call
        shared: asyncio.Future | None = None      # future shared by callers in this window

        async def run(fut: asyncio.Future, a: tuple, kw: dict) -> None:
            await asyncio.sleep(delay)            # wait for quiet period
            try:
                fut.set_result(await fn(*a, **kw))  # run the real function
            except Exception as e:                # propagate errors to waiters
                fut.set_exception(e)              # store the error

        @functools.wraps(fn)                      # keep name/docstring
        def wrapper(*a: Any, **kw: Any) -> asyncio.Future:
            nonlocal timer, shared                # we update both
            if timer is not None and not timer.done():  # a call is still waiting
                timer.cancel()                    # drop the older call (reset the timer)
            else:
                shared = asyncio.get_running_loop().create_future()  # new window -> new future
            timer = asyncio.create_task(run(shared, a, kw))  # schedule latest call
            return shared                         # everyone awaits the same result

        return wrapper
    return decorator


# ---------- TEST CASES ----------
calls: list[str] = []                             # records real executions


@debounce(0.05)
async def search(q: str) -> str:
    calls.append(q)                               # note real call
    return f"results for {q}"                     # fake result


async def main() -> None:
    f1 = search("p")                              # typed 'p'
    await asyncio.sleep(0.01)                     # 10 ms later
    f2 = search("py")                             # typed 'py'
    await asyncio.sleep(0.01)                     # 10 ms later
    f3 = search("pyt")                            # typed 'pyt'
    print(await f3, f1 is f3, f2 is f3)           # one shared result
    print("real calls:", calls)                   # only the last query ran
    await asyncio.sleep(0.1)                      # long pause -> new window
    print(await search("pytest"), calls)          # a second real call


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# results for pyt True True
# real calls: ['pyt']
# results for pytest ['pyt', 'pytest']
```

---

## 🔍 Why This Works (3 lines max)
The wrapper keeps one `Task` (the timer). A new call does `timer.cancel()` so the old `sleep` never finishes. A shared `Future` lets all earlier callers `await` the final result instead of getting `CancelledError`.
हिंदी: Task cancel = पुराना call खत्म; shared Future से सब callers को last result मिलता है।

---

## ⚡ Alternative Solution
```python
import asyncio                                    # asyncio library


class Debouncer:
    def __init__(self, delay: float) -> None:
        self.delay = delay                        # quiet period in seconds
        self._task: asyncio.Task | None = None    # pending task

    def call(self, coro_fn, *args) -> None:       # fire-and-forget style
        self.cancel()                             # cancel previous pending call
        self._task = asyncio.create_task(self._later(coro_fn, args))  # schedule new one

    async def _later(self, coro_fn, args) -> None:
        await asyncio.sleep(self.delay)           # wait; CancelledError raised here if superseded
        await coro_fn(*args)                      # run only if not cancelled

    def cancel(self) -> None:
        if self._task and not self._task.done():  # something pending
            self._task.cancel()                   # cancel it


async def save(text: str) -> None:
    print("saved:", text)                         # side effect


async def main() -> None:
    d = Debouncer(0.05)                           # 50 ms debounce
    for t in ["h", "he", "hel", "hell", "hello"]: # rapid typing
        d.call(save, t)                           # each call replaces previous
        await asyncio.sleep(0.01)                 # 10 ms between keys
    await asyncio.sleep(0.1)                      # wait for quiet period
    d.call(save, "bye")                           # new call...
    d.cancel()                                    # ...cancelled before it fires
    await asyncio.sleep(0.1)                      # nothing printed


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# saved: hello
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: copying the JS version - there is no setTimeout/clearTimeout in asyncio
def debounce(fn, delay):
    timer = None
    async def wrapper(*a):
        clearTimeout(timer)           # NameError - not Python!
        ...

# ❌ Also wrong: cancelling but leaving earlier callers awaiting a dead task
#    -> they get CancelledError (or hang). Share a Future, or document that superseded calls return None.
```

---

## 🎯 Interview Tip (1 line)
Say: "Debounce in asyncio = cancel the previous sleeping Task; decide what superseded callers receive (shared Future or None)."

---

## 🔗 Related Questions
→ Q081 (debounce) | Q141 (complete debounce) | Q181 (search with debounce) | Q206 (cancel a task)
