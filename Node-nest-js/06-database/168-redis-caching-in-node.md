# 168. Redis Caching in Node
# हिंदी में: Node में Redis Caching — Strategies और Invalidation

---

## 🔵 Simple Definition (English)
**Redis caching strategies** describe HOW an application keeps cached data in sync with the source-of-truth database. The main patterns are **cache-aside** (app checks cache, falls back to DB, writes back), **write-through** (every write goes to cache AND DB together), and **write-behind** (write to cache first, DB updated asynchronously later). Proper **cache invalidation** (removing/updating stale cache entries when the underlying data changes) is the hardest part of caching correctly.

## 🔵 सरल परिभाषा (Hindi)
**Redis caching strategies** बताती हैं कि app cached data को source-of-truth database के साथ sync कैसे रखे। Main patterns: **cache-aside** (app cache check करता, DB पर fallback, write back), **write-through** (हर write cache AND DB दोनों में जाता), **write-behind** (पहले cache में write, DB बाद में async update)। सही **cache invalidation** (underlying data बदलने पर stale cache entries हटाना/update करना) caching का सबसे कठिन हिस्सा है।

---

## 🔴 Problem it Solves
Caching speeds up reads, but introduces a NEW problem: the cache can become out of sync with the real data ("stale cache") — e.g., a product's price changes in the database, but the cached version still shows the old price until it expires or is explicitly invalidated. Without a deliberate invalidation strategy, users see outdated data, sometimes causing real business issues (showing a sold-out item as available, or an old price at checkout).

## 🔴 यह क्यों बना? (Hindi)
Caching reads तेज़ करता है, पर एक नई problem लाता है: cache real data से out of sync हो सकता है ("stale cache") — जैसे product की price database में बदली, पर cached version पुरानी price दिखाता रहेगा जब तक expire न हो या explicitly invalidate न हो। बिना सोची invalidation strategy के, users outdated data देखते हैं, कभी-कभी real business issues होते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Cache-aside** (most common): read checks cache first, falls back to DB on miss, writes result to cache. Writes to the DB do NOT automatically update the cache — the next read will be a miss until TTL expires or you manually invalidate.
Step 2 → **Write-through**: every write updates BOTH the cache and the DB synchronously, so the cache is NEVER stale after a write (but adds latency to every write).
Step 3 → **Write-behind (write-back)**: writes go to the cache immediately (fast), and are asynchronously flushed to the DB later — fastest writes, but risks data loss if the cache crashes before flushing.
Step 4 → **Explicit invalidation**: on any update/delete to the source data, actively `DEL` the corresponding cache key(s) so the next read is forced to refetch fresh data — more precise than waiting for TTL expiry.
Step 5 → **TTL-based expiry**: set a reasonable expiry on every cached key as a SAFETY NET, even when using explicit invalidation — protects against missed invalidation paths (bugs, direct DB edits bypassing the app).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Cache-aside**: read पहले cache check करती, miss पर DB fallback, result cache में write। DB writes automatically cache update नहीं करते।
Step 2 → **Write-through**: हर write cache AND DB दोनों synchronously update करता — cache कभी stale नहीं होता, पर हर write में latency बढ़ती।
Step 3 → **Write-behind**: writes पहले cache में (fast), DB में बाद async flush होता — fastest writes, पर crash पर data loss risk।
Step 4 → **Explicit invalidation**: source data update/delete पर cache key `DEL` करो ताकि अगली read fresh data fetch करे।
Step 5 → **TTL-based expiry**: हर cached key पर reasonable expiry set करो safety net के रूप में, explicit invalidation के साथ भी।

---

## 🟡 Real World Example
**Razorpay's merchant-settings service** uses cache-aside with EXPLICIT invalidation: when a merchant updates their payout bank account, the API handler does `await db.updateMerchantSettings(...)` followed immediately by `await redis.del('merchant:settings:' + merchantId)` — forcing the NEXT read to fetch fresh data from the database rather than waiting up to the cache's 10-minute TTL to naturally expire. This combination (explicit invalidation + TTL as a safety net) prevents a merchant from seeing stale bank details for up to 10 minutes after a critical update.

## 🟡 Real Example Hindi mein
**Razorpay की merchant-settings service** cache-aside + EXPLICIT invalidation इस्तेमाल करती है: merchant अपना payout bank account update करे तो DB update के बाद immediately `redis.del('merchant:settings:' + merchantId)` चलता है — अगली read fresh data fetch करे, 10-minute TTL का इंतज़ार नहीं। ये combination merchant को critical update के बाद stale bank details दिखने से बचाता है।

---

## 💻 Code Example — Basic

```javascript
// redis-caching-basic.js
// npm install ioredis
const Redis = require('ioredis');
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

// Simulated "database" for demonstration
const fakeDb = { 'product:1': { id: 1, name: 'Shoe', price: 1999 } };

// ─── CACHE-ASIDE READ ─────────────────────────────────────────────────────────
async function getProduct(id) {
  const cacheKey = `product:${id}`;
  const cached = await redis.get(cacheKey);
  if (cached) {
    console.log('Cache HIT');
    return JSON.parse(cached);
  }
  console.log('Cache MISS — fetching from "DB"');
  const data = fakeDb[cacheKey];
  if (data) await redis.set(cacheKey, JSON.stringify(data), 'EX', 300); // 5 min TTL
  return data;
}

// ─── EXPLICIT INVALIDATION ON WRITE ──────────────────────────────────────────
async function updateProductPrice(id, newPrice) {
  const cacheKey = `product:${id}`;
  fakeDb[cacheKey].price = newPrice; // update the "DB"
  await redis.del(cacheKey);          // invalidate the stale cache entry immediately
  console.log('Updated DB and invalidated cache for', cacheKey);
}

async function main() {
  console.log(await getProduct(1)); // MISS, then cached
  console.log(await getProduct(1)); // HIT

  await updateProductPrice(1, 1799); // invalidates cache

  console.log(await getProduct(1)); // MISS again — fetches fresh, updated price

  await redis.quit();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// redis-caching-advanced.js — stampede protection, write-through, bulk invalidation
const Redis = require('ioredis');
const redis = new Redis(process.env.REDIS_URL);

// ─── 1. CACHE STAMPEDE PROTECTION using SET NX (lock) ────────────────────────
async function getProductWithLock(id, dbFetchFn) {
  const cacheKey = `product:${id}`;
  const lockKey = `lock:${cacheKey}`;

  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  // Try to acquire a short-lived lock — only ONE request will succeed (NX = set if not exists)
  const acquiredLock = await redis.set(lockKey, '1', 'EX', 5, 'NX');

  if (acquiredLock) {
    try {
      const data = await dbFetchFn(id); // only the lock-holder queries the DB
      await redis.set(cacheKey, JSON.stringify(data), 'EX', 300);
      return data;
    } finally {
      await redis.del(lockKey);
    }
  } else {
    // Another request is already fetching — wait briefly and retry reading cache
    await new Promise((resolve) => setTimeout(resolve, 100));
    return getProductWithLock(id, dbFetchFn); // retry
  }
}

// ─── 2. WRITE-THROUGH CACHING — keep cache and DB always in sync ────────────
async function writeThroughUpdate(id, newData, dbWriteFn) {
  await dbWriteFn(id, newData);                                     // write to DB
  await redis.set(`product:${id}`, JSON.stringify(newData), 'EX', 300); // immediately refresh cache too
  // Cache is NEVER stale after this write completes — unlike cache-aside's invalidate-then-refetch gap
}

// ─── 3. BULK/PATTERN-BASED INVALIDATION ──────────────────────────────────────
async function invalidateAllProductsForCategory(categoryId) {
  // SCAN is safer than KEYS in production — doesn't block the Redis server on huge keyspaces
  const stream = redis.scanStream({ match: `product:category:${categoryId}:*` });
  const keysToDelete = [];

  for await (const keys of stream) {
    keysToDelete.push(...keys);
  }

  if (keysToDelete.length > 0) {
    await redis.del(...keysToDelete); // bulk delete all matched keys in one command
    console.log(`Invalidated ${keysToDelete.length} cache keys for category ${categoryId}`);
  }
}

async function run() {
  await writeThroughUpdate('1', { id: 1, name: 'Shoe', price: 1599 }, async (id, data) => {
    console.log('Simulated DB write:', id, data);
  });

  const product = await getProductWithLock('1', async (id) => ({ id, name: 'Shoe', price: 1599 }));
  console.log('Fetched product:', product);

  await redis.quit();
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express app demonstrating cache-aside reads + explicit invalidation on updates
const express = require('express');
const Redis = require('ioredis');
const app = express();
app.use(express.json());
const redis = new Redis(process.env.REDIS_URL);

app.get('/api/products/:id', async (req, res) => {
  const cacheKey = `product:${req.params.id}`;
  const cached = await redis.get(cacheKey);
  if (cached) return res.json(JSON.parse(cached));

  const product = await db.findProduct(req.params.id); // hypothetical DB call
  if (!product) return res.status(404).json({ error: 'Not found' });

  await redis.set(cacheKey, JSON.stringify(product), 'EX', 300);
  res.json(product);
});

app.put('/api/products/:id', async (req, res) => {
  await db.updateProduct(req.params.id, req.body); // update source of truth first
  await redis.del(`product:${req.params.id}`);      // then invalidate the stale cache entry
  res.json({ message: 'Updated and cache invalidated' });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Updating the database but forgetting to invalidate the cache
```javascript
// Wrong — DB has new price, but cache still serves the OLD price until TTL expires
await db.updateProduct(id, { price: newPrice });
// missing: await redis.del(`product:${id}`);

// Right — always invalidate (or update) the cache right after a write to the source data
await db.updateProduct(id, { price: newPrice });
await redis.del(`product:${id}`);
```

❌ Mistake 2: Relying ONLY on TTL with no explicit invalidation for frequently-changing critical data
✅ Correct: For data where staleness has real consequences (prices, inventory, account settings), pair a TTL safety net WITH explicit invalidation on write — don't make users wait out the full TTL window to see critical updates.

---

## 🧠 Tricky Interview Question

**Q: You invalidate the cache (`DEL`) immediately AFTER updating the database. A request reads the cache microseconds BEFORE the `DEL` runs but AFTER the DB update committed. What does it see, and is this a bug?**

Answer: That request would see the OLD cached value — not technically a "bug" in the invalidation logic itself, but a brief WINDOW of staleness (a race condition inherent to cache-aside with a two-step update+invalidate). This is usually acceptable for most data (eventual consistency within milliseconds), but for critical operations (payments, stock reservation), you need STRONGER consistency guarantees: either read-through logic that always re-validates against the DB for that specific critical path, or wrap the update+invalidate in a way that readers can detect a version/timestamp mismatch and refetch.

---

## ⚫ Interview Questions + Answers

Q1: What's the key trade-off between cache-aside and write-through caching?
A1: Cache-aside only updates the cache on READ misses — writes to the DB don't touch the cache, leaving a staleness window until the next read (miss) or TTL expiry, UNLESS you explicitly invalidate. Write-through updates the cache synchronously on EVERY write, keeping it always fresh, but adds latency to every write operation (now waiting on both the DB write and cache write) and wastes cache space for data that might never be read again.

Q2: What is cache stampede, and how do you prevent it?
A2: Cache stampede happens when a popular cache key expires and MANY concurrent requests simultaneously experience a cache miss, all hammering the database at once. Prevention: use a distributed lock (`SET key val NX EX ttl`) so only ONE request fetches from the DB and repopulates the cache while others wait briefly and retry reading the now-fresh cache; or use probabilistic early expiration / stale-while-revalidate patterns.

Q3: Why is `SCAN` preferred over `KEYS` for finding cache keys matching a pattern in production?
A3: `KEYS pattern` scans the ENTIRE keyspace in one blocking operation — on a large production dataset, this can freeze the Redis server for other clients during the scan, causing a system-wide outage. `SCAN` (and `scanStream` in ioredis) iterates the keyspace INCREMENTALLY in small batches (cursor-based), never blocking the server for more than a tiny slice of time per call.

Q4: How would you design cache invalidation for data that's cached under MULTIPLE different keys (e.g., a product cached both individually and within a category listing)?
A4: You need to invalidate ALL related cache keys when the underlying data changes, not just the primary one — e.g., maintain a naming convention/pattern (`product:1`, `category:5:products`) and invalidate both on update, or maintain a reverse index (a Redis SET tracking which composite cache keys reference a given product) so you can look up and invalidate everything affected. Alternatively, shorter TTLs on composite/listing caches reduce the staleness window without complex invalidation logic.

Q5: When would write-behind (write-back) caching be appropriate despite its data-loss risk?
A5: When write throughput is extremely high and slight data loss on a rare crash is an acceptable trade-off for massive write-latency improvement — e.g., high-frequency analytics event counters, view counts, or non-critical activity logs where losing the last few seconds of unflushed writes during a crash is tolerable. It's NOT appropriate for financial transactions or anything requiring strong durability guarantees.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Read-heavy workloads where the same data is requested repeatedly and tolerates brief staleness
- You can clearly identify invalidation points (specific write operations) to keep cache correctness high

❌ Avoid when:
- Data changes so frequently that cache hit rates would be too low to justify the complexity (cache churns before it's ever reused)
- Absolute real-time consistency is required for every read (e.g., real-time account balance during a transaction) — read directly from the source of truth instead, or use very short TTLs with explicit locking

---

## 📊 Visual Diagram
```
CACHING STRATEGIES COMPARISON
──────────────────────────────────────────────
CACHE-ASIDE:
  Read:  check cache → miss → DB → write to cache → return
  Write: write to DB only (cache becomes stale until TTL/invalidation)

WRITE-THROUGH:
  Write: write to DB AND cache together (synchronous, always fresh)

WRITE-BEHIND:
  Write: write to cache immediately, flush to DB asynchronously later
         (fastest, but risk of loss if cache crashes before flush)

EXPLICIT INVALIDATION (layered on cache-aside):
  Write: write to DB → DEL cache key → next read is a forced miss (fresh data)

STAMPEDE PROTECTION:
  Cache miss → try SET lock NX EX 5
    ├─ got lock  → fetch from DB → populate cache → release lock
    └─ no lock   → wait briefly → retry reading cache
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cache-aside | App manages cache on read miss | Read miss पर app cache manage करता |
| write-through | Cache + DB updated together | Cache + DB साथ update |
| write-behind | Cache first, DB updated later | पहले cache, बाद में DB |
| invalidation | Removing stale cache entries | Stale cache entries हटाना |
| TTL | Expiry safety net | Expiry का safety net |
| cache stampede | Many misses hit DB at once | बहुत misses एक साथ DB hit |
| SCAN | Non-blocking keyspace iteration | Non-blocking keyspace iteration |

---

## ⚡ 3-Line Summary
English:
1. Cache-aside (read-fallback-write) is the most common pattern; always pair it with explicit invalidation on writes, not just TTL expiry, for critical data.
2. Prevent cache stampede with a distributed lock so only one request repopulates a hot expired key while others wait.
3. Use `SCAN`/`scanStream` instead of `KEYS` for pattern-based bulk invalidation in production to avoid blocking the Redis server.

Hindi:
1. Cache-aside (read-fallback-write) सबसे common pattern है; critical data के लिए सिर्फ TTL नहीं, explicit invalidation भी साथ रखो।
2. Cache stampede से बचने के लिए distributed lock इस्तेमाल करो ताकि एक ही request hot expired key refill करे।
3. Production में pattern-based bulk invalidation के लिए `KEYS` की जगह `SCAN`/`scanStream` इस्तेमाल करो, Redis server block न हो।

---

## ➡️ Next Topic
**169. Database Transactions** — ACID properties, transaction isolation levels, and implementing multi-step atomic operations across SQL and NoSQL databases.
