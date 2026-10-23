# 45. Cache-Aside Pattern (Lazy Loading)
# हिंदी में: Cache-Aside — ऐप पहले cache में देखता है; नहीं मिला तो DB से लाकर cache में रखता है (ज़रूरत पड़ने पर ही cache भरना)

---

## 🔵 Simple Definition (English)
In **cache-aside** (also called **lazy loading**), the **application** manages the cache:
1. **Read:** check the cache → on a **hit**, return it → on a **miss**, read from the DB, **store it in the cache**, then return it.
2. **Write:** update the **DB**, then **invalidate (delete)** the cache key, so the next read reloads fresh data.
The cache sits "aside" the DB; the DB doesn't know the cache exists. It's the **most common caching pattern**.

## 🔵 सरल परिभाषा (Hindi)
Cache-aside में ऐप ख़ुद cache संभालता है: पढ़ते समय पहले cache देखो, नहीं मिला तो DB से लाओ और cache में रख दो।
लिखते समय DB अपडेट करो और cache की key हटा दो, ताकि अगली बार ताज़ा डेटा आए। सबसे आम caching तरीका यही है।

---

## 🔴 Problem it Solves
You want caching benefits **without**:
- Pre-loading the entire DB into memory (wasteful; most data is never read).
- Changing the DB or adding special infrastructure.
- Making the cache a hard dependency (if Redis dies, the app should still work).

Cache-aside caches **only what's actually requested** (popular data naturally stays hot), keeps the DB as the **source of truth**, and degrades gracefully when the cache is down.

## 🔴 यह क्यों बना? (Hindi)
पूरा DB memory में भरना बेकार है (ज़्यादातर डेटा कभी पढ़ा ही नहीं जाता), और cache को ज़रूरी dependency भी नहीं बनाना।
Cache-aside सिर्फ़ वही डेटा cache करता है जो माँगा गया, DB सच का स्रोत रहता है, और Redis गिरे तो ऐप DB से चलता रहता है।

---

## 🟢 How it Works — Step by Step

### Read path

```
App                         Redis                        DB
 │ 1. GET product:7  ───────►│
 │◄──── nil (MISS) ──────────│
 │ 2. SELECT * FROM products WHERE id=7 ───────────────►│
 │◄──────────────────────────────────── row ────────────│
 │ 3. SET product:7 <json> EX 600 ──►│
 │ 4. return row
 ...
 │ 5. GET product:7  ───────►│
 │◄──── <json> (HIT) ────────│   ← no DB call
```

### Write path (update DB, then DELETE cache)

```
App                         DB                          Redis
 │ 1. UPDATE products SET price=999 WHERE id=7 ──►│
 │◄─────────────────────────── OK ────────────────│
 │ 2. DEL product:7 ─────────────────────────────────────────►│
 │ next read → MISS → loads fresh price → caches it
```

### Why DELETE instead of UPDATE the cache on write?

```
Option A: update cache with new value
  Two concurrent writers:  W1 sets DB=100, W2 sets DB=200
  Cache updates arrive out of order: cache=200 then 100 → cache=100, DB=200 ❌ stale forever (until TTL)

Option B: delete cache key  ✅ (preferred)
  Next reader loads the current DB value. Simpler and safer.
  Also avoids computing expensive cached values that nobody reads.
```

### The remaining race (and fixes)

```
Rare race with delete-on-write:
  t1 Reader: cache MISS → reads DB (old value 100)
  t2 Writer: UPDATE DB = 200 → DEL cache
  t3 Reader: SET cache = 100   ← stale value written AFTER the delete ❌

Mitigations:
  1. Always set a TTL → staleness is bounded (e.g. ≤ 5 min)
  2. Delayed double delete: DEL now, and DEL again after ~500 ms
  3. Versioned keys: product:7:v{version} — writer bumps version; old key ignored
  4. Read-repair via CDC: DB change stream → invalidate keys (reliable, decoupled)
  5. For must-be-fresh reads, bypass cache
```

### Order of operations matters

```
✅ Update DB → then delete cache
❌ Delete cache → then update DB
   (between the two, a reader reloads OLD data into cache → stale until TTL)
❌ Update cache only (DB later) → that's write-back, different pattern (Topic 47)
If the DEL fails (Redis blip) → retry / log / TTL saves you. Never fail the user's write because DEL failed.
```

### Cache-aside vs other patterns (preview)

```
Cache-aside   → app reads cache, loads from DB on miss; writes go to DB + invalidate   ← default
Read-through  → cache library/provider loads from DB on miss (app only talks to cache)
Write-through → write to cache AND DB synchronously (Topic 46)
Write-back    → write to cache, flush to DB later (Topic 47)
Refresh-ahead → refresh hot keys before they expire
```

## 🟢 कैसे काम करता है? (Hindi)
1. पढ़ना: Redis में key देखो → मिली तो लौटा दो; नहीं मिली तो DB से पढ़ो, Redis में TTL के साथ रखो, लौटा दो।
2. लिखना: पहले DB अपडेट करो, फिर cache की key DELETE करो (update नहीं)।
3. Delete इसलिए, क्योंकि दो writers के बीच cache update उल्टे क्रम में पहुँचे तो ग़लत value अटक सकती है।
4. एक दुर्लभ race में पुराना डेटा cache में आ सकता है — TTL, delayed double delete या versioned keys से बचाओ।
5. Redis की ग़लती पर यूज़र का write फ़ेल मत करो; TTL आख़िर में सब ठीक कर देता है।

---

## 🟡 Real World Example

**Facebook Memcache ("Scaling Memcache at Facebook", 2013)** — the most famous cache-aside system. Web servers read from memcache, fall back to MySQL on a miss and fill the cache. On writes they update MySQL and **delete** the memcache key. To fix the stale-set race, they introduced **leases**: a miss gets a lease token, and a set is rejected if a delete happened in between. They also invalidate across regions via their MySQL replication stream (McSqueal).

**E-commerce product pages (Flipkart, Myntra)** — product details are cached aside with TTLs of minutes. Price or stock updates trigger invalidation events so the next view loads fresh data.

**Most Node/Django/Rails apps** — cache-aside with Redis is the default pattern behind "make this endpoint faster".

## 🟡 Real Example Hindi में
Facebook का Memcache सबसे मशहूर cache-aside सिस्टम है — miss पर MySQL से पढ़कर cache भरते हैं, write पर cache key delete करते हैं, और stale race रोकने के लिए "lease" token इस्तेमाल करते हैं।
Flipkart/Myntra के product pages मिनटों के TTL के साथ cache होते हैं; कीमत बदलने पर invalidation event से key हट जाती है।

---

## 🟠 My Stack Example

### Node.js — production cache-aside with timeouts, versioned keys, safe invalidation
```js
const CACHE_TIMEOUT_MS = 50;
const withTimeout = (p, ms) => Promise.race([p, new Promise((_, r) => setTimeout(() => r(new Error('timeout')), ms))]);

async function getProduct(id) {
  const key = `product:v1:${id}`;                     // bump v1 → v2 when the JSON shape changes
  try {
    const hit = await withTimeout(redis.get(key), CACHE_TIMEOUT_MS);
    if (hit) { metrics.cacheHit.inc({ type: 'product' }); return JSON.parse(hit); }
  } catch { metrics.cacheError.inc(); }               // Redis slow/down → go to DB

  metrics.cacheMiss.inc({ type: 'product' });
  const { rows: [p] } = await pool.query('SELECT id, name, price, stock FROM products WHERE id=$1', [id]);
  if (p) {
    const ttl = 600 + Math.floor(Math.random() * 120); // jitter → avoid mass expiry (Topic 50)
    redis.set(key, JSON.stringify(p), { EX: ttl }).catch(() => {});
  } else {
    redis.set(key, 'null', { EX: 60 }).catch(() => {}); // negative cache → stop repeated misses for missing ids
  }
  return p ?? null;
}

async function updateProductPrice(id, price) {
  await pool.query('UPDATE products SET price=$1 WHERE id=$2', [price, id]);   // 1. DB first
  const key = `product:v1:${id}`;
  await redis.del(key).catch((e) => logger.warn({ e, key }, 'invalidate failed'));  // 2. delete
  setTimeout(() => redis.del(key).catch(() => {}), 500);                             // 3. delayed double delete
}
```

### FastAPI — decorator-style cache-aside
```python
def cache_aside(prefix: str, ttl: int):
    def deco(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            key = f"{prefix}:{':'.join(map(str, args))}"
            try:
                if (hit := await r.get(key)) is not None:
                    return json.loads(hit)
            except Exception:
                pass
            value = await fn(*args, **kwargs)
            try: await r.set(key, json.dumps(value, default=str), ex=ttl)
            except Exception: pass
            return value
        return wrapper
    return deco

@cache_aside("restaurant", ttl=300)
async def get_restaurant(rid: int): ...
```

### Invalidate via events (decoupled & reliable)
```
Postgres ──(outbox or Debezium CDC)──► Kafka topic "products.changed"
                                           │
                               cache-invalidator service → DEL product:v1:{id}
Advantage: every writer (admin panel, batch job, other services) triggers invalidation,
not just the API code path that remembered to call DEL.
```

### What it looks like on the client
```
Server cache-aside makes GET /products/7 fast. On the client, React Query/SWR is ALSO
cache-aside-like: useQuery reads its cache, fetches on miss/stale; after a mutation you
invalidateQueries(['product', 7]) — same idea, different layer.
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain the cache-aside pattern.**
A1: The application owns the caching logic. On read, it checks the cache. On a hit it returns the value. On a miss it loads from the database, populates the cache with a TTL and returns. On write, it updates the database (the source of truth) and then invalidates the cached entry, so the next read loads fresh data. Only requested data gets cached, and if the cache fails, the app can still read from the DB.

**Q2: Why delete the cache entry on write instead of updating it?**
A2: Concurrent writers can update the cache out of order and leave a permanently stale value until TTL. Updating the cache also wastes work for keys that may never be read, and with complex cached views it's error-prone to recompute correctly. Deleting is idempotent and simple: the next reader fetches the current value from the DB.

**Q3: What consistency issues does cache-aside have and how do you mitigate them?**
A3: Stale reads are possible within the TTL. A race where a reader that missed writes an old value after a writer's invalidation can make it last until the TTL. If invalidation fails, stale data stays. Mitigations: always use TTLs (with jitter), update the DB then delete (never the reverse), delayed double delete, versioned keys, lease or compare-and-set mechanisms (Facebook leases), CDC-driven invalidation, and bypassing the cache for critical reads.

**Q4: What is negative caching and why use it?**
A4: Caching "not found" results (e.g. a `null` marker with a short TTL) so repeated requests for non-existent keys don't hit the DB every time. It protects against cache penetration attacks (random IDs) and buggy clients. Keep the TTL short so newly created items appear soon, or invalidate on create. Bloom filters are a complementary defence (Topic 53).

**Q5: When is cache-aside not a good fit?**
A5: When data must always be fresh (use the DB directly), when write-heavy data is invalidated so often the hit rate is poor, when the first-request (cold miss) latency is unacceptable (use refresh-ahead or pre-warming), or when you want the cache always populated with writes (write-through). It also needs discipline: every write path must invalidate, which is why CDC-based invalidation helps in larger systems.

---

## 🔷 Trade-offs
✅ Advantages:
- Simple, cache only what's needed, DB stays source of truth.
- Resilient: cache failure → slower, not broken.
- Works with any DB, flexible per-endpoint TTLs.

❌ Disadvantages:
- First request (miss) is slow; cold cache after deploy/restart.
- Stale data possible (TTL window, races).
- Every write path must remember to invalidate.
- Thundering herd on popular key expiry (Topic 50).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache-aside | App loads cache on miss | ज़रूरत पर ऐप ख़ुद cache भरे |
| Lazy loading | Load only when requested | माँगने पर ही लाना |
| Invalidation | Delete stale cache entry | पुराना cache हटाना |
| Source of truth | Authoritative data store (DB) | असली डेटा का स्रोत |
| Negative caching | Caching "not found" | "नहीं मिला" को cache करना |
| Delayed double delete | Delete again after delay | थोड़ी देर बाद दोबारा delete |
| Versioned key | Key includes version number | version वाली key |
| Lease | Token preventing stale sets | stale set रोकने का token |

---

## ⚡ 3-Line Summary
**English:**
1. Cache-aside: read cache → on miss read DB and populate cache (TTL); on write update DB then delete key.
2. Delete, don't update, on writes; use TTL + jitter, negative caching, and timeouts on cache calls.
3. Handle rare stale races with delayed double delete, versioned keys, leases or CDC invalidation.

**Hindi:**
1. Cache-aside: पहले cache, miss पर DB से लाकर cache में रखो; write पर DB अपडेट और key delete।
2. Write पर delete करो, update नहीं; TTL + jitter, negative cache और timeouts रखो।
3. Stale race के लिए delayed double delete, versioned keys या CDC invalidation।

---

## ➡️ Next Topic Suggestion
**46. Write-Through Pattern** — Cache-aside fills the cache lazily on reads. Next: write-through, where every write goes to cache AND DB together so the cache is always fresh, and when that's worth it.
