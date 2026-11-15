---

# Q207. Chain async operations
# Category: ASYNC CHALLENGES
# Difficulty: ⭐ Easy

---

## ❓ Question
Call three async functions where each depends on the previous result (user -> orders -> total). Then write a reusable `chain(value, *steps)` helper.

---

## 💡 Quick Concept (2 lines only)
Just `await` each step and pass its result to the next — async code reads like synchronous code (no `.then()` chains).
हिंदी: हर step का result अगले step को दो — async/await से code सीधा पढ़ने जैसा रहता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                       # asyncio

async def get_user(uid: int) -> dict:
    await asyncio.sleep(0.01)                        # simulated DB call
    return {"id": uid, "name": "Ann"}                # user row

async def get_orders(user: dict) -> list[str]:
    await asyncio.sleep(0.01)                        # simulated API call
    return [f"order-1-{user['name']}", f"order-2-{user['name']}"]  # depends on step 1

async def total_price(orders: list[str]) -> int:
    await asyncio.sleep(0.01)                        # simulated pricing service
    return len(orders) * 50                          # depends on step 2

async def main() -> None:
    user = await get_user(1)                         # step 1
    orders = await get_orders(user)                  # step 2 uses step 1's result
    total = await total_price(orders)                # step 3 uses step 2's result
    print(user, orders, total)                       # Expected: see below
    # Chain with a helper: each step receives the previous result
    async def chain(value, *steps):
        for step in steps:                           # run steps in order
            value = await step(value)                # feed output into next step
        return value                                 # final result
    print(await chain(1, get_user, get_orders, total_price))  # Expected: 100

asyncio.run(main())

# --- Real output (Python 3.13) ---
# {'id': 1, 'name': 'Ann'} ['order-1-Ann', 'order-2-Ann'] 100
# 100
```

---

## 🔍 Why This Works (3 lines max)
Dependencies force sequential order: `get_orders` needs `user`, `total_price` needs `orders`. The helper generalises this as a loop that feeds each output into the next awaited step.
हिंदी: Dependency है इसलिए एक के बाद एक; helper loop में output अगले step को देता है।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: functools.reduce-style chain with a loop over async callables
# ============================================
import asyncio                                       # asyncio

async def double(x: int) -> int:
    await asyncio.sleep(0)                           # pretend I/O
    return x * 2

async def inc(x: int) -> int:
    await asyncio.sleep(0)                           # pretend I/O
    return x + 1

async def main() -> None:
    x = 5                                            # initial value
    for step in (double, inc, double):               # (5*2 + 1) * 2
        x = await step(x)                            # pipe through
    print(x)                                         # Expected: 22

asyncio.run(main())

# --- Real output (Python 3.13) ---
# 22
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using gather for dependent steps — user isn't ready yet
# await asyncio.gather(get_user(1), get_orders(user))   # NameError: 'user' is not defined

# ✅ Correct: await sequentially when data flows from one step to the next
user = await get_user(1)
orders = await get_orders(user)
```

---

## 🎯 Interview Tip (1 line)
Say: "Independent calls go in `gather`; dependent calls are chained with `await` — I split the pipeline into those two kinds of stages."

---

## 🔗 Related Questions
→ Q201 (sequential) | Q211 (waterfall) | Q086 (pipe) | Q085 (compose)
