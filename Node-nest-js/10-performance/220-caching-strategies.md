# 220. Caching Strategies
# हिंदी में: Caching Strategies — Repeated काम को बार-बार न करना

---

## 🔵 Simple Definition (English)
**Caching** stores the result of an expensive operation (a DB query, an API call, a computation) so future requests for the same data can be served instantly from memory/fast storage instead of redoing the work. Common layers: **in-memory** (Node process memory, fastest but per-instance), **Redis/Memcached** (shared across instances, slightly slower), and **HTTP/CDN caching** (closest to the user, for static or semi-static responses).

## 🔵 सरल परिभाषा (Hindi)
**Caching** किसी expensive operation (DB query, API call, computation) का result store करती है ताकि future requests को उसी data के लिए दोबारा काम किए बिना memory/fast storage से instantly serve किया जा सके। Common layers: **in-memory** (Node process memory, सबसे fast पर per-instance), **Redis/Memcached** (सभी instances में shared, थोड़ा slower), और **HTTP/CDN caching** (user के सबसे करीब, static या semi-static responses के लिए)।

---

## 🔴 Problem it Solves
Without caching, every single request re-executes the same expensive work: the same complex SQL JOIN, the same external API call, the same CPU-heavy calculation — even if 1000 users requested the exact same unchanged data in the last minute. This wastes CPU, hammers the database, and causes high latency and poor scalability. Caching trades a small amount of staleness risk for massive reductions in load and latency — often a 10-100x speedup for read-heavy endpoints.

## 🔴 यह क्यों बना? (Hindi)
Caching के बिना, हर single request same expensive काम दोबारा करता है: वही complex SQL JOIN, वही external API call, वही CPU-heavy calculation — भले ही पिछले मिनट में 1000 users ने same unchanged data request किया हो। ये CPU waste करता है, database को hammer करता है, और high latency, poor scalability पैदा करता है। Caching थोड़े staleness risk के बदले load और latency में massive reduction देती है — read-heavy endpoints के लिए अक्सर 10-100x speedup।

---

## 🟢 How it Works — Step by Step

Step 1 → Identify read-heavy, expensive, and relatively stable data (product catalog, user profile, config, computed aggregates)
Step 2 → Choose a cache layer: in-memory (single instance, simplest) or Redis (shared across all app instances, essential for horizontally scaled apps)
Step 3 → On a request: check cache first ("cache-aside" pattern) — if present (**cache hit**), return it immediately; if absent (**cache miss**), fetch from the real source, store in cache, then return
Step 4 → Set a **TTL (time-to-live)** so stale data auto-expires after a reasonable window
Step 5 → **Invalidate** the cache explicitly when the underlying data changes (e.g., clear `product:123` cache key when that product is updated) — critical to avoid serving stale data for important changes
Step 6 → Monitor cache hit rate — a low hit rate means the cache isn't helping (data changes too fast, or keys are too fragmented) and the strategy needs rethinking

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → वो read-heavy, expensive, और relatively stable data पहचानो (product catalog, user profile, config, computed aggregates)
Step 2 → Cache layer चुनो: in-memory (single instance, simplest) या Redis (सभी app instances में shared, horizontally scaled apps के लिए ज़रूरी)
Step 3 → Request पर: पहले cache check करो ("cache-aside" pattern) — अगर मिला (**cache hit**), तुरंत return करो; नहीं मिला (**cache miss**) तो real source से fetch करो, cache में store करो, फिर return करो
Step 4 → एक **TTL (time-to-live)** set करो ताकि stale data reasonable समय के बाद auto-expire हो जाए
Step 5 → जब underlying data बदले तो cache को explicitly **invalidate** करो (जैसे product update होने पर `product:123` cache key clear करो)
Step 6 → Cache hit rate monitor करो — low hit rate मतलब cache help नहीं कर रहा (data बहुत तेज़ बदलता है, या keys बहुत fragmented हैं) और strategy को rethink करना होगा

---

## 🟡 Real World Example
**Zomato's restaurant-listing API** (`GET /restaurants?city=bangalore`) is one of the most-hit endpoints, but restaurant data (name, menu, rating) changes only a few times a day per restaurant. The team caches the response in Redis with a 5-minute TTL keyed by `restaurants:bangalore:page1`. On a cache hit (99% of requests during peak hours), the response comes from Redis in ~2ms instead of a complex DB query joining restaurants, ratings, and delivery zones that took ~300ms. When a restaurant updates its menu, a targeted cache invalidation (`DEL restaurants:bangalore:*`) clears just the affected city's cached pages instead of waiting for TTL expiry.

## 🟡 Real Example Hindi mein
**Zomato का restaurant-listing API** (`GET /restaurants?city=bangalore`) सबसे ज़्यादा hit होने वाले endpoints में है, पर restaurant data (name, menu, rating) दिन में सिर्फ कुछ बार बदलता है। Team Redis में response को 5-minute TTL के साथ `restaurants:bangalore:page1` key से cache करती है। Cache hit पर (peak hours में 99% requests), response ~2ms में Redis से आता है बजाय उस complex DB query के जो ~300ms लेती थी। जब restaurant अपना menu update करता है, targeted cache invalidation (`DEL restaurants:bangalore:*`) सिर्फ affected city के cached pages clear करती है।

---

## 💻 Code Example — Basic

```javascript
// in-memory-cache.js — simple cache-aside pattern using a Map (single instance)
const cache = new Map();
const TTL_MS = 60 * 1000; // 1 minute

async function getProductCached(productId, fetchFromDbFn) {
  const cacheKey = `product:${productId}`;
  const cached = cache.get(cacheKey);

  // Cache HIT: return immediately if entry exists and hasn't expired
  if (cached && Date.now() - cached.storedAt < TTL_MS) {
    console.log('Cache HIT for', cacheKey);
    return cached.data;
  }

  // Cache MISS: fetch from the real (slow) source
  console.log('Cache MISS for', cacheKey);
  const data = await fetchFromDbFn(productId);

  // Store in cache for next time
  cache.set(cacheKey, { data, storedAt: Date.now() });
  return data;
}

// Simulated slow DB call
async function fetchProductFromDb(id) {
  await new Promise(resolve => setTimeout(resolve, 300)); // simulate 300ms DB latency
  return { id, name: `Product ${id}`, price: 999 };
}

// First call: cache MISS (~300ms). Second call within 1 min: cache HIT (~0ms)
(async () => {
  console.time('first call');
  await getProductCached(1, fetchProductFromDb);
  console.timeEnd('first call'); // ~300ms

  console.time('second call');
  await getProductCached(1, fetchProductFromDb);
  console.timeEnd('second call'); // ~0ms — served from cache
})();
```

## 💻 Code Example — Advanced

```javascript
// redis-cache.js — production cache-aside pattern with Redis (shared across instances)
const Redis = require('ioredis');
const redis = new Redis(process.env.REDIS_URL);

async function getRestaurantsCached(city, page = 1) {
  const cacheKey = `restaurants:${city}:page${page}`;

  // Try cache first
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached); // cache HIT
  }

  // Cache MISS — fetch from DB (expensive query)
  const restaurants = await fetchRestaurantsFromDb(city, page);

  // Store with a TTL (300 seconds = 5 minutes); EX sets expiry in seconds
  await redis.set(cacheKey, JSON.stringify(restaurants), 'EX', 300);
  return restaurants;
}

// INVALIDATION: call this whenever restaurant data for a city changes
async function invalidateCityCache(city) {
  // Use pattern matching to clear ALL cached pages for that city
  const keys = await redis.keys(`restaurants:${city}:*`);
  if (keys.length > 0) {
    await redis.del(...keys); // delete all matching keys at once
  }
}

// ─── WRITE-THROUGH PATTERN (update cache immediately on write) ───────────
async function updateRestaurantMenu(restaurantId, newMenu, city) {
  await db.restaurants.update(restaurantId, { menu: newMenu }); // update source of truth
  await invalidateCityCache(city); // immediately clear stale cached listings
  // (alternative: write-through would UPDATE the cache directly here instead
  // of just invalidating, avoiding a cache-miss penalty for the next reader)
}

// ─── CACHE STAMPEDE PROTECTION ─────────────────────────────────────────────
// Problem: if 1000 requests hit a MISSED key simultaneously, all 1000 hit the
// DB at once ("stampede"). Fix: use a short-lived lock so only ONE request
// repopulates the cache while others wait or get slightly stale data.
async function getWithStampedeProtection(key, fetchFn, ttlSeconds = 300) {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const lockKey = `lock:${key}`;
  // NX = only set if not exists, EX = auto-expire the lock after 10s (safety)
  const gotLock = await redis.set(lockKey, '1', 'NX', 'EX', 10);

  if (!gotLock) {
    // Someone else is already repopulating — wait briefly and retry from cache
    await new Promise(r => setTimeout(r, 100));
    const retryCache = await redis.get(key);
    if (retryCache) return JSON.parse(retryCache);
  }

  const data = await fetchFn();
  await redis.set(key, JSON.stringify(data), 'EX', ttlSeconds);
  await redis.del(lockKey);
  return data;
}

async function fetchRestaurantsFromDb(city, page) {
  // Simulated expensive query
  return [{ id: 1, name: 'Sample Restaurant', city }];
}
```

---

## 🟠 Express.js Integration

```javascript
// middleware/cacheMiddleware.js — generic HTTP response caching middleware
const Redis = require('ioredis');
const redis = new Redis(process.env.REDIS_URL);

function cacheResponse(ttlSeconds = 60) {
  return async function (req, res, next) {
    // Use the full URL (including query string) as the cache key
    const cacheKey = `http:${req.originalUrl}`;

    const cached = await redis.get(cacheKey);
    if (cached) {
      res.set('X-Cache', 'HIT'); // helpful header for debugging
      return res.json(JSON.parse(cached));
    }

    // Monkey-patch res.json to cache the response before sending it
    const originalJson = res.json.bind(res);
    res.json = (body) => {
      redis.set(cacheKey, JSON.stringify(body), 'EX', ttlSeconds); // fire-and-forget
      res.set('X-Cache', 'MISS');
      return originalJson(body);
    };

    next();
  };
}

// Apply to a read-heavy, relatively stable route
app.get('/restaurants', cacheResponse(300), async (req, res) => {
  const restaurants = await fetchRestaurantsFromDb(req.query.city, req.query.page);
  res.json(restaurants); // automatically cached by the middleware above
});

// HTTP-level caching headers (CDN/browser caching) for truly static resources
app.get('/static/logo.png', (req, res) => {
  res.set('Cache-Control', 'public, max-age=86400'); // CDN/browser caches for 1 day
  res.sendFile('./assets/logo.png');
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Caching data without a TTL or invalidation strategy
```javascript
// WRONG: cached forever, no expiry, no way to update when source data changes
cache.set('user:123', userData); // stays stale forever after an update!

// CORRECT: always set a TTL AND invalidate on writes
await redis.set('user:123', JSON.stringify(userData), 'EX', 300);
// On update: await redis.del('user:123');
```

❌ Mistake 2: Using in-memory caching on a horizontally scaled (multi-instance) app
```javascript
// WRONG: each of 5 server instances has its OWN in-memory cache —
// inconsistent data (one instance shows stale data, another shows fresh)
const cache = new Map(); // per-process, not shared!

// CORRECT: use a shared cache (Redis) so all instances see the same cached state
const redis = new Redis(process.env.REDIS_URL); // shared across ALL instances
```

---

## 🧠 Tricky Interview Question

**Q: You cache a user's cart total with a 10-minute TTL. The user adds an item to their cart, but the displayed total doesn't update for several minutes. What went wrong, and what's the fix?**
Answer: This is a classic **cache invalidation bug** — the code likely only relies on TTL expiry and never explicitly invalidates the cache when the underlying data (cart) actually changes. TTL-only caching is fine for data that's okay to be briefly stale (like a restaurant listing), but WRONG for data the user just actively modified and expects to see updated immediately. Fix: on every cart mutation (add/remove item), explicitly call `redis.del('cart:' + userId)` (or update the cache directly — write-through) so the NEXT read is forced to recompute fresh data, rather than waiting out the full TTL window.

---

## ⚫ Interview Questions + Answers

Q1: What is the "cache-aside" pattern?
A1: The application code is responsible for managing the cache: on a read, check the cache first; if missing (miss), fetch from the real source, store the result in the cache, then return it. On a write, update the real source and either invalidate or update the corresponding cache entry. This is the most common and flexible caching pattern, used directly in app code (as opposed to "read-through"/"write-through" patterns often built into caching libraries/proxies).

Q2: What's the difference between cache invalidation and TTL expiry?
A2: TTL (time-to-live) is a PASSIVE mechanism — the cached entry automatically expires after a fixed duration regardless of whether the underlying data actually changed. Invalidation is ACTIVE — explicitly deleting/updating a cache entry the moment the underlying data changes. Relying only on TTL means users can see stale data for up to the full TTL window after a real update; combining both (TTL as a safety net + invalidation for correctness on known changes) is the standard best practice.

Q3: What is a "cache stampede" and how do you prevent it?
A3: A stampede happens when a popular cache key expires (or is evicted) and MANY concurrent requests simultaneously experience a cache miss, all hitting the expensive underlying source (DB/API) at once — potentially overloading it. Prevention: use a distributed lock (`SET key val NX EX ttl` in Redis) so only one request repopulates the cache while others wait briefly or serve slightly stale data; or stagger TTLs with jitter so keys don't all expire at the exact same moment.

Q4: When would you use HTTP/CDN caching versus application-level (Redis) caching?
A4: HTTP/CDN caching (`Cache-Control` headers) works best for truly static or rarely-changing public content (images, JS bundles, public API responses that don't vary per user) — it's cached at the EDGE, closest to the user, reducing even network round-trip to your server. Application-level (Redis) caching works for dynamic, per-user, or computed data that still needs server-side logic/auth but benefits from avoiding redundant expensive backend work (DB queries, aggregations).

Q5: How do you decide what TTL to use for a given cached resource?
A5: Balance staleness tolerance against load reduction: data that rarely changes and isn't critical to be instantly fresh (restaurant listings, product catalogs) can have longer TTLs (minutes to hours). Data that changes frequently or must reflect near-real-time state (stock availability, account balance) needs very short TTLs or should rely primarily on active invalidation rather than TTL alone. Also consider: how expensive is a cache miss (DB load) versus how harmful is serving stale data for that specific use case.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data is read far more often than it changes (read-heavy workloads)
- The underlying computation/query is expensive relative to how often the result actually changes
- Reducing database/API load under high traffic is a priority

❌ Avoid when:
- Data must always be perfectly real-time/consistent (e.g., live stock trading prices, bank balance mid-transaction)
- The data changes so frequently that cache hit rates would be near zero (caching overhead outweighs benefit)

---

## 📊 Visual Diagram
```
CACHE-ASIDE PATTERN:
────────────────────────────────────────────────
  Request comes in
        │
        ▼
  Check cache (Redis/in-memory)
        │
   ┌────┴────┐
   │         │
  HIT       MISS
   │         │
   │         ▼
   │   Fetch from DB/API (slow)
   │         │
   │         ▼
   │   Store in cache (with TTL)
   │         │
   └────┬────┘
        ▼
  Return response

INVALIDATION on write:
  Update DB → DELETE/UPDATE corresponding cache key(s)
  (never rely on TTL alone for data the user just changed)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache hit | Data found in cache | Cache में data मिल गया |
| Cache miss | Data not in cache, must fetch from source | Cache में नहीं, source से fetch करना पड़ा |
| TTL | Time before a cache entry auto-expires | Cache entry के auto-expire होने का समय |
| Invalidation | Explicitly clearing a cache entry on data change | Data बदलने पर cache को explicitly clear करना |
| Cache-aside | App manages cache: check, miss, fetch, store | App खुद cache manage करता है |
| Cache stampede | Many requests missing cache simultaneously | बहुत requests का एक साथ miss होना |
| CDN caching | Edge-level caching close to the user | User के पास edge पर caching |

---

## ⚡ 3-Line Summary
English:
1. Caching stores expensive operation results so repeat requests are served instantly, dramatically reducing load and latency for read-heavy data.
2. Use the cache-aside pattern with Redis for shared, multi-instance caching; always set a TTL AND actively invalidate on writes to the underlying data.
3. Protect against cache stampedes with locking, and choose TTL length based on how stale the data can safely be versus how expensive a cache miss is.

Hindi:
1. Caching expensive operation के results store करती है ताकि repeat requests instantly serve हों — read-heavy data के लिए load और latency massively कम होती है।
2. Shared, multi-instance caching के लिए Redis के साथ cache-aside pattern use करो; हमेशा TTL set करो AND underlying data के writes पर actively invalidate करो।
3. Locking से cache stampedes से बचाव करो, और TTL length को इस आधार पर चुनो कि data कितना stale हो सकता है vs cache miss कितनी expensive है।

---

## ➡️ Next Topic
**221. Database Query Optimization** — slow queries को पहचानना और indexes, query restructuring से उन्हें optimize करना।
