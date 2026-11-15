---

# Q093. Implement All-Settled
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `all_settled(*aws)` that waits for **every** awaitable to finish and returns a list of dicts: `{"status": "fulfilled", "value": ...}` or `{"status": "rejected", "reason": ...}`. It must never raise because of a failing awaitable. Like `Promise.allSettled`.

---

## 💡 Quick Concept (2 lines only)
Wrap each awaitable in a small coroutine that catches exceptions and converts the outcome into data, then `gather` the wrappers.
हिंदी: All-settled हर task का नतीजा (success या error) डेटा में बदलकर लौटाता है — कभी raise नहीं करता।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio  # concurrency
from typing import Any, Awaitable  # type hints


async def all_settled(*aws: Awaitable) -> list[dict[str, Any]]:
    async def settle(aw: Awaitable) -> dict[str, Any]:  # Step 1: wrapper that never raises
        try:
            return {"status": "fulfilled", "value": await aw}  # success -> data
        except Exception as e:  # failure -> data
            return {"status": "rejected", "reason": e}  # keep the exception object
    return await asyncio.gather(*(settle(a) for a in aws))  # Step 2: run all concurrently, keep order


# ============================================
# TEST CASES
# ============================================
async def job(name: str, delay: float, fail: bool = False) -> str:  # simulated I/O
    await asyncio.sleep(delay)  # pretend work
    if fail:
        raise ValueError(f"{name} failed")  # simulated error
    return name  # result


async def main() -> None:
    res = await all_settled(job("a", 0.2), job("b", 0.1, True), job("c", 0.05))
    for r in res:  # order follows the input, not the finish time
        print(r)
    # Expected: {'status': 'fulfilled', 'value': 'a'}
    #           {'status': 'rejected', 'reason': ValueError('b failed')}
    #           {'status': 'fulfilled', 'value': 'c'}
    print(await all_settled())  # Expected: []


asyncio.run(main())
```

---

## 🔍 Why This Works (3 lines max)
Each wrapper converts an exception into a normal return value, so `gather` never sees a failure and always waits for everyone. Results keep input order.
Note: we catch `Exception`, not `BaseException`, so cancellation still works.
हिंदी: हर error को value बना दिया जाता है, इसलिए gather बीच में नहीं रुकता।

---

## ⚡ Alternative Solution
```python
async def alt() -> None:
    res = await asyncio.gather(job("a", 0.1), job("b", 0.05, True), return_exceptions=True)  # built-in
    print(res)  # Expected: ['a', ValueError('b failed')]
    print([("ok" if not isinstance(r, BaseException) else "err") for r in res])  # Expected: ['ok', 'err']


asyncio.run(alt())
# return_exceptions=True gives the same idea, but you must check isinstance() yourself.
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: plain gather — first error raises and you lose the other results
async def bad():
    try:
        await asyncio.gather(job("a", 0.1), job("b", 0.05, True))
    except ValueError as e:
        print("lost a's result:", e)  # lost a's result: b failed

# ✅ Correct: wrap each awaitable (all_settled) or use return_exceptions=True
```

---

## 🎯 Interview Tip (1 line)
Say: "all_settled converts failures into data so one bad task can't hide the rest — gather(return_exceptions=True) is the built-in equivalent."

---

## 🔗 Related Questions
→ Q091 (gather) | Q094 (any) | Q208 (handle multiple async errors) | Q202 (run in parallel)
