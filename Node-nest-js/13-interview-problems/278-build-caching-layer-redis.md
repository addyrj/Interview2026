# 278. Build Caching Layer (Redis)
# हिंदी में: Redis से Caching Layer बनाना

---

## 🔵 Simple Definition (English)
A **Redis caching layer** sits between your Node.js app and a slower data source (database, third-party API), storing frequently-accessed results in Redis's in-memory store. On repeat requests, the app checks Redis FIRST — if present (**cache hit**), it skips the slow source entirely; if absent (**cache miss**), it fetches from the source and stores the result for next time.

## 🔵 सरल परिभाषा (Hindi)
**Redis caching layer** Node.js app और slower data source (database, third-party API) के बीच बैठती है, frequently-accessed results को Redis के in-memory store में रखती है। Repeat requests पर app पहले Redis check करती है — मिल जाए (**cache hit**) तो slow source skip, न मिले (**cache miss**) तो source से fetch करके next time के लिए store।

---

## 🔴 Problem it Solves
Databases are slow relative to memory — a complex SQL join might take 200ms, while reading the same data from Redis (RAM-based, sub-millisecond) takes under 1ms. For data that's read far more often than it changes (product listings, user profiles, computed aggregates like "trending restaurants"), re-querying the database for every single request wastes resources and adds unnecessary latency at scale. Caching absorbs repeated reads, dramatically reducing database load and response times.

## 🔴 यह क्यों बना? (Hindi)
Databases memory की तुलना में slow होते हैं — एक complex SQL join 200ms ले सकता है, जबकि वही data Redis (RAM-based) से sub-millisecond में मिल जाता है। जो data change से ज़्यादा बार read होता है (product listings, user profiles, "trending restaurants" जैसे computed aggregates), हर request पर DB query करना resources waste करता है और latency बढ़ाता है। Caching repeated reads absorb करती है, DB load और response time dramatically कम करती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Install and connect to Redis (`npm install redis` or `ioredis`).
Step 2 → **Cache-aside pattern** (most common): on read, check Redis first (`GET key`); if hit, return it; if miss, query the DB, then write the result to Redis (`SET key value EX ttl`) before returning.
Step 3 → Choose a sensible **TTL (time to live)** — how long cached data stays valid before auto-expiring (e.g. 5 minutes for a product listing, 1 hour for rarely-changing config).
Step 4 → **Invalidate** the cache explicitly when underlying data changes (e.g. `DEL product:42` right after an UPDATE query) — relying only on TTL expiry means stale data is served until expiry.
Step 5 → Design cache KEYS carefully: include all parameters that affect the result (`products:category:electronics:page:2`), so different query variations don't collide.
Step 6 → Handle **cache stampede** (many concurrent requests missing cache simultaneously, all hammering the DB at once) with locking or probabilistic early expiration.
Step 7 → Monitor hit/miss ratio — a very low hit ratio means your caching strategy (keys/TTL) needs rethinking.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Redis install/connect करो।
Step 2 → **Cache-aside pattern**: read पर पहले Redis check (`GET`); hit तो return; miss तो DB query करके Redis में store (`SET ... EX ttl`) फिर return।
Step 3 → सही **TTL** चुनो — cached data कितनी देर valid रहे।
Step 4 → Underlying data बदलने पर cache explicitly **invalidate** करो (`DEL`) — सिर्फ TTL पर depend न करो।
Step 5 → Cache keys सावधानी से design करो — सभी affecting parameters include करो।
Step 6 → **Cache stampede** handle करो locking या probabilistic early expiration से।
Step 7 → Hit/miss ratio monitor करो।

---

## 🟡 Real World Example
**Flipkart's** product detail pages are read millions of times per day but prices/descriptions change relatively rarely. They cache rendered product data in Redis with a 10-minute TTL, keyed by `product:<id>:v<version>`. On a price update, instead of waiting for TTL expiry, the update pipeline immediately publishes a cache-invalidation event that deletes the stale key. During flash sales (huge read spikes on popular products), this cache absorbs 95%+ of traffic, letting the database handle only writes and genuine cache misses — without Redis, the database would need to be scaled many times larger just to survive the read spike.

## 🟡 Real Example Hindi mein
**Flipkart** के product detail pages रोज़ लाखों बार read होते हैं पर prices/descriptions कम बदलते हैं। वे rendered product data को Redis में 10-minute TTL के साथ cache करते हैं, key `product:<id>:v<version>` से। Price update पर, TTL expiry का wait किए बिना, update pipeline immediately stale key delete करता है। Flash sales के दौरान, ये cache 95%+ traffic absorb करता है, DB सिर्फ writes और genuine misses handle करता है।

---

## 💻 Code Example — Basic

```javascript
// basic-redis-cache.js — cache-aside pattern, minimal implementation
// npm install redis
// Requires a local or remote Redis server running
// Run: node basic-redis-cache.js

const { createClient } = require('redis');

async function main() {
  const client = createClient({ url: 'redis://localhost:6379' });
  await client.connect();

  // Simulate a slow database call
  function slowFetchFromDB(productId) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ id: productId, name: 'Wireless Mouse', price: 799 });
      }, 500); // pretend this query takes 500ms
    });
  }

  async function getProduct(productId) {
    const cacheKey = `product:${productId}`;

    // 1. Check cache first
    const cached = await client.get(cacheKey);
    if (cached) {
      console.log('Cache HIT');
      return JSON.parse(cached);
    }

    // 2. Cache miss — fetch from "database"
    console.log('Cache MISS — fetching from DB');
    const product = await slowFetchFromDB(productId);

    // 3. Store in cache with 60-second TTL for next time
    await client.set(cacheKey, JSON.stringify(product), { EX: 60 });

    return product;
  }

  console.time('First call');
  await getProduct(42); // MISS — takes ~500ms
  console.timeEnd('First call');

  console.time('Second call');
  await getProduct(42); // HIT — takes <5ms
  console.timeEnd('Second call');

  await client.quit();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// advanced-redis-cache.js — reusable cache wrapper + invalidation + stampede protection
// npm install redis

const { createClient } = require('redis');

class CacheService {
  constructor(redisUrl) {
    this.client = createClient({ url: redisUrl });
    this.locks = new Map(); // in-process lock to reduce stampede (single-instance mitigation)
  }

  async connect() {
    await this.client.connect();
  }

  // Generic "get or compute and cache" helper — the core cache-aside pattern
  async getOrSet(key, ttlSeconds, computeFn) {
    const cached = await this.client.get(key);
    if (cached !== null) {
      return JSON.parse(cached);
    }

    // Stampede protection: if another request is ALREADY computing this key,
    // wait for it instead of also hitting the DB (single-process mitigation;
    // for multi-instance, use a Redis-based distributed lock like SETNX).
    if (this.locks.has(key)) {
      return this.locks.get(key);
    }

    const computePromise = (async () => {
      try {
        const freshValue = await computeFn();
        await this.client.set(key, JSON.stringify(freshValue), { EX: ttlSeconds });
        return freshValue;
      } finally {
        this.locks.delete(key); // release lock whether success or failure
      }
    })();

    this.locks.set(key, computePromise);
    return computePromise;
  }

  // Explicit invalidation — call this whenever underlying data changes
  async invalidate(key) {
    await this.client.del(key);
  }

  // Invalidate multiple keys matching a pattern (use sparingly — SCAN-based, can be slow on huge keyspaces)
  async invalidatePattern(pattern) {
    for await (const key of this.client.scanIterator({ MATCH: pattern })) {
      await this.client.del(key);
    }
  }
}

// ─── Usage example ──────────────────────────────────────────────────────────
async function demo() {
  const cache = new CacheService('redis://localhost:6379');
  await cache.connect();

  async function fetchTrendingRestaurants(city) {
    console.log(`Querying DB for trending restaurants in ${city}...`);
    // Simulate an expensive aggregation query
    await new Promise((r) => setTimeout(r, 300));
    return [{ name: 'Spice Villa', rating: 4.5 }, { name: 'Curry House', rating: 4.3 }];
  }

  const key = 'trending:restaurants:bangalore';
  const result1 = await cache.getOrSet(key, 300, () => fetchTrendingRestaurants('bangalore'));
  console.log('Result 1 (DB hit):', result1);

  const result2 = await cache.getOrSet(key, 300, () => fetchTrendingRestaurants('bangalore'));
  console.log('Result 2 (cache hit, no DB query logged):', result2);

  // When a restaurant's rating changes, invalidate the stale aggregate
  await cache.invalidate(key);
}

demo();
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { createClient } = require('redis');

const app = express();
app.use(express.json());

const redisClient = createClient({ url: process.env.REDIS_URL || 'redis://localhost:6379' });
redisClient.connect();

// Generic caching middleware for GET routes
function cacheMiddleware(ttlSeconds) {
  return async (req, res, next) => {
    const cacheKey = `route:${req.originalUrl}`;
    const cached = await redisClient.get(cacheKey);

    if (cached) {
      res.setHeader('X-Cache', 'HIT');
      return res.json(JSON.parse(cached));
    }

    // Monkey-patch res.json to intercept and cache the response before sending
    const originalJson = res.json.bind(res);
    res.json = (body) => {
      redisClient.set(cacheKey, JSON.stringify(body), { EX: ttlSeconds }); // fire-and-forget
      res.setHeader('X-Cache', 'MISS');
      return originalJson(body);
    };

    next();
  };
}

app.get('/api/products/:id', cacheMiddleware(60), async (req, res) => {
  // Simulate DB fetch — only runs on cache miss
  const product = { id: req.params.id, name: 'Keyboard', price: 1999 };
  res.json(product);
});

// Invalidate cache on update — critical to avoid serving stale data
app.put('/api/products/:id', async (req, res) => {
  // ... update DB here ...
  await redisClient.del(`route:/api/products/${req.params.id}`);
  res.json({ message: 'Product updated, cache invalidated' });
});

app.listen(3000, () => console.log('Cached API server on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Caching data indefinitely with no TTL and no invalidation plan
✅ Correct: Always set a TTL as a safety net, even if you also do explicit invalidation — protects against missed invalidation code paths leaving stale data forever.

```javascript
// Wrong: no expiry — if the invalidation call is ever missed/buggy, data is stale forever
await client.set('product:42', JSON.stringify(product));

// Right: TTL as a safety net + explicit invalidation on update
await client.set('product:42', JSON.stringify(product), { EX: 600 }); // expires in 10 min regardless
```

❌ Mistake 2: Caching errors or empty results, causing persistent "no data" responses
✅ Correct: Don't cache a failed DB call or legitimately-empty-but-possibly-temporary result without a very short TTL — a transient DB hiccup shouldn't become a 10-minute outage.

```javascript
// Wrong: caches an error state for the full TTL
try {
  const data = await db.query(...);
  await client.set(key, JSON.stringify(data), { EX: 600 });
} catch (err) {
  await client.set(key, JSON.stringify(null), { EX: 600 }); // now serves "null" for 10 min!
}

// Right: don't cache failures, or use a much shorter TTL for them
try {
  const data = await db.query(...);
  await client.set(key, JSON.stringify(data), { EX: 600 });
} catch (err) {
  throw err; // let the caller handle it, don't poison the cache
}
```

---

## 🧠 Tricky Interview Question

```javascript
// Two requests arrive at the EXACT same millisecond, cache is empty for this key.
// What happens with this naive implementation under high concurrency?
async function getProduct(id) {
  const cached = await client.get(`product:${id}`);
  if (cached) return JSON.parse(cached);

  const product = await db.query('SELECT * FROM products WHERE id = ?', [id]); // slow, 500ms
  await client.set(`product:${id}`, JSON.stringify(product), { EX: 60 });
  return product;
}
// If 1000 requests for the SAME uncached product arrive within that 500ms window...
```
Answer: This is the **cache stampede** (or "thundering herd") problem. All 1000 requests see a cache miss (none of them has written the result yet), so ALL 1000 independently query the database simultaneously — exactly the load spike caching was supposed to prevent, potentially overwhelming the DB. Fixes: (1) **Request coalescing/locking** — track in-flight computations (as in the advanced example's `locks` Map) so only ONE request actually queries the DB while the other 999 await that same promise. (2) **Distributed lock via Redis** (`SET key value NX EX ttl` — only one process successfully acquires it) for multi-instance deployments. (3) **Probabilistic early expiration** — refresh the cache slightly before actual TTL expiry, spreading out refreshes instead of all happening at the exact same expiry moment.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between cache-aside, write-through, and write-behind caching strategies?
A1: **Cache-aside** (most common, as built above): app checks cache on read, populates it on miss; writes go to the DB and the cache is invalidated/updated separately. **Write-through**: every write goes to the cache AND the DB synchronously, keeping them always in sync, but adds write latency. **Write-behind (write-back)**: writes go to the cache first, and the DB is updated asynchronously later — fastest writes but risks data loss if the cache fails before the DB write completes; used in specific high-throughput scenarios with tolerance for eventual consistency.

Q2: How do you choose an appropriate TTL for cached data?
A2: Balance freshness vs load reduction: shorter TTL means fresher data but more cache misses (more DB load); longer TTL reduces DB load but risks serving stale data longer. Factors: how often the underlying data actually changes (rarely-changing config → long TTL; frequently-updated stock counts → short TTL or event-based invalidation instead), and the business cost of staleness (showing a slightly outdated restaurant rating is low-risk; showing stale payment/stock-availability status is high-risk and should prefer invalidation over TTL alone).

Q3: What's the risk of using Redis as your ONLY data store (no underlying database)?
A3: Redis is primarily an in-memory store — while it supports persistence (RDB snapshots, AOF logs), a server crash/restart can still lose recent writes depending on persistence configuration, and it's not designed for complex relational queries, joins, or ACID transactions across multiple keys the way a traditional database is. Redis is best used as a CACHE or fast auxiliary store (sessions, rate limits, leaderboards) layered on top of a durable primary database, not as the sole source of truth for critical business data.

Q4: How would you cache data that varies by user (e.g. a personalized dashboard) without the cache growing unbounded?
A4: Key the cache per-user (`dashboard:user:<userId>`) with a reasonably short TTL, and set a Redis `maxmemory` policy (e.g. `allkeys-lru` — evict least-recently-used keys automatically when memory limit is hit) so the cache self-manages size instead of growing forever. For truly personalized, rarely-repeated views, caching may not even help much (low hit rate) — profile actual access patterns before investing in caching infrastructure for low-reuse data.

Q5: How do you keep a Redis cache in sync when multiple Node.js instances can each write/invalidate it?
A5: Since Redis is a single shared store (not per-instance), any instance invalidating a key (`DEL`) immediately makes it unavailable to ALL instances — this is actually one of Redis's advantages over in-memory per-process caching. The remaining challenge is ORDERING: if instance A updates the DB and invalidates the cache, but instance B's slightly-delayed read repopulates the cache with now-stale data (race condition between the DB write and cache invalidation), you can get a brief stale window. Mitigations: invalidate the cache key BEFORE committing the DB write is finalized is wrong order too; the safer pattern is to update DB first, then delete cache key (not set it) — forcing the NEXT read to repopulate fresh from the now-updated DB.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Read-heavy workloads where the same data is requested repeatedly (product catalogs, user profiles, computed aggregates/leaderboards)
- Expensive computations/queries (joins, aggregations, external API calls) that don't need to be recomputed every request
- You need shared, fast state across multiple server instances (sessions, rate limits)

❌ Avoid when:
- Data changes on every read or is almost never repeated (low cache-hit-rate scenarios waste memory for little benefit)
- Strong consistency is mandatory and even brief staleness is unacceptable (e.g. real-time account balance during a transaction) — go direct to the source of truth with proper locking instead
- The dataset is small enough that the database itself is already fast enough (premature optimization adds complexity for no real gain)

---

## 📊 Visual Diagram
```
CACHE-ASIDE PATTERN
────────────────────
Request → App
            │
            ▼
      ┌───────────┐   HIT    ┌──────────────┐
      │  Redis     │ ───────► │ Return cached │──► Response (fast, <5ms)
      │  GET key   │          │ data          │
      └─────┬─────┘
            │ MISS
            ▼
      ┌───────────┐
      │ Database   │  (slow, ~200-500ms)
      │ query      │
      └─────┬─────┘
            │
            ▼
      ┌───────────┐
      │ Redis       │
      │ SET key, TTL│  ← populate for next request
      └─────┬─────┘
            ▼
       Return data ──► Response

INVALIDATION ON WRITE:
  UPDATE product SET price = 999 WHERE id = 42
            │
            ▼
      DEL product:42   ← next read is forced to be a MISS, refetches fresh data
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache Hit | Data found in cache, DB skipped | Cache में data मिल गया, DB skip |
| Cache Miss | Data not in cache, must fetch from source | Cache में नहीं, source से fetch करना पड़ा |
| TTL | Time before cached data auto-expires | Cached data auto-expire होने का समय |
| Invalidation | Explicitly removing stale cached data | Stale cached data को explicitly हटाना |
| Cache Stampede | Many requests missing cache simultaneously, overloading source | कई requests एक साथ miss, source overload |
| Cache-aside | Pattern: app manages cache read/write around the DB | App खुद cache read/write manage करे DB के आसपास |

---

## ⚡ 3-Line Summary
English: 1. A Redis caching layer uses the cache-aside pattern: check cache first, fall back to the slow source on miss, then populate the cache for next time. 2. Always set a TTL as a safety net, and explicitly invalidate on writes rather than relying on expiry alone. 3. Guard against cache stampede with request coalescing or distributed locks when many concurrent requests might miss the same key simultaneously.
Hindi: 1. Redis caching layer cache-aside pattern use करती है: पहले cache check, miss पर slow source, फिर next time के लिए cache populate। 2. हमेशा TTL safety net की तरह रखो, और writes पर explicitly invalidate करो, सिर्फ expiry पर depend मत करो। 3. Cache stampede से बचने के लिए request coalescing या distributed locks use करो।

---

## ➡️ Next Topic
**279. Build Job Queue (BullMQ)** — BullMQ से background job queue और worker system बनाना।
