# 109. Rate Limiting in Express
# हिंदी में: Rate Limiting — API Abuse रोकना

---

## 🔵 Simple Definition (English)
**Rate limiting** restricts how many requests a client (identified by IP, API key, or user ID) can make to your API within a time window (e.g., 100 requests per 15 minutes). It protects servers from abuse, brute-force attacks, and accidental overload, and ensures fair resource usage across clients.

## 🔵 सरल परिभाषा (Hindi)
**Rate limiting** यह limit करता है कि एक client (IP, API key, या user ID से identify) कितनी requests एक time window में भेज सकता है (जैसे 15 minutes में 100 requests)। ये server को abuse, brute-force attacks, और accidental overload से बचाता है, और सभी clients के बीच fair resource usage ensure करता है।

---

## 🔴 Problem it Solves
Without rate limiting, a single malicious or buggy client can send thousands of requests per second to an endpoint — a login endpoint could be brute-forced trying millions of password combinations; a search API could be scraped relentlessly by bots; a buggy frontend retry loop could hammer the backend. This can degrade performance for all legitimate users, increase infra costs, or bring the server down entirely (a DoS-like effect even without malicious intent). Rate limiting caps request frequency per client, protecting shared infrastructure.

## 🔴 यह क्यों बना? (Hindi)
Rate limiting के बिना, एक malicious या buggy client हज़ारों requests per second किसी endpoint को भेज सकता है — login endpoint पर millions password combinations का brute-force हो सकता है; search API को bots relentlessly scrape कर सकते हैं; एक buggy frontend retry loop backend को hammer कर सकता है। ये सभी legitimate users के लिए performance degrade कर सकता है, infra cost बढ़ा सकता है, या server को पूरी तरह down कर सकता है (malicious intent न होने पर भी DoS जैसा effect)। Rate limiting हर client की request frequency cap करता है, shared infrastructure को protect करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Middleware intercepts each incoming request and identifies the client (usually by IP address, or API key/user ID for authenticated routes).
Step 2 → It maintains a counter per client, tracked in-memory (for single-server apps) or in a shared store like Redis (for multi-server/distributed apps).
Step 3 → On each request, the counter is incremented; if it exceeds the configured limit within the time window, the request is rejected with `429 Too Many Requests`.
Step 4 → After the time window expires (sliding or fixed window), the counter resets, allowing new requests.
Step 5 → Response headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`) inform the client how many requests remain and when they can retry.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Middleware हर incoming request को intercept करके client को identify करता है (usually IP address, या authenticated routes के लिए API key/user ID)।
Step 2 → ये per-client counter maintain करता है, in-memory (single-server apps के लिए) या Redis जैसे shared store में (multi-server/distributed apps के लिए)।
Step 3 → हर request पर counter increment होता है; अगर configured limit time window में exceed हो जाए, तो request `429 Too Many Requests` के साथ reject हो जाती है।
Step 4 → Time window (sliding या fixed) खत्म होने पर counter reset होता है, नई requests allow होती हैं।
Step 5 → Response headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`) client को बताते हैं कि कितनी requests बची हैं और कब retry करना है।

---

## 🟡 Real World Example
**Zomato login/OTP endpoint:** `/api/auth/send-otp` is rate-limited to 3 requests per phone number per 10 minutes. Without this, an attacker (or a buggy script) could trigger thousands of OTP SMS messages, running up SMS gateway costs (each SMS costs money) and potentially overwhelming the OTP service. Zomato also rate-limits the general `/api/*` traffic per IP to prevent scraping of restaurant/menu data by competitors' bots. Rate limit responses include `Retry-After: 120` telling the client exactly when to try again.

## 🟡 Real Example Hindi mein
**Zomato login/OTP endpoint:** `/api/auth/send-otp` हर phone number के लिए 10 minutes में 3 requests तक rate-limited है। इसके बिना, कोई attacker (या buggy script) हज़ारों OTP SMS messages trigger कर सकता था, SMS gateway cost बढ़ती (हर SMS का पैसा लगता है) और OTP service overwhelm हो सकती थी। Zomato general `/api/*` traffic को भी per-IP rate-limit करता है ताकि competitors के bots restaurant/menu data scrape न कर सकें। Rate limit response में `Retry-After: 120` होता है जो client को exactly बताता है कि कब retry करना है।

---

## 💻 Code Example — Basic

```javascript
// rate-limit-basic.js
const express = require('express');
const rateLimit = require('express-rate-limit'); // npm install express-rate-limit

const app = express();

// Create a basic rate limiter: 100 requests per 15 minutes per IP
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes in milliseconds
  max: 100, // max 100 requests per window per client (IP by default)
  message: { error: 'Too many requests, please try again later.' }, // custom error body
  standardHeaders: true, // return RateLimit-* headers (modern standard)
  legacyHeaders: false, // disable old X-RateLimit-* headers
});

// Apply to all routes
app.use(limiter);

app.get('/api/products', (req, res) => {
  res.json({ products: ['item1', 'item2'] }); // counts toward the 100/15min limit
});

app.listen(3000, () => console.log('Server with global rate limiting on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// rate-limit-advanced.js — Redis-backed distributed rate limiting + per-route limits
const express = require('express');
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis'); // npm install rate-limit-redis
const Redis = require('ioredis'); // npm install ioredis

const app = express();
app.use(express.json());

const redisClient = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

// ─── 1. SHARED STORE — essential when running multiple server instances ──────
// Without Redis, each server instance has its own in-memory counter, so a
// client could get 100 req/15min PER instance behind a load balancer (bypass!)
function createLimiter({ windowMs, max, prefix }) {
  return rateLimit({
    windowMs,
    max,
    standardHeaders: true,
    legacyHeaders: false,
    store: new RedisStore({
      sendCommand: (...args) => redisClient.call(...args), // delegate to ioredis
      prefix: `rl:${prefix}:`, // namespace keys per limiter type
    }),
    keyGenerator: (req) => req.ip, // identify client by IP (could use req.user.id for auth routes)
    handler: (req, res) => {
      res.status(429).json({
        error: 'Rate limit exceeded',
        retryAfter: res.getHeader('Retry-After'), // seconds until reset
      });
    },
  });
}

// ─── 2. STRICT LIMIT for sensitive auth endpoints (brute-force protection) ────
const authLimiter = createLimiter({ windowMs: 10 * 60 * 1000, max: 5, prefix: 'auth' });

// ─── 3. LOOSER LIMIT for general API browsing ─────────────────────────────────
const apiLimiter = createLimiter({ windowMs: 15 * 60 * 1000, max: 300, prefix: 'api' });

// ─── 4. PER-USER LIMIT for authenticated routes (after auth middleware sets req.user)
const perUserLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 20, // 20 requests per minute per logged-in user
  keyGenerator: (req) => req.user?.id || req.ip, // key by user id if authenticated
  standardHeaders: true,
});

app.post('/auth/login', authLimiter, (req, res) => {
  res.json({ message: 'Login attempt processed' }); // only 5 attempts per 10 min per IP
});

app.use('/api', apiLimiter); // general API limit

app.get('/api/orders', perUserLimiter, (req, res) => {
  req.user = { id: 'user_42' }; // simulated auth
  res.json({ orders: [] });
});

app.listen(4000, () => console.log('Distributed rate-limited API running on port 4000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const rateLimit = require('express-rate-limit');
const app = express();

// Global baseline limiter for all routes
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 500 }));

// Stricter limiter specifically for payment-related routes (Razorpay-style)
const paymentLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 10, // only 10 payment attempts per minute per IP
  message: { error: 'Too many payment attempts, slow down.' },
});

app.post('/api/payments/charge', paymentLimiter, async (req, res) => {
  // process payment — protected from rapid repeated charge attempts
  res.json({ status: 'processing' });
});

app.listen(5000, () => console.log('Payment API with tiered rate limiting running'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using in-memory store (default) when running multiple server instances behind a load balancer
✅ Correct: Use a shared store (Redis) so the rate limit counter is consistent across all instances — otherwise each instance allows its own full quota, multiplying the effective limit.

```javascript
// Wrong — each of 4 server instances has its own in-memory counter
// Client effectively gets 100 * 4 = 400 requests/15min across the cluster
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

// Right — shared Redis store enforces the true global limit
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  store: new RedisStore({ sendCommand: (...args) => redisClient.call(...args) }),
}));
```

❌ Mistake 2: Rate limiting by IP alone when many users share one IP (corporate NAT, mobile carrier-grade NAT)
✅ Correct: For authenticated routes, key by `user.id` instead of (or in addition to) IP, so one heavy user doesn't block everyone else on the same NAT'd IP.

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const rateLimit = require('express-rate-limit');
const app = express();

const limiter = rateLimit({ windowMs: 60000, max: 2 });
app.use('/api', limiter);

app.get('/api/a', (req, res) => res.send('a'));
app.get('/api/b', (req, res) => res.send('b'));
app.listen(3000);
```
If a client calls `/api/a` twice then `/api/b` once within 60 seconds, what happens on the third call?

Answer: The third call (`/api/b`) gets **429 Too Many Requests**. The rate limiter is mounted on the `/api` path prefix, meaning the counter is shared across ALL routes under `/api`, not per individual route. So calling `/api/a` twice already consumes the full quota of `max: 2` for that client within the window — any subsequent request to any `/api/*` route, including a different endpoint like `/api/b`, is blocked until the window resets. This is a common misunderstanding — rate limits are scoped to where the middleware is mounted, not to each specific route unless separate limiter instances are applied per-route.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between fixed window and sliding window rate limiting algorithms?
A1: **Fixed window**: counts requests in discrete time blocks (e.g., 12:00-12:15). Simple but has a burst problem at window boundaries — a client could send `max` requests at 12:14:59 and another `max` at 12:15:01, doubling the effective rate briefly. **Sliding window** (or sliding window log/counter): continuously tracks the rolling time window, smoothing out the boundary burst issue, giving more accurate rate enforcement at the cost of slightly more computation/memory.

Q2: Why is Redis commonly used as the rate limiter store instead of in-memory?
A2: In-memory counters (plain JS objects/Maps) live inside a single Node.js process. If the app runs multiple instances (horizontal scaling, PM2 cluster mode, Kubernetes pods) behind a load balancer, each instance has its OWN counter — a client's requests get distributed across instances, effectively multiplying their real limit by the number of instances. Redis provides a single shared, atomic counter all instances read/write to, enforcing the true global limit.

Q3: How should you rate-limit a login endpoint differently from a general browsing endpoint?
A3: Login/auth endpoints need much stricter limits (e.g., 5 attempts per 10-15 minutes per IP/username) to prevent brute-force password guessing, since each attempt is a security-sensitive action. General browsing/read endpoints can have looser limits (hundreds per 15 min) since the risk is mostly about load, not security exploitation. Use separate `rateLimit()` instances with different `windowMs`/`max` per route group.

Q4: What HTTP status code and headers should a rate-limited response include?
A4: Status `429 Too Many Requests`. Headers should include `Retry-After` (seconds until the client can retry) and ideally `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` (or legacy `X-RateLimit-*` equivalents) so well-behaved clients can back off intelligently instead of blindly retrying.

Q5: How would you rate-limit by API key instead of IP address?
A5: Use the `keyGenerator` option to extract the API key from the request (e.g., `req.headers['x-api-key']`) instead of defaulting to `req.ip`: `rateLimit({ keyGenerator: (req) => req.headers['x-api-key'] || req.ip })`. This allows different limits per API key/tier (e.g., free tier gets 100 req/day, paid tier gets 10,000 req/day) — often implemented by looking up the key's plan and dynamically setting `max` via a custom middleware wrapping the limiter.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Public-facing APIs that could be scraped, abused, or brute-forced (login, OTP, payment endpoints)
- Protecting shared infrastructure from a single noisy client degrading service for everyone
- Enforcing tiered API usage plans (free vs paid tiers with different quotas)

❌ Avoid when:
- Internal service-to-service calls within a trusted private network where throughput, not abuse prevention, is the concern (use different mechanisms like circuit breakers/backpressure instead)
- The limiting logic needs extremely complex business rules beyond simple time-window counting — consider a dedicated API gateway (Kong, AWS API Gateway) instead of hand-rolled middleware

---

## 📊 Visual Diagram
```
RATE LIMITING FLOW (per IP, 5 req / 10 min):

  Request 1 ──▶ counter=1 ──▶ 200 OK   (4 remaining)
  Request 2 ──▶ counter=2 ──▶ 200 OK   (3 remaining)
  Request 3 ──▶ counter=3 ──▶ 200 OK   (2 remaining)
  Request 4 ──▶ counter=4 ──▶ 200 OK   (1 remaining)
  Request 5 ──▶ counter=5 ──▶ 200 OK   (0 remaining)
  Request 6 ──▶ counter=6 ──▶ 429 Too Many Requests (Retry-After: 300s)

  ... 10 minutes pass, window resets ...

  Request 7 ──▶ counter=1 ──▶ 200 OK   (4 remaining)

MULTI-SERVER WITHOUT SHARED STORE (the bug):
  Server A (in-memory counter) ──▶ allows 5
  Server B (in-memory counter) ──▶ allows another 5
  = client effectively gets 10, not 5   ❌

MULTI-SERVER WITH REDIS (correct):
  Server A ──┐
             ├──▶ Redis (single shared counter) ──▶ enforces true limit of 5 ✅
  Server B ──┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rate Limiting | Capping requests per client per time window | Time window में requests की सीमा |
| windowMs | Duration of the counting window in ms | Window की duration (ms में) |
| 429 | HTTP status for too many requests | बहुत ज़्यादा requests वाला status |
| keyGenerator | Function to identify the client (IP/user/key) | Client identify करने का function |
| Fixed window | Counts requests in discrete time blocks | Fixed time blocks में counting |
| Sliding window | Continuous rolling-time rate tracking | Continuous rolling window tracking |
| Retry-After | Header telling client when to retry | कब retry करें बताने वाला header |

---

## ⚡ 3-Line Summary
English:
1. Rate limiting caps how many requests a client can make in a time window, protecting against brute-force, scraping, and overload.
2. Use `express-rate-limit` with an in-memory store for single-instance apps, Redis-backed store for multi-instance/distributed deployments.
3. Apply stricter limits to sensitive routes (login, OTP, payments) and looser limits for general browsing, keying by user ID for authenticated routes instead of just IP.

Hindi:
1. Rate limiting client की requests को time window में cap करता है, brute-force, scraping, और overload से protect करता है।
2. Single-instance apps के लिए in-memory store, multi-instance/distributed deployments के लिए Redis-backed store use करो `express-rate-limit` के साथ।
3. Sensitive routes (login, OTP, payments) पर strict limits लगाओ और general browsing पर loose limits, authenticated routes में IP के बदले user ID से key करो।

---

## ➡️ Next Topic
**110. Cookie Parser** — Parsing and reading cookies from incoming requests in Express।
