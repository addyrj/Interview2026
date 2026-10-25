# 136. Rate Limiting — Advanced
# हिंदी में: Rate Limiting — Advanced

---

## 🔵 Simple Definition (English)
**Advanced rate limiting** goes beyond a single fixed-window counter — it uses algorithms like **sliding window**, **token bucket**, and **distributed stores (Redis)** to limit requests per user/IP/API-key across multiple server instances, with different limits per endpoint or user tier.

## 🔵 सरल परिभाषा (Hindi)
**Advanced rate limiting** सिर्फ एक fixed-window counter से आगे जाती है — यह **sliding window**, **token bucket** algorithms और **distributed stores (Redis)** use करती है ताकि multiple server instances में user/IP/API-key के according requests limit हों, हर endpoint या user tier के लिए अलग limits के साथ।

---

## 🔴 Problem it Solves
A basic in-memory rate limiter (storing counts in a JS object) breaks the moment you run multiple server instances (load balanced) — each instance has its own counter, so a user could get 5x the allowed limit by hitting different instances. Also, simple fixed-window limiters have a "boundary burst" flaw: a user could send max requests at the very end of one window and max requests at the very start of the next, doubling the effective burst. Advanced rate limiting with Redis (shared store) and sliding-window/token-bucket algorithms solves both problems, plus allows per-tier limits (free vs paid users).

## 🔴 यह क्यों बना? (Hindi)
Basic in-memory rate limiter multiple server instances में टूट जाता है — हर instance का अपना counter होता है, user अलग instances hit करके limit से 5x ज़्यादा requests भेज सकता है। Simple fixed-window limiters में "boundary burst" flaw भी है। Advanced rate limiting Redis (shared store) और sliding-window/token-bucket algorithms से दोनों problems solve करता है, plus per-tier limits (free vs paid users) allow करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Choose algorithm: **Fixed window** (simple, boundary burst issue), **Sliding window log** (accurate, memory-heavy), **Sliding window counter** (good balance), **Token bucket** (allows bursts, refills over time), **Leaky bucket** (smooths output rate)
Step 2 → Use a shared store (Redis) instead of in-memory, so all server instances see the same counters
Step 3 → Key the limit by identity: IP for anonymous users, API key/user ID for authenticated users (more accurate, avoids shared-IP false positives like office NAT)
Step 4 → Define multiple limit tiers: e.g., free tier 100 req/hour, paid tier 10,000 req/hour, checked by looking up the user's plan
Step 5 → Apply DIFFERENT limits per endpoint: login (strict, 5/15min to prevent brute force) vs general API reads (generous, 1000/hour)
Step 6 → Return `429 Too Many Requests` with `Retry-After` and `X-RateLimit-Remaining` headers so clients can back off gracefully
Step 7 → Implement token-bucket for burst-tolerant APIs (allow short bursts, but average rate stays capped over time)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Algorithm चुनो: Fixed window, Sliding window, Token bucket, Leaky bucket
Step 2 → Shared store (Redis) use करो, in-memory नहीं
Step 3 → Identity से key करो: IP या user ID/API key
Step 4 → Multiple limit tiers define करो (free vs paid)
Step 5 → हर endpoint के लिए अलग limits apply करो
Step 6 → `429` के साथ `Retry-After`, `X-RateLimit-Remaining` headers दो
Step 7 → Burst-tolerant APIs के लिए token-bucket implement करो

---

## 🟡 Real World Example
**Razorpay's payment API:** Different rate limits per plan — a startup on the free tier gets 100 requests/minute, an enterprise client gets 10,000 requests/minute, tracked via their API key in Redis (shared across all API gateway instances globally). The login endpoint has a MUCH stricter limit (5 attempts per 15 minutes per IP+email combo) to prevent credential-stuffing attacks, completely separate from the generous general API limit. When a client exceeds their limit, Razorpay returns `429` with `Retry-After: 42` telling exactly how many seconds to wait.

## 🟡 Real Example Hindi mein
**Razorpay का payment API:** हर plan के लिए अलग rate limits — free tier 100 req/min, enterprise client 10,000 req/min, Redis में track होता है सभी API gateway instances में shared। Login endpoint पर बहुत strict limit है (5 attempts/15 min) credential-stuffing से बचने के लिए। Limit exceed होने पर `429` के साथ `Retry-After` header मिलता है।

---

## 💻 Code Example — Basic

```javascript
// ratelimit-basic.js — fixed window counter with Redis (shared across instances)
// Run with: node ratelimit-basic.js (requires Redis running locally)

const { createClient } = require('redis');  // npm install redis

async function main() {
  const redis = createClient();
  await redis.connect();

  // ─── FIXED WINDOW RATE LIMITER ────────────────────────────────────────────
  async function isAllowed(key, limit, windowSeconds) {
    const redisKey = `ratelimit:${key}`;

    // INCR atomically increments the counter (creates it at 0 if not exists)
    const count = await redis.incr(redisKey);

    if (count === 1) {
      // First request in this window — set expiry for the window duration
      await redis.expire(redisKey, windowSeconds);
    }

    return count <= limit;  // allowed if under the limit
  }

  // Simulate 7 requests from the same user within a 10-second window, limit = 5
  for (let i = 1; i <= 7; i++) {
    const allowed = await isAllowed('user:42', 5, 10);
    console.log(`Request ${i}: ${allowed ? 'ALLOWED' : 'BLOCKED (429)'}`);
  }
  // Requests 1-5: ALLOWED, Requests 6-7: BLOCKED

  await redis.quit();
}

main().catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// ratelimit-advanced.js — sliding window counter + token bucket algorithms

// ─── 1. SLIDING WINDOW COUNTER (more accurate than fixed window) ────────────
// Combines current + previous window counts, weighted by time elapsed —
// avoids the "boundary burst" problem of fixed windows.
async function slidingWindowAllowed(redis, key, limit, windowSeconds) {
  const now = Date.now();
  const currentWindow = Math.floor(now / 1000 / windowSeconds);
  const currentKey = `rl:${key}:${currentWindow}`;
  const previousKey = `rl:${key}:${currentWindow - 1}`;

  const currentCount = parseInt((await redis.get(currentKey)) || '0', 10);
  const previousCount = parseInt((await redis.get(previousKey)) || '0', 10);

  // Weight: how far into the current window are we? (0 = just started, 1 = ending)
  const elapsedInCurrentWindow = (now / 1000) % windowSeconds;
  const weightOfPrevious = 1 - elapsedInCurrentWindow / windowSeconds;

  // Estimated total requests in the "sliding" window
  const estimatedCount = currentCount + previousCount * weightOfPrevious;

  if (estimatedCount >= limit) return false;

  await redis.incr(currentKey);
  await redis.expire(currentKey, windowSeconds * 2);  // keep around for next window's calc
  return true;
}

// ─── 2. TOKEN BUCKET ALGORITHM (allows bursts, refills over time) ───────────
// Each user has a "bucket" of tokens; each request consumes 1 token.
// Tokens refill at a steady rate — allows short bursts up to bucket capacity.
class TokenBucket {
  constructor(capacity, refillRatePerSecond) {
    this.capacity = capacity;                  // max tokens (burst allowance)
    this.refillRate = refillRatePerSecond;      // tokens added per second
    this.buckets = new Map();                   // key -> { tokens, lastRefill }
  }

  consume(key, tokensNeeded = 1) {
    const now = Date.now();
    let bucket = this.buckets.get(key);

    if (!bucket) {
      bucket = { tokens: this.capacity, lastRefill: now };
      this.buckets.set(key, bucket);
    }

    // Refill tokens based on elapsed time since last check
    const elapsedSeconds = (now - bucket.lastRefill) / 1000;
    const refillAmount = elapsedSeconds * this.refillRate;
    bucket.tokens = Math.min(this.capacity, bucket.tokens + refillAmount);
    bucket.lastRefill = now;

    if (bucket.tokens >= tokensNeeded) {
      bucket.tokens -= tokensNeeded;
      return true;   // allowed
    }
    return false;    // not enough tokens — rate limited
  }
}

// Usage: 10-token bucket, refills 2 tokens/second → allows bursts up to 10, then throttles
const bucket = new TokenBucket(10, 2);
for (let i = 1; i <= 12; i++) {
  console.log(`Request ${i}: ${bucket.consume('user:42') ? 'ALLOWED' : 'BLOCKED'}`);
}

module.exports = { slidingWindowAllowed, TokenBucket };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — tiered rate limiting with express-rate-limit + Redis store
const express = require('express');
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const { createClient } = require('redis');

const app = express();
app.use(express.json());

const redisClient = createClient();
redisClient.connect();

// Factory: creates a rate limiter with Redis-backed shared counting
function createLimiter({ windowMs, max, message }) {
  return rateLimit({
    store: new RedisStore({ sendCommand: (...args) => redisClient.sendCommand(args) }),
    windowMs,
    max,
    standardHeaders: true,   // sends RateLimit-* headers
    legacyHeaders: false,
    message: { error: message },
    keyGenerator: (req) => req.user?.id || req.ip,  // key by user ID if authenticated, else IP
  });
}

// Strict limit for login (prevent brute force / credential stuffing)
const loginLimiter = createLimiter({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: 'Too many login attempts. Try again in 15 minutes.',
});

// Tiered limit based on user's subscription plan (checked dynamically)
function tieredLimiter(req, res, next) {
  const plan = req.user?.plan || 'free';
  const limits = { free: 100, pro: 1000, enterprise: 10000 };
  const limiter = createLimiter({
    windowMs: 60 * 60 * 1000,   // 1 hour
    max: limits[plan],
    message: `Rate limit exceeded for ${plan} plan.`,
  });
  limiter(req, res, next);
}

app.post('/auth/login', loginLimiter, (req, res) => res.json({ message: 'checked' }));
app.get('/api/data', authenticate, tieredLimiter, (req, res) => res.json({ data: [] }));

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using in-memory rate limiting with multiple server instances
```javascript
// WRONG: each PM2/Kubernetes replica has its own in-memory counter
const limiter = rateLimit({ windowMs: 60000, max: 100 });  // default in-memory store
// With 4 server instances behind a load balancer, effective limit becomes 400!

// CORRECT: use a shared store (Redis) so all instances share the same counts
const limiter = rateLimit({
  store: new RedisStore({ sendCommand: (...args) => redisClient.sendCommand(args) }),
  windowMs: 60000,
  max: 100,  // true global limit of 100, enforced across all instances
});
```

❌ Mistake 2: Rate limiting by IP only, ignoring shared-IP scenarios
```javascript
// WRONG: office/college NAT means hundreds of users share one public IP
const limiter = rateLimit({ windowMs: 60000, max: 10 });  // keyGenerator defaults to req.ip
// One legitimate user's heavy usage blocks everyone else behind the same IP!

// CORRECT: prefer authenticated identity (user ID/API key) when available, fall back to IP
const limiter = rateLimit({
  windowMs: 60000,
  max: 10,
  keyGenerator: (req) => req.user?.id || req.ip,
});
```

---

## 🧠 Tricky Interview Question

```javascript
// Fixed window: limit = 10 requests per 60-second window.
// Window boundaries at :00 and :60 seconds of each minute.
// Attacker sends 10 requests at second 59, then 10 more at second 61.
// Total: 20 requests within a 2-second span. Does the fixed-window limiter block this?
```
Answer: **No — the fixed-window algorithm allows all 20 requests**, because the first 10 land in window [0-60) and the second 10 land in the NEXT window [60-120) — each window independently stays within its limit of 10, even though only 2 seconds elapsed in real time. This is the classic "boundary burst" problem of fixed-window counters, allowing up to **2x the intended rate** right at window boundaries. A sliding-window algorithm (weighting the previous window's count based on how much it overlaps with the "true" trailing window) or a sliding-window log (tracking exact timestamps) correctly catches and blocks this burst.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between token bucket and leaky bucket algorithms?
A1: **Token bucket**: tokens accumulate up to a capacity; each request consumes a token; if the bucket has tokens, bursts are allowed immediately up to capacity, then throttled to the refill rate. **Leaky bucket**: requests are queued and processed (leaked out) at a FIXED steady rate regardless of how fast they arrive — it smooths bursts into a constant output rate rather than allowing them through immediately. Token bucket is burst-friendly (good for APIs where occasional spikes are fine); leaky bucket enforces a strictly smooth, constant rate (good for traffic shaping).

Q2: Why key rate limits by user ID/API key instead of just IP address when possible?
A2: IP-based limiting has two problems: (1) shared IPs (corporate NAT, mobile carrier CGNAT) cause many legitimate users to be bucketed together and limited as one, (2) a single malicious user can rotate IPs (via proxies/VPNs) to bypass IP-based limits entirely. Keying by authenticated identity (user ID, API key) ties the limit to the actual account, which is much harder to rotate/evade and doesn't penalize innocent users sharing an IP.

Q3: How would you implement different rate limits for different endpoints in the same app?
A3: Create separate rate limiter middleware instances with different `windowMs`/`max` config per use case, and apply each to its specific route(s): e.g., `loginLimiter` (5/15min) on `/auth/login`, `generalApiLimiter` (1000/hour) on general `/api/*` routes, `exportLimiter` (2/day) on expensive operations like bulk data export. Each limiter can use its own Redis key prefix so they don't interfere with each other's counters.

Q4: What should a rate-limited response (429) include to be client-friendly?
A4: Status code `429 Too Many Requests`, plus headers: `Retry-After: <seconds>` (how long to wait before retrying), `X-RateLimit-Limit` (the max allowed), `X-RateLimit-Remaining` (requests left in current window), `X-RateLimit-Reset` (timestamp when the window resets). A JSON body explaining the limit in human terms helps API consumers implement proper backoff/retry logic instead of hammering the endpoint blindly.

Q5: How do you rate limit WebSocket connections or long-lived connections, which don't fit the typical HTTP request/response rate-limiting model?
A5: For WebSockets, rate limit at the CONNECTION level (max connections per IP/user, e.g., using a counter incremented on connect and decremented on disconnect) and at the MESSAGE level (track message timestamps per connection, apply token-bucket logic per socket for messages/second). Libraries like `ws` combined with a custom token-bucket per-connection, or a Redis-backed sliding window keyed by connection's user ID, both work. Additionally, limit connection attempts per second (to prevent connection-flood DoS) separately from message rate once connected.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running multiple server instances/load-balanced deployments — Redis-backed shared limiting is mandatory, not optional.
- Different user tiers/endpoints need genuinely different limits (login vs general API vs expensive export operations).
- APIs that need to tolerate legitimate short bursts (token bucket) while still capping average rate.

❌ Avoid when:
- A single-instance, low-traffic internal tool where simple in-memory fixed-window limiting is genuinely sufficient — don't over-engineer.

---

## 📊 Visual Diagram

```
TOKEN BUCKET ALGORITHM:
──────────────────────────────────────────────────────────

  Bucket capacity: 10 tokens, refill rate: 2 tokens/sec

  t=0s:  [██████████] 10 tokens  → burst of 10 requests → ALL ALLOWED, bucket empty
  t=0s:  [          ]  0 tokens  → 11th request → BLOCKED (429)
  t=1s:  [██        ]  2 tokens  → (refilled 2 tokens after 1 second)
  t=1s:  [          ]  0 tokens  → 1 request consumed → ALLOWED, next BLOCKED
  t=5s:  [██████████] 10 tokens  → (fully refilled after 5 seconds) → burst allowed again

SLIDING WINDOW vs FIXED WINDOW:
  Fixed:    |----window1----|----window2----|
            [10 req @ 59s]  [10 req @ 61s]   → 20 req in 2 sec, both windows "pass" ❌
  Sliding:  weighted blend of window1 (tail) + window2 (head)
            → correctly detects 20 req in 2 sec window → BLOCKS excess ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fixed window | Counter resets at fixed time boundaries | Fixed time पर reset होने वाला counter |
| Sliding window | Weighted blend of current+previous window | Current+previous window का weighted blend |
| Token bucket | Burst-tolerant algorithm with refilling tokens | Refilling tokens वाला burst-tolerant algorithm |
| Leaky bucket | Smooths requests to a constant output rate | Requests को constant rate में smooth करना |
| Distributed rate limiting | Shared counting across multiple server instances | Multiple instances में shared counting |
| Boundary burst | Exploit at fixed-window edges doubling effective rate | Fixed-window edge का exploit |

---

## ⚡ 3-Line Summary
English:
1. Advanced rate limiting uses Redis-backed shared counters (not in-memory) so limits hold across multiple server instances.
2. Sliding-window or token-bucket algorithms fix the "boundary burst" flaw of simple fixed-window counters while allowing controlled bursts.
3. Apply different limits per endpoint (strict for login) and per user tier (free vs paid), keyed by authenticated identity when possible.

Hindi:
1. Advanced rate limiting Redis-backed shared counters use करती है ताकि limits multiple server instances में भी सही रहें।
2. Sliding-window या token-bucket algorithms fixed-window की "boundary burst" problem fix करते हैं।
3. हर endpoint और user tier के लिए अलग limits apply करो, authenticated identity से key करो।

---

## ➡️ Next Topic
**137. Input Validation + Sanitization** — Joi/Zod से request data validate और clean करना।
