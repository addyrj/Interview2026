# 73. Circuit Breaker Pattern
# हिंदी में: Circuit Breaker — घर के बिजली के fuse की तरह: कोई service बार-बार फ़ेल हो रही हो तो उसे कॉल करना कुछ देर के लिए बंद कर दो, ताकि पूरा सिस्टम न गिरे

---

## 🔵 Simple Definition (English)
A **circuit breaker** wraps calls to a remote dependency (another service, DB, payment API). It **monitors failures**, and when failures cross a threshold it **"opens"**: further calls **fail immediately** (or use a fallback) without hitting the dependency. After a cool-down, it lets a few **trial requests** through (**half-open**). If they succeed it **closes** again; if they fail it re-opens.
States: **CLOSED → OPEN → HALF-OPEN → CLOSED**.

## 🔵 सरल परिभाषा (Hindi)
Circuit breaker बाहरी service की कॉल्स पर नज़र रखता है। बहुत ज़्यादा failures हों तो वो "खुल" (OPEN) जाता है — कुछ समय तक कॉल सीधे मना या fallback, ताकि बीमार service पर और बोझ न पड़े।
थोड़ी देर बाद कुछ test कॉल्स (HALF-OPEN) — सफल रहीं तो फिर सामान्य (CLOSED)।

---

## 🔴 Problem it Solves
**Cascading failures.** Suppose the Recommendation service becomes slow (10 s per call):
```
Home API calls Recommendations for every request → each request waits 10s
→ Home API threads/connections/event-loop pile up → Home API runs out of resources
→ Home API is now slow for EVERYTHING (even parts that don't need recommendations)
→ Mobile apps retry → more load → the failure spreads to Gateway → whole app down ❌
```
Meanwhile, the struggling service gets **hammered with even more requests**, so it can't recover.

A circuit breaker:
- **Fails fast** (ms instead of 10 s timeouts) → frees resources.
- Gives the dependency **breathing room to recover**.
- Enables **graceful degradation** (show the home screen without recommendations).

## 🔴 यह क्यों बना? (Hindi)
एक service धीमी हुई तो उसे बुलाने वाली service भी अटकती है, फिर उसे बुलाने वाली — पूरा सिस्टम एक के बाद एक गिरता है (cascading failure), और बीमार service पर और ज़्यादा बोझ।
Circuit breaker तुरंत मना (fail fast) करके resources बचाता है, बीमार service को ठीक होने का समय देता है, और ऐप थोड़ा कम फ़ीचर के साथ चलता रहता है।

---

## 🟢 How it Works — Step by Step

```
                   failures ≥ threshold
     ┌──────────┐  (e.g. 50% of last 20 calls,   ┌──────────┐
     │  CLOSED  │──── or 5 consecutive) ────────►│   OPEN   │
     │ (normal) │                                 │ fail fast│
     └────▲─────┘                                 └────┬─────┘
          │                                            │ after reset timeout (e.g. 30s)
          │ trial calls succeed                        ▼
          │                                     ┌────────────┐
          └─────────────────────────────────────│ HALF-OPEN  │
                                                │ allow few  │
                     trial call fails ─────────►│ test calls │──┐
                     (back to OPEN)             └────────────┘  │
                          ▲─────────────────────────────────────┘
```

```
CLOSED:    calls go through; record success/failure/timeout in a rolling window
OPEN:      calls rejected immediately → error or FALLBACK; no load on dependency
HALF-OPEN: allow N probe calls; success → CLOSED (reset stats); failure → OPEN (wait again)
```

### What counts as failure
```
✓ timeouts (most important!), connection errors, 5xx responses, 429 from dependency
✗ 4xx client errors (400, 404, 422) — the dependency is healthy; don't trip the breaker
Also "slow call rate": e.g. > 50% of calls slower than 2s → open
```

### Fallback options when OPEN
```
- Cached / stale data (last known menu, cached recommendations)
- Default value (empty recommendations list, "ETA unavailable")
- Alternative provider (SMS via provider B, payment gateway B)
- Queue the work for later (send email later)
- Clear error to user ("Payments are temporarily unavailable, please retry in a minute")
```

### Per-dependency breakers (bulkheading, Topic 76)
```
One breaker PER dependency (and sometimes per endpoint/host), not one global breaker:
  breaker:payment-gateway, breaker:recommendations, breaker:maps-api
A broken maps API must not block payments.
```

### Breaker + timeout + retry together (order matters)
```
Request → [Circuit breaker] → [Retry w/ backoff (limited)] → [Timeout per attempt] → dependency
- Timeout: never wait forever (Topic 79)
- Retry: only for transient errors, idempotent ops, small count (Topic 74)
- Breaker: stops retry storms when dependency is truly down
```

### Tuning (example defaults)
```
rolling window: last 20 calls or 10 seconds
minimum calls before evaluating: 10
failure rate threshold: 50%
open duration (reset timeout): 30 s
half-open probes: 3
```

## 🟢 कैसे काम करता है? (Hindi)
1. CLOSED: सामान्य हालत — कॉल्स जाती हैं, और सफल/फ़ेल/timeout की गिनती होती है।
2. Failures सीमा पार (जैसे पिछली 20 में से 50%) → OPEN: कॉल्स तुरंत मना या fallback (cache, default, दूसरा provider)।
3. कुछ समय (30 सेकंड) बाद HALF-OPEN: थोड़ी test कॉल्स जाने दो।
4. Test सफल → CLOSED; फ़ेल → फिर OPEN।
5. हर dependency का अलग breaker रखो; 4xx errors को failure मत गिनो; timeout और सीमित retry के साथ इस्तेमाल करो।

---

## 🟡 Real World Example

**Netflix Hystrix** — Netflix popularized circuit breakers in microservices with Hystrix (2012). If the "ratings" service failed, the UI rendered without star ratings instead of failing the whole page. Hystrix is now in maintenance, succeeded by **Resilience4j** and service-mesh breakers (Envoy/Istio).

**Payment gateway routing (Razorpay/Juspay/PayU)** — payment orchestrators keep per-bank and per-gateway health. If a bank's UPI success rate drops, traffic is routed to other PSP banks or gateways and the bad route is retried later. That's a circuit breaker plus fallback at business level.

**Swiggy/Zomato home screen** — non-critical widgets (offers carousel, recommendations) are behind breakers and timeouts, so a failing recommendation service doesn't stop users from ordering.

**AWS SDKs / Envoy** — Envoy's outlier detection ejects failing hosts from load balancing temporarily, which is per-host circuit breaking.

## 🟡 Real Example Hindi में
Netflix ने Hystrix से circuit breaker मशहूर किया — "ratings" service फ़ेल हो तो पेज बिना stars के खुलता था, पूरा पेज नहीं गिरता था।
Payment gateways हर बैंक की सफलता दर देखते हैं — किसी बैंक का UPI बिगड़ा तो ट्रैफ़िक दूसरे बैंक पर भेज देते हैं, यह business स्तर का circuit breaker है।

---

## 🟠 My Stack Example

### Node.js — opossum (popular circuit breaker library)
```js
import CircuitBreaker from 'opossum';

async function fetchRecommendations(userId) {
  const r = await fetch(`${RECO_URL}/users/${userId}/recs`, { signal: AbortSignal.timeout(800) });  // timeout!
  if (r.status >= 500) throw new Error(`reco ${r.status}`);
  return r.json();
}

const recoBreaker = new CircuitBreaker(fetchRecommendations, {
  timeout: 1000,                    // treat as failure if slower
  errorThresholdPercentage: 50,     // open when ≥ 50% fail
  volumeThreshold: 10,              // need at least 10 calls in window
  rollingCountTimeout: 10_000,      // 10s window
  resetTimeout: 30_000,             // OPEN → HALF-OPEN after 30s
  errorFilter: (err) => err.status >= 400 && err.status < 500,   // 4xx don't count
});
recoBreaker.fallback(async (userId) => (await redis.get(`reco:last:${userId}`).then(JSON.parse).catch(() => null)) ?? []);
recoBreaker.on('open', () => logger.warn('reco breaker OPEN'));
recoBreaker.on('halfOpen', () => logger.info('reco breaker HALF-OPEN'));
recoBreaker.on('close', () => logger.info('reco breaker CLOSED'));

app.get('/api/v1/home', authenticate, async (req, res) => {
  const [restaurants, recs] = await Promise.all([
    getNearbyRestaurants(req.query),
    recoBreaker.fire(req.user.id),            // never blocks home for long
  ]);
  res.json({ restaurants, recommendations: recs });
});
// Export breaker stats to Prometheus (opossum-prometheus) and alert on OPEN.
```

### Fallback to a second provider (SMS)
```js
const msg91 = new CircuitBreaker(sendViaMsg91, { timeout: 3000, resetTimeout: 60_000 });
const twilio = new CircuitBreaker(sendViaTwilio, { timeout: 3000, resetTimeout: 60_000 });
msg91.fallback((to, text) => twilio.fire(to, text));
await msg91.fire(phone, `Your OTP is ${otp}`);
```

### Python / FastAPI — pybreaker
```python
import pybreaker, httpx
maps_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)

@maps_breaker
async def eta_from_maps(origin, dest):
    async with httpx.AsyncClient(timeout=1.5) as c:
        r = await c.get(MAPS_URL, params={"o": origin, "d": dest}); r.raise_for_status(); return r.json()["eta"]

async def get_eta(origin, dest):
    try:
        return await eta_from_maps(origin, dest)
    except (pybreaker.CircuitBreakerError, httpx.HTTPError):
        return estimate_eta_by_distance(origin, dest)          # fallback heuristic
```

### Service mesh / Envoy (no code changes)
```yaml
# Istio DestinationRule — outlier detection (eject bad hosts) + connection limits
trafficPolicy:
  connectionPool: { http: { http1MaxPendingRequests: 100, maxRequestsPerConnection: 10 } }
  outlierDetection: { consecutive5xxErrors: 5, interval: 10s, baseEjectionTime: 30s, maxEjectionPercent: 50 }
```

### React Native client-side breaker (protect your API & UX)
```ts
// If the API keeps failing, stop hammering it; show offline/cached UI and retry later
let failures = 0, openUntil = 0;
async function guardedFetch(url: string) {
  if (Date.now() < openUntil) throw new Error('CIRCUIT_OPEN');
  try { const r = await api.get(url); failures = 0; return r; }
  catch (e) { if (++failures >= 5) openUntil = Date.now() + 30_000; throw e; }
}
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a circuit breaker and why is it needed?**
A1: A wrapper around remote calls that tracks failures and, when they exceed a threshold, opens to reject calls immediately (or return a fallback) for a cool-down period, then half-opens to test recovery with limited calls before closing again. It prevents cascading failures (callers exhausting threads or connections while waiting on a failing dependency), gives the dependency time to recover instead of hammering it, and enables graceful degradation.

**Q2: Explain the three states.**
A2: Closed: normal, calls pass and outcomes are recorded in a rolling window. Open: the failure or slow-call rate exceeded the threshold, so calls fail fast with no traffic to the dependency for the reset timeout. Half-open: after the timeout, a small number of probe calls go through. If they succeed, the breaker returns to closed (stats reset). If they fail, it goes back to open.

**Q3: What should count as a failure for the breaker?**
A3: Signals that the dependency is unhealthy: timeouts and slow calls above a latency threshold, connection refused or reset, 5xx responses, and possibly 429 or 503 overload signals. Not client errors like 400, 404 or 422, which mean the request was bad, not the service. Count only after a minimum number of calls to avoid tripping on noise.

**Q4: How do circuit breakers, retries and timeouts work together?**
A4: Every attempt has a timeout so callers never hang. Retries (few, with exponential backoff and jitter, only for idempotent operations and transient errors) handle brief blips. The circuit breaker sits around them and stops retries entirely when the dependency is clearly down, preventing retry storms. Retry budgets and bulkheads (separate pools per dependency) complete the picture.

**Q5: Give examples of fallbacks when a breaker is open.**
A5: Serve cached or stale data (last known menu, cached profile), return defaults or partial responses (a home screen without recommendations, a distance-based ETA instead of a maps API ETA), switch to an alternate provider (backup SMS or payment gateway), queue the operation for later (emails, analytics), or return a clear, fast error with a retry hint for critical operations like payments.

---

## 🔷 Trade-offs
✅ Advantages:
- Prevents cascading failures; fast failure; lets dependencies recover; enables graceful degradation.

❌ Disadvantages:
- Tuning thresholds is tricky (too sensitive → false trips; too lax → slow reaction).
- Fallback logic adds complexity; stale data risk.
- Per-instance breakers see only local traffic (different instances may be in different states).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Circuit breaker | Stops calls to failing dependency | ख़राब service की कॉल रोकना |
| Closed | Normal state | सामान्य हालत |
| Open | Failing fast, no calls | तुरंत मना करने की हालत |
| Half-open | Trial calls to test recovery | जाँच के लिए कुछ कॉल्स |
| Cascading failure | Failure spreading across services | एक के बाद एक गिरना |
| Fallback | Alternative response | वैकल्पिक जवाब |
| Fail fast | Error immediately instead of waiting | इंतज़ार की जगह तुरंत error |
| Outlier detection | Eject unhealthy hosts (Envoy) | बीमार सर्वर हटाना |
| Reset timeout | Time before half-open | फिर कोशिश से पहले का समय |

---

## ⚡ 3-Line Summary
**English:**
1. Circuit breaker: CLOSED (normal) → OPEN (fail fast after too many failures) → HALF-OPEN (probe) → CLOSED.
2. Prevents cascading failures and lets dependencies recover; count timeouts/5xx, not 4xx; one breaker per dependency.
3. Combine with timeouts, limited retries with backoff, and fallbacks (cache, defaults, alternate provider).

**Hindi:**
1. Circuit breaker: सामान्य → बहुत failures पर तुरंत मना (OPEN) → जाँच (HALF-OPEN) → सामान्य।
2. पूरे सिस्टम को गिरने से बचाता है; timeout/5xx गिनो, 4xx नहीं; हर dependency का अलग breaker।
3. Timeout, सीमित retry और fallback (cache, default, दूसरा provider) के साथ इस्तेमाल करो।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Circuit Breaker](https://www.youtube.com/results?search_query=circuit+breaker+pattern+bytebytego) | States (closed/open/half-open), cascading failures |
| 📺 YouTube | [Hussein Nasser — Circuit Breaker Pattern](https://www.youtube.com/results?search_query=circuit+breaker+microservices+hussein+nasser) | Implementation in Node.js, real examples |
| 📝 Article | [Martin Fowler — Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html) | Original pattern definition by Martin Fowler |
| 📝 Article | [Netflix Tech Blog — Hystrix](https://netflixtechblog.com/making-the-netflix-api-more-resilient-a8ec62159c2d) | How Netflix built resilience at scale with circuit breakers |
| 🐙 GitHub | [resilience4j](https://github.com/resilience4j/resilience4j) | Java circuit breaker library — see annotations and configs |

---

## ➡️ Next Topic Suggestion
**74. Retry + Exponential Backoff** — Before the breaker opens, brief glitches should be retried, but carefully. Next: when to retry, exponential backoff, retry budgets, and how naive retries can take down a system.
