---

# Q091. Implement asyncio.gather
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `my_gather(*aws, return_exceptions=False)` that runs awaitables **concurrently** and returns results **in input order**. If one fails (and `return_exceptions=False`) the error propagates and the others are cancelled.

```python
await my_gather(work("a", 0.3), work("b", 0.1), work("c", 0.2))  # ['a', 'b', 'c'] in ~0.3s
```

---

## 💡 Quick Concept (2 lines only)
Wrap each awaitable in a Task with `ensure_future` so they all start immediately, then await them one by one — the total time is the slowest task, not the sum.
हिंदी: सब coroutines को Task बनाकर साथ चलाओ, फिर order में results इकट्ठा करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio  # event loop + tasks
from typing import Any, Awaitable  # type hints


async def my_gather(*aws: Awaitable, return_exceptions: bool = False) -> list[Any]:
    tasks = [asyncio.ensure_future(a) for a in aws]  # Step 1: schedule ALL now (concurrent start)
    results: list[Any] = []  # Step 2: ordered results
    try:
        for t in tasks:  # Step 3: await in input order
            if return_exceptions:  # collect errors as values
                try:
                    results.append(await t)  # normal result
                except Exception as e:
                    results.append(e)  # store the exception object
            else:
                results.append(await t)  # first error propagates
    except BaseException:  # error or outer cancellation
        for t in tasks:
            t.cancel()  # Step 4: stop the siblings
        raise  # re-raise to the caller
    return results  # Step 5: ordered list


# ============================================
# TEST CASES
# ============================================
async def work(name: str, delay: float, fail: bool = False) -> str:  # simulated I/O
    await asyncio.sleep(delay)  # pretend network wait
    if fail:
        raise ValueError(f"{name} failed")  # simulated error
    return name  # result


async def main() -> None:
    loop = asyncio.get_running_loop()  # for timing
    t = loop.time()  # start
    print(await my_gather(work("a", 0.3), work("b", 0.1), work("c", 0.2)))  # Expected: ['a', 'b', 'c']
    print(round(loop.time() - t, 1))  # Expected: 0.3  (not 0.6)
    print(await my_gather())  # Expected: []
    print(await my_gather(work("a", 0.1), work("b", 0.05, True), return_exceptions=True))
    # Expected: ['a', ValueError('b failed')]
    try:
        await my_gather(work("a", 0.1), work("b", 0.05, True))
    except ValueError as e:
        print("raised:", e)  # Expected: raised: b failed


asyncio.run(main())
```

---

## 🔍 Why This Works (3 lines max)
`ensure_future` starts every coroutine before the first `await`, so sleeps overlap; awaiting tasks in list order preserves result order regardless of finish order.
The `except` block cancels the remaining tasks so nothing leaks.
हिंदी: Tasks एक साथ शुरू होते हैं, इसलिए कुल समय सबसे धीमे task जितना लगता है।

---

## ⚡ Alternative Solution
```python
async def gather_tg(*coros):  # Python 3.11+ structured concurrency
    async with asyncio.TaskGroup() as tg:  # cancels siblings on first error automatically
        tasks = [tg.create_task(c) for c in coros]  # start all
    return [t.result() for t in tasks]  # all done after the with-block


async def m2():
    print(await gather_tg(work("x", 0.2), work("y", 0.1)))  # Expected: ['x', 'y']
    try:
        await gather_tg(work("x", 0.2), work("y", 0.1, True))
    except* ValueError as eg:  # TaskGroup raises an ExceptionGroup
        print("group:", eg.exceptions)  # Expected: group: (ValueError('y failed'),)


asyncio.run(m2())
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: awaiting inside a list comprehension = sequential, not concurrent
async def m3():
    loop = asyncio.get_running_loop(); t = loop.time()
    r = [await work("a", 0.1), await work("b", 0.1), await work("c", 0.1)]  # ❌ one after another
    print(r, round(loop.time() - t, 1))  # ['a', 'b', 'c'] 0.3  (should be 0.1)

# ✅ Correct: create tasks first (ensure_future / create_task), then await them
```

---

## 🎯 Interview Tip (1 line)
Say: "Schedule everything first so it runs concurrently, keep input order, cancel siblings on failure — and mention TaskGroup as the modern, safer option."

---

## 🔗 Related Questions
→ Q092 (race) | Q093 (all-settled) | Q159 (complete async gather wrapper) | Q202 (run in parallel) | Q208 (multiple async errors)
