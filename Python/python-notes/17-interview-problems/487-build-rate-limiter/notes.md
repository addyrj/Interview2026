---

# 487. Build Rate Limiter
# हिंदी में: Rate Limiter बनाना (token bucket + sliding window)

Full runnable solution: [main.py](main.py) (TokenBucket, SlidingWindowLimiter, FastAPI dependency returning 429).

---

## 🔵 Simple Definition (English)
A rate limiter allows only a fixed number of requests per client in a time period and rejects extra ones with HTTP 429. Common algorithms are token bucket (allows bursts) and sliding window (strict count).

## 🔵 सरल परिभाषा (Hindi)
Rate limiter हर client को तय समय में सिर्फ़ तय संख्या में requests देता है और ज़्यादा होने पर HTTP 429 लौटाता है। आम algorithms हैं token bucket (burst की छूट) और sliding window (सख़्त गिनती)।

---

## 🔴 Problem it Solves
Without limits, one buggy client, a scraper or a brute-force attacker can use all your capacity. Limits protect availability, control costs (OpenAI calls) and make usage fair.

## 🔴 यह क्यों बना? (Hindi)
Limit न हो तो एक buggy client, scraper या brute-force attacker पूरी capacity खा सकता है। Limit से availability, खर्च (OpenAI calls) और निष्पक्षता सुरक्षित रहती है।

---

## 🟢 How it Works — Step by Step

```
Token bucket:
Step 1 → Bucket holds up to `capacity` tokens, refills `rate` tokens/second
Step 2 → On each request: tokens = min(capacity, tokens + elapsed*rate)
Step 3 → tokens >= 1 -> take one, allow. Else reject (429)

Sliding window:
Step 1 → Keep a deque of request timestamps per client
Step 2 → Drop timestamps older than `window` seconds
Step 3 → len(deque) >= limit -> reject, else append now and allow
```

## 🟢 कैसे काम करता है? (Hindi)
```
Token bucket:
Step 1 → Bucket में अधिकतम `capacity` tokens, हर सेकंड `rate` tokens वापस भरते हैं
Step 2 → हर request पर: tokens = min(capacity, tokens + बीता समय * rate)
Step 3 → tokens >= 1 तो एक लो और allow; नहीं तो reject (429)

Sliding window:
Step 1 → हर client के request timestamps की deque रखो
Step 2 → `window` सेकंड से पुराने timestamps हटाओ
Step 3 → len >= limit तो reject, वरना now जोड़कर allow
```

---

## 🟡 Real World Example
Razorpay-style API: 100 requests per minute per API key; login endpoint: 5 attempts per minute per IP to stop password guessing; an AI app: 20 LLM calls per user per hour to cap cost. Production keeps counters in Redis so all servers share them.

## 🟡 Real Example Hindi mein
Razorpay जैसी API: हर API key पर 100 requests/मिनट; login endpoint: password अंदाज़ा रोकने के लिए हर IP पर 5 कोशिशें/मिनट; AI app: खर्च सीमित करने के लिए हर user को 20 LLM calls/घंटा। Production में counters Redis में रखते हैं ताकि सब servers share करें।

---

## 💻 Code Example — Basic
```python
# Fixed-size token bucket with a fake clock (deterministic)
class Bucket:  # tiny token bucket
    def __init__(self, capacity: int, rate: float) -> None:  # setup
        self.capacity, self.rate = capacity, rate  # limits
        self.tokens: float = float(capacity)  # start full
        self.t: float = 0.0  # last refill time

    def allow(self, now: float) -> bool:  # now is passed in for testing
        self.tokens = min(self.capacity, self.tokens + (now - self.t) * self.rate)  # refill
        self.t = now  # remember time
        if self.tokens >= 1:  # enough tokens?
            self.tokens -= 1  # spend one
            return True  # allowed
        return False  # rejected

b = Bucket(2, 1)  # 2 burst, 1 token per second
print([b.allow(0), b.allow(0), b.allow(0), b.allow(1)])  # burst then refill
# Output: [True, True, False, True]
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: sliding window + FastAPI dependency
class SlidingWindowLimiter:
    def __init__(self, limit: int, window: float, clock=time.monotonic) -> None:
        self.limit, self.window, self.clock = limit, window, clock
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = self.clock()
        q = self.hits[key]
        while q and q[0] <= now - self.window:
            q.popleft()  # forget old requests
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True

def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    if not limiter.allow(ip):
        raise HTTPException(429, "Too Many Requests", headers={"Retry-After": "60"})
```
Real output of `python main.py`:
```
[True, True, True, False, False]
[True, True, False]
[200, 200, 200, 429, 429]
all ok
```

---

## 🟠 JavaScript vs Python Comparison
Express has `express-rate-limit`; FastAPI has `slowapi` (wraps `limits`) or a custom dependency. The algorithms are identical.

```python
# Python way
@app.get("/ping", dependencies=[Depends(rate_limit)])
def ping(): ...
```
```javascript
// JavaScript way
app.get("/ping", rateLimit({ windowMs: 60_000, max: 3 }), (req, res) => res.json({}));
```

---

## 🟠 FastAPI Connection
Use a dependency (per route) or a middleware (global). Return 429 with a `Retry-After` header so well-behaved clients back off. Behind a proxy, read the real client IP from `X-Forwarded-For` (only from a trusted proxy).

```python
@app.middleware("http")  # global limit for all routes
async def limit_all(request: Request, call_next):
    if not limiter.allow(request.client.host if request.client else "?"):
        return JSONResponse({"detail": "Too Many Requests"}, status_code=429)  # reject early
    return await call_next(request)  # continue normally
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: In-memory counters with several workers: each worker has its own count, so the real limit is `limit x workers`.
✅ Correct: shared store (Redis `INCR` + `EXPIRE`, or a Lua script).

❌ Mistake 2: Using `time.time()` for intervals; it can jump when the system clock changes.
✅ Correct: `time.monotonic()`.

```python
# Wrong
now = time.time()
# Right
now = time.monotonic()
```

❌ Mistake 3: Never deleting idle keys, so the dict grows with every IP ever seen.
✅ Correct: expire idle entries (TTL in Redis, periodic cleanup in memory).

---

## 🧠 Tricky Interview Question
A fixed window allows 100 requests per minute. Can a client send 200 requests in 2 seconds?

Answer: Yes. 100 requests at 12:00:59 and 100 more at 12:01:00 fall in different windows. This boundary burst is why sliding window or token bucket are preferred over a simple fixed window counter.

---

## ⚫ Interview Questions + Answers

Q1: Token bucket vs leaky bucket?
A1: Token bucket permits bursts up to capacity then a steady rate. Leaky bucket outputs at a constant rate (smooths traffic).

Q2: Fixed vs sliding window?
A2: Fixed is cheap but has boundary bursts. Sliding log is exact but stores timestamps; sliding counter approximates with less memory.

Q3: Distributed rate limiting?
A3: Central store (Redis) with atomic ops; accept small inaccuracy or use per-node quotas.

Q4: What status code and headers?
A4: 429 with `Retry-After`; many APIs also send `X-RateLimit-Limit/Remaining/Reset`.

Q5: What to key on?
A5: API key or user id when known, IP as fallback (NAT shares IPs), maybe per endpoint.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Public APIs, login endpoints, costly operations (LLM, SMS)

❌ Avoid when:
- Internal trusted calls where throttling only adds latency (use quotas or back-pressure instead)

---

## 📊 Visual Diagram
```
 Token bucket (capacity 3, +1/sec)
 t=0  [###]  req,req,req -> allowed   [   ]
 t=0  req -> REJECT 429
 t=2  refill 2 tokens     [## ]  -> 2 allowed

 Sliding window (limit 3 / 60s): timestamps deque [t1 t2 t3] -> 4th rejected
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rate limit | Max requests per period | समय में अधिकतम requests |
| Token bucket | Refilling allowance | भरता रहने वाला कोटा |
| Sliding window | Count in last N seconds | पिछले N सेकंड की गिनती |
| 429 | Too Many Requests | बहुत ज़्यादा requests |
| Retry-After | When to retry | कब दोबारा कोशिश करें |

---

## ⚡ 3-Line Summary
English: Rate limiters cap requests per client and answer 429 beyond the cap.
Token bucket allows bursts; sliding window is strict.
Use Redis when you run several workers.
Hindi: Rate limiter हर client की requests सीमित करता है और सीमा के बाद 429 देता है।
Token bucket burst देता है; sliding window सख़्त है।
कई workers हों तो Redis इस्तेमाल करो।

---

## ➡️ Next Topic
488. Build Email Service: after protecting the API, build a reliable service that sends templated emails with retries.

---
