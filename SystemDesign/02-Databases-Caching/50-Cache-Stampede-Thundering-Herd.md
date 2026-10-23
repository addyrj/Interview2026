# 50. Cache Stampede + Thundering Herd
# हिंदी में: Cache Stampede — किसी लोकप्रिय cache key के expire होते ही हज़ारों requests एक साथ DB पर टूट पड़ना; Thundering Herd — बहुत सारे clients का एक साथ जागकर एक ही resource पर हमला

---

## 🔵 Simple Definition (English)
- **Cache stampede (dog-piling):** a **hot cache key expires** (or is invalidated), and **many concurrent requests all miss at once**. Each one recomputes the value or queries the DB **simultaneously**, overloading it.
- **Thundering herd:** a broader term for **many clients/processes waking up at the same time** to hit the same resource: after a cache flush, a server restart, a network blip (all clients reconnect), or synchronized retries.

## 🔵 सरल परिभाषा (Hindi)
Cache stampede: एक बहुत लोकप्रिय key (जैसे homepage) expire हुई और उसी पल 10,000 requests को cache में नहीं मिली — सब एक साथ DB पर पहुँचीं और DB गिर गया।
Thundering herd: बहुत सारे clients एक साथ जागकर (restart, reconnect, retry) एक ही चीज़ पर टूट पड़ें।

---

## 🔴 Problem it Solves
Caches hide how weak the DB really is. If a homepage query takes 2 s and the cache serves 20,000 req/s:
```
t=0     key "home:feed" expires
t=0–2s  20,000 × 2 = 40,000 requests miss → all run the 2-second query on the DB
        DB CPU 100% → query takes 20s → more requests pile up → timeouts → retries → outage
```
This is how **a single expiring key can take down a whole site**. The fixes ensure that **only one request recomputes**, while others wait or get stale data.

## 🔴 यह क्यों बना? (Hindi)
Cache DB की कमज़ोरी छिपाता है। Homepage key expire हुई और 2 सेकंड की query के दौरान 40,000 requests सीधे DB पर गईं — DB 100%, query 20 सेकंड, retries, पूरा सिस्टम डाउन।
समाधान यह पक्का करते हैं कि सिर्फ़ एक request दोबारा गणना करे, बाक़ी इंतज़ार करें या पुराना डेटा लें।

---

## 🟢 How it Works — Step by Step

### The stampede

```
              key expires at t=0
                    │
 req1 ─ MISS ─┐     │
 req2 ─ MISS ─┤     ▼
 req3 ─ MISS ─┼──► DB (same expensive query × N)  💥
  ...         │
 reqN ─ MISS ─┘
```

### Fix 1 — Mutex / lock (single flight across servers)

```
 req1: MISS → SET lock:home NX EX 10 → got lock → query DB → SET home → DEL lock
 req2..N: MISS → lock exists → wait 50 ms & retry cache (or return stale value)

 Only ONE DB query. Others wait briefly.
 ⚠️ lock must have a TTL (process may crash); waiting requests need a timeout.
```

### Fix 2 — Request coalescing (in-process single-flight)

```
Within one app instance, concurrent requests for the same key share ONE in-flight Promise.
 100 concurrent requests on 1 instance → 1 DB call (not 100).
 Across 20 instances → at most 20 DB calls (combine with Fix 1 for 1).
```

### Fix 3 — Stale-while-revalidate / soft TTL (serve stale, refresh in background)

```
Store: { value, softExpiresAt }   with hard TTL = soft TTL + grace (e.g. 5 min + 1 min)
 now < softExpiresAt         → fresh, return
 softExpired but not hard    → return STALE value immediately + ONE background refresh (with lock)
 hard expired                → normal miss (lock/coalesce)
Users never wait; DB sees one refresh. ⭐ best UX
```

### Fix 4 — Probabilistic early expiration (XFetch)

```
Each request, as expiry approaches, has a small, increasing chance to refresh EARLY:
  refresh if  now - delta * beta * ln(random()) >= expiry
  (delta = time it takes to recompute, beta ≈ 1)
Refreshes are spread out randomly → no synchronized miss. No locks needed.
```

### Fix 5 — TTL jitter (avoid mass expiry)

```
❌ 100,000 product keys all cached at deploy time with TTL 3600 → all expire at the same second
✅ TTL = 3600 ± random(0–600) → expirations spread over 10 minutes
```

### Fix 6 — Pre-warming / never-expire hot keys

```
Background job refreshes known hot keys (homepage, top restaurants, config) every N seconds.
Keys never expire for users; refresher keeps them fresh.
Warm caches before switching traffic (after deploy, failover, new region).
```

### Thundering herd (beyond caches)

```
Scenario                                 Fix
───────────────────────────────────────  ──────────────────────────────────────────
All clients reconnect after outage/deploy exponential backoff + JITTER on reconnect
All retries happen at the same time      retry with backoff + jitter (Topics 74–75)
Cron at 00:00 on 1M devices              spread schedules randomly (± minutes)
Redis cluster restart → cold cache       warm-up, gradual traffic ramp, rate-limit DB
Celebrity post → millions open at once   request coalescing, CDN, pre-compute
Many workers waiting on one lock/queue   wake one at a time (fair locks), load shedding
```

## 🟢 कैसे काम करता है? (Hindi)
1. Lock: पहली miss वाली request `SET lock NX` से ताला लेती है और DB से लाती है; बाक़ी थोड़ा रुककर फिर cache देखती हैं।
2. Request coalescing: एक सर्वर पर एक ही key की 100 requests एक ही DB call साझा करती हैं।
3. Stale-while-revalidate: soft TTL पूरा होने पर पुराना डेटा तुरंत दो और पीछे सिर्फ़ एक refresh चलाओ — यूज़र को इंतज़ार नहीं।
4. TTL में jitter डालो ताकि सारी keys एक साथ expire न हों; ज़रूरी keys को background job से पहले ही ताज़ा रखो।
5. Reconnect और retry में भी exponential backoff + jitter — वरना सारे clients एक साथ टूट पड़ेंगे।

---

## 🟡 Real World Example

**Facebook (2010 outage)** — an automated config-verification system saw an invalid value and tried to "fix" it by querying the database. Every client did this at once, and the DB cluster was overwhelmed in a feedback loop. Facebook was down for about 2.5 hours. A textbook thundering herd.

**Facebook memcache leases** — to prevent stampedes, a miss returns a lease token only to the first requester. Others get "wait and retry shortly" (or a stale value), so only one client recomputes the value.

**Hotstar / JioCinema at match start** — millions of users open the app at the same second (toss time). Pre-warmed caches, CDN-served home pages and staggered client refresh schedules prevent the herd from hitting origin.

**Ticket sales (BookMyShow, Coldplay India 2024)** — massive traffic at sale-open time. Virtual waiting rooms (queue-it style) admit users gradually, turning a herd into a steady stream.

## 🟡 Real Example Hindi में
2010 में Facebook पर सारे clients ने एक साथ DB से config "ठीक" करने की कोशिश की — DB गिर गया और 2.5 घंटे outage रहा। यह thundering herd का मशहूर उदाहरण है।
Coldplay India जैसी ticket sale में waiting room से यूज़र्स को धीरे-धीरे अंदर भेजा जाता है, ताकि भीड़ एक साथ सर्वर पर न टूटे।

---

## 🟠 My Stack Example

### Node — single-flight (in-process coalescing) + Redis lock + stale-while-revalidate
```js
const inflight = new Map();                                   // key → Promise

function singleFlight(key, fn) {
  if (inflight.has(key)) return inflight.get(key);
  const p = fn().finally(() => inflight.delete(key));
  inflight.set(key, p);
  return p;
}

// value stored as { v, softExp } with hard TTL = soft + grace
async function getWithSWR(key, softTtlSec, loader, graceSec = 120) {
  const raw = await redis.get(key).catch(() => null);
  const now = Date.now();
  if (raw) {
    const { v, softExp } = JSON.parse(raw);
    if (now < softExp) return v;                              // fresh
    refreshInBackground(key, softTtlSec, graceSec, loader);   // stale → serve + refresh once
    return v;
  }
  return singleFlight(key, () => loadWithLock(key, softTtlSec, graceSec, loader));   // hard miss
}

async function loadWithLock(key, softTtlSec, graceSec, loader) {
  const lockKey = `lock:${key}`;
  const token = crypto.randomUUID();
  const gotLock = await redis.set(lockKey, token, { NX: true, PX: 10_000 });
  if (!gotLock) {                                             // someone else is loading
    for (let i = 0; i < 20; i++) {                            // wait up to ~1s
      await sleep(50);
      const raw = await redis.get(key);
      if (raw) return JSON.parse(raw).v;
    }
    return loader();                                          // fallback (rare)
  }
  try {
    const v = await loader();
    const ttl = softTtlSec + graceSec + Math.floor(Math.random() * 60);   // jitter
    await redis.set(key, JSON.stringify({ v, softExp: Date.now() + softTtlSec * 1000 }), { EX: ttl });
    return v;
  } finally {
    // release only if we still own the lock
    await redis.eval(`if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('del',KEYS[1]) end return 0`,
                     { keys: [lockKey], arguments: [token] });
  }
}

function refreshInBackground(key, softTtlSec, graceSec, loader) {
  singleFlight(`refresh:${key}`, () => loadWithLock(key, softTtlSec, graceSec, loader)).catch(() => {});
}

// usage
app.get('/api/v1/home', async (req, res) => {
  const feed = await getWithSWR('home:feed:mumbai', 60, () => buildHomeFeed('mumbai'));
  res.json(feed);
});
```

### FastAPI — asyncio single-flight
```python
_inflight: dict[str, asyncio.Future] = {}

async def single_flight(key: str, coro_fn):
    if key in _inflight:
        return await _inflight[key]
    fut = asyncio.get_running_loop().create_future()
    _inflight[key] = fut
    try:
        result = await coro_fn()
        fut.set_result(result)
        return result
    except Exception as e:
        fut.set_exception(e); raise
    finally:
        _inflight.pop(key, None)
```

### Pre-warm hot keys (cron / worker)
```js
setInterval(async () => {
  for (const city of TOP_CITIES) {
    const feed = await buildHomeFeed(city);
    await redis.set(`home:feed:${city}`, JSON.stringify({ v: feed, softExp: Date.now() + 60_000 }), { EX: 300 });
  }
}, 30_000);
```

### Client side: avoid the reconnect herd (React Native)
```ts
// exponential backoff with FULL jitter for reconnect/retry
const delay = (attempt: number) => Math.random() * Math.min(30_000, 1000 * 2 ** attempt);
// socket.io-client: reconnectionDelay: 1000, reconnectionDelayMax: 30000, randomizationFactor: 0.5
// Background sync scheduled at random minute offsets, not exactly on the hour
```

### Nginx/CDN level
```nginx
proxy_cache_lock on;                       # only one request populates a cache entry; others wait
proxy_cache_use_stale updating error timeout;  # serve stale while one request refreshes
proxy_cache_background_update on;
```
CloudFront/Cloudflare do request collapsing at the edge for cacheable content.

---

## ⚫ Interview Questions + Answers

**Q1: What is a cache stampede and how do you prevent it?**
A1: When a hot cached item expires or is invalidated, many concurrent requests miss at once and all hit the backend to recompute it, overloading it. Prevention: a distributed lock or single-flight so only one request recomputes, in-process request coalescing, stale-while-revalidate (serve the old value while one refresh runs), probabilistic early refresh (XFetch), TTL jitter to avoid synchronized expiry, pre-warming or background refresh of known hot keys, and edge features like Nginx `proxy_cache_lock`.

**Q2: What is the thundering herd problem? Give examples outside caching.**
A2: Many clients or processes simultaneously reacting to the same event and hitting the same resource. Examples: all mobile clients reconnecting to WebSocket servers after a deploy, synchronized retries after an outage, cron jobs at exactly midnight on millions of devices, many workers woken by one available lock or connection, and everyone loading a ticket page at sale time. Fixes: backoff with jitter, randomized schedules, waiting rooms or queues, rate limiting and load shedding, and gradual traffic ramp-up.

**Q3: Locking vs stale-while-revalidate — which is better?**
A3: Locking guarantees one recomputation, but other requests must wait (added latency) or need a fallback, and locks need TTLs and careful release. Stale-while-revalidate gives the best user latency, since requests get the slightly stale value instantly while one background refresh runs, but you must store the value past its soft expiry and accept brief staleness. In practice, use SWR for hot keys where slight staleness is fine, and a lock or single-flight for cold misses.

**Q4: Why add jitter to TTLs?**
A4: If many keys are written at the same time (deploy, cache warm-up, batch job) with the same TTL, they all expire at the same moment, causing a synchronized wave of misses and a DB load spike. Randomizing TTLs (e.g. ±10–20%) spreads expirations over time, smoothing backend load. The same idea applies to retries and reconnects.

**Q5: Your Redis cluster restarted and the DB is getting crushed. What do you do now and to prevent it next time?**
A5: Now: shed or rate-limit traffic to protect the DB (serve degraded responses for non-critical features, return cached CDN content), enable request coalescing or locks if available, and prioritize warming the hottest keys. Prevention: Redis replicas with automatic failover (no full cold start), persistence for faster warm restarts, pre-warming scripts, single-flight and SWR in code, circuit breakers and bulkheads around DB calls, gradual traffic ramp-up, and capacity tests for the cold-cache scenario.

---

## 🔷 Trade-offs
✅ Locks/single-flight: one recomputation → protects backend — ❌ waiting latency, lock complexity.
✅ SWR / soft TTL: zero user wait — ❌ brief staleness, more memory.
✅ Early probabilistic refresh: no locks, smooth — ❌ some extra recomputations.
✅ Pre-warming: hot keys never miss — ❌ must know hot keys; background load.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache stampede | Many simultaneous misses on hot key | एक साथ हज़ारों misses |
| Dog-piling | Another name for stampede | भीड़ का टूट पड़ना |
| Thundering herd | Many clients waking at once | सबका एक साथ जागना |
| Single-flight | One in-flight load per key | एक key, एक ही लोडिंग |
| Request coalescing | Merge identical concurrent requests | एक जैसी requests को जोड़ना |
| Soft TTL | Refresh point before hard expiry | असली expiry से पहले का बिंदु |
| Jitter | Random spread of timings | समय में random फ़र्क़ |
| Pre-warming | Filling cache before traffic | ट्रैफ़िक से पहले cache भरना |
| Lease | Permission token to recompute | दोबारा गणना की अनुमति |

---

## ⚡ 3-Line Summary
**English:**
1. Stampede: a hot key expires and many requests recompute it at once → DB overload; thundering herd: many clients act simultaneously.
2. Fixes: lock/single-flight, request coalescing, stale-while-revalidate, early refresh, TTL jitter, pre-warming.
3. Beyond caches: backoff + jitter for retries/reconnects, waiting rooms, load shedding.

**Hindi:**
1. Stampede: लोकप्रिय key expire → हज़ारों requests DB पर; thundering herd: सबका एक साथ हमला।
2. इलाज: lock/single-flight, coalescing, stale-while-revalidate, early refresh, jitter, pre-warming।
3. Cache के बाहर भी: retry/reconnect में backoff + jitter, waiting room, load shedding।

---

## ➡️ Next Topic Suggestion
**51. CDN — Content Delivery Network** — The biggest cache of all sits at the edge of the internet. Next: how CDNs work, what to cache there (static, images, video, even API responses), cache keys, and purging.
