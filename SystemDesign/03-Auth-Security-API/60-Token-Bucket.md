# 60. Token Bucket Algorithm
# हिंदी में: Token Bucket — एक बाल्टी जिसमें तय रफ़्तार से टोकन भरते हैं; हर request एक टोकन ख़र्च करती है; बाल्टी ख़ाली तो request रुक जाती है

---

## 🔵 Simple Definition (English)
In the **token bucket** algorithm, each client has a **bucket** that holds up to **B tokens (capacity)** and is **refilled at R tokens per second**. Each request **consumes one token** (or more, by cost). If tokens are available, the request is allowed; if the bucket is **empty**, it's rejected (429) or delayed.
It allows **short bursts** (up to B) while enforcing an **average rate** (R).

## 🔵 सरल परिभाषा (Hindi)
हर यूज़र की एक बाल्टी है जिसमें अधिकतम B टोकन आ सकते हैं, और हर सेकंड R टोकन भरते हैं। हर request एक टोकन लेती है; टोकन ख़त्म तो request मना।
इससे थोड़े समय के लिए तेज़ी (burst, B तक) मिलती है, पर औसत रफ़्तार R से ज़्यादा नहीं होती।

---

## 🔴 Problem it Solves
Simple fixed-window counters ("100 per minute") have issues:
- **Edge bursts:** 100 requests at 12:00:59 + 100 at 12:01:00 = 200 in 2 seconds.
- **No burst control:** real clients are bursty (an app opening fires 10 API calls at once). A strict per-second limit would reject legitimate bursts.

The token bucket gives **exactly what we usually want**: "on average 10 req/s, but allow a burst of up to 20 at once", using only **2 numbers of state per client** (tokens + last refill time).

## 🔴 यह क्यों बना? (Hindi)
Fixed window में सीमा के किनारे पर दो गुना requests हो जाती हैं, और सख़्त प्रति-सेकंड सीमा ऐप खुलते समय की 10 साथ वाली requests भी रोक देती है।
Token bucket ठीक वही देता है जो चाहिए: "औसत 10/सेकंड, पर एक साथ 20 तक चलेगा" — और हर यूज़र के लिए सिर्फ़ 2 numbers रखने पड़ते हैं।

---

## 🟢 How it Works — Step by Step

```
          refill: R tokens/sec  (e.g. 10/s)
                    │
                    ▼
            ┌───────────────┐
            │ ● ● ● ● ● ●   │   capacity B = 20 tokens (max burst)
            │ ● ● ● ● ●     │   current = 11
            └───────┬───────┘
                    │ each request takes 1 token
                    ▼
     request ──► token available? ── yes ──► ALLOW (tokens - 1)
                                  └─ no  ──► REJECT 429 (or wait)
```

### Lazy refill (no timer needed)

```
State per key: tokens, last_refill_ts

On each request at time now:
  elapsed  = now - last_refill_ts
  tokens   = min(B, tokens + elapsed × R)        ← add tokens earned since last time
  last_refill_ts = now
  if tokens ≥ cost:  tokens -= cost → ALLOW
  else:             → REJECT, retry_after = (cost - tokens) / R
```

### Example: R = 2 tokens/s, B = 5

```
t=0.0  tokens 5  → 5 requests at once → all allowed (burst)  → tokens 0
t=0.1  request   → tokens 0 + 0.1×2 = 0.2 → REJECT (retry after 0.4s)
t=1.0  tokens = min(5, 0.2 + 0.9×2) = 2.0 → 2 requests allowed
t=10   idle 9s → tokens refill to 5 (capped) → another burst possible
Long-run average can't exceed 2 req/s.
```

### Variants
```
Weighted cost      → expensive endpoints cost more tokens (export = 10, read = 1)
Multiple buckets   → per-second AND per-day (short burst + daily quota)
Hierarchical       → per user AND per tenant AND global
Token bucket for SHAPING (not just limiting) → queue requests until tokens available (adds latency)
```

### Token bucket vs leaky bucket (preview of next topic)
```
Token bucket:  allows bursts up to B; output can be bursty; limits average rate
Leaky bucket:  output at constant rate; bursts are queued/smoothed (or dropped)
```

### Where it's used
```
AWS API Gateway throttling (rate + burst), AWS EC2 API, EBS burst credits (similar concept),
Stripe API limiter, Nginx limit_req (leaky-bucket-like with burst), Linux tc (traffic shaping),
Envoy local rate limit, Guava RateLimiter, most SDK client-side throttles.
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर key के लिए दो चीज़ें रखो: अभी कितने टोकन हैं, और आख़िरी बार कब भरे।
2. Request आने पर बीते समय के हिसाब से टोकन जोड़ो (elapsed × R), पर B से ज़्यादा नहीं।
3. टोकन ≥ 1 हो तो अनुमति और 1 घटाओ; नहीं तो 429 और बताओ कितनी देर बाद आना है।
4. ख़ाली बैठे यूज़र की बाल्टी भर जाती है, इसलिए एक साथ B requests (burst) चल जाती हैं।
5. भारी endpoint ज़्यादा टोकन ले सकता है (weighted cost); Redis में Lua script से atomic रखो।

---

## 🟡 Real World Example

**AWS API Gateway** — throttling is configured as **rate** (steady-state requests per second) and **burst** (bucket capacity), exactly the token bucket. The default account limit is 10,000 RPS with a 5,000 burst.

**Stripe** — has publicly described using token-bucket rate limiters, backed by Redis, for request rate limiting per user, alongside concurrency limiters.

**AWS EBS gp2 volumes and EC2 T-series CPU credits** — earn credits over time and spend them on bursts. That's the same idea applied to IOPS and CPU.

**Mobile SDKs** — analytics SDKs (Firebase, Segment) throttle uploads client-side using token-bucket-like logic so the app doesn't flood the network.

## 🟡 Real Example Hindi में
AWS API Gateway में throttling "rate" और "burst" से सेट होती है — यही token bucket है। Stripe भी Redis वाले token bucket से हर यूज़र की requests सीमित करता है।
AWS की T-series मशीनें खाली समय में CPU credits कमाती हैं और ज़रूरत पर burst में ख़र्च करती हैं — वही सोच।

---

## 🟠 My Stack Example

### Redis Lua — atomic token bucket (works across all API instances)
```lua
-- KEYS[1] = bucket key ; ARGV: capacity, refill_per_sec, now_ms, cost
local cap    = tonumber(ARGV[1])
local rate   = tonumber(ARGV[2])
local now    = tonumber(ARGV[3])
local cost   = tonumber(ARGV[4])

local b = redis.call('HMGET', KEYS[1], 'tokens', 'ts')
local tokens = tonumber(b[1]) or cap
local ts     = tonumber(b[2]) or now

tokens = math.min(cap, tokens + (now - ts) / 1000 * rate)
local allowed = 0
local retry_ms = 0
if tokens >= cost then
  tokens = tokens - cost
  allowed = 1
else
  retry_ms = math.ceil((cost - tokens) / rate * 1000)
end
redis.call('HSET', KEYS[1], 'tokens', tokens, 'ts', now)
redis.call('PEXPIRE', KEYS[1], math.ceil(cap / rate * 1000) * 2)   -- idle buckets expire
return { allowed, math.floor(tokens), retry_ms }
```

### Node.js middleware using it
```js
const TOKEN_BUCKET_LUA = fs.readFileSync('./token_bucket.lua', 'utf8');
// (use redis.scriptLoad + evalSha in production)

function tokenBucket({ capacity, refillPerSec, cost = () => 1, key }) {
  return async (req, res, next) => {
    try {
      const [allowed, remaining, retryMs] = await redis.eval(TOKEN_BUCKET_LUA, {
        keys: [`tb:${key(req)}`],
        arguments: [String(capacity), String(refillPerSec), String(Date.now()), String(cost(req))],
      });
      res.set('RateLimit-Limit', String(capacity)).set('RateLimit-Remaining', String(remaining));
      if (allowed === 1) return next();
      res.set('Retry-After', String(Math.ceil(retryMs / 1000)));
      return res.status(429).json({ error: 'RATE_LIMITED' });
    } catch { return next(); }              // fail open if Redis unavailable
  };
}

// 10 req/s average, burst 20; exports cost 10 tokens
app.use('/api', authenticate, tokenBucket({
  capacity: 20, refillPerSec: 10,
  key: (req) => req.user.id,
  cost: (req) => (req.path.startsWith('/reports/export') ? 10 : 1),
}));
```

### In-process token bucket (client-side throttle / single instance)
```ts
class TokenBucket {
  private tokens: number; private last = Date.now();
  constructor(private capacity: number, private ratePerSec: number) { this.tokens = capacity; }
  tryTake(cost = 1) {
    const now = Date.now();
    this.tokens = Math.min(this.capacity, this.tokens + ((now - this.last) / 1000) * this.ratePerSec);
    this.last = now;
    if (this.tokens >= cost) { this.tokens -= cost; return true; }
    return false;
  }
}
// React Native: throttle analytics uploads or "pull-to-refresh" spam
const refreshBucket = new TokenBucket(3, 0.2);   // burst 3, then 1 per 5 s
if (!refreshBucket.tryTake()) showToast('Please wait a moment');
```

### Python (FastAPI) calling the same Lua script
```python
TB = r.register_script(open("token_bucket.lua").read())

async def allow(user_id: str, cap=20, rate=10, cost=1):
    allowed, remaining, retry_ms = await TB(keys=[f"tb:{user_id}"], args=[cap, rate, int(time.time()*1000), cost])
    return allowed == 1, remaining, retry_ms
```

### Protect a downstream API you call (outbound throttle)
```js
// Partner allows 50 req/s → use a token bucket (bottleneck library) so you never exceed it
import Bottleneck from 'bottleneck';
const limiter = new Bottleneck({ reservoir: 50, reservoirRefreshAmount: 50, reservoirRefreshInterval: 1000, maxConcurrent: 10 });
const callPartner = limiter.wrap((payload) => fetch(PARTNER_URL, { method: 'POST', body: JSON.stringify(payload) }));
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain the token bucket algorithm.**
A1: Each client has a bucket with capacity B, refilled at R tokens per second. A request consumes tokens (usually one). If enough tokens are present it's allowed, otherwise it's rejected or delayed. The capacity bounds the maximum burst, and the refill rate bounds the long-term average. It's implemented lazily: on each request, add `elapsed × R` tokens (capped at B), then try to subtract the cost.

**Q2: How is token bucket different from a fixed window counter?**
A2: A fixed window counts requests per calendar window and resets abruptly, so clients can send 2× the limit across a window boundary, and it can't express "allow a short burst but limit the average". The token bucket refills continuously, so there are no boundary spikes, and its burst size is configurable separately from the sustained rate.

**Q3: How would you implement a token bucket in a distributed system?**
A3: Store `tokens` and `last_refill_ts` per key in Redis and do the refill and consume step atomically in a Lua script (or with a transaction), so concurrent requests on different instances can't double-spend. Expire idle keys. Use server time consistently (the script's `now` from one source, or Redis `TIME`) to avoid clock skew. For extreme scale, use local buckets per instance with a share of the global rate, or a centralized rate-limit service.

**Q4: How do you choose capacity (B) and rate (R)?**
A4: R is the sustained throughput the backend or business allows per client (from capacity planning, or the plan tier: 10 req/s). B should cover legitimate bursts, such as the number of parallel calls when an app screen loads, or batch operations, without letting a client spike enough to hurt others. Monitor 429 rates and adjust. Use weighted costs for expensive endpoints, and add a second long-window bucket (daily quota) if needed.

**Q5: When would you prefer leaky bucket over token bucket?**
A5: When the downstream system needs a smooth, constant rate with no bursts: sending to an SMS provider at exactly 50 per second, writing to a fragile legacy system, or network traffic shaping. A leaky bucket queues requests and processes them at a fixed rate (excess dropped when the queue is full). A token bucket is better for user-facing APIs where short bursts are normal and you want to limit the average.

---

## 🔷 Trade-offs
✅ Advantages:
- Allows natural bursts while enforcing average rate; tiny state per key; O(1).
- Flexible: weighted costs, multiple buckets, works for limiting or shaping.

❌ Disadvantages:
- Bursts can still momentarily stress backends (choose B carefully).
- Two parameters to tune; distributed version needs atomic ops and clock care.
- Doesn't by itself guarantee smooth output (use leaky bucket for that).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Token bucket | Bucket of tokens refilled at rate R | टोकन वाली बाल्टी |
| Capacity (B) | Max tokens = max burst | अधिकतम टोकन |
| Refill rate (R) | Tokens added per second | प्रति सेकंड भरने वाले टोकन |
| Burst | Many requests at once | एक साथ कई requests |
| Lazy refill | Compute tokens on request | request पर ही टोकन गिनना |
| Weighted cost | Expensive request uses more tokens | भारी request ज़्यादा टोकन |
| Lua script | Atomic Redis logic | Redis में atomic code |
| Traffic shaping | Smoothing traffic over time | ट्रैफ़िक को समान करना |

---

## ⚡ 3-Line Summary
**English:**
1. Token bucket: capacity B (max burst) refilled at R/sec (average rate); each request consumes tokens.
2. Implement lazily with (tokens, last_ts) and atomic Redis Lua for distributed limits.
3. Best for user-facing APIs (bursty clients); used by AWS API Gateway, Stripe, Envoy.

**Hindi:**
1. Token bucket: B टोकन की बाल्टी, R प्रति सेकंड भरती है; हर request टोकन लेती है।
2. (tokens, last_ts) से lazy गिनती, और Redis Lua से कई सर्वरों में atomic।
3. User APIs के लिए सबसे बढ़िया; AWS API Gateway, Stripe इसे इस्तेमाल करते हैं।

---

## ➡️ Next Topic Suggestion
**61. Leaky Bucket Algorithm** — The token bucket allows bursts. Next: its sibling, the leaky bucket, which smooths traffic to a constant output rate, ideal for protecting fragile downstream systems.
