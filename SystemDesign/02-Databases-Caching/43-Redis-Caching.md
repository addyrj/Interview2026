# 43. Redis — Caching
# हिंदी में: Redis — RAM में डेटा रखने वाला बहुत तेज़ key-value store, जिसे cache के रूप में DB का बोझ कम करने के लिए इस्तेमाल करते हैं

---

## 🔵 Simple Definition (English)
**Redis** (REmote DIctionary Server) is an **in-memory key-value data store**. Because data lives in RAM, reads and writes take **~0.1–1 ms**. It's most commonly used as a **cache** in front of a database: store the results of expensive queries/API calls so repeated requests skip the slow path. It also supports rich data structures, TTLs, pub/sub, streams and persistence.

## 🔵 सरल परिभाषा (Hindi)
Redis एक in-memory (RAM में) key-value database है — इसलिए बहुत तेज़ (1 ms से कम)।
इसका सबसे आम काम cache है: धीमी DB query का नतीजा Redis में रख दो, अगली बार वहीं से जवाब दो — DB पर बोझ कम, ऐप तेज़।

---

## 🔴 Problem it Solves
- Databases read from disk and do joins and aggregations: **5–100 ms** per query, with limited connections and CPU.
- Most apps read the **same data again and again**: the menu of a popular restaurant, a product page, user profiles, config, a leaderboard.
- Traffic spikes (sale, IPL) multiply DB load → DB becomes the bottleneck.

A cache gives:
- **Lower latency** (RAM vs disk + query work),
- **Less DB load** (80–99% of reads served from cache),
- **Higher throughput** (Redis does 100k+ ops/s per node),
- **Spike absorption**.

## 🔴 यह क्यों बना? (Hindi)
DB हर query में 5-100 ms लेता है और उसकी क्षमता सीमित है, जबकि ऐप बार-बार वही डेटा पढ़ता है (मेन्यू, product, profile)।
Cache से जवाब 1 ms में आता है, DB पर 80-99% reads का बोझ हट जाता है, और सेल जैसे ट्रैफ़िक में भी सिस्टम टिका रहता है।

---

## 🟢 How it Works — Step by Step

### Cache in the request path

```
           ┌──────────┐   1. GET menu:42          ┌─────────┐
 Client ──►│  API     │──────────────────────────►│  Redis  │
           │ (Node/   │◄── 2a. HIT → return (1ms) │  (RAM)  │
           │ FastAPI) │                           └─────────┘
           │          │   2b. MISS
           │          │──────────────────────────►┌──────────┐
           │          │◄── 3. rows (40 ms) ────────│ Postgres │
           │          │   4. SET menu:42 ... EX 300└──────────┘
           └──────────┘   5. return
Next request for menu:42 → HIT
```

### Why Redis is so fast

```
1. In-memory: RAM access ~100 ns vs SSD ~100 µs
2. Simple data structures with O(1)/O(log n) operations
3. Single-threaded command execution → no locks, no context switches
   (I/O threads for network since Redis 6; one command at a time = atomic)
4. Event loop (epoll) handles 10k+ clients
5. Efficient protocol (RESP), pipelining, small encodings
```

### Key concepts

```
Keys & values:     "user:42:profile" → JSON string
TTL / expiry:      SET key value EX 300  → auto-deleted after 300s
Eviction:          when memory is full: maxmemory-policy allkeys-lru (Topic 49)
Persistence:       RDB snapshots / AOF log (optional for cache; critical if Redis is a store)
Replication:       primary → replicas; Sentinel for auto-failover
Cluster:           16,384 hash slots spread across shards → horizontal scaling
Atomic ops:        INCR, SETNX, Lua scripts, MULTI/EXEC
```

### What to cache (and what not to)

```
✅ Cache:
  - Read-heavy, rarely-changing data: menus, product details, categories, config, feature flags
  - Expensive computations: aggregates, recommendations, rendered HTML fragments
  - External API responses: exchange rates, maps/geocode results
  - Sessions, auth lookups, rate-limit counters (Redis as primary store for ephemeral data)

❌ Don't cache (or be careful):
  - Data that must be 100% fresh: wallet balance at payment time, stock at checkout
  - Highly personalized data with low reuse (cache hit rate would be tiny)
  - Huge objects (> ~100 KB per key hurts latency); unbounded lists
  - Sensitive data without encryption/ACLs
```

### Cache key design

```
<entity>:<id>[:<variant>]       product:7, product:7:v2, menu:42:veg
<scope>:<params-hash>           search:city=mumbai&q=biryani → search:a9f3c1
Include version/locale/role if output differs:  product:7:hi-IN, home:user:42
Namespacing helps bulk invalidation and memory analysis.
```

### Measuring a cache
```
Hit ratio = hits / (hits + misses)       target > 80–95% for hot data
Latency p99 of Redis calls              should be ~1 ms
Memory usage, evictions/sec, keyspace size
INFO stats → keyspace_hits, keyspace_misses, evicted_keys
```

### Redis vs Memcached vs in-process cache

```
┌──────────────────┬───────────────────────┬──────────────────┬──────────────────────┐
│                  │ Redis                 │ Memcached        │ In-process (LRU Map) │
├──────────────────┼───────────────────────┼──────────────────┼──────────────────────┤
│ Data types       │ Rich (hash, list, set,│ Strings only     │ Any JS/Py object     │
│                  │ zset, stream...)      │                  │                      │
│ Persistence      │ Optional              │ No               │ No                   │
│ Replication/HA   │ Yes                   │ No (client-side) │ No                   │
│ Shared across    │ Yes                   │ Yes              │ No (per process)     │
│ instances        │                       │                  │                      │
│ Latency          │ ~0.5 ms (network)     │ ~0.5 ms          │ ~µs (no network)     │
│ Use              │ Default choice        │ Simple, huge     │ Tiny hot data, L1    │
│                  │                       │ caches (FB)      │ cache in front of    │
│                  │                       │                  │ Redis                │
└──────────────────┴───────────────────────┴──────────────────┴──────────────────────┘
Multi-level cache: L1 in-process (1–5s TTL) → L2 Redis → DB
```

## 🟢 कैसे काम करता है? (Hindi)
1. ऐप पहले Redis में key ढूँढता है (जैसे `menu:42`) — मिल गई (HIT) तो 1 ms में जवाब।
2. नहीं मिली (MISS) तो DB से लाओ, Redis में TTL के साथ रखो (`EX 300`), फिर जवाब दो।
3. Redis तेज़ है क्योंकि डेटा RAM में है, एक-एक command चलता है (कोई lock नहीं), और event loop इस्तेमाल करता है।
4. Memory भरने पर पुरानी keys हटती हैं (eviction, LRU)।
5. Cache करो: बार-बार पढ़ा जाने वाला, कम बदलने वाला डेटा। Cache मत करो: payment के समय का balance या stock।

---

## 🟡 Real World Example

**Twitter** — runs one of the largest Redis deployments (thousands of instances, terabytes of RAM) for home timelines. Each user's timeline is a Redis list of tweet IDs, so reading the timeline is a single cache read.

**Swiggy / Zomato** — restaurant menus, serviceability (is this restaurant delivering to your location?), ETAs and offers are cached in Redis, often with short TTLs during peak hours, so the core DBs only handle writes and cache misses.

**Stack Overflow** — uses Redis as a shared L2 cache plus in-memory L1 caches on web servers. It's a big reason they serve huge traffic on very few servers.

**GitHub, Shopify, Instagram** — use Redis or Memcached heavily for sessions, rate limits, job queues and caching rendered fragments.

## 🟡 Real Example Hindi में
Twitter की हर यूज़र की timeline Redis की एक list है — खोलते ही एक cache read और timeline तैयार।
Swiggy/Zomato में मेन्यू, delivery ETA और offers Redis में cache होते हैं, ताकि rush hour में DB पर सिर्फ़ writes और कुछ misses जाएँ।

---

## 🟠 My Stack Example

### Node.js — reusable cache helper (node-redis v4)
```js
import { createClient } from 'redis';
export const redis = createClient({ url: process.env.REDIS_URL });
redis.on('error', (e) => logger.error({ e }, 'redis error'));
await redis.connect();

export async function cached(key, ttlSec, loader) {
  try {
    const hit = await redis.get(key);
    if (hit !== null) return JSON.parse(hit);          // HIT
  } catch (e) { logger.warn({ e }, 'cache read failed'); }  // Redis down → fall through

  const value = await loader();                        // MISS → DB/API
  redis.set(key, JSON.stringify(value), { EX: ttlSec }).catch(() => {});
  return value;
}

app.get('/api/v1/restaurants/:id/menu', async (req, res) => {
  const menu = await cached(`menu:${req.params.id}`, 300, () =>
    db.query('SELECT id, name, price, veg FROM menu_items WHERE restaurant_id = $1 AND available', [req.params.id])
      .then(r => r.rows));
  res.set('Cache-Control', 'public, max-age=60').json(menu);
});

// invalidate on change
app.put('/api/v1/menu-items/:id', auth, async (req, res) => {
  const item = await updateItem(req.params.id, req.body);
  await redis.del(`menu:${item.restaurant_id}`);
  res.json(item);
});
```

### FastAPI — redis.asyncio
```python
import json, redis.asyncio as aioredis
r = aioredis.from_url(REDIS_URL, decode_responses=True)

async def cached(key: str, ttl: int, loader):
    try:
        if (hit := await r.get(key)) is not None:
            return json.loads(hit)
    except aioredis.RedisError:
        pass
    value = await loader()
    try: await r.set(key, json.dumps(value, default=str), ex=ttl)
    except aioredis.RedisError: pass
    return value

@app.get("/products/{pid}")
async def product(pid: int):
    return await cached(f"product:{pid}", 600, lambda: repo.get_product(pid))
```

### Docker Compose
```yaml
redis:
  image: redis:7-alpine
  command: ["redis-server", "--maxmemory", "512mb", "--maxmemory-policy", "allkeys-lru"]
  ports: ["127.0.0.1:6379:6379"]
```
AWS: **ElastiCache for Redis / Valkey** (Multi-AZ replica + auto-failover). Lighter options: Upstash (serverless Redis for Vercel), Redis Cloud.

### Useful CLI
```bash
redis-cli INFO stats | grep keyspace        # hits / misses
redis-cli --bigkeys                          # find huge keys
redis-cli MONITOR                            # see live commands (dev only!)
redis-cli TTL menu:42
```

### Frontend/mobile layers of caching (end to end)
```
RN app: React Query cache (staleTime) + expo-image disk cache
Browser: HTTP cache (Cache-Control), Next.js fetch cache / ISR
Edge: CDN (CloudFront) caches public GETs
Server: Redis
DB: shared_buffers (Postgres's own cache)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is Redis and why is it fast?**
A1: An in-memory key-value store with rich data structures. It's fast because data is in RAM, operations are simple and mostly O(1) or O(log n), commands run on a single thread (no locking or context switching, and each command is atomic), it uses an efficient event loop for networking, and it has a compact protocol with pipelining. Typical latency is sub-millisecond, and one node handles 100k+ ops/sec.

**Q2: When should you use a cache, and what should you not cache?**
A2: Cache read-heavy, expensive or slow-to-compute data that's reused across requests and can tolerate some staleness: product and menu data, config, aggregates, external API responses, sessions. Avoid caching data that must be perfectly fresh at decision time (balances, stock at checkout), low-reuse personalized data (poor hit rate), and very large values. Never treat the cache as the only copy of important data unless Redis is configured as a durable store.

**Q3: What happens if Redis goes down?**
A3: If designed correctly, the app falls back to the database with short Redis timeouts and graceful error handling, at higher latency. The risk is a sudden load spike on the DB (all misses at once), which can take it down. Mitigations: Redis replicas with automatic failover (Sentinel, ElastiCache Multi-AZ), circuit breakers around cache calls, request coalescing, rate limiting and load shedding during cache outages, and warming the cache after recovery.

**Q4: How do you measure if your cache is effective?**
A4: Hit ratio (hits / (hits + misses)) per key pattern, latency of cache calls (p99), DB load reduction (QPS and CPU before vs after), memory usage, eviction rate (high evictions mean the cache is too small or TTLs are wrong) and key count. Also track staleness incidents, i.e. bugs from stale data, to tune TTLs and invalidation.

**Q5: Redis vs Memcached?**
A5: Both are in-memory caches with similar latency. Redis has rich data types (hashes, lists, sets, sorted sets, streams, geo), optional persistence, replication and failover, clustering, Lua scripting and pub/sub, so it's the default choice. Memcached is simpler: strings only, multi-threaded, no persistence or replication. It's good for very large, simple caches, and Facebook famously uses it at massive scale. Pick Redis unless you have a specific reason.

---

## 🔷 Trade-offs
✅ Advantages:
- Sub-ms reads, massive DB offload, higher throughput, absorbs spikes.
- Rich data structures enable sessions, counters, leaderboards, queues, locks.

❌ Disadvantages:
- Stale data / invalidation complexity ("two hard things in CS").
- RAM is expensive; data must fit memory.
- Another dependency to run and keep highly available.
- Cache outages can overload the DB (thundering herd).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache | Fast temporary copy of data | तेज़ अस्थायी copy |
| Cache hit / miss | Found / not found in cache | cache में मिला / नहीं मिला |
| Hit ratio | % of requests served by cache | cache से जवाब का % |
| TTL | Time to live (auto expire) | कितनी देर रहेगा |
| Eviction | Removing keys when memory full | memory भरने पर keys हटाना |
| In-memory | Stored in RAM | RAM में रखा हुआ |
| Invalidation | Removing stale cached data | पुराना cache हटाना |
| Multi-level cache | L1 (local) + L2 (Redis) | कई परतों वाला cache |

---

## ⚡ 3-Line Summary
**English:**
1. Redis is an in-memory key-value store (~sub-ms) — the default cache in front of databases.
2. Cache read-heavy, reusable, staleness-tolerant data with TTLs; measure hit ratio.
3. Design for Redis failure (timeouts, fallback, HA) and plan invalidation from day one.

**Hindi:**
1. Redis = RAM में key-value store (1 ms से कम) — DB के आगे सबसे आम cache।
2. बार-बार पढ़ा जाने वाला, थोड़ा पुराना चलने वाला डेटा TTL के साथ cache करो; hit ratio नापो।
3. Redis गिरने का प्लान रखो (timeout, fallback, HA) और invalidation पहले दिन से सोचो।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Redis Caching](https://www.youtube.com/results?search_query=redis+caching+system+design+bytebytego) | Cache-aside, write-through, eviction visuals |
| 📺 YouTube | [Hussein Nasser — Redis Internals](https://www.youtube.com/results?search_query=redis+internals+hussein+nasser) | How Redis single-thread model works, pipelines |
| 📝 Article | [Redis Official Docs — Caching patterns](https://redis.io/docs/latest/develop/use/patterns/caching/) | Official patterns: cache-aside, write-through, write-behind |
| 📝 Article | [AWS ElastiCache Best Practices](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/best-practices.html) | Cluster mode, lazy loading, write-through on AWS |
| 🐙 GitHub | [system-design-primer — Cache](https://github.com/donnemartin/system-design-primer#cache) | Cache levels, when to update cache, CDN caching |

---

## ➡️ Next Topic Suggestion
**44. Redis Data Structures** — Redis is much more than GET/SET. Next: strings, hashes, lists, sets, sorted sets, streams, geo, bitmaps and HyperLogLog, and which real feature each one powers.
