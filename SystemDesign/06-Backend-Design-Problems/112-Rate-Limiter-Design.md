# 112. Rate Limiter Design (Distributed)
# हिंदी में: Rate Limiter Design — एक ऐसी साझा सेवा बनाना जो सारे API servers पर हर user/API key/IP की requests की सीमा (जैसे 100/मिनट) तेज़ी और सही तरीके से लागू करे

---

## 🔵 Simple Definition (English)
Design a **distributed rate limiting system** that enforces rules like "100 requests/min per user", "5 OTPs/hour per phone" or "10,000 requests/day per API key on the free plan" **across many API servers and regions**, adding **minimal latency** (< 1–2 ms), staying **highly available**, and returning standard **429 + headers** when limits are hit.
Building blocks: rules configuration, a fast counter store (Redis), an algorithm (token bucket or sliding window), and an enforcement point (gateway or middleware).

## 🔵 सरल परिभाषा (Hindi)
ऐसी सेवा बनाना जो सारे सर्वरों पर एक साथ नियम लागू करे — "हर user 100 requests/मिनट", "हर phone पर 3 OTP/घंटा" — बहुत कम देरी (1-2 ms) में, हमेशा उपलब्ध रहकर, और सीमा पार होने पर 429 लौटाकर।

---

## 🔴 Problem it Solves
(Concepts in Topics 59–62; this is the **system design** of it.) Without a central, distributed limiter:
- Per-server in-memory limits multiply with instance count (10 servers = 10× the intended limit).
- Abuse (brute force, scraping, OTP pumping), noisy tenants and retry storms overload services.
- Paid API tiers can't be enforced.
- Rules are hardcoded in every service and inconsistent.

## 🔴 यह क्यों बना? (Hindi)
हर सर्वर पर अलग गिनती हो तो 10 सर्वर = 10 गुना सीमा। Brute force, scraping, OTP दुरुपयोग, एक बड़े ग्राहक का बोझ सबको धीमा करता है; paid plans की सीमा लागू नहीं होती; हर service में नियम अलग-अलग।
एक केंद्रीय, distributed limiter ये सब हल करता है।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional:
  - Limit by key: user id, API key, IP, phone, tenant, endpoint — and combinations
  - Multiple rules per request (per-second burst + per-day quota)
  - Different limits per plan/endpoint; dynamic rule updates without deploy
  - Return 429 + Retry-After + RateLimit-* headers; optional "shadow mode" (log only)
Non-functional:
  - Low latency overhead (p99 < 2 ms), high throughput (1M+ checks/s)
  - Highly available: limiter failure must not take the API down (fail-open for most rules)
  - Accurate enough (small overshoot OK), consistent across instances (and regions, roughly)
```

### 2. Estimation

```
API traffic: 200k RPS peak; ~2 rules per request → 400k limiter checks/s
Redis: ~100k ops/s per shard comfortably (Lua scripts heavier) → 6–8 shards (Redis Cluster)
Memory: 10M active keys × ~100 bytes ≈ 1 GB (token bucket = 2 fields per key) → small
Latency: in-region Redis RTT ~0.3–1 ms
```

### 3. Where to enforce

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Edge/CDN/WAF      → coarse per-IP & bot limits (cheap, stops floods early)  │
│ API Gateway       → per API key / user / plan limits (central, all services)│
│ Service middleware→ business-specific limits (OTP per phone, coupon per user)│
└─────────────────────────────────────────────────────────────────────────────┘
Design centrally as a library + shared store, or a sidecar/service (Envoy global rate limit service).
```

### 4. Architecture

```
 Client ──► API Gateway / Service middleware
                 │ 1. build keys from request (user:42, apikey:abc, ip:1.2.3.4, route)
                 │ 2. lookup applicable rules (local cache, refreshed from Rules Service)
                 │ 3. atomic check+update in Redis (Lua: token bucket / sliding window)
                 │       ├─ allowed → forward request, add RateLimit-* headers
                 │       └─ limited → 429 + Retry-After (no backend call)
                 ▼
          Redis Cluster (sharded by key hash) — counters with TTL
                 ▲
 Rules Service (DB + admin UI) ──push/poll──► rule cache in every gateway instance
 Metrics/logs: allowed/limited counts per rule → dashboards, alerts (sudden 429 spikes)
```

### 5. Algorithm choice
```
Token bucket (Topic 60)          → per-user API limits with bursts  ⭐ default
Sliding window counter (Topic 62)→ "N per rolling minute/hour" (OTP, login)
Fixed window                     → daily/monthly quotas (reset at midnight / billing cycle)
Concurrency limiter              → max in-flight requests per tenant (expensive endpoints)
```

### 6. Rules config example
```yaml
rules:
  - id: api-free-plan
    match: { plan: free }
    key: apiKey
    limits: [{ algorithm: token_bucket, capacity: 20, refill_per_sec: 1 },        # 60/min with burst 20
             { algorithm: fixed_window, limit: 10000, window: 1d }]               # daily quota
  - id: otp-per-phone
    match: { route: "POST /auth/otp" }
    key: body.phone
    limits: [{ algorithm: sliding_window, limit: 3, window: 1h }]
    on_limit: { status: 429, failure_mode: closed }                                  # security → fail closed
  - id: login-per-ip
    match: { route: "POST /auth/login" }
    key: ip
    limits: [{ algorithm: sliding_window, limit: 20, window: 15m }]
```

### 7. Deep dives (what interviewers probe)

```
Atomicity / races:  read-modify-write must be atomic → Redis Lua script (or MULTI); never GET then SET
Hot keys:           a single huge customer key on one shard → local pre-aggregation, split key
                    (key:{shard N}), or a dedicated tenant cell
Latency:            pipeline multiple rule checks in one Lua call; keep Redis in same AZ/region;
                    local in-memory "token cache" for very high RPS keys (sync every 100 ms) →
                    slight inaccuracy, huge speed
Failure modes:      Redis down → fail OPEN (allow) for general limits + local in-memory fallback
                    limiter per instance; fail CLOSED for security-critical (OTP, login)
                    Use timeouts (~5 ms) on limiter calls; circuit breaker
Multi-region:       per-region counters (limit/region) — simplest; or global via async sync
                    (CRDT counters) accepting overshoot; strict global limits are slow
Clock:              use Redis server time (TIME) inside the script, not app clocks
Client experience:  headers + Retry-After; docs; SDK backoff; shadow mode before enforcing new rules
Observability:      count limited requests per rule & key class; alert on unexpected spikes
                    (bug or attack); top-N limited keys
```

## 🟢 कैसे काम करता है? (Hindi)
1. नियम तय करो: किस key पर (user, API key, IP, phone), कितनी सीमा, कौन-सा algorithm — और उन्हें एक Rules Service में रखो जो सारे gateways को भेजे।
2. हर request पर gateway keys बनाता है, नियम देखता है, और Redis में Lua script से atomic गिनती/टोकन जाँचता है।
3. सीमा के अंदर → आगे भेजो (RateLimit headers के साथ); बाहर → 429 + Retry-After, backend तक request जाती ही नहीं।
4. Redis गिरे तो सामान्य नियम में अनुमति (fail open) और local limiter; OTP/login जैसे security नियम में मना (fail closed)।
5. Multi-region में हर region की अलग गिनती सबसे आसान; hot keys, latency (pipeline, local cache) और monitoring पर ध्यान।

---

## 🟡 Real World Example

**Stripe** — runs several limiters: a request rate limiter (token bucket in Redis), a concurrent request limiter, a fleet-usage load shedder that reserves capacity for critical traffic, and a worker utilization load shedder. It's described in Stripe's engineering blog "Scaling your API with rate limiters".

**GitHub API** — per-user and per-app limits (5,000/hour) with `X-RateLimit-*` headers, plus secondary limits on concurrency and content-creation bursts to stop abuse.

**Cloudflare** — rate limiting at the edge across hundreds of locations using a sliding window counter. It's approximate but extremely scalable, and stops attacks before they reach origin servers.

**Lyft / Envoy global rate limit service** — an open-source Go service backed by Redis, called by Envoy proxies to enforce descriptors-based limits across the mesh.

## 🟡 Real Example Hindi में
Stripe कई limiters चलाता है — Redis वाला token bucket, एक साथ चल रही requests की सीमा, और ज़रूरी ट्रैफ़िक के लिए क्षमता बचाने वाला load shedder।
GitHub API में 5,000/घंटा की सीमा और headers; Cloudflare edge पर ही attacks रोकता है; Lyft ने Envoy के लिए open-source rate limit service बनाई।

---

## 🟠 My Stack Example

### Gateway middleware evaluating multiple rules in ONE Redis round trip (Node)
```js
// rules cached locally, refreshed every 10 s from DB/Redis
let rules = await loadRules(); setInterval(async () => { rules = await loadRules().catch(() => rules); }, 10_000);

const LUA = fs.readFileSync('./limits.lua', 'utf8');   // evaluates N token-bucket checks atomically

export function rateLimiter() {
  return async (req, res, next) => {
    const applicable = rules.filter((r) => r.matches(req));
    if (!applicable.length) return next();
    const keys = applicable.map((r) => `rl:${r.id}:${r.keyOf(req)}`);
    const args = applicable.flatMap((r) => [r.capacity, r.refillPerSec, r.cost?.(req) ?? 1]);
    let result;
    try {
      result = await withTimeout(redis.eval(LUA, { keys, arguments: args.map(String) }), 5);   // 5 ms budget
    } catch {
      const critical = applicable.some((r) => r.failureMode === 'closed');
      if (critical) return res.status(503).json({ error: 'TRY_AGAIN' });
      return localFallbackLimiter(req, res, next);                                           // fail open-ish
    }
    const [allowed, remaining, retryMs, ruleIdx] = result;
    res.set('RateLimit-Limit', String(applicable[ruleIdx]?.capacity ?? '')).set('RateLimit-Remaining', String(remaining));
    if (allowed === 1) return next();
    metrics.limited.inc({ rule: applicable[ruleIdx].id });
    res.set('Retry-After', String(Math.ceil(retryMs / 1000))).status(429).json({ error: 'RATE_LIMITED', rule: applicable[ruleIdx].id });
  };
}
```

### limits.lua (multiple buckets, deny if ANY rule fails, using Redis time)
```lua
local t = redis.call('TIME'); local now = tonumber(t[1]) * 1000 + math.floor(tonumber(t[2]) / 1000)
local n = #KEYS
local states = {}
for i = 1, n do
  local cap, rate, cost = tonumber(ARGV[(i-1)*3+1]), tonumber(ARGV[(i-1)*3+2]), tonumber(ARGV[(i-1)*3+3])
  local b = redis.call('HMGET', KEYS[i], 'tokens', 'ts')
  local tokens = tonumber(b[1]) or cap
  local ts = tonumber(b[2]) or now
  tokens = math.min(cap, tokens + (now - ts) / 1000 * rate)
  if tokens < cost then
    return { 0, math.floor(tokens), math.ceil((cost - tokens) / rate * 1000), i - 1 }   -- deny, no writes
  end
  states[i] = { tokens - cost, cap, rate }
end
for i = 1, n do                                   -- all passed → commit
  redis.call('HSET', KEYS[i], 'tokens', states[i][1], 'ts', now)
  redis.call('PEXPIRE', KEYS[i], math.ceil(states[i][2] / states[i][3] * 1000) * 2)
end
return { 1, math.floor(states[1][1]), 0, 0 }
```
⚠️ In Redis Cluster, all KEYS in one script must hash to the same slot. Use hash tags (`rl:{user:42}:…`), or run one script per key.

### FastAPI dependency using the same Lua
```python
LIMITS = r.register_script(open("limits.lua").read())
async def rate_limit(request: Request, user=Depends(current_user)):
    allowed, remaining, retry_ms, _ = await LIMITS(keys=[f"rl:{{u{user['id']}}}:api"], args=[20, 1, 1])
    if not allowed:
        raise HTTPException(429, "RATE_LIMITED", headers={"Retry-After": str(max(1, retry_ms // 1000))})
```

### Managed alternatives
```
AWS API Gateway usage plans (rate + burst + quota per API key), AWS WAF rate-based rules,
Cloudflare Rate Limiting, Kong rate-limiting-advanced, Envoy global ratelimit service
```

### Client side (RN / web)
```
Respect 429 + Retry-After with jittered backoff; disable "Resend OTP" for the window; show friendly message
```

---

## ⚫ Interview Questions + Answers

**Q1: Design a distributed rate limiter for an API used by millions of users.**
A1: Enforce at the API gateway (plus edge per-IP limits and service-level business limits). Use configurable rules (key type, algorithm, limits, failure mode) stored in a rules service and cached in gateways. Keep counters in a sharded Redis cluster, updated atomically via Lua scripts (token bucket for API limits, sliding window for security limits), with keys expiring by TTL. Return 429 with Retry-After and RateLimit headers, emit metrics per rule, fail open with local fallback for general limits and fail closed for security limits, keep limiter calls on a tight timeout budget, and use per-region counters for multi-region deployments.

**Q2: How do you keep the limiter from adding latency?**
A2: Co-locate Redis with the gateways (same AZ or region), evaluate all applicable rules in one Lua call (one round trip), pipeline requests, and use short timeouts. For extremely hot keys, keep a local in-memory token cache synced periodically or use local plus global hybrid limiting (accepting slight overshoot). Cache rules locally rather than fetching them per request. Overhead is typically under 1–2 ms.

**Q3: What happens if Redis goes down?**
A3: Decide per rule. For general API fairness limits, fail open, allowing traffic, optionally with a conservative per-instance in-memory limiter so you still have some protection. For security-critical limits (login, OTP, payments abuse), fail closed or degrade (CAPTCHA). Protect Redis calls with timeouts and a circuit breaker so a slow limiter doesn't stall the API. Run Redis with replicas and automatic failover.

**Q4: How do you handle rate limiting across multiple regions?**
A4: Simplest: independent per-region counters, with limits split per region, which gives low latency but lets a client using several regions get more in total. For global limits, replicate counters asynchronously between regions (CRDT-style G-Counters summed per region) and accept temporary overshoot. Strict global synchronous counters add cross-region latency and are rarely worth it. Route each client to a home region when strictness matters.

**Q5: How do you prevent race conditions in the counters?**
A5: Never read a counter in the app and write it back separately, because concurrent requests on different servers would both pass. Perform the check-and-update atomically on the Redis server: INCR with EXPIRE for fixed windows, a sorted-set ZREMRANGEBYSCORE/ZCARD/ZADD sequence inside MULTI or Lua for sliding logs, or a Lua token bucket. Use the server's clock (`TIME`) inside the script. In Redis Cluster, keep multi-key scripts on one slot using hash tags.

---

## 🔷 Trade-offs
✅ Central distributed limiter: consistent rules, protects all services, enables paid tiers.
❌ Extra dependency and latency; Redis availability matters; hot keys.
✅ Fail-open: availability — ❌ temporary loss of protection.
✅ Per-region counters: fast — ❌ global overshoot.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Distributed rate limiter | Shared limits across servers | सारे सर्वरों में साझा सीमा |
| Rule | Key + algorithm + limit config | सीमा का नियम |
| Enforcement point | Where limits are checked | सीमा कहाँ जाँची जाती है |
| Lua script | Atomic logic in Redis | Redis में atomic code |
| Fail open / closed | Allow / deny on limiter failure | ख़राबी पर अनुमति / मना |
| Hot key | One key with huge traffic | बहुत ज़्यादा ट्रैफ़िक वाली key |
| Shadow mode | Log-only, not enforced | सिर्फ़ लिखो, रोको नहीं |
| Quota | Long-period allowance | लंबी अवधि की सीमा |
| Hash tag | Force keys to same cluster slot | keys को एक slot में रखना |

---

## ⚡ 3-Line Summary
**English:**
1. Enforce at edge (IP), gateway (user/API key/plan) and service (business rules); rules configurable and cached locally.
2. Shared Redis cluster + atomic Lua (token bucket / sliding window), one round trip, Redis server time, 429 + headers.
3. Decide failure modes per rule (open vs closed), handle hot keys, per-region counters for multi-region, monitor limited traffic.

**Hindi:**
1. Edge (IP), gateway (user/API key) और service (business नियम) पर सीमा; नियम बदलने लायक और local cache में।
2. साझा Redis + atomic Lua, एक round trip, Redis का समय, 429 + headers।
3. हर नियम का failure mode तय करो, hot keys संभालो, regions की अलग गिनती, monitoring।

---

## ➡️ Next Topic Suggestion
**113. Authentication Service** — Rate limiting protects login and OTP endpoints. Next: design a complete authentication service (signup, login, OTP, social login, sessions/tokens, MFA, account security) for web and mobile.
