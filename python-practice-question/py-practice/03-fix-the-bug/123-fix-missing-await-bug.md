---

# Q123. Fix missing await bug
# Category: FIX THE BUG
# Difficulty: ⭐ Easy

---

## ❓ Question
`user` should be a dict but behaves like a weird object, and Python prints a warning. Fix it.

```python
async def fetch_user(uid):
    await asyncio.sleep(0.01)        # simulated I/O
    return {"id": uid, "name": f"user{uid}"}

async def main():
    user = fetch_user(1)             # BUG
    print(user["name"])
```

---

## 💡 Quick Concept (2 lines only)
Calling an `async def` function only creates a coroutine object; the body doesn't run until you `await` it (or schedule it as a task).
हिंदी: `async def` call करने से सिर्फ coroutine object बनता है — चलाने के लिए `await` ज़रूरी है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                        # event loop + sleep

async def fetch_user(uid: int) -> dict:
    await asyncio.sleep(0.01)                         # simulated I/O
    return {"id": uid, "name": f"user{uid}"}          # result

async def buggy() -> None:
    user = fetch_user(1)                              # BUG: no await -> coroutine object, never runs
    print(type(user).__name__)                        # Output: coroutine
    print(user)                                       # Output: <coroutine object fetch_user at 0x...>  (address varies)
    # stderr: RuntimeWarning: coroutine 'fetch_user' was never awaited

async def buggy2() -> None:
    user = fetch_user(1)                              # still a coroutine
    try:
        print(user["name"])                           # indexing a coroutine
    except TypeError as e:
        print("TypeError:", e)                        # Output: TypeError: 'coroutine' object is not subscriptable

async def fixed() -> None:
    user = await fetch_user(1)                        # FIX: await runs it and returns the dict
    print(user["name"])                               # use the result

# ============================================
# TEST CASES
# ============================================
asyncio.run(buggy())                                  # Expected: coroutine / <coroutine object ...> (+ RuntimeWarning on stderr)
asyncio.run(buggy2())                                 # Expected: TypeError: 'coroutine' object is not subscriptable
asyncio.run(fixed())                                  # Expected: user1
```

---

## 🔍 Why This Works (3 lines max)
`await` suspends the caller until the coroutine finishes and gives back its return value. Forgetting it leaves a never-started coroutine (and the "never awaited" warning when it is garbage collected).
हिंदी: `await` coroutine को चलाकर उसका result देता है; भूलने पर काम कभी होता ही नहीं।

---

## ⚡ Alternative Solution
```python
# Run several at once: gather or create_task (still must be awaited!)
async def main():
    users = await asyncio.gather(*(fetch_user(i) for i in range(3)))   # concurrent
    print([u["id"] for u in users])                                    # Output: [0, 1, 2]
    task = asyncio.create_task(fetch_user(9))                          # scheduled immediately
    print((await task)["name"])                                        # Output: user9
asyncio.run(main())
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: a coroutine object is always truthy -> silent logic bug (no exception!)
async def cond():
    async def is_ok() -> bool:
        return False
    if is_ok():                                  # forgot await
        print("truthy coroutine -> always runs") # Output: truthy coroutine -> always runs
    if await is_ok():                            # ✅ correct
        print("never")
    else:
        print("awaited -> False")                # Output: awaited -> False
asyncio.run(cond())
# Tip: run with `python -X dev` or enable asyncio debug mode, and use a linter (ruff RUF006 / pyright) to catch this.
```

---

## 🎯 Interview Tip (1 line)
Say: "A call to an async function returns a coroutine; nothing runs until awaited or wrapped in a task — and `RuntimeWarning: never awaited` is the tell."

---

## 🔗 Related Questions
→ Q172 (async/await internals) | Q202 (run coroutines in parallel) | Q201 (run sequentially) | Q124 (blocking call in async)
