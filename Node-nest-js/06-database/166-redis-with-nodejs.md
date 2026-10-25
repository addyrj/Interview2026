# 166. Redis with Node.js
# हिंदी में: Node.js के साथ Redis

---

## 🔵 Simple Definition (English)
**Redis** is an in-memory key-value data store, used with Node.js for caching, session storage, rate limiting, pub/sub messaging, and leaderboards. Because data lives in RAM, Redis operations are extremely fast (sub-millisecond) compared to disk-based databases. Node.js connects to Redis using client libraries like `redis` (official) or `ioredis` (feature-rich alternative).

## 🔵 सरल परिभाषा (Hindi)
**Redis** एक in-memory key-value data store है, Node.js के साथ caching, session storage, rate limiting, pub/sub messaging, leaderboards के लिए इस्तेमाल होता है। Data RAM में रहता है, तो Redis operations बहुत तेज़ (sub-millisecond) होते हैं disk-based databases के मुकाबले। Node.js `redis` (official) या `ioredis` client libraries से connect करता है।

---

## 🔴 Problem it Solves
Repeatedly querying a relational/document database for the SAME data (a user's profile, a product listing, a frequently-computed report) adds latency and database load on every request, even when the data rarely changes. Redis solves this by keeping frequently-accessed data in memory, so subsequent reads are served in microseconds instead of milliseconds — dramatically reducing load on the primary database and speeding up response times for hot data.

## 🔴 यह क्यों बना? (Hindi)
बार-बार same data (user profile, product listing, frequently-computed report) के लिए relational/document database query करना हर request पर latency और database load बढ़ाता है, चाहे data शायद ही बदलता हो। Redis frequently-accessed data को memory में रखकर इसे solve करता है — बाद की reads microseconds में serve होती हैं, primary database का load कम होता है, response times तेज़ होते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Install: `npm install redis` (or `ioredis`), create a client: `redis.createClient({ url: 'redis://localhost:6379' })`.
Step 2 → Connect: `await client.connect()` (the modern `redis` v4 client requires explicit connection).
Step 3 → Store data: `SET key value` with optional expiry (`EX seconds`) — Redis auto-evicts keys after they expire, perfect for caching.
Step 4 → Retrieve data: `GET key` — if it exists (cache hit), return it; if not (cache miss), fetch from the real DB and `SET` it for next time.
Step 5 → Use specialized data structures beyond simple strings: Hashes (`HSET`/`HGET`) for objects, Lists (`LPUSH`/`RPOP`) for queues, Sets (`SADD`) for unique collections, Sorted Sets (`ZADD`) for leaderboards/rankings.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Install करो: `npm install redis` (या `ioredis`), client बनाओ।
Step 2 → Connect करो: `await client.connect()` (modern `redis` v4 client explicit connect चाहता है)।
Step 3 → Data store करो: `SET key value` optional expiry के साथ (`EX seconds`) — Redis expire होने पर auto-evict करता है, caching के लिए perfect।
Step 4 → Data retrieve करो: `GET key` — मिले (cache hit) तो return, न मिले (cache miss) तो real DB से fetch करके `SET` करो।
Step 5 → Simple strings के आगे specialized structures: Hashes, Lists, Sets, Sorted Sets।

---

## 🟡 Real World Example
**Flipkart's product-listing page** caches each product's detail page in Redis with a 5-minute TTL (time-to-live): `GET product:12345` — if present, serve instantly from Redis (microseconds); if missing (cache miss, or expired), fetch from MongoDB/PostgreSQL, then `SET product:12345 <data> EX 300` to cache it for the next 5 minutes. During flash sales, this single cache layer absorbs 90%+ of read traffic that would otherwise hammer the primary database.

## 🟡 Real Example Hindi mein
**Flipkart का product-listing page** हर product detail page को Redis में 5-minute TTL के साथ cache करता है। मिल जाए तो instantly serve (microseconds में); न मिले तो database से fetch करके cache में डाल दो। Flash sales के दौरान, ये एक cache layer 90%+ read traffic absorb कर लेता है जो primary database को hammer कर देता।

---

## 💻 Code Example — Basic

```javascript
// redis-basic.js
// npm install redis
// Requires a running Redis instance (local: `redis-server`, or Docker: `docker run -p 6379:6379 redis`)
const { createClient } = require('redis');

async function main() {
  const client = createClient({ url: process.env.REDIS_URL || 'redis://localhost:6379' });

  client.on('error', (err) => console.error('Redis Client Error:', err));
  await client.connect(); // v4+ client requires explicit connect

  // Basic SET/GET
  await client.set('greeting', 'Hello from Redis');
  const value = await client.get('greeting');
  console.log('Value:', value); // "Hello from Redis"

  // SET with expiry (TTL) — key auto-deletes after 10 seconds, great for caching
  await client.set('session:abc123', JSON.stringify({ userId: 42 }), { EX: 10 });
  const session = await client.get('session:abc123');
  console.log('Session:', JSON.parse(session));

  // Check TTL remaining
  const ttl = await client.ttl('session:abc123');
  console.log('TTL remaining (seconds):', ttl);

  // DELETE a key
  await client.del('greeting');
  console.log('After delete:', await client.get('greeting')); // null

  await client.quit();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// redis-advanced.js — Production patterns: cache-aside, hashes, pub/sub, rate limiting
const { createClient } = require('redis');

const client = createClient({ url: process.env.REDIS_URL });
client.on('error', (err) => console.error('Redis error:', err));

// ─── 1. CACHE-ASIDE PATTERN (most common caching strategy) ───────────────────
async function getProduct(productId, dbFetchFn) {
  const cacheKey = `product:${productId}`;
  const cached = await client.get(cacheKey);
  if (cached) {
    console.log('Cache HIT');
    return JSON.parse(cached);
  }

  console.log('Cache MISS — querying database');
  const product = await dbFetchFn(productId); // falls back to the real database
  await client.set(cacheKey, JSON.stringify(product), { EX: 300 }); // cache for 5 minutes
  return product;
}

// ─── 2. HASH for storing structured objects efficiently ─────────────────────
async function cacheUserProfile(userId, profile) {
  // HSET stores multiple fields under one key — more memory-efficient than a JSON string for partial updates
  await client.hSet(`user:${userId}`, profile);
  await client.expire(`user:${userId}`, 3600); // 1 hour TTL
}

async function getUserField(userId, field) {
  return client.hGet(`user:${userId}`, field); // fetch just ONE field, not the whole object
}

// ─── 3. RATE LIMITING using INCR + EX (sliding counter pattern) ──────────────
async function checkRateLimit(userId, maxRequests = 10, windowSeconds = 60) {
  const key = `ratelimit:${userId}`;
  const count = await client.incr(key); // atomic increment
  if (count === 1) {
    await client.expire(key, windowSeconds); // set TTL only on the FIRST request in the window
  }
  return count <= maxRequests;
}

// ─── 4. PUB/SUB for real-time events across multiple app instances ──────────
async function setupPubSub() {
  const publisher = createClient({ url: process.env.REDIS_URL });
  const subscriber = createClient({ url: process.env.REDIS_URL });
  await publisher.connect();
  await subscriber.connect();

  await subscriber.subscribe('order-events', (message) => {
    console.log('Received event:', JSON.parse(message));
  });

  // Elsewhere in the app (even a different server instance):
  await publisher.publish('order-events', JSON.stringify({ type: 'order.created', orderId: 'ord-1' }));
}

async function run() {
  await client.connect();
  try {
    const product = await getProduct('p1', async () => ({ id: 'p1', name: 'Shoe', price: 1999 }));
    console.log('Product:', product);

    const allowed = await checkRateLimit('user-1', 5, 60);
    console.log('Request allowed:', allowed);
  } finally {
    await client.quit();
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express app using Redis as a caching layer in front of a database call
const express = require('express');
const { createClient } = require('redis');

const app = express();
const redisClient = createClient({ url: process.env.REDIS_URL });
redisClient.connect();

app.get('/api/products/:id', async (req, res) => {
  const cacheKey = `product:${req.params.id}`;
  try {
    const cached = await redisClient.get(cacheKey);
    if (cached) return res.json({ source: 'cache', data: JSON.parse(cached) });

    const product = await db.findProductById(req.params.id); // hypothetical DB call
    if (!product) return res.status(404).json({ error: 'Not found' });

    await redisClient.set(cacheKey, JSON.stringify(product), { EX: 300 });
    res.json({ source: 'database', data: product });
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Caching data without an expiry (TTL)
```javascript
// Wrong — key lives forever, serving STALE data indefinitely after the source changes
await client.set('product:1', JSON.stringify(product)); // no EX!

// Right — always set a reasonable TTL for cached data
await client.set('product:1', JSON.stringify(product), { EX: 300 });
```

❌ Mistake 2: Using Redis as the PRIMARY data store for critical data without persistence consideration
✅ Correct: Redis is in-memory first — while it supports persistence (RDB snapshots, AOF logs), a misconfigured instance can lose data on restart. Use Redis for cache/ephemeral/derivable data, and a durable database (PostgreSQL/MongoDB) as the source of truth for critical data.

---

## 🧠 Tricky Interview Question

```javascript
// Two concurrent requests both check the cache at the same time, both get a cache MISS
// Both then query the database AND both set the cache. What problem does this create?
```
Answer: This is the **cache stampede** (or "thundering herd") problem — when a popular cache key expires, MANY concurrent requests simultaneously miss the cache and hit the database at once, spiking database load exactly when it's least able to handle it. Common fixes: (1) **Locking** — use `SET key value NX EX ttl` (set-if-not-exists) so only ONE request computes the value while others wait/retry. (2) **Probabilistic early expiration** — refresh the cache slightly before actual expiry. (3) **Stale-while-revalidate** — serve the slightly stale cached value while ONE request refreshes it in the background.

---

## ⚫ Interview Questions + Answers

Q1: Why is Redis so much faster than a disk-based database for simple key lookups?
A1: Redis stores all data in RAM (memory), and memory access is orders of magnitude faster than disk I/O (even SSDs) — typical Redis operations complete in under a millisecond. It also uses highly optimized, simple data structures (hash tables, skip lists) tailored to its specific operations, avoiding the overhead of a general-purpose query planner/parser that relational databases have.

Q2: What is the "cache-aside" pattern?
A2: The application code is responsible for managing the cache: on a read, check Redis first; if present (cache hit), return it; if absent (cache miss), fetch from the primary database, then WRITE the result into Redis for future reads (with a TTL). Redis sits "aside" the main data flow rather than being transparently in front of every database call — this is the most common and flexible caching pattern in Node.js apps.

Q3: What's the difference between the `redis` and `ioredis` npm packages?
A3: `redis` is the official, actively maintained Node.js client with a modern Promise-based API (v4+). `ioredis` is a popular alternative with built-in support for Redis Cluster, Sentinel (for high availability), more flexible pipelining, and has historically had broader feature coverage for advanced Redis deployments. For simple caching use cases, either works; for complex production topologies (cluster/sentinel), `ioredis` has traditionally had smoother support, though `redis` v4 has closed much of that gap.

Q4: How would you implement basic rate limiting with Redis?
A4: Use `INCR` (atomic increment) on a key representing the user+time-window (e.g., `ratelimit:user123`), and set an expiry (`EXPIRE`) ONLY the first time the key is created (when the incremented value is 1) so the counter resets after the window. Compare the returned count against your limit — if it exceeds the max allowed requests, reject the request (429 Too Many Requests). This is atomic and safe under concurrent requests because `INCR` is a single atomic Redis operation.

Q5: What is Redis Pub/Sub, and what are its limitations compared to a message queue like Kafka or RabbitMQ?
A5: Pub/Sub lets a publisher broadcast messages to a named channel, and all currently-SUBSCRIBED clients receive them instantly. Limitations: messages are NOT persisted — if no subscriber is listening when a message is published, it's lost forever (fire-and-forget, no replay); there's no built-in message acknowledgment, retry, or durable queuing. For use cases needing guaranteed delivery, message persistence, or complex routing, a dedicated message queue (Kafka, RabbitMQ, or Redis Streams which DOES persist) is more appropriate.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Caching frequently-read, infrequently-changing data to reduce database load and latency
- Session storage, rate limiting, leaderboards (sorted sets), real-time counters
- Lightweight pub/sub for ephemeral real-time notifications where occasional message loss is acceptable

❌ Avoid when:
- You need guaranteed durability/persistence for critical business data as the PRIMARY store (use a proper database)
- You need guaranteed message delivery with replay/acknowledgment (use a message queue, or Redis Streams specifically, not plain Pub/Sub)

---

## 📊 Visual Diagram
```
REDIS CACHE-ASIDE PATTERN
──────────────────────────────────────────────
  Request arrives
        │
        ▼
  GET product:123 from Redis
        │
   ┌────┴────┐
 HIT        MISS
   │           │
   │           ▼
   │     Query primary DB (Postgres/Mongo)
   │           │
   │           ▼
   │     SET product:123 <data> EX 300  (cache it)
   │           │
   └─────┬─────┘
         ▼
  Return data to client

RATE LIMITING:
  INCR ratelimit:user123   → count
  IF count == 1: EXPIRE ratelimit:user123 60
  IF count > maxAllowed: reject request
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| in-memory store | Data kept in RAM | RAM में रखा data |
| TTL | Time until key expires | Key expire होने तक का time |
| cache-aside | App manages cache manually | App manually cache manage करता है |
| cache stampede | Many misses hit DB at once | बहुत सारे misses एक साथ DB hit करें |
| pub/sub | Publish-subscribe messaging | Publish-subscribe messaging |
| INCR | Atomic increment operation | Atomic increment operation |
| hash (Redis) | Field-value map under one key | एक key के नीचे field-value map |

---

## ⚡ 3-Line Summary
English:
1. Redis is an in-memory key-value store used for caching, sessions, rate limiting, and pub/sub, offering sub-millisecond access times.
2. The cache-aside pattern (check cache, fall back to DB, write back with a TTL) is the most common caching strategy.
3. Always set a TTL on cached data, and watch for cache stampede when a hot key expires under heavy concurrent load.

Hindi:
1. Redis एक in-memory key-value store है caching, sessions, rate limiting, pub/sub के लिए, sub-millisecond access times के साथ।
2. Cache-aside pattern (cache check करो, DB पर fallback, TTL के साथ write back) सबसे common caching strategy है।
3. Cached data पर हमेशा TTL set करो, और heavy concurrent load में hot key expire होने पर cache stampede से सावधान रहो।

---

## ➡️ Next Topic
**167. ioredis Package** — Deep dive into `ioredis`'s API, cluster/sentinel support, and pipelining for batch operations.
