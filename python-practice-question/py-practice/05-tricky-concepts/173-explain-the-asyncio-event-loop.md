---

# Q173. Explain the asyncio Event Loop
# Category: Tricky Concepts
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
How does the asyncio event loop schedule tasks and callbacks? What is the exact print order below, and what happens if a coroutine blocks?

---

## 💡 Quick Concept (2 lines only)
The loop is a single-thread scheduler: it runs ready callbacks/tasks one at a time and waits for I/O or timers when idle. Tasks only switch at `await`.
हिंदी: Event loop एक thread में काम करता है — task तभी बदलता है जब `await` आए; blocking code पूरा loop रोक देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                               # Step 1: asyncio

async def worker(name: str, delay: float) -> str:
    print(f"{name} start")                   # runs when the loop gives it a turn
    await asyncio.sleep(delay)               # suspend: loop runs others / waits on timer
    print(f"{name} end")                     # resumed after delay
    return name                              # result

async def main() -> None:
    loop = asyncio.get_running_loop()        # Step 2: the running loop
    print(type(loop).__name__ != "", loop.is_running())   # Expected: True True
    loop.call_soon(print, "call_soon callback")           # ready queue, runs next iteration
    loop.call_later(0.02, print, "call_later 0.02")       # timer heap, fires at +20ms
    t1 = asyncio.create_task(worker("A", 0.03))           # scheduled (not started yet)
    t2 = asyncio.create_task(worker("B", 0.01))           # scheduled
    print("main before await")               # still synchronous inside main
    res = await asyncio.gather(t1, t2)       # main suspends -> loop runs the ready queue
    print(res)                               # results in input order

# ============================================
# TEST CASES
# ============================================
asyncio.run(main())                          # creates loop, runs main, closes loop
# Expected output:
# True True
# main before await
# call_soon callback
# A start
# B start
# B end
# call_later 0.02
# A end
# ['A', 'B']
```

---

## 🔍 Why This Works (3 lines max)
Each loop iteration: run all ready callbacks in FIFO order, then wait (selector) for I/O or the nearest timer. `call_soon` was queued before the tasks, so it runs first; timers fire by deadline (10ms, 20ms, 30ms), not by creation order.
हिंदी: Loop पहले ready queue चलाता है, फिर timers/I/O का इंतज़ार करता है; timer deadline के हिसाब से चलते हैं।

---

## ⚡ Alternative Solution
```python
import asyncio                               # asyncio
import time                                  # blocking sleep for the demo

async def hog() -> None:
    print("hog start")                       # starts first
    time.sleep(0.1)                          # BLOCKS the whole loop (no await!)
    print("hog end")                         # ticker could not run meanwhile

async def ticker() -> None:
    print("tick")                            # only runs after hog yields/finishes

async def main2() -> None:
    await asyncio.gather(hog(), ticker())    # both scheduled

asyncio.run(main2())                         # Expected: hog start / hog end / tick

# Using the loop API manually (what asyncio.run does for you)
async def one() -> int:
    return 7                                 # trivial coroutine
loop = asyncio.new_event_loop()              # create a loop
print(loop.run_until_complete(one()))        # Expected: 7
loop.close()                                 # always close it
```

---

## ⚠️ Common Mistake
```python
import asyncio, time                         # modules

# ❌ Wrong: time.sleep() inside async code -> everything freezes for 1s
async def bad() -> None:
    time.sleep(1)                            # blocks the event loop

# ✅ Correct: non-blocking sleep, or push blocking work to a thread
async def good() -> None:
    await asyncio.sleep(1)                   # yields to the loop
    await asyncio.to_thread(time.sleep, 1)   # blocking call in a worker thread
```

---

## 🎯 Interview Tip (1 line)
Say: "One thread, cooperative scheduling: ready queue + timer heap + selector for I/O; never block the loop — use `await` or `asyncio.to_thread`."

---

## 🔗 Related Questions
→ Q172 (async/await internals) | Q124 (fix blocking call in async) | Q164 (the GIL) | Q299 (threading vs multiprocessing vs asyncio)
