# 62. Sliding Window Algorithm
# हिंदी में: Sliding Window — "पिछले 60 सेकंड में कितनी requests हुईं" को हर पल नए सिरे से गिनना, ताकि घड़ी के मिनट की सीमा पर दो गुना requests न हो सकें

---

## 🔵 Simple Definition (English)
**Sliding window** rate limiting counts requests in the **last N seconds relative to now** (a window that moves with time), instead of fixed clock windows like "12:01:00–12:01:59". Two main variants:
1. **Sliding window log:** store a **timestamp for every request**; count those within `[now − window, now]`. Exact, but memory-heavy.
2. **Sliding window counter:** keep counts for the **current and previous fixed windows** and compute a **weighted estimate**. Nearly exact, O(1) memory. ⭐ Most common.

## 🔵 सरल परिभाषा (Hindi)
Sliding window में हम "अभी से पिछले 60 सेकंड" की requests गिनते हैं — खिड़की समय के साथ खिसकती रहती है।
Log तरीका: हर request का समय सेव करो (बिल्कुल सही, पर ज़्यादा memory)। Counter तरीका: अभी की और पिछली खिड़की की गिनती से अनुमान लगाओ (लगभग सही, बहुत कम memory) — यही सबसे आम है।

---

## 🔴 Problem it Solves
The **fixed window counter** (`INCR rl:user:12:01` with a 60 s expiry) is simple but has the **boundary burst problem**:
```
Limit: 100 / minute
12:00:30–12:00:59 → 0 requests
12:00:59.9        → 100 requests  (window 12:00 → allowed)
12:01:00.1        → 100 requests  (new window 12:01 → allowed)
= 200 requests in 0.2 seconds ❌ (2× the intended limit)
```
Sliding windows make the limit hold for **any** 60-second period, giving smoother, fairer enforcement.

## 🔴 यह क्यों बना? (Hindi)
Fixed window में 12:00:59 पर 100 और 12:01:00 पर फिर 100 requests — 0.2 सेकंड में 200, यानी सीमा की दो गुनी।
Sliding window किसी भी 60 सेकंड के हिस्से में सीमा पक्की रखता है — ज़्यादा सही और न्यायपूर्ण।

---

## 🟢 How it Works — Step by Step

### Variant 1: Sliding window LOG (exact)

```
Store each request timestamp in a sorted set per key.
On request at time now:
  1. remove timestamps < now − window       (ZREMRANGEBYSCORE)
  2. count remaining                         (ZCARD)
  3. if count < limit → add now (ZADD) → ALLOW
     else → REJECT; retry_after = oldest_timestamp + window − now

Timeline (limit 3 per 10s):
 t=1  ✓ [1]
 t=2  ✓ [1,2]
 t=5  ✓ [1,2,5]
 t=8  ✗ (3 in [−2,8])
 t=11 ✓ [2,5,11]   ← t=1 slid out of window
Memory: O(limit) per key  (100k users × 1000 limit = 100M entries ❌ at scale)
```

### Variant 2: Sliding window COUNTER (approximate, cheap) ⭐

```
Keep two fixed-window counters: previous window and current window.
Estimate requests in the sliding window:

  estimate = prev_count × (overlap fraction of previous window) + curr_count

  overlap = (window − elapsed_in_current) / window

Example: limit 100/min
  previous minute (12:00) count = 80
  current minute  (12:01) count = 30
  now = 12:01:15 → 15s into current window → overlap of previous = 45/60 = 0.75
  estimate = 80 × 0.75 + 30 = 90  → under 100 → ALLOW (then curr = 31)

Assumes previous window's requests were evenly spread — small error, but:
  Cloudflare measured ~0.003% of requests wrongly allowed/limited across 400M requests.
Memory: 2 counters per key ✅
```

### Comparing all rate limiting algorithms

```
┌────────────────────────┬────────────┬──────────┬───────────────┬──────────────────────┐
│ Algorithm              │ Accuracy   │ Memory   │ Bursts        │ Notes                │
├────────────────────────┼────────────┼──────────┼───────────────┼──────────────────────┤
│ Fixed window counter   │ Low (2×    │ O(1)     │ edge bursts   │ simplest (INCR+TTL)  │
│                        │ at edges)  │          │               │                      │
│ Sliding window log     │ Exact      │ O(limit) │ none          │ costly at scale      │
│ Sliding window counter │ ~Exact     │ O(1)     │ smoothed      │ ⭐ best general       │
│ Token bucket           │ Exact avg  │ O(1)     │ allowed (B)   │ ⭐ bursty APIs        │
│ Leaky bucket (queue)   │ Exact rate │ O(queue) │ smoothed      │ shaping downstream   │
└────────────────────────┴────────────┴──────────┴───────────────┴──────────────────────┘
Interview tip: mention fixed window's edge problem → propose sliding window counter or
token bucket, both implemented atomically in Redis.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Log तरीका: हर request का timestamp Redis sorted set में; 60 सेकंड से पुराने हटाओ, बचे गिनो, सीमा से कम तो नया जोड़ो।
2. Log बिल्कुल सही है, पर हर यूज़र के लिए सैकड़ों timestamps — बड़े स्केल पर बहुत memory।
3. Counter तरीका: सिर्फ़ दो गिनती रखो — पिछला मिनट और यह मिनट।
4. अनुमान = पिछली गिनती × (पिछली खिड़की का बचा हिस्सा) + अभी की गिनती; सीमा से कम तो अनुमति।
5. Cloudflare के अनुसार इसकी ग़लती लगभग शून्य (0.003%) है, और memory सिर्फ़ 2 numbers।

---

## 🟡 Real World Example

**Cloudflare Rate Limiting** — publicly described using the **sliding window counter** (previous + current counts with weighting) across its global network, because it gives near-exact limits with minimal memory and works with simple counters spread across edge nodes.

**Kong / many API gateways** — offer "sliding" window policies backed by Redis to avoid fixed-window edge spikes for paying API customers.

**Login protection at banks** — "max 5 failed attempts in any 15-minute period" is a sliding window, so attackers can't time their attempts around window resets.

**Figma, Stripe engineering blogs** — discuss moving from fixed windows to sliding windows or token buckets after noticing synchronized bursts at window boundaries.

## 🟡 Real Example Hindi में
Cloudflare दुनिया भर में sliding window counter इस्तेमाल करता है — सिर्फ़ दो गिनती से लगभग बिल्कुल सही सीमा।
बैंक login में "किसी भी 15 मिनट में 5 ग़लत कोशिश" sliding window है — हैकर window reset का फ़ायदा नहीं उठा सकता।

---

## 🟠 My Stack Example

### Sliding window LOG with Redis sorted set (exact) — Node
```js
async function slidingLog(key, limit, windowMs) {
  const now = Date.now();
  const member = `${now}-${Math.random().toString(36).slice(2)}`;
  const res = await redis.multi()
    .zRemRangeByScore(key, 0, now - windowMs)
    .zCard(key)
    .exec();
  const count = Number(res[1]);
  if (count >= limit) {
    const [oldest] = await redis.zRangeWithScores(key, 0, 0);
    return { allowed: false, retryAfterMs: oldest ? oldest.score + windowMs - now : windowMs };
  }
  await redis.multi().zAdd(key, { score: now, value: member }).pExpire(key, windowMs).exec();
  return { allowed: true, remaining: limit - count - 1 };
}
// (For strict atomicity under high concurrency, move the whole thing into one Lua script.)
```

### Sliding window COUNTER with Redis Lua (cheap, ~exact) ⭐
```lua
-- KEYS[1] = key prefix ; ARGV: limit, window_sec, now_sec(float)
local limit  = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now    = tonumber(ARGV[3])

local curr_start = math.floor(now / window) * window
local prev_start = curr_start - window
local curr_key = KEYS[1] .. ':' .. curr_start
local prev_key = KEYS[1] .. ':' .. prev_start

local curr = tonumber(redis.call('GET', curr_key) or '0')
local prev = tonumber(redis.call('GET', prev_key) or '0')

local elapsed = now - curr_start
local weight  = (window - elapsed) / window
local estimate = prev * weight + curr

if estimate >= limit then
  return { 0, math.floor(estimate) }
end
redis.call('INCR', curr_key)
redis.call('EXPIRE', curr_key, window * 2)
return { 1, math.floor(estimate) + 1 }
```
```js
const SW = fs.readFileSync('sliding_window.lua', 'utf8');
async function allow(userId, limit = 100, windowSec = 60) {
  const [ok, used] = await redis.eval(SW, { keys: [`sw:${userId}`], arguments: [String(limit), String(windowSec), String(Date.now() / 1000)] });
  return { allowed: ok === 1, remaining: Math.max(0, limit - used) };
}
```

### FastAPI — same Lua via redis-py
```python
SW = r.register_script(open("sliding_window.lua").read())

async def rate_limit(request: Request, user=Depends(current_user)):
    ok, used = await SW(keys=[f"sw:{user['id']}"], args=[100, 60, time.time()])
    if not ok:
        raise HTTPException(429, "RATE_LIMITED", headers={"Retry-After": "10"})

@app.get("/search", dependencies=[Depends(rate_limit)])
async def search(q: str): ...
```

### Fixed window (for comparison — simplest)
```js
const key = `fw:${uid}:${Math.floor(Date.now() / 60000)}`;
const n = await redis.incr(key);
if (n === 1) await redis.expire(key, 60);
if (n > 100) return res.status(429).end();
```

### Choosing in your projects
```
Login / OTP / password reset → sliding window log (exact, low volume per key)
General API per user          → sliding window counter or token bucket
Partner/outbound pacing       → leaky bucket (queue)
Quick internal tool           → fixed window is fine
```

---

## ⚫ Interview Questions + Answers

**Q1: What's wrong with fixed window rate limiting?**
A1: Windows reset at fixed clock boundaries, so a client can use its full quota at the end of one window and again at the start of the next, sending up to 2× the limit in a short span. Traffic also spikes synchronously at window starts across many clients. It's simple and cheap (one counter with a TTL), and acceptable for coarse limits.

**Q2: Explain sliding window log vs sliding window counter.**
A2: The log stores a timestamp per request (e.g. in a Redis sorted set), removes entries older than the window and counts the rest. It's exact, but memory is O(limit) per client and operations cost more. The counter keeps only the current and previous fixed-window counts and estimates the sliding count as `prev × overlap_fraction + curr`. It's O(1) memory and nearly exact (assuming requests were uniform in the previous window). That's what Cloudflare uses at scale.

**Q3: How would you implement a sliding window limiter in Redis atomically?**
A3: Put the logic in a Lua script so the read-compute-increment happens atomically on the Redis server. For the counter variant: compute current and previous window keys from time, GET both, compute the weighted estimate, reject if it's at or over the limit, otherwise INCR the current key with an EXPIRE of about 2 windows. For the log variant: ZREMRANGEBYSCORE, ZCARD, conditional ZADD and PEXPIRE inside the script. Use a consistent time source.

**Q4: Sliding window vs token bucket — which would you choose for an API?**
A4: Both are good O(1) choices. The token bucket explicitly allows bursts up to capacity while enforcing an average rate, which fits clients that naturally send bursts (an app screen load). The sliding window counter enforces "no more than N in any rolling window" with smoother behaviour and simpler semantics for users ("100 per minute"). Many gateways offer both. Pick based on whether bursts are desirable, and expose clear headers either way.

**Q5: Design rate limiting for "5 failed login attempts per account in any 15 minutes, then lock".**
A5: Use a sliding window log per account key (low volume, needs exactness): on each failure, ZADD the timestamp and ZREMRANGEBYSCORE older than 15 minutes. If ZCARD reaches 5 or more, set a lock key with a 15-minute TTL and reject logins with a generic message. Clear on successful login. Add a per-IP limit to stop credential stuffing across accounts, CAPTCHA after 3 failures, alerts for spikes, and don't reveal whether the account exists.

---

## 🔷 Trade-offs
✅ Sliding log: exact — ❌ memory O(limit), heavier ops.
✅ Sliding counter: O(1), near-exact, no edge bursts — ❌ small approximation error.
✅ Fixed window: simplest — ❌ 2× edge bursts.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fixed window | Count per clock interval | घड़ी के अंतराल में गिनती |
| Sliding window | Count over last N seconds from now | अभी से पिछले N सेकंड |
| Window boundary burst | 2× traffic at window edges | सीमा पर दो गुना requests |
| Sliding log | Store all request timestamps | हर request का समय रखना |
| Sliding counter | Weighted prev + current counts | दो गिनतियों से अनुमान |
| Sorted set | Redis structure ordered by score | score से sorted सेट |
| Atomic script | Lua executes without interruption | बिना रुकावट चलने वाला code |
| Lockout | Temporary block after failures | ग़लतियों के बाद अस्थायी रोक |

---

## ⚡ 3-Line Summary
**English:**
1. Fixed windows allow 2× bursts at edges; sliding windows enforce the limit over any rolling period.
2. Sliding log = exact (sorted set of timestamps, O(limit) memory); sliding counter = weighted prev+curr counts (O(1), ~exact) ⭐.
3. Implement atomically in Redis Lua; use log for low-volume security limits, counter/token bucket for general APIs.

**Hindi:**
1. Fixed window में किनारे पर दो गुना requests; sliding window किसी भी 60 सेकंड में सीमा पक्की रखता है।
2. Sliding log = बिल्कुल सही पर ज़्यादा memory; sliding counter = दो गिनती से लगभग सही, बहुत कम memory।
3. Redis Lua में atomic बनाओ; login/OTP के लिए log, सामान्य API के लिए counter या token bucket।

---

## ➡️ Next Topic Suggestion
**63. API Versioning** — Your API is now secure and protected. Next: how to change it over time without breaking web and (especially) old mobile app versions: URL vs header versioning, deprecation and backward compatibility.
