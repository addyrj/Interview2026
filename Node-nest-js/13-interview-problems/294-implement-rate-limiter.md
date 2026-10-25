# 294. Implement Rate Limiter
# हिंदी में: Rate Limiter खुद बनाना (Implementation)

---

## 🔵 Simple Definition (English)
A **rate limiter** restricts how many requests a client (by IP, user, or API key) can make in a given time window, protecting your API from abuse, brute force, and overload. Common algorithms: fixed window, sliding window, token bucket, and leaky bucket.

## 🔵 सरल परिभाषा (Hindi)
**Rate limiter** यह control करता है कि एक client (IP, user, या API key से) किसी time window में कितने requests कर सकता है — यह API को abuse, brute force, और overload से बचाता है। Common algorithms: fixed window, sliding window, token bucket, leaky bucket।

---

## 🔴 Problem it Solves
Without limits, a single buggy client or malicious actor can flood your API, exhaust database connections, spike costs (3rd-party API billing), or enable brute-force attacks (password guessing, OTP guessing). Rate limiting provides fairness between users and protects backend resources from being overwhelmed.

## 🔴 यह क्यों बना? (Hindi)
Limits के बिना एक buggy client या malicious actor API को flood कर सकता है, database connections खत्म कर सकता है, costs spike कर सकता है (3rd-party API billing), या brute-force attacks (password/OTP guessing) possible बना सकता है। Rate limiting users के बीच fairness देता है और backend resources को overwhelm होने से बचाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Identify the client key (IP address, user ID, or API key) for each incoming request.
Step 2 → Choose an algorithm: **Fixed window** (count resets every N seconds — simple but bursty at boundaries), **Sliding window** (smooths out boundary bursts using weighted previous+current window), or **Token bucket** (tokens refill at a steady rate, each request consumes one — allows controlled bursts).
Step 3 → On each request, check/update the counter or token count atomically (critical in distributed systems — use Redis `INCR`+`EXPIRE` or Lua script to avoid race conditions).
Step 4 → If under the limit, allow the request and decrement/increment the counter.
Step 5 → If over the limit, reject with `429 Too Many Requests` and a `Retry-After` header.
Step 6 → In distributed deployments (multiple server instances), store counters in a shared store (Redis), not in-memory, so limits apply globally, not per-instance.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर incoming request के लिए client key पहचानो (IP address, user ID, या API key)।
Step 2 → Algorithm चुनो: **Fixed window** (हर N seconds में counter reset — simple पर boundary पर bursty), **Sliding window** (previous+current window weighted करके boundary burst smooth करता है), या **Token bucket** (tokens एक steady rate पर refill होते हैं, हर request एक token खर्च करती है — controlled bursts allow करता है)।
Step 3 → हर request पर counter/token count atomically check/update करो (distributed systems में critical — Redis `INCR`+`EXPIRE` या Lua script use करो race conditions avoid करने के लिए)।
Step 4 → Limit के अंदर हो तो request allow करो और counter update करो।
Step 5 → Limit के ऊपर हो तो `429 Too Many Requests` के साथ reject करो, `Retry-After` header दो।
Step 6 → Distributed deployments (multiple server instances) में counters shared store (Redis) में रखो, in-memory नहीं, ताकि limit globally apply हो, per-instance नहीं।

---

## 🟡 Real World Example
**Razorpay's payment API** rate-limits merchants to, say, 100 requests/second per API key to prevent any one integration from overwhelming shared infrastructure, and separately rate-limits OTP/login attempts per phone number to prevent brute force. Internally, this is implemented with Redis-backed token buckets so the limit holds true across their horizontally-scaled API gateway fleet, not just per server.

## 🟡 Real Example Hindi mein
**Razorpay का payment API** merchants को rate-limit करता है (जैसे 100 requests/second प्रति API key) ताकि कोई एक integration shared infrastructure को overwhelm न करे, और अलग से OTP/login attempts को phone number के हिसाब से rate-limit करता है brute force रोकने के लिए। Internally यह Redis-backed token buckets से implement होता है ताकि limit उनके horizontally-scaled API gateway fleet पर globally लागू हो, सिर्फ एक server पर नहीं।

---

## 💻 Code Example — Basic

```javascript
// rate-limiter-basic.js
// In-memory fixed-window rate limiter. Run: node rate-limiter-basic.js

class FixedWindowRateLimiter {
  constructor(maxRequests, windowMs) {
    this.maxRequests = maxRequests;   // e.g., 5 requests
    this.windowMs = windowMs;         // e.g., per 10000ms (10 sec)
    this.clients = new Map();         // clientKey -> { count, windowStart }
  }

  isAllowed(clientKey) {
    const now = Date.now();
    let record = this.clients.get(clientKey);

    // No record yet, or current window has expired -> start a fresh window
    if (!record || now - record.windowStart >= this.windowMs) {
      record = { count: 0, windowStart: now };
      this.clients.set(clientKey, record);
    }

    if (record.count >= this.maxRequests) {
      return false; // limit exceeded for this window
    }

    record.count++;
    return true;
  }
}

// --- Demo: simulate a client hammering an endpoint ---
const limiter = new FixedWindowRateLimiter(3, 5000); // 3 requests per 5 seconds

for (let i = 1; i <= 5; i++) {
  const allowed = limiter.isAllowed('client-ip-1');
  console.log(`Request ${i}: ${allowed ? 'ALLOWED' : 'BLOCKED (429)'}`);
}
```

## 💻 Code Example — Advanced

```javascript
// rate-limiter-advanced.js
// Production-style Redis-backed token bucket rate limiter — safe for distributed/multi-instance servers.
// npm i ioredis
const Redis = require('ioredis');
const redis = new Redis();

// Lua script makes the check-and-decrement ATOMIC, avoiding race conditions
// where two concurrent requests both read "tokens available" before either writes back.
const TOKEN_BUCKET_SCRIPT = `
  local key = KEYS[1]
  local capacity = tonumber(ARGV[1])
  local refillRate = tonumber(ARGV[2])  -- tokens per second
  local now = tonumber(ARGV[3])
  local requested = tonumber(ARGV[4])

  local bucket = redis.call('HMGET', key, 'tokens', 'timestamp')
  local tokens = tonumber(bucket[1])
  local timestamp = tonumber(bucket[2])

  if tokens == nil then
    tokens = capacity
    timestamp = now
  end

  -- Refill tokens based on elapsed time since last request
  local elapsed = math.max(0, now - timestamp)
  tokens = math.min(capacity, tokens + elapsed * refillRate)

  local allowed = 0
  if tokens >= requested then
    tokens = tokens - requested
    allowed = 1
  end

  redis.call('HMSET', key, 'tokens', tokens, 'timestamp', now)
  redis.call('EXPIRE', key, 3600) -- cleanup stale buckets eventually

  return { allowed, tokens }
`;

class TokenBucketRateLimiter {
  constructor({ capacity, refillRatePerSec }) {
    this.capacity = capacity;
    this.refillRatePerSec = refillRatePerSec;
  }

  // clientKey e.g. `ratelimit:user:123` or `ratelimit:ip:1.2.3.4`
  async isAllowed(clientKey, cost = 1) {
    const now = Date.now() / 1000; // seconds, for refill math
    const result = await redis.eval(
      TOKEN_BUCKET_SCRIPT,
      1,
      clientKey,
      this.capacity,
      this.refillRatePerSec,
      now,
      cost
    );
    const [allowed, remainingTokens] = result;
    return { allowed: allowed === 1, remainingTokens: Number(remainingTokens) };
  }
}

module.exports = { TokenBucketRateLimiter };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express middleware using the token bucket rate limiter
const express = require('express');
const { TokenBucketRateLimiter } = require('./rate-limiter-advanced');

const app = express();

// 10 requests capacity, refilling at 1 token/second (steady-state: ~1 req/sec, burst up to 10)
const limiter = new TokenBucketRateLimiter({ capacity: 10, refillRatePerSec: 1 });

function rateLimitMiddleware(req, res, next) {
  // Key by IP for anonymous endpoints, or req.user.id for authenticated ones
  const clientKey = `ratelimit:${req.ip}`;

  limiter.isAllowed(clientKey).then(({ allowed, remainingTokens }) => {
    res.set('X-RateLimit-Remaining', Math.floor(remainingTokens)); // transparency for clients
    if (!allowed) {
      res.set('Retry-After', '1'); // hint: retry after 1 second
      return res.status(429).json({ error: 'Too many requests, slow down' });
    }
    next();
  }).catch(next);
}

app.use('/api/', rateLimitMiddleware); // apply only to /api routes

app.get('/api/orders', (req, res) => {
  res.json({ orders: [] });
});

app.listen(3000, () => console.log('Rate-limited API on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Storing rate limit counters in-memory on a multi-instance deployment
✅ Correct: Use a shared store (Redis) so the limit is enforced globally, not per server instance (otherwise N instances = N× the real limit)

```javascript
// Wrong — each server instance has its own counter, defeating the limit under a load balancer
const counters = new Map(); // in-memory, per-process

// Right — shared across all instances
await redis.eval(TOKEN_BUCKET_SCRIPT, 1, key, capacity, refillRate, now, cost);
```

❌ Mistake 2: Check-then-increment without atomicity, causing race conditions under concurrent requests
✅ Correct: Use Redis `INCR` (atomic) or a Lua script, not separate `GET` then `SET` calls

```javascript
// Wrong — race condition: two requests can both read count=4 (limit 5) before either writes count=5
let count = await redis.get(key);
if (count < 5) await redis.set(key, count + 1);

// Right — INCR is atomic
const count = await redis.incr(key);
if (count === 1) await redis.expire(key, 60);
if (count > 5) { /* reject */ }
```

---

## 🧠 Tricky Interview Question

```javascript
// Fixed-window limiter: max 5 requests per 10-second window.
// A client sends 5 requests at t=9.9s (end of window 1), then 5 more at t=10.1s (start of window 2).
```
Answer: All 10 requests get through — because the fixed-window algorithm resets the count the instant the window boundary passes, a client can send `maxRequests` right before a boundary and `maxRequests` again right after, effectively doubling their allowed rate in a short burst around the boundary. This is the classic "boundary burst" flaw of fixed windows. The fix: use a **sliding window** (weight the previous window's count proportionally into the current one) or a **token bucket** (continuous refill, no hard reset boundary) — both of which smooth out this burst behavior, which is why production systems (Razorpay, Stripe) prefer token/leaky bucket over naive fixed windows.

---

## ⚫ Interview Questions + Answers

Q1: Compare fixed window, sliding window, and token bucket algorithms.
A1: Fixed window: simplest, but allows 2x burst at window boundaries. Sliding window: smooths boundaries by weighting previous window's count, more accurate but slightly more computation. Token bucket: tokens refill continuously at a fixed rate, allows controlled bursts up to bucket capacity while enforcing a long-term average rate — generally preferred in production APIs.

Q2: How do you rate-limit per-user AND per-IP simultaneously?
A2: Apply two independent rate limiter checks in the middleware chain — one keyed by `req.user.id` (if authenticated) and one keyed by `req.ip` — and reject if EITHER limit is exceeded. This protects against both a single compromised account and a single IP running many accounts.

Q3: Why use Redis instead of an in-memory counter for rate limiting in production?
A3: Production APIs run multiple instances behind a load balancer; an in-memory counter is per-process, so the "global" limit effectively multiplies by the number of instances. Redis (or similar shared store) gives a single source of truth so limits hold true cluster-wide, and Redis's atomic operations (INCR, Lua scripts) avoid race conditions.

Q4: How should a rate-limited response communicate retry timing to the client?
A4: Return HTTP 429 with a `Retry-After` header (seconds until next allowed request) and optionally `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers so well-behaved clients can back off intelligently instead of retrying immediately and making things worse.

Q5: How would you rate-limit a GraphQL API differently from REST?
A5: Since a single GraphQL request can contain many nested queries/mutations, simple request-count limiting is insufficient — you typically compute a "query cost" (based on query complexity/depth/field count) and rate-limit on cumulative cost per time window (a token bucket where each query consumes variable tokens based on its complexity), rather than treating every request as equal cost.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Public APIs, login/OTP endpoints, or any endpoint vulnerable to abuse or brute force
- Protecting expensive downstream resources (DB, 3rd-party paid APIs) from overload

❌ Avoid when:
- Purely internal, trusted service-to-service calls with their own circuit breakers/backpressure already in place
- Extremely low-traffic internal admin tools where the overhead isn't justified

---

## 📊 Visual Diagram
```
 TOKEN BUCKET:
 ┌─────────────────────────┐
 │  Bucket (capacity = 10) │  tokens refill at 1/sec continuously
 │  ●●●●●●● (7 tokens)     │
 └────────────┬────────────┘
              │ request arrives, cost = 1 token
              ▼
      tokens >= cost?
       /            \
     yes             no
      │               │
 consume token    reject (429 + Retry-After)
      │
   allow request
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fixed window | Counter resets every fixed interval | हर fixed interval में counter reset |
| Sliding window | Weighted blend of current+previous window | Current+previous window का weighted blend |
| Token bucket | Tokens refill continuously, consumed per request | Tokens continuously refill, per request खर्च होते हैं |
| Atomicity | Operation completes fully or not at all, no race | पूरा complete या बिल्कुल नहीं, race नहीं |
| 429 | HTTP status for rate-limit exceeded | Rate-limit cross होने का HTTP status |

---

## ⚡ 3-Line Summary
English: Rate limiters cap request frequency per client using fixed window, sliding window, or token bucket algorithms, with token bucket preferred for smooth burst handling. In production, counters must live in a shared atomic store (Redis + Lua/INCR) so limits hold across multiple server instances.
Hindi: Rate limiters per client request frequency को fixed window, sliding window, या token bucket algorithms से cap करते हैं, smooth burst handling के लिए token bucket preferred है। Production में counters shared atomic store (Redis + Lua/INCR) में रहने चाहिए ताकि multiple instances पर limit सही लागू हो।

---

## ➡️ Next Topic
**295. Implement LRU Cache** — building a Least-Recently-Used cache with O(1) get/put using a Map + doubly linked list.
