---

# Q172. Explain async/await Internals
# Category: Tricky Concepts
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
How do `async def` and `await` work under the hood? What is a coroutine object, and what actually runs it?

---

## 💡 Quick Concept (2 lines only)
`async def` returns a coroutine object (a generator-like state machine); `await` delegates to another awaitable and suspends by yielding up to whoever drives it.
हिंदी: `async def` call करने पर coroutine object मिलता है, चलता नहीं; `await` उसे suspend करके control event loop को देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION — drive a coroutine by hand (no event loop)
# ============================================
class Awaitable:                             # Step 1: custom awaitable
    def __await__(self):                     # must return an iterator
        print("  suspending")                # runs on first send()
        yield                                # Step 2: suspension point -> control goes to the driver
        print("  resumed")                   # runs on second send()
        return "done"                        # becomes the value of `await`

async def coro() -> str:                     # Step 3: coroutine function
    print("start")                           # nothing runs at call time
    result = await Awaitable()               # delegate (like `yield from`)
    return result                            # final result

# ============================================
# TEST CASES
# ============================================
c = coro()                                   # creates coroutine object, runs NOTHING yet
print(type(c).__name__)                      # Expected: coroutine
c.send(None)                                 # start it: Expected prints: start / suspending
try:
    c.send(None)                             # resume: Expected prints: resumed
except StopIteration as e:                   # return value travels inside StopIteration
    print("returned:", e.value)              # Expected: returned: done
```

---

## 🔍 Why This Works (3 lines max)
Coroutines are built on generator machinery: `await x` ≈ `yield from x.__await__()`. A bare `yield` suspends the whole await chain up to the event loop, which later resumes it with `send()`; the `return` value arrives via `StopIteration.value`.
हिंदी: `await` असल में `yield from` जैसा है; event loop ही `send()` से coroutine को आगे बढ़ाता है, return value `StopIteration` में आती है।

---

## ⚡ Alternative Solution
```python
import asyncio                               # real event loop does the driving

async def inner() -> int:                    # leaf coroutine
    await asyncio.sleep(0)                   # sleep(0) = one bare yield to the loop
    return 42                                # result

async def outer() -> int:                    # awaits another coroutine
    return await inner() + 1                 # runs inner inline, no new task

print(asyncio.run(outer()))                  # Expected: 43

async def main() -> None:
    t = asyncio.create_task(inner())         # wraps coroutine in a Task, scheduled on the loop
    print(t.done())                          # Expected: False (hasn't had a turn yet)
    await asyncio.sleep(0)                   # give the loop a turn: task starts, then yields
    await asyncio.sleep(0)                   # another turn: task finishes
    print(t.done(), t.result())              # Expected: True 42

asyncio.run(main())                          # run main
```

---

## ⚠️ Common Mistake
```python
import asyncio                               # asyncio

async def f() -> int:                        # simple coroutine
    return 1

# ❌ Wrong: calling without await just creates a coroutine object
x = f()                                      # nothing ran; ignoring it -> "coroutine 'f' was never awaited" RuntimeWarning
print(type(x).__name__)                      # Output: coroutine
x.close()                                    # (cleanup so the warning doesn't fire here)

# ✅ Correct: await it (or wrap with create_task / asyncio.run)
async def good() -> None:
    print(await f())                         # Output: 1
asyncio.run(good())                          # run
```

---

## 🎯 Interview Tip (1 line)
Say: "A coroutine is a resumable state machine; `await` suspends it, the event loop resumes it with `send()` — only `await`ing something that yields to the loop (I/O, sleep) gives concurrency."

---

## 🔗 Related Questions
→ Q165 (generators) | Q173 (event loop) | Q123 (fix missing await) | Q202 (run in parallel)
