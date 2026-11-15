---

# Q186. Build Rate Limiter (Token Bucket)
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a token bucket rate limiter: capacity `N` tokens (burst size), refilled at `rate` tokens/second. `allow()` returns `True` and spends a token if one is available, otherwise `False`.

```python
b = TokenBucket(capacity=3, rate=1)
[b.allow() for _ in range(5)]  # [True, True, True, False, False]
```

---

## 💡 Quick Concept (2 lines only)
Don't run a timer — compute the refill lazily: `tokens += elapsed * rate`, capped at capacity. Allows short bursts but enforces the average rate.
हिंदी: Timer नहीं चाहिए — हर call पर बीते समय के हिसाब से tokens जोड़ो (capacity तक) और एक token खर्च करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import time  # real clock
from typing import Callable  # type hints

class TokenBucket:
    def __init__(self, capacity: int, rate: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.capacity = capacity  # max burst size
        self.rate = rate  # tokens added per second
        self.clock = clock  # injectable clock
        self.tokens = float(capacity)  # start full
        self.last = clock()  # last refill time

    def allow(self, cost: float = 1) -> bool:
        now = self.clock()  # current time
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)  # refill, capped
        self.last = now  # remember refill time
        if self.tokens >= cost:  # enough tokens?
            self.tokens -= cost  # spend them
            return True  # request allowed
        return False  # rate limited

# ============================================
# TEST CASES
# ============================================
t = [0.0]  # fake time
b = TokenBucket(capacity=3, rate=1, clock=lambda: t[0])  # 3 burst, 1 token/sec
print([b.allow() for _ in range(5)])  # Expected: [True, True, True, False, False]
t[0] = 2.0  # 2 seconds pass -> 2 tokens
print([b.allow() for _ in range(3)])  # Expected: [True, True, False]
t[0] = 100.0  # long idle -> capped at capacity
print([b.allow() for _ in range(4)])  # Expected: [True, True, True, False]
```

---

## 🔍 Why This Works (3 lines max)
Refill is computed from elapsed time on each call, so no background thread is needed. `min(capacity, ...)` stops idle time from building an unlimited burst. O(1) time and memory per limiter.
हिंदी: हर call पर बीते समय से tokens निकलते हैं, `min(capacity)` से burst सीमित रहता है।

---

## ⚡ Alternative Solution
```python
import asyncio  # async
import threading  # lock
import time  # clock

class ThreadSafeBucket:  # thread-safe + awaitable version
    def __init__(self, capacity: int, rate: float, clock=time.monotonic) -> None:
        self.capacity, self.rate, self.clock = capacity, rate, clock  # config
        self.tokens, self.last = float(capacity), clock()  # state
        self._lock = threading.Lock()  # protect state across threads

    def allow(self) -> bool:
        with self._lock:  # one thread at a time
            now = self.clock()  # now
            self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)  # refill
            self.last = now  # update
            if self.tokens >= 1:
                self.tokens -= 1  # spend
                return True  # ok
            return False  # limited

    async def wait(self) -> None:
        while not self.allow():  # until a token is free
            await asyncio.sleep(1 / self.rate)  # wait for refill

async def main() -> None:
    b = ThreadSafeBucket(capacity=1, rate=50)  # 50 tokens/sec
    start = time.monotonic()  # begin
    for _ in range(3):
        await b.wait()  # blocks when empty
    print("3 calls took >= 0.02s:", time.monotonic() - start >= 0.02)  # Expected: True
asyncio.run(main())
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting the cap -> after 1 hour idle you allow a 3600-request burst (not run)
# self.tokens = self.tokens + (now - self.last) * self.rate     # unbounded!

# ❌ Also wrong: updating `last` only when allowed -> refill is double-counted on rejected calls

# ✅ Correct: always cap with min(capacity, ...) and always update `last` on every call
```

---

## 🎯 Interview Tip (1 line)
Say: "Token bucket allows bursts, leaky bucket smooths output, fixed window has boundary spikes — and in production I'd back it with Redis."

---

## 🔗 Related Questions
→ Q082 (throttle) | Q230 (rate limiting endpoint) | Q185 (cache with TTL) | Q203 (Semaphore)
