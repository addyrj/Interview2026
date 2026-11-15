---

# Q208. Handle multiple async errors (gather / TaskGroup)
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Three tasks run together and two of them fail. Show how `gather` (default), `gather(return_exceptions=True)` and `TaskGroup` with `except*` each behave.

---

## 💡 Quick Concept (2 lines only)
gather raises the first error only; `return_exceptions=True` returns errors as values; TaskGroup cancels siblings and raises an `ExceptionGroup` with all errors.
हिंदी: gather पहली error देता है, `return_exceptions=True` सब error values में देता है, TaskGroup सब errors का group देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                       # asyncio

async def ok(n: int) -> int:
    await asyncio.sleep(0.01)                        # simulated I/O
    return n                                         # success

async def bad(msg: str) -> int:
    await asyncio.sleep(0.02)                        # simulated I/O
    raise ValueError(msg)                            # failure

async def main() -> None:
    # 1) gather default: first exception propagates, others keep running
    try:
        await asyncio.gather(ok(1), bad("e1"), bad("e2"))
    except ValueError as e:
        print("gather:", e)                          # Expected: gather: e1
    # 2) return_exceptions=True: collect everything
    res = await asyncio.gather(ok(1), bad("e1"), bad("e2"), return_exceptions=True)
    print(res)                                       # Expected: [1, ValueError('e1'), ValueError('e2')]
    # 3) TaskGroup: cancels siblings, raises ALL errors as an ExceptionGroup
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(bad("e1")); tg.create_task(bad("e2")); tg.create_task(ok(3))
    except* ValueError as eg:                        # except* matches inside the group
        print("taskgroup:", [str(e) for e in eg.exceptions])  # Expected: ['e1', 'e2']

asyncio.run(main())

# --- Real output (Python 3.13) ---
# gather: e1
# [1, ValueError('e1'), ValueError('e2')]
# taskgroup: ['e1', 'e2']
```

---

## 🔍 Why This Works (3 lines max)
With default gather the other tasks are NOT cancelled and their later errors are not reported. TaskGroup (3.11+) cancels remaining tasks when one fails and bundles all failures; `except*` matches by type inside the group.
हिंदी: TaskGroup बाकी tasks cancel करता है और सारे errors `ExceptionGroup` में देता है।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: split results into successes and failures
# ============================================
import asyncio                                       # asyncio

async def job(n: int) -> int:
    await asyncio.sleep(0.01)                        # simulated I/O
    if n % 2:                                        # odd numbers fail
        raise ValueError(f"bad {n}")
    return n * 10                                    # even numbers succeed

async def main() -> None:
    res = await asyncio.gather(*(job(n) for n in range(4)), return_exceptions=True)
    good = [r for r in res if not isinstance(r, BaseException)]  # successes
    bad = [r for r in res if isinstance(r, BaseException)]       # failures
    print(good, [str(b) for b in bad])               # Expected: [0, 20] ['bad 1', 'bad 3']

asyncio.run(main())

# --- Real output (Python 3.13) ---
# [0, 20] ['bad 1', 'bad 3']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: plain `except ValueError` around a TaskGroup
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(bad("e1"))
except ValueError:        # never matches: TaskGroup raises ExceptionGroup, not ValueError
    ...

# ✅ Correct: except* ValueError as eg: ...   (see solution)
```

---

## 🎯 Interview Tip (1 line)
Say: "gather for fire-and-collect, TaskGroup when failures should abort the whole group — and remember `except*` for ExceptionGroups."

---

## 🔗 Related Questions
→ Q260 (exception groups) | Q202 (parallel) | Q093 (all-settled) | Q094 (any)
