# 59. Rate Limiting
# हिंदी में: Rate Limiting — किसी यूज़र/IP/API key को एक तय समय में सीमित संख्या में ही requests करने देना (जैसे 100 requests प्रति मिनट)

---

## 🔵 Simple Definition (English)
**Rate limiting** controls **how many requests a client can make in a time window** (e.g. 100 requests/minute per user, or 5 login attempts per 15 minutes per IP). Requests over the limit are **rejected (HTTP 429 Too Many Requests)**, delayed, or queued.
It protects services from **abuse, overload and cost explosions**, and ensures **fair usage** among clients.

## 🔵 सरल परिभाषा (Hindi)
Rate limiting यानी हर यूज़र/IP/API key के लिए सीमा — जैसे 1 मिनट में 100 requests। सीमा पार हुई तो 429 error ("बहुत ज़्यादा requests") मिलता है।
इससे सर्वर हमलों, ओवरलोड और बेकार ख़र्च से बचता है, और सब यूज़र्स को बराबर मौका मिलता है।

---

## 🔴 Problem it Solves
Without limits:
- **Brute force:** 1M password guesses on `/login`; OTP guessing (6 digits = 1M combos).
- **Scraping:** competitors scrape all your restaurant menus and prices.
- **DoS / traffic spikes:** one buggy client in a retry loop takes down the API for everyone.
- **Cost attacks:** SMS OTP abuse ("SMS pumping") costs lakhs of rupees; LLM API endpoints cost money per call.
- **Noisy neighbours:** in a multi-tenant SaaS, one big customer starves the others.

Rate limiting enforces **fairness and protection** at the edge, the gateway and in the app.

## 🔴 यह क्यों बना? (Hindi)
बिना सीमा के: login पर लाखों password guesses, OTP guessing, competitors का पूरा डेटा scrape करना, एक ख़राब client का retry loop पूरी API गिरा देना, और OTP SMS के दुरुपयोग से लाखों का बिल।
Rate limiting बराबरी और सुरक्षा देता है — edge, gateway और ऐप, हर स्तर पर।

---

## 🟢 How it Works — Step by Step

### The flow

```
Request → identify client KEY (user id / API key / IP / IP+route / tenant)
        → look up its counter/bucket in shared store (Redis)
        → under limit?  YES → allow, update counter → handler
                        NO  → 429 Too Many Requests + Retry-After header
```

### Response headers (good API citizenship)

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30                          ← seconds to wait
RateLimit-Limit: 100                     (IETF draft standard headers)
RateLimit-Remaining: 0
RateLimit-Reset: 30
(legacy: X-RateLimit-Limit / X-RateLimit-Remaining / X-RateLimit-Reset)
```

### Algorithms (details in Topics 60–62)

```
┌──────────────────────┬───────────────────────────────────┬─────────────────────────────────┐
│ Algorithm            │ Idea                              │ Trait                           │
├──────────────────────┼───────────────────────────────────┼─────────────────────────────────┤
│ Fixed window counter │ count per minute bucket (12:01)   │ simplest; burst at edges (2×)   │
│ Sliding window log   │ store each request timestamp      │ exact; memory heavy             │
│ Sliding window       │ weighted current + previous window│ accurate & cheap ⭐ common       │
│ counter              │                                   │                                 │
│ Token bucket         │ tokens refill at rate r, cap b    │ allows bursts up to b ⭐ common  │
│ Leaky bucket         │ queue drains at constant rate     │ smooths output; no bursts       │
└──────────────────────┴───────────────────────────────────┴─────────────────────────────────┘
```

### Where to rate limit (defence in depth)

```
Layer                      Example                                 Granularity
─────────────────────────  ──────────────────────────────────────  ─────────────────────
CDN / WAF                  Cloudflare, AWS WAF rate rules          per IP, bot score
Load balancer / gateway    Nginx limit_req, Kong, AWS API Gateway  per IP / API key / route
Application                Redis-based limiter in Node/FastAPI     per user / tenant / action
Business logic             "max 3 OTPs per phone per hour",        per phone/card/account
                           "5 failed logins → lock 15 min"
Downstream protection      limit calls YOU make to a partner API   per dependency
```

### Choosing the key

```
Anonymous endpoints   → IP (careful: NAT/mobile carriers put many users behind one IP)
Logged-in endpoints   → user id
Public API            → API key / client id (+ plan tier: free 60/min, pro 1000/min)
Multi-tenant SaaS     → tenant id (fairness between customers)
Sensitive actions     → phone number / email / card (OTP, password reset, payments)
Combine: per-IP AND per-account for login (stop distributed + targeted attacks)
```

### Distributed rate limiting

```
4 API instances with in-memory counters → real limit = 4× intended ❌
Shared Redis counters + atomic ops (INCR / Lua) → one global limit ✅
At huge scale: local token buckets synced periodically, or a dedicated rate-limit service
(Envoy global rate limit service, Lyft ratelimit) — trade exactness for latency.
Fail open or closed if Redis is down? → usually fail OPEN for general APIs (availability),
fail CLOSED for security-critical limits (OTP, login).
```

### Client side: be a good citizen
```
Respect 429 + Retry-After; exponential backoff + jitter; don't retry non-idempotent requests blindly;
debounce search input; batch requests; cache responses.
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर request से एक key बनाओ — user id, API key, IP, या phone number।
2. Redis में उस key का counter/bucket देखो; सीमा के अंदर तो अनुमति और counter बढ़ाओ।
3. सीमा पार → 429 + `Retry-After` header भेजो।
4. कई सर्वर हों तो counters Redis में (साझा) रखो, नहीं तो असली सीमा 4 गुना हो जाएगी।
5. कई परतों पर लगाओ: CDN/WAF (IP), gateway (API key), ऐप (user), और business नियम (एक phone पर 3 OTP/घंटा)।

---

## 🟡 Real World Example

**GitHub API** — 5,000 requests/hour for authenticated users and 60/hour unauthenticated, with `X-RateLimit-*` headers. It also has secondary limits for abusive concurrency.

**Twitter/X (2023)** — temporarily imposed read limits on posts per day per account to fight scraping, showing that rate limiting is a business lever, not just a technical one.

**OTP/SMS pumping fraud** — attackers trigger thousands of OTP SMS to premium-rate numbers. Companies like Twitter reported losing millions of dollars a year to it. Indian startups add per-phone, per-IP and per-device OTP limits plus CAPTCHA.

**Stripe** — uses multiple limiters (request rate, concurrency, fleet-wide load shedder) and has written about prioritizing critical traffic (payments) over non-critical traffic during overload.

**IRCTC Tatkal** — limits on bookings per user per day and session-level throttles at 10 AM fight bots.

## 🟡 Real Example Hindi में
GitHub API logged-in यूज़र को 5,000 requests/घंटा देती है और headers में बचा हुआ बताती है। Twitter ने 2023 में scraping रोकने के लिए रोज़ पढ़े जाने वाले posts की सीमा लगाई।
OTP SMS fraud में हैकर हज़ारों OTP भिजवाकर करोड़ों का नुक़सान कराते हैं — इसलिए एक phone/IP/device पर OTP की सीमा और CAPTCHA ज़रूरी है।

---

## 🟠 My Stack Example

### Nginx — per-IP limits at the edge
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_status 429;

location /api/      { limit_req zone=api burst=40 nodelay; proxy_pass http://api; }
location /auth/login { limit_req zone=login burst=5;        proxy_pass http://api; }
```

### Node.js — Redis-backed limiter per user (rate-limiter-flexible)
```js
import { RateLimiterRedis } from 'rate-limiter-flexible';

const apiLimiter = new RateLimiterRedis({ storeClient: redis, keyPrefix: 'rl:api', points: 100, duration: 60 });
const otpPerPhone = new RateLimiterRedis({ storeClient: redis, keyPrefix: 'rl:otp:phone', points: 3, duration: 3600 });
const otpPerIp    = new RateLimiterRedis({ storeClient: redis, keyPrefix: 'rl:otp:ip', points: 10, duration: 3600 });

const limit = (limiter, keyFn) => async (req, res, next) => {
  try {
    const r = await limiter.consume(keyFn(req));
    res.set({ 'RateLimit-Limit': limiter.points, 'RateLimit-Remaining': r.remainingPoints,
              'RateLimit-Reset': Math.ceil(r.msBeforeNext / 1000) });
    next();
  } catch (r) {
    if (r instanceof Error) return next();                 // Redis down → fail open (general API)
    res.set('Retry-After', String(Math.ceil(r.msBeforeNext / 1000)));
    res.status(429).json({ error: 'RATE_LIMITED' });
  }
};

app.use('/api', authenticate, limit(apiLimiter, (req) => req.user.id));
app.post('/auth/otp',
  limit(otpPerIp, (req) => req.ip),
  limit(otpPerPhone, (req) => req.body.phone),           // business limit
  sendOtp);
```

### Login brute-force protection (per account + per IP, lockout)
```js
const loginFails = new RateLimiterRedis({ storeClient: redis, keyPrefix: 'rl:loginfail', points: 5, duration: 900, blockDuration: 900 });
app.post('/auth/login', async (req, res) => {
  const key = `${req.body.email}:${req.ip}`;
  const status = await loginFails.get(key);
  if (status && status.consumedPoints >= 5) return res.status(429).json({ error: 'TOO_MANY_ATTEMPTS' });
  const user = await verifyCredentials(req.body.email, req.body.password);
  if (!user) { await loginFails.consume(key).catch(() => {}); return res.status(401).end(); }
  await loginFails.delete(key);
  // ...issue tokens
});
```

### FastAPI — slowapi for per-IP + a small Redis helper for per-phone
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_URL)
app.state.limiter = limiter

async def hit(key: str, limit: int, window: int) -> bool:
    n = await r.incr(key)
    if n == 1:
        await r.expire(key, window)
    return n <= limit

@app.post("/auth/otp")
@limiter.limit("10/hour")                                   # per IP
async def send_otp(request: Request, body: OtpIn):
    if not await hit(f"rl:otp:{body.phone}", 3, 3600):      # per phone (business rule)
        raise HTTPException(429, "Too many OTP requests", headers={"Retry-After": "3600"})
    ...
```

### Tiered limits for a public API (by plan)
```js
const PLAN_LIMITS = { free: 60, pro: 1000, enterprise: 10000 };   // per minute
const limiters = Object.fromEntries(Object.entries(PLAN_LIMITS).map(([plan, pts]) =>
  [plan, new RateLimiterRedis({ storeClient: redis, keyPrefix: `rl:plan:${plan}`, points: pts, duration: 60 })]));
app.use('/v1', apiKeyAuth, (req, res, next) => limit(limiters[req.client.plan], (r) => r.client.id)(req, res, next));
```

### React Native / Next.js client
```ts
api.interceptors.response.use(undefined, async (err) => {
  if (err.response?.status === 429) {
    const wait = Number(err.response.headers['retry-after'] ?? 2) * 1000;
    await sleep(wait + Math.random() * 500);              // backoff + jitter
    return api(err.config);                               // only for idempotent requests!
  }
  throw err;
});
// Debounce search, disable "Resend OTP" button with a countdown (matches server limit)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is rate limiting and why is it important?**
A1: Restricting the number of requests a client (identified by user, API key, IP or tenant) can make in a period, and rejecting or delaying the excess with 429. It protects against brute force, scraping and DoS, prevents one client from monopolizing resources, controls costs (SMS, LLM calls), shields downstream dependencies, and enforces business plans or quotas.

**Q2: How do you implement rate limiting across multiple servers?**
A2: Keep counters or buckets in a shared, fast store (usually Redis) and update them atomically (INCR with EXPIRE, MULTI, or a Lua script for token bucket or sliding window), keyed by client identity and route. Use Redis Cluster or sharding at scale. For very high scale or low latency, use local in-memory buckets with periodic synchronization or a dedicated global rate-limit service, accepting slight inaccuracy. Decide the fail-open vs fail-closed behaviour if the store is unavailable.

**Q3: What should the API return when a client is rate-limited?**
A3: HTTP 429 Too Many Requests with a `Retry-After` header (seconds or a date), and ideally `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset` (or X- variants) on all responses so clients can self-throttle, plus a clear error body. Clients should back off with jitter and retry only idempotent requests.

**Q4: Rate limit by IP or by user? What are the pitfalls?**
A4: By user or API key for authenticated traffic, since it's accurate and fair. By IP for anonymous endpoints, combined with other signals. IP pitfalls: many legitimate users share one IP (mobile carrier NAT, offices, colleges), while attackers rotate IPs via botnets or proxies. Behind proxies you must use the real client IP (trusted X-Forwarded-For). For sensitive flows, combine per-IP, per-account and per-device limits with CAPTCHA and anomaly detection.

**Q5: How would you protect an OTP endpoint from abuse?**
A5: Layered limits: per phone number (e.g. 3 per hour, with increasing cooldowns), per IP and per device fingerprint, plus a global circuit breaker on SMS spend. Add CAPTCHA or app attestation (Play Integrity, App Attest) after thresholds, block premium or high-risk country prefixes, and limit verification attempts per OTP (e.g. 5 tries, then invalidate). Use short OTP expiry, monitor delivery and conversion ratios to detect SMS pumping, and consider WhatsApp or flash-call alternatives.

---

## 🔷 Trade-offs
✅ Advantages:
- Protects availability, security, cost; enables fair multi-tenancy and paid tiers.

❌ Disadvantages:
- Can block legitimate users (shared IPs, spikes) → bad UX if too strict.
- Distributed limiting adds latency and a dependency (Redis).
- Exact global limits are expensive; approximations allow small overshoot.
- Attackers adapt (IP rotation) → needs layered defenses.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rate limit | Max requests per time window | समय में अधिकतम requests |
| 429 Too Many Requests | Status for exceeded limit | सीमा पार होने का status |
| Retry-After | When to retry | कब दोबारा कोशिश करें |
| Throttling | Slowing/limiting requests | requests धीमी करना |
| Quota | Long-period allowance (per day/month) | लंबे समय की सीमा |
| Burst | Short spike above average rate | अचानक तेज़ी |
| Fail open / closed | Allow / deny when limiter fails | limiter ख़राब हो तो अनुमति / मना |
| Brute force | Trying many guesses | बार-बार अंदाज़े से कोशिश |
| SMS pumping | OTP abuse fraud | OTP SMS का धोखा |

---

## ⚡ 3-Line Summary
**English:**
1. Rate limiting caps requests per key (user/API key/IP/tenant) per window; excess gets 429 + Retry-After.
2. Apply in layers (CDN/WAF, gateway/Nginx, app with Redis, business rules like OTP per phone).
3. Use shared atomic counters for distributed limits; pick algorithms (fixed/sliding window, token/leaky bucket) per need.

**Hindi:**
1. Rate limiting = हर key (user/IP/API key) के लिए समय में सीमित requests; ज़्यादा पर 429 + Retry-After।
2. कई परतों पर लगाओ: CDN, Nginx, Redis वाला ऐप limiter, और business नियम।
3. कई सर्वरों के लिए Redis में atomic counters; ज़रूरत के हिसाब से algorithm चुनो।

---

## ➡️ Next Topic Suggestion
**60. Token Bucket Algorithm** — The most widely used rate limiting algorithm (AWS, Stripe, Nginx-like burst behaviour). Next: how tokens refill, how bursts work, and a Redis Lua implementation.
