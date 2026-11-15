---

# Q202. Run coroutines in parallel
# Category: ASYNC CHALLENGES
# Difficulty: ⭐ Easy

---

## ❓ Question
Run several coroutines concurrently and get all results in input order. Show that total time equals the slowest one, not the sum.

---

## 💡 Quick Concept (2 lines only)
`asyncio.gather(*coros)` schedules them all as tasks at once and returns results in the order passed.
हिंदी: `gather` सब coroutines एक साथ चलाता है — time = सबसे slow वाले का।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                       # event loop + gather
import time                                          # timing

async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)                       # simulated I/O
    return f"{name} done"                            # result

async def main() -> None:
    start = time.perf_counter()                      # start timer
    results = await asyncio.gather(                  # run all at the same time
        fetch("A", 0.2), fetch("B", 0.1), fetch("C", 0.1),
    )
    print(results)                                   # Expected: ['A done', 'B done', 'C done'] (input order)
    print(f"{time.perf_counter() - start:.1f}s")     # Expected: ~0.2s (the slowest one)

asyncio.run(main())

# --- Real output (Python 3.13) ---
# ['A done', 'B done', 'C done']
# 0.2s
```

---

## 🔍 Why This Works (3 lines max)
gather wraps each coroutine in a Task, all start in the same loop iteration, and while one sleeps the others run. Result order follows input order, not completion order. Total ~0.2s vs 0.4s sequentially.
हिंदी: सब tasks साथ शुरू होते हैं; result का order input जैसा ही रहता है।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: TaskGroup (3.11+) and as_completed
# ============================================
import asyncio                                       # asyncio

async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)                       # simulated I/O
    return f"{name} done"                            # result

async def main() -> None:
    async with asyncio.TaskGroup() as tg:            # all tasks awaited at block exit
        tasks = [tg.create_task(fetch(n, d)) for n, d in [("A", 0.2), ("B", 0.1)]]
    print([t.result() for t in tasks])               # Expected: ['A done', 'B done']
    for fut in asyncio.as_completed([fetch("A", 0.2), fetch("B", 0.1)]):  # finish order
        print(await fut)                             # Expected: B done, then A done

asyncio.run(main())

# --- Real output (Python 3.13) ---
# ['A done', 'B done']
# B done
# A done
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: await in a loop looks async but is sequential
async def main():
    for d in (0.1, 0.1, 0.1):
        await f(d)          # one by one
    # measured: 0.3s (real run) instead of ~0.1s

# ✅ Correct: asyncio.gather(*(f(d) for d in (0.1, 0.1, 0.1)))  -> ~0.1s
```

---

## 🎯 Interview Tip (1 line)
Say: "gather is great, but TaskGroup (3.11+) gives structured concurrency — if one fails, siblings are cancelled."

---

## 🔗 Related Questions
→ Q201 (sequential) | Q091 (implement gather) | Q159 (gather wrapper) | Q208 (multiple errors)
