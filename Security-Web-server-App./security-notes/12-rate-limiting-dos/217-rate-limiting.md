---

# 217. Rate Limiting — DDoS, Brute Force, API Abuse Prevention
# हिंदी में: Rate Limiting — Attacks से API को Protect करना
# Risk Level: ⛔ High

---

## 🔵 Simple Definition (English)
Rate limiting restricts how many requests a client can make in a given time window. Without it, attackers can brute-force login endpoints, scrape all your data, enumerate user IDs, or overwhelm your server with DDoS. Rate limiting is the primary defense against these volumetric attacks.

## 🔵 सरल परिभाषा (Hindi)
Rate limiting decide करता है कि एक client कितने requests एक time window में कर सकता है। इसके बिना attacker login endpoint को brute-force कर सकता है, सारा data scrape कर सकता है, या server को DDoS से crash कर सकता है। Rate limiting इन सभी attacks की primary defense है।

---

## ⚠️ The Attack / Threat

```
ATTACK 1 — Brute Force Login:
for (password of 1000000 passwords) {
  POST /login { email: "victim@email.com", password }
}
→ Without rate limit: tries all passwords in minutes!

ATTACK 2 — Credential Stuffing:
Use breached credentials (HaveIBeenPwned 10B+ records)
→ POST /login for each email:password pair
→ Even if no rate limit per IP, distributed across 10K IPs

ATTACK 3 — API Key Enumeration:
for (i = 1; i < 100000; i++) {
  GET /api/users/${i}  → harvest all user data
}

ATTACK 4 — DDoS (Volumetric):
Botnet of 100K machines → each sends 1000 req/sec
→ 100M requests/sec → server collapses

ATTACK 5 — Account Enumeration:
POST /login 1000 times with different emails:
  - Fast response "Invalid password" → email EXISTS
  - Slow response or "Email not found" → email DOES NOT EXIST
→ Build list of valid accounts

Sliding Window Algorithm:
[──────────── 60 seconds ────────────]
t=0s  req1  req2  req3 ... req100  ← 100 req/min limit
t=30s req101 → BLOCKED!
t=61s window slides → oldest request (t=0s) drops out
      req101 is now within new window → ALLOWED ✅

Fixed Window vs Sliding Window:
Fixed: 100 req / 60s window
  t=59s: 100 requests → full
  t=61s: reset! 100 more → attacker sends 200 req in 2 seconds (boundary burst)
Sliding: always counts last 60 seconds → no boundary burst
```

---

## 💻 Vulnerable Code (What NOT to do)

```javascript
// ❌ VULNERABLE — No rate limiting

app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await db.findByEmail(email);
  
  // ❌ No rate limit — attacker tries 1M passwords in minutes
  if (!user || !bcrypt.compareSync(password, user.passwordHash)) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  res.json({ token: generateToken(user.id) });
});

// ❌ Rate limit only on IP — bypassed by rotating IPs:
app.use('/login', rateLimitByIP);
// Attacker uses 10K IPs → each gets 100 attempts → 1M total attempts

// ❌ Rate limit without proper headers — client doesn't know limit:
// No X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After headers

// ❌ In-memory rate limit (doesn't work for multi-instance):
const requestCounts = new Map();  // only works for single process!
// 10 server instances → each has own Map → 10x the allowed requests
```

---

## 💻 Secure Code (What TO do)

```javascript
// ✅ SECURE RATE LIMITING

// ─── Basic Setup with express-rate-limit ─────────────────────
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis').default;
const { createClient } = require('redis');

const redisClient = createClient({ url: process.env.REDIS_URL });
await redisClient.connect();

// ─── Global Rate Limit (all routes) ──────────────────────────
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,                   // limit per IP per window
  standardHeaders: true,      // Return rate limit info in headers
  legacyHeaders: false,       // Disable the `X-RateLimit-*` headers
  // Response headers sent:
  // RateLimit-Limit: 100
  // RateLimit-Remaining: 95
  // RateLimit-Reset: 1640000000
  
  store: new RedisStore({     // ✅ Works across multiple server instances
    sendCommand: (...args) => redisClient.sendCommand(args),
  }),
  
  message: {
    error: 'Too many requests, please try again later.',
    retryAfter: 'Check Retry-After header'
  },
  
  handler: (req, res) => {
    res.status(429).json({
      error: 'Rate limit exceeded',
      retryAfter: Math.ceil(req.rateLimit.resetTime / 1000),
    });
  },
  
  skip: (req) => {
    // ✅ Skip rate limiting for trusted internal services:
    const trustedIPs = new Set(['10.0.0.1', '10.0.0.2']);
    return trustedIPs.has(req.ip);
  }
});

app.use(globalLimiter);

// ─── Strict Login Rate Limiting ───────────────────────────────
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 5,                     // only 5 login attempts per IP per 15 min
  skipSuccessfulRequests: true,  // don't count successful logins
  store: new RedisStore({ sendCommand: (...args) => redisClient.sendCommand(args) }),
});

// Rate limit per account (not just IP) — defeats IP rotation:
const loginAccountLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  keyGenerator: (req) => {
    // ✅ Key by email (normalized) not IP:
    return `login:account:${req.body.email?.toLowerCase()}`;
  },
  store: new RedisStore({ sendCommand: (...args) => redisClient.sendCommand(args) }),
});

app.post('/login',
  loginLimiter,           // per IP: 5 attempts / 15 min
  loginAccountLimiter,    // per account: 10 attempts / 15 min
  async (req, res) => {
    const { email, password } = req.body;
    const user = await db.findByEmail(email);
    
    // ✅ Constant time comparison regardless of user existence
    // (prevents timing attacks and account enumeration):
    const dummyHash = '$2b$10$dummyhashtopreventtimingattacks';
    const hash = user?.passwordHash ?? dummyHash;
    const isValid = await bcrypt.compare(password, hash);
    
    if (!user || !isValid) {
      return res.status(401).json({ error: 'Invalid credentials' });
      // ✅ Same error for "user not found" and "wrong password"
      // → prevents account enumeration
    }
    
    res.json({ token: generateToken(user.id) });
  }
);

// ─── API Rate Limiting (different tiers) ─────────────────────
// Authenticated users get higher limits:
const apiLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1 minute
  max: (req) => {
    if (!req.user) return 30;                    // unauthenticated: 30/min
    if (req.user.plan === 'premium') return 1000; // premium: 1000/min
    if (req.user.plan === 'pro') return 300;      // pro: 300/min
    return 100;                                   // free: 100/min
  },
  keyGenerator: (req) => {
    return req.user?.id || req.ip;  // key by user ID if authenticated
  },
  store: new RedisStore({ sendCommand: (...args) => redisClient.sendCommand(args) }),
});

app.use('/api', authenticate, apiLimiter);

// ─── Redis-based Sliding Window (Manual Implementation) ────────
// More precise than fixed window — no boundary burst attack:
async function slidingWindowRateLimit(key, limit, windowSeconds) {
  const now = Date.now();
  const windowStart = now - (windowSeconds * 1000);
  
  const pipeline = redisClient.multi();
  pipeline.zRemRangeByScore(key, 0, windowStart);  // remove old entries
  pipeline.zCard(key);                              // count current
  pipeline.zAdd(key, { score: now, value: `${now}-${Math.random()}` });
  pipeline.expire(key, windowSeconds);
  
  const results = await pipeline.exec();
  const requestCount = results[1];  // count BEFORE adding current
  
  return {
    allowed: requestCount < limit,
    remaining: Math.max(0, limit - requestCount - 1),
    resetAt: new Date(now + windowSeconds * 1000)
  };
}

// Use in middleware:
app.post('/login', async (req, res, next) => {
  const key = `ratelimit:login:ip:${req.ip}`;
  const { allowed, remaining } = await slidingWindowRateLimit(key, 5, 900);  // 5 per 15 min
  
  res.setHeader('X-RateLimit-Remaining', remaining);
  
  if (!allowed) {
    return res.status(429).json({ error: 'Too many login attempts' });
  }
  next();
});

// ─── Token Bucket Algorithm (allows controlled bursts) ────────
// Use ioredis + Lua script for atomic token bucket:
const tokenBucketScript = `
  local key = KEYS[1]
  local capacity = tonumber(ARGV[1])
  local refillRate = tonumber(ARGV[2])  -- tokens per second
  local now = tonumber(ARGV[3])
  local requested = tonumber(ARGV[4])
  
  local bucket = redis.call('HMGET', key, 'tokens', 'lastRefill')
  local tokens = tonumber(bucket[1]) or capacity
  local lastRefill = tonumber(bucket[2]) or now
  
  -- Refill tokens based on elapsed time:
  local elapsed = now - lastRefill
  tokens = math.min(capacity, tokens + (elapsed * refillRate))
  
  if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', key, 'tokens', tokens, 'lastRefill', now)
    redis.call('EXPIRE', key, 3600)
    return 1  -- allowed
  else
    redis.call('HMSET', key, 'tokens', tokens, 'lastRefill', now)
    redis.call('EXPIRE', key, 3600)
    return 0  -- rejected
  end
`;
```

---

## 🟠 Implementation in My Stack (NestJS)

```typescript
// ─── NestJS + Throttler ───────────────────────────────────────
// app.module.ts
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { ThrottlerStorageRedisService } from 'nestjs-throttler-storage-redis';
import Redis from 'ioredis';

@Module({
  imports: [
    ThrottlerModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        throttlers: [
          { name: 'short',  ttl: 1000,          limit: 3   },  // 3/sec
          { name: 'medium', ttl: 10000,          limit: 20  },  // 20/10s
          { name: 'long',   ttl: 60000,          limit: 100 },  // 100/min
        ],
        storage: new ThrottlerStorageRedisService(
          new Redis(config.get('REDIS_URL'))
        ),
      }),
    }),
  ],
  providers: [
    { provide: APP_GUARD, useClass: ThrottlerGuard },  // global guard
  ],
})

// Override per route:
@Controller('auth')
export class AuthController {
  @Post('login')
  @Throttle({ short: { limit: 5, ttl: 900000 } })  // 5 per 15 min for login
  async login(@Body() dto: LoginDto) { ... }
  
  @Get('profile')
  @SkipThrottle()  // no limit for profile reads
  getProfile() { ... }
}
```

---

## 🔧 Libraries + Tools
| Tool | Purpose | Use |
|------|---------|-----|
| `express-rate-limit` | Express rate limiting | `rateLimit({ max: 100, windowMs: 60000 })` |
| `rate-limit-redis` | Redis store for distributed rate limiting | Multi-instance rate limits |
| `@nestjs/throttler` | NestJS built-in throttling | `ThrottlerModule.forRoot()` |
| `nestjs-throttler-storage-redis` | Redis backend for NestJS throttler | Distributed NestJS throttling |
| Nginx `limit_req` | Rate limit at proxy layer | `limit_req_zone $binary_remote_addr` |
| AWS WAF | Cloud-level rate limiting + DDoS | Per IP, per user, geo-blocking |
| Cloudflare Rate Limiting | Edge rate limiting | Before traffic hits your server |

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between rate limiting by IP vs by user?**
A1: **IP-based**: limits requests per IP address. Simple to implement, but bypassed by botnets (10K IPs → 10K×100 = 1M requests). Also problematic for NAT — thousands of users behind one corporate IP address get collectively rate-limited. **User-based**: limits by authenticated user ID. Can't be bypassed by IP rotation, but only works after authentication — doesn't protect login endpoint itself. **Best practice**: use both — IP-based for the login endpoint (before auth), user-based for authenticated API endpoints. Additionally, rate limit by email/username on login to prevent distributed brute force against a single account.

**Q2: What is the difference between fixed window and sliding window rate limiting?**
A2: **Fixed window**: counts requests in a fixed time bucket (e.g., 0-60s, 60-120s). Problem: at the boundary, attacker can send 100 requests at t=59s and 100 more at t=61s — 200 requests in 2 seconds, double the limit. **Sliding window**: counts requests in the last N seconds from "now" — constantly sliding. No boundary burst. More accurate but requires storing timestamps (e.g., sorted set in Redis with ZREMRANGEBYSCORE for cleanup). **Token bucket**: allows controlled bursts — starts with full bucket (e.g., 10 tokens), refills at 1 token/second, each request consumes 1 token. Good for APIs that need to allow short bursts of activity.

**Q3: How do you implement rate limiting in a distributed system (multiple servers)?**
A3: In-memory rate limiting (Map/object) only works for single processes — each server instance has independent counters, giving N×limit total. For distributed rate limiting: use Redis as the shared counter store. All server instances write/read the same Redis key. Use atomic operations — Redis `INCR` + `EXPIRE` for simple counters, or Sorted Sets for sliding window (ZADD + ZRANGEBYSCORE + ZREMRANGEBYSCORE in a pipeline). Libraries like `rate-limit-redis` and `nestjs-throttler-storage-redis` handle this automatically.

**Q4: How do you prevent brute force while not locking out legitimate users?**
A4: Progressive strategies: (1) **Progressive delays** — 1st failure: normal; 5th failure: 1s delay; 10th: 10s; 20th: account lockout. (2) **Account lockout + notification** — after 5 failures, lock for 30 minutes AND email the user with a reset link. (3) **CAPTCHA after N failures** — show CAPTCHA after 3 failed attempts (stops bots, not annoying for legitimate users who rarely fail). (4) **IP + account combination** — same IP with multiple failed accounts → suspicious, block IP; single account multiple failures → lock account. (5) **Rate limit per account not just per IP** — key: `login:account:{email}` — defeats distributed brute force.

**Q5: What's the standard HTTP response for rate limiting and what headers should you return?**
A5: HTTP `429 Too Many Requests` is the standard status code. Include these response headers: `Retry-After: 900` (seconds until reset — RFC 7231), `RateLimit-Limit: 100` (the limit), `RateLimit-Remaining: 0` (requests remaining in window), `RateLimit-Reset: 1640000000` (Unix timestamp when window resets). These allow clients to implement proper backoff — instead of retrying immediately and wasting requests, clients wait the exact duration specified by Retry-After. Well-behaved API clients use exponential backoff + Retry-After, and you should document your rate limits in your API docs.

---

## ✅ Security Checklist
```
□ Login endpoint rate limited per IP (5-10 attempts / 15 min)
□ Login endpoint rate limited per account/email (defeats IP rotation)
□ API endpoints rate limited per authenticated user
□ Redis store used (not in-memory — works across instances)
□ 429 status code with Retry-After header on rate limit hit
□ Rate limit headers (X-RateLimit-Limit/Remaining/Reset) in all responses
□ Sliding window algorithm (not fixed window — prevents boundary burst)
□ Account lockout with email notification after N failures
□ DDoS protection at edge (Cloudflare, AWS WAF) for volumetric attacks
□ No rate limit bypass for specific User-Agents or IPs except trusted internal
□ Rate limits logged and monitored (alert on spike in 429s)
□ Same-error response for "user not found" and "wrong password"
```

---

## 📊 Visual Diagram

```
WITHOUT RATE LIMITING:
Attacker → 1,000,000 POST /login → tries all passwords → account compromised ☠️

WITH RATE LIMITING (per IP + per account):
Attacker → 5 POST /login from IP 1.2.3.4 → 429 Too Many Requests
           Retry-After: 900 (seconds)
           ↓
Attacker → switches to 10,000 different IPs
           → Each IP: 5 attempts → 50,000 total attempts
           → Per-account limit: 10 per 15 min → account blocked after 10
           → Distributed attack significantly slowed ✅

SLIDING WINDOW VISUALIZATION:
|←──────── 60 second window ──────────→|
t=10: req1 req2 ... req98              (98 so far, 2 remaining)
t=11: req99 req100                     (full)
t=11.1: req101 → BLOCKED! window full

[time passes]
t=70: req1(from t=10) drops out of window
t=70.1: req101 now allowed (window has space)

RATE LIMIT RESPONSE:
HTTP/1.1 429 Too Many Requests
RateLimit-Limit: 5
RateLimit-Remaining: 0
RateLimit-Reset: 1640001800
Retry-After: 900
Content-Type: application/json

{ "error": "Too many requests", "retryAfter": 900 }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rate Limiting | Restrict requests per time window | समय सीमा में requests की limit |
| Brute Force | Try all possible values | सभी possibilities try करना |
| Sliding Window | Count requests in last N seconds | पिछले N seconds का count |
| Token Bucket | Allow controlled bursts | Burst-friendly rate limiting |
| DDoS | Distributed Denial of Service | Botnet से server को overwhelm करना |
| 429 | HTTP Too Many Requests status | Rate limit hit होने पर response |
| Retry-After | Header telling client when to retry | कब retry करना header में बताना |

---

## ⚡ 3-Line Summary
**English:**
1. Rate limiting is the primary defense against brute force, credential stuffing, API scraping, and DDoS — without it, login endpoints are wide open to automated attacks.
2. Use Redis-backed sliding window rate limiting, apply limits per IP AND per account/email, return 429 with Retry-After header.
3. For production: add edge-level protection (Cloudflare/AWS WAF) for volumetric DDoS — app-level rate limiting alone can't handle million-req/sec attacks.

**Hindi:**
1. Rate limiting brute force, credential stuffing, API scraping, और DDoS की primary defense है।
2. Redis-backed sliding window use करो, IP और account दोनों per limit लगाओ, 429 + Retry-After header return करो।
3. Production में edge protection (Cloudflare/AWS WAF) add करो — volumetric DDoS app level पर handle नहीं होता।

---

## 🚨 Red Flag Signs
- Login endpoint with no rate limiting
- Rate limiting using in-memory store (Map/object) in multi-instance deployment
- Rate limiting only by IP (bypassed by botnet)
- No 429 response or Retry-After header
- Same rate limit for login and health-check endpoints
- No alert/monitoring on spike in 429 responses
- `max: 1000` on a sensitive endpoint like /reset-password

---

## ➡️ Next Topic
**218. DDoS Protection** — Types of DDoS attacks, Layer 3/4 vs Layer 7, Cloudflare WAF, AWS Shield, application-level mitigation strategies.
