---

# Q230. Rate limiting endpoint
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐⭐

---

## ❓ Question
Add rate limiting (3 requests per 10 seconds per client IP) to a FastAPI route using a dependency. Return `429` with a `Retry-After` header when exceeded. Make the clock injectable so tests are deterministic. Show a fixed-window alternative.

---

## 💡 Quick Concept (2 lines only)
Sliding window keeps timestamps per client and drops the old ones; if the count is at the limit, reject with 429 + `Retry-After`. A callable class makes a clean reusable dependency.
हिंदी: हर client के timestamps रखो, पुराने हटाओ, limit पूरी हो तो 429 और `Retry-After` भेजो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import math, time  # ceil + clock
from collections import defaultdict, deque  # per-client storage
from fastapi import FastAPI, Depends, HTTPException, Request  # web
from fastapi.testclient import TestClient  # client

class SlidingWindowLimiter:  # callable dependency
    def __init__(self, limit: int, window: float, clock=time.monotonic) -> None:  # config
        self.limit, self.window, self.clock = limit, window, clock  # store config
        self.hits: dict[str, deque[float]] = defaultdict(deque)  # timestamps per client

    def __call__(self, request: Request) -> None:  # FastAPI calls this per request
        key = request.client.host if request.client else "anon"  # identify client by IP
        now = self.clock()  # current time
        q = self.hits[key]  # that client's hits
        while q and q[0] <= now - self.window:  # drop hits older than window
            q.popleft()  # evict
        if len(q) >= self.limit:  # over limit?
            retry = math.ceil(self.window - (now - q[0]))  # seconds until a slot frees
            raise HTTPException(429, "Too Many Requests", headers={"Retry-After": str(retry)})  # reject
        q.append(now)  # record this hit

fake_now = [0.0]  # controllable clock so test is deterministic
limiter = SlidingWindowLimiter(limit=3, window=10, clock=lambda: fake_now[0])  # 3 req / 10 s

app = FastAPI()  # app

@app.get("/data", dependencies=[Depends(limiter)])  # protect route
async def data() -> dict[str, str]:  # handler
    return {"ok": "yes"}  # body

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)  # client
print([client.get("/data").status_code for _ in range(5)])  # Expected: [200, 200, 200, 429, 429]
r = client.get("/data")  # still blocked
print(r.status_code, r.headers["retry-after"])  # Expected: 429 10
fake_now[0] = 11.0  # jump time forward 11 s
print(client.get("/data").status_code)  # Expected: 200 (window slid)
```

---

## 🔍 Why This Works (3 lines max)
The deque holds hit times inside the window; `popleft()` evicts expired ones, so `len(q)` is the live count. Injecting `clock` lets tests jump time instead of sleeping. State lives in memory — per process only.
हिंदी: Clock को inject करने से test में sleep नहीं करना पड़ता; state memory में है, इसलिए multi-server पर Redis चाहिए।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: fixed window counter (simpler, allows bursts at edges) ----
class FixedWindow:  # simpler limiter
    def __init__(self, limit: int, window: int, clock) -> None:  # config
        self.limit, self.window, self.clock = limit, window, clock  # store
        self.counts: dict[tuple[str, int], int] = defaultdict(int)  # (client, bucket) -> count

    def __call__(self, request: Request) -> None:  # per request
        bucket = int(self.clock() // self.window)  # which window are we in
        key = (request.client.host, bucket)  # type: ignore[union-attr]  # counter key
        self.counts[key] += 1  # count this hit
        if self.counts[key] > self.limit:  # too many in this bucket
            raise HTTPException(429, "slow down")  # reject

fw = FixedWindow(2, 10, lambda: fake_now[0])  # 2 per 10 s
app2 = FastAPI()  # app

@app2.get("/x", dependencies=[Depends(fw)])  # route
async def x() -> str:  # handler
    return "ok"  # body

c2 = TestClient(app2)  # client
print([c2.get("/x").status_code for _ in range(3)])  # Expected: [200, 200, 429]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: global counter for ALL clients -> one noisy user blocks everybody
count = 0
# ❌ Wrong: raising a plain 500/400, or no Retry-After -> clients can't back off properly
# ❌ Wrong: in-memory dict with 4 uvicorn workers -> each worker has its own counts (limit x4)

# ✅ Correct: per-client key, status 429 + Retry-After, and Redis (INCR + EXPIRE) when running many workers
```

---

## 🎯 Interview Tip (1 line)
Say: "Per-key sliding window or token bucket; in production the counters live in Redis so all workers share them, usually at the gateway."

---

## 🔗 Related Questions
→ Q186 (token bucket) | Q222 (dependencies) | Q225 (middleware) | Q232 (error handlers)
