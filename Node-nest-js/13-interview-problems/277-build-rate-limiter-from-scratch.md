# 277. Build Rate Limiter from Scratch
# हिंदी में: शुरू से Rate Limiter बनाना

---

## 🔵 Simple Definition (English)
A **rate limiter** restricts how many requests a client (by IP, user ID, or API key) can make within a time window, protecting your API from abuse, accidental traffic spikes, and brute-force attacks. Building one from scratch means implementing the counting algorithm yourself (not just plugging in `express-rate-limit`) — a very common system-design-style interview question.

## 🔵 सरल परिभाषा (Hindi)
**Rate limiter** एक time window में client (IP, user ID, या API key) को कितनी requests करने दी जाएं, ये restrict करता है — abuse, accidental traffic spikes, और brute-force attacks से API को बचाता है। Scratch से बनाने का मतलब है counting algorithm खुद implement करना — ये एक बहुत common system-design-style interview question है।

---

## 🔴 Problem it Solves
Without rate limiting, a single misbehaving client (buggy retry loop, scraper, or malicious actor) can send unlimited requests, exhausting server resources (CPU, DB connections) and degrading service for everyone else. It also enables brute-force attacks on login endpoints (trying thousands of passwords per second). Rate limiting caps request volume per identity, protecting fairness and availability — critical for any public API, especially payment/auth endpoints.

## 🔴 यह क्यों बना? (Hindi)
Rate limiting के बिना, एक misbehaving client (buggy retry loop, scraper, malicious actor) unlimited requests भेज सकता है, server resources (CPU, DB connections) खत्म कर सकता है, सबके लिए service degrade कर सकता है। ये login endpoints पर brute-force attacks भी enable करता है। Rate limiting हर identity के लिए request volume cap करती है, fairness और availability protect करती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Choose an identity key to track: IP address, user ID, or API key.
Step 2 → Choose an algorithm:
  - **Fixed Window**: count requests in fixed clock intervals (e.g. per minute) — simple but allows bursts at window boundaries (2x limit possible right at the edge).
  - **Sliding Window Log**: store timestamp of every request, count how many fall within the last N seconds — accurate but memory-heavy at scale.
  - **Sliding Window Counter**: approximate sliding window using weighted counts from current + previous fixed window — good balance of accuracy and memory.
  - **Token Bucket**: a bucket holds tokens, refilled at a steady rate; each request consumes a token; empty bucket = rejected. Allows controlled bursts up to bucket capacity.
  - **Leaky Bucket**: similar to token bucket but processes requests at a FIXED output rate, queuing excess — smooths bursts rather than allowing them.
Step 3 → Store counters/timestamps in a fast datastore: in-memory `Map` for single-instance, **Redis** for distributed/multi-instance apps (shared state across servers).
Step 4 → On each request: check/update the counter, allow or reject (`429 Too Many Requests`) based on the limit.
Step 5 → Return informative headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After` — so well-behaved clients can back off correctly.
Step 6 → Clean up expired entries periodically (or use Redis TTL/expiry) to avoid unbounded memory growth.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Identity key चुनो: IP address, user ID, या API key।
Step 2 → Algorithm चुनो: Fixed Window, Sliding Window Log, Sliding Window Counter, Token Bucket, या Leaky Bucket।
Step 3 → Counters/timestamps fast datastore में store करो: single-instance के लिए in-memory `Map`, distributed के लिए **Redis**।
Step 4 → हर request पर counter check/update करो, limit के आधार पर allow/reject (`429`) करो।
Step 5 → Informative headers return करो: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`।
Step 6 → Expired entries periodically clean up करो, unbounded memory growth से बचने के लिए।

---

## 🟡 Real World Example
**Razorpay's** payment API uses a token-bucket rate limiter per API key: each merchant gets a bucket of, say, 100 tokens refilling at 10/second, allowing short bursts (e.g. processing a batch of 100 refunds at once) while still capping sustained load at 10 req/s. Login endpoints use a STRICTER fixed-window limiter (5 attempts per 15 minutes per IP+username combo) specifically to slow brute-force password guessing, returning `429` with a `Retry-After` header so legitimate users retrying after a typo know exactly how long to wait.

## 🟡 Real Example Hindi mein
**Razorpay** का payment API हर API key के लिए token-bucket rate limiter use करता है: हर merchant को 100 tokens का bucket मिलता है जो 10/second refill होता है, short bursts allow करता है जबकि sustained load 10 req/s तक cap करता है। Login endpoints पर STRICTER fixed-window limiter (15 मिनट में 5 attempts per IP+username) brute-force password guessing रोकने के लिए।

---

## 💻 Code Example — Basic

```javascript
// basic-rate-limiter.js — fixed window algorithm, in-memory, no dependencies
// Run: node basic-rate-limiter.js

const http = require('http');

const WINDOW_MS = 60 * 1000; // 1 minute window
const MAX_REQUESTS = 5;      // max 5 requests per window per IP

// Map: IP -> { count, windowStart }
const requestCounts = new Map();

function isRateLimited(ip) {
  const now = Date.now();
  const record = requestCounts.get(ip);

  if (!record || now - record.windowStart > WINDOW_MS) {
    // New window starts — reset the counter
    requestCounts.set(ip, { count: 1, windowStart: now });
    return false; // not limited
  }

  record.count++;
  if (record.count > MAX_REQUESTS) {
    return true; // limited — too many requests in this window
  }
  return false;
}

const server = http.createServer((req, res) => {
  const ip = req.socket.remoteAddress;

  if (isRateLimited(ip)) {
    res.writeHead(429, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Too many requests, please try again later' }));
    return;
  }

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ message: 'Request successful' }));
});

server.listen(3000, () => console.log('Rate-limited server on port 3000'));

// Test: run `for i in {1..7}; do curl http://localhost:3000; done`
// First 5 succeed, next 2 return 429 (within the same minute window)
```

## 💻 Code Example — Advanced

```javascript
// advanced-rate-limiter.js — Token Bucket algorithm, reusable middleware
// Handles bursts gracefully while enforcing a steady-state limit

class TokenBucket {
  constructor({ capacity, refillRatePerSecond }) {
    this.capacity = capacity;                   // max tokens the bucket can hold
    this.refillRatePerSecond = refillRatePerSecond;
    this.tokens = capacity;                       // start full
    this.lastRefill = Date.now();
  }

  // Refill tokens based on elapsed time since last check
  refill() {
    const now = Date.now();
    const elapsedSeconds = (now - this.lastRefill) / 1000;
    const tokensToAdd = elapsedSeconds * this.refillRatePerSecond;
    this.tokens = Math.min(this.capacity, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }

  // Try to consume 1 token; returns true if allowed, false if bucket is empty
  tryConsume() {
    this.refill();
    if (this.tokens >= 1) {
      this.tokens -= 1;
      return true;
    }
    return false;
  }

  getRemainingTokens() {
    this.refill();
    return Math.floor(this.tokens);
  }
}

// ─── Express middleware factory using Token Bucket per client ────────────
function createRateLimiter({ capacity = 10, refillRatePerSecond = 1 } = {}) {
  const buckets = new Map(); // clientKey -> TokenBucket instance

  // Periodic cleanup to prevent unbounded memory growth from one-time visitors
  setInterval(() => {
    const now = Date.now();
    for (const [key, bucket] of buckets) {
      if (now - bucket.lastRefill > 10 * 60 * 1000) buckets.delete(key); // 10 min idle
    }
  }, 5 * 60 * 1000);

  return function rateLimiterMiddleware(req, res, next) {
    const clientKey = req.user?.id || req.ip; // prefer authenticated user ID over IP

    if (!buckets.has(clientKey)) {
      buckets.set(clientKey, new TokenBucket({ capacity, refillRatePerSecond }));
    }
    const bucket = buckets.get(clientKey);

    if (bucket.tryConsume()) {
      res.setHeader('X-RateLimit-Limit', capacity);
      res.setHeader('X-RateLimit-Remaining', bucket.getRemainingTokens());
      return next();
    }

    res.setHeader('Retry-After', Math.ceil(1 / refillRatePerSecond)); // seconds until 1 token available
    res.status(429).json({ error: 'Rate limit exceeded. Please slow down.' });
  };
}

module.exports = { TokenBucket, createRateLimiter };
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { createRateLimiter } = require('./advanced-rate-limiter');

const app = express();

// Different limits for different route sensitivity levels
const generalLimiter = createRateLimiter({ capacity: 100, refillRatePerSecond: 5 }); // lenient
const authLimiter = createRateLimiter({ capacity: 5, refillRatePerSecond: 0.0056 }); // ~5 per 15 min, strict

app.use('/api/', generalLimiter);
app.post('/auth/login', authLimiter, (req, res) => {
  // ... actual login logic ...
  res.json({ message: 'Login attempt processed' });
});

app.get('/api/products', (req, res) => {
  res.json({ data: ['Laptop', 'Mouse'] });
});

app.listen(3000, () => console.log('App with tiered rate limiting on port 3000'));

// PRODUCTION NOTE: for multi-instance deployments, replace the in-memory Map
// with Redis (INCR + EXPIRE commands, or a Lua script for atomic token-bucket logic)
// so all instances share the same rate-limit state.
// npm install rate-limiter-flexible — a battle-tested library implementing
// exactly these algorithms with Redis support, if not building from scratch.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using in-memory counters in a horizontally-scaled (multi-instance) deployment
✅ Correct: In-memory state is PER PROCESS — if you run 4 Node instances behind a load balancer, each gets its own counter, effectively multiplying your real limit by 4. Use Redis for shared state across instances.

```javascript
// Wrong: works fine with 1 instance, silently allows 4x traffic with 4 instances
const counts = new Map(); // local to this process only

// Right: shared counter via Redis
// const count = await redisClient.incr(`rate:${clientKey}`);
// if (count === 1) await redisClient.expire(`rate:${clientKey}`, windowSeconds);
```

❌ Mistake 2: Fixed window algorithm allowing a 2x burst at window boundaries
✅ Correct: A client can send `MAX_REQUESTS` right at the END of window 1, then another `MAX_REQUESTS` immediately at the START of window 2 — effectively 2x the limit in a short burst. Sliding window or token bucket avoids this.

```javascript
// Wrong (fixed window flaw):
// 11:00:59 → 5 requests allowed (end of window 1)
// 11:01:00 → 5 MORE requests allowed (start of window 2)
// = 10 requests in 1 second, despite a "5 per minute" limit

// Right: sliding window counter or token bucket smooths this out,
// since tokens/weight carry over proportionally rather than resetting sharply
```

---

## 🧠 Tricky Interview Question

```javascript
// Interviewer: "Your rate limiter uses req.ip as the key. What breaks this?"
app.use((req, res, next) => {
  const key = req.ip;
  // ... rate limit logic keyed by IP ...
});
```
Answer: Several things break IP-based rate limiting: (1) **NAT/shared IPs** — an entire office or mobile carrier's users can share one public IP, so one heavy user exhausts the limit for everyone behind that IP (common complaint: "why am I rate-limited, I just started using this app?"). (2) **Behind a proxy/load balancer**, `req.ip` might show the PROXY's IP for every client unless `app.set('trust proxy', 1)` is configured to read `X-Forwarded-For` correctly — otherwise ALL traffic looks like it's from one IP (the LB), instantly hitting the limit for everyone. (3) **IP spoofing/rotation** — attackers can rotate through many IPs (via proxies/VPNs/botnets) to bypass IP-based limits entirely. Better: combine IP with authenticated user ID or API key where available, since those are harder to rotate freely.

---

## ⚫ Interview Questions + Answers

Q1: Compare Token Bucket vs Fixed Window Counter — when would you choose one over the other?
A1: Fixed Window is simpler to implement and reason about but has the boundary-burst flaw (2x limit possible at window edges). Token Bucket naturally allows controlled bursts (useful for bursty-but-legitimate traffic like batch operations) while still enforcing a steady-state average rate via the refill rate — generally preferred for APIs where occasional bursts are acceptable but sustained abuse isn't. Fixed Window is fine for simpler use cases (e.g. "max 100 requests/hour") where boundary effects are tolerable.

Q2: How would you rate-limit per API key instead of per IP, and why might that be better for a B2B API?
A2: Extract the key from `Authorization` header or a custom `X-API-Key` header, use it as the counter identity instead of `req.ip`. This is better for B2B APIs because: multiple legitimate clients/users at one company might share an office IP (NAT issue from above) but should each get their own quota based on their individual API key/subscription tier; also API keys map directly to billing/plan tiers (free tier: 100/day, paid tier: 10,000/day), which IP addresses cannot represent.

Q3: What HTTP status code and headers should a rate-limited response include?
A3: `429 Too Many Requests` is the standard status code (RFC 6585). Headers: `Retry-After` (seconds until the client should retry), `X-RateLimit-Limit` (max allowed in window), `X-RateLimit-Remaining` (how many left), `X-RateLimit-Reset` (Unix timestamp when the window resets). These let well-behaved clients implement proper backoff instead of guessing or hammering retries.

Q4: How would you implement a DISTRIBUTED rate limiter using Redis, and what race condition must you avoid?
A4: Use Redis `INCR` (atomic increment) on a key like `rate:{clientId}:{windowId}`, setting `EXPIRE` on first increment. The race condition to avoid: checking `GET` then conditionally `SET`/`INCR` separately is NOT atomic — two concurrent requests could both read "4" (under the limit of 5), both proceed, and both increment to 6, overshooting the limit. Fix: use Redis's atomic `INCR` (single command, no read-then-write gap) or a Lua script (`EVAL`) for more complex multi-step logic (like token bucket) to ensure atomicity across the check-and-update.

Q5: Should rate limiting happen at the application layer (Express middleware) or the infrastructure layer (Nginx, API Gateway, CDN)?
A5: Both, for different purposes. Infrastructure-layer limiting (Nginx `limit_req`, AWS API Gateway throttling, Cloudflare rate limiting) is cheap, fast, and blocks abusive traffic BEFORE it even reaches your Node process — ideal for coarse, IP-based DDoS-style protection. Application-layer limiting (Express middleware, as built above) is needed for business-logic-aware limits (per-user quotas, per-API-key tiers, different limits per endpoint sensitivity) that infra layers typically can't express. Production systems usually layer both: infra as the first coarse filter, app-layer for fine-grained business rules.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any public API, especially auth/login endpoints (brute-force protection)
- Protecting expensive operations (search, report generation, email/SMS sending) from abuse
- Enforcing fair usage across tiered subscription plans

❌ Avoid when:
- Internal service-to-service calls within a trusted private network with no abuse risk (though circuit breakers/timeouts still matter there)
- You've already got equivalent limiting fully handled at the infra/gateway layer and don't need finer per-user granularity

---

## 📊 Visual Diagram
```
TOKEN BUCKET ALGORITHM
───────────────────────
Bucket capacity: 10 tokens, refill rate: 2 tokens/second

Time:  0s        1s        2s        3s
Tokens: [██████████] → request×3 → [███████░░░] → +2 refill → [█████████░]
         (full)        (-3 tokens)   (7 left)      (refilled)   (9 left)

Request arrives → tryConsume():
  1. Refill based on elapsed time since last check
  2. If tokens >= 1: consume 1, ALLOW request
  3. If tokens < 1: REJECT (429), client must wait for refill

FIXED WINDOW BOUNDARY BURST PROBLEM:
  Window 1 (11:00:00-11:00:59): [█████] 5 requests used (allowed, at 11:00:59)
  Window 2 (11:01:00-11:01:59): [█████] 5 MORE requests (allowed, at 11:01:00)
  → 10 requests within 1 real second, despite "5 per minute" limit!
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Token Bucket | Algorithm allowing controlled bursts via refillable tokens | Refillable tokens से controlled bursts allow करने वाला algorithm |
| Fixed Window | Simple counter reset at fixed intervals | Fixed intervals पर reset होने वाला simple counter |
| Sliding Window | More accurate time-based counting avoiding boundary bursts | Boundary bursts से बचने वाला accurate time-based counting |
| 429 Too Many Requests | Standard rate-limit HTTP status code | Rate-limit का standard HTTP status code |
| Retry-After | Header telling client when to retry | Client को कब retry करना बताने वाला header |
| Atomic Operation | Operation that can't be interrupted mid-way (no race condition) | बीच में interrupt न होने वाला operation |

---

## ⚡ 3-Line Summary
English: 1. Rate limiters cap requests per identity (IP/user/API key) within a time window, using algorithms like fixed window, sliding window, or token bucket. 2. Token bucket is generally preferred — it allows controlled bursts while enforcing a steady-state average rate. 3. For multi-instance deployments, use Redis (with atomic operations) instead of in-memory state to share limits across all server instances.
Hindi: 1. Rate limiters हर identity (IP/user/API key) के लिए time window में requests cap करते हैं — fixed window, sliding window, या token bucket algorithms से। 2. Token bucket आम तौर पर preferred है — controlled bursts allow करता है जबकि steady-state average rate enforce करता है। 3. Multi-instance deployments में Redis (atomic operations के साथ) use करो, in-memory state नहीं, ताकि सब instances में limit shared रहे।

---

## ➡️ Next Topic
**278. Build Caching Layer (Redis)** — Redis से caching layer design और implement करना।
