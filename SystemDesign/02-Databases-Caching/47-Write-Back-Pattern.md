# 47. Write-Back Pattern (Write-Behind)
# हिंदी में: Write-Back — पहले सिर्फ़ cache में लिखो और तुरंत "OK" दो; DB में बाद में (batch में) लिखा जाएगा

---

## 🔵 Simple Definition (English)
In **write-back** (also called **write-behind**) caching, writes go **only to the cache** first and are acknowledged immediately. The cache (or a background worker) **asynchronously flushes** the changes to the database later, often **batched and coalesced** (many updates to the same key become one DB write).
It gives the **fastest writes and lowest DB load**, but risks **data loss** if the cache fails before flushing.

## 🔵 सरल परिभाषा (Hindi)
Write-back में डेटा पहले सिर्फ़ cache (Redis) में लिखा जाता है और तुरंत "OK" मिल जाता है; DB में बाद में batch में लिखा जाता है।
सबसे तेज़ writes और DB पर सबसे कम बोझ — पर cache गिर गया तो flush से पहले का डेटा खो सकता है।

---

## 🔴 Problem it Solves
Some workloads have **huge write volumes** where each individual write is small and not critical:
- View counts, like counts, play counts (millions/minute on viral content).
- Live location pings from delivery partners every 3 seconds.
- Analytics events, "last seen" timestamps, game scores, IoT sensor readings.

Writing each one synchronously to the DB:
- **Overloads the DB** (hot rows, too many transactions, WAL and replication load).
- **Slows down users** (each write waits for a DB commit).

Write-back absorbs bursts in memory and turns **1,000,000 tiny writes into a few thousand batched DB writes**.

## 🔴 यह क्यों बना? (Hindi)
View count, like count, लोकेशन ping, analytics events — करोड़ों छोटे writes जो हर एक बहुत ज़रूरी नहीं।
हर एक सीधे DB में लिखो तो DB बैठ जाए। Write-back इन्हें memory में जमा करके 10 लाख writes को कुछ हज़ार batch writes में बदल देता है।

---

## 🟢 How it Works — Step by Step

```
 WRITE (fast path)
 App ──► Redis: INCR views:video:7      ──► ACK immediately (~1 ms)
 App ──► Redis: INCR views:video:7
 App ──► Redis: INCR views:video:7      (1000s of increments)
                     │
                     │  every N seconds / N items (async flusher)
                     ▼
            Worker: read & reset deltas → batch write
                     │
                     ▼
 DB: UPDATE videos SET views = views + 1543 WHERE id = 7   ← ONE write for 1543 events

 READ: from cache (has latest value), DB is slightly behind
```

### Key mechanisms

```
1. Dirty tracking   → know which keys changed since last flush (a Set of dirty keys / delta hash)
2. Coalescing       → many updates to the same key → one DB write (last value or summed delta)
3. Batching         → flush many keys in one multi-row statement / COPY
4. Flush trigger    → time-based (every 5s), size-based (1000 dirty keys), on eviction, on shutdown
5. Durability aid   → Redis AOF (appendfsync everysec), replicas; or use a durable log (Kafka/Streams)
6. Idempotent flush → flushing the same batch twice must not double count (use delta IDs / upserts)
```

### Atomic "read & reset" for counters (avoid losing increments)

```
❌ GET delta → write DB → SET delta 0      (increments between GET and SET are LOST)
✅ GETDEL / RENAME the delta key atomically, or Lua: read value + DECRBY that value
✅ Or rotate keys: write to views:7:{minute}; flusher processes previous minutes only
```

### Risks

```
Data loss:        Redis crashes before flush → last N seconds of writes lost
                  (OK for view counts, NOT OK for payments/orders)
Inconsistency:    DB is behind the cache → reports/analytics from DB lag
Ordering:         if multiple flushers/caches, updates may be applied out of order
Complexity:       flusher monitoring, backlog, retries, shutdown flush
```

### Write-back vs queue-based write-behind

```
Cache-based write-back  : Redis holds latest state + deltas; flusher syncs to DB
Log/queue write-behind  : App appends events to Kafka / Redis Stream (durable) → consumers
                          aggregate & write to DB in batches   ← safer, replayable
Many production systems prefer the queue version: same benefits, better durability.
```

### When to use

```
✅ High-frequency, low-value-per-write data: counters, views, likes, last_seen, telemetry,
   leaderboards, analytics, rate-limit counters, gaming state
✅ Bursty writes that would overwhelm the DB
✅ OK to lose a few seconds of data / eventual consistency
❌ Money, orders, inventory decisions, anything that must be durable at ACK time
```

## 🟢 कैसे काम करता है? (Hindi)
1. Write सिर्फ़ Redis में होता है (`INCR views:7`) और तुरंत "OK"।
2. एक background worker हर कुछ सेकंड में बदली हुई keys पढ़ता है और DB में batch में लिखता है।
3. एक ही key के हज़ारों updates मिलकर एक DB write बन जाते हैं (coalescing)।
4. पढ़ना और reset करना atomic होना चाहिए (GETDEL/Lua), वरना बीच के increments खो जाएँगे।
5. ख़तरा: flush से पहले Redis गिरा तो कुछ सेकंड का डेटा गया — इसलिए पैसे/ऑर्डर के लिए कभी नहीं; view count, likes, location के लिए बढ़िया।

---

## 🟡 Real World Example

**YouTube / Instagram view counts** — views are counted in fast in-memory or streaming systems and periodically aggregated into durable storage. That's why counts update in bursts and sometimes lag behind real-time.

**Delivery partner location (Swiggy/Zomato/Uber)** — GPS pings every few seconds go to Redis (latest location for live tracking). The full history is batched to Cassandra/S3 for analytics, not written one by one to the primary DB.

**Operating systems & disks** — the OS page cache is write-back: `write()` returns before the data hits disk, and `fsync()` forces it. Databases call fsync on commit for exactly this reason.

**CPU caches** — L1/L2 caches are write-back, which is where the term comes from.

## 🟡 Real Example Hindi में
YouTube/Instagram के view count पहले memory में गिने जाते हैं और बाद में DB में जुड़ते हैं — इसलिए count कभी-कभी झटकों में बढ़ता है।
Swiggy/Uber के डिलीवरी पार्टनर की हर कुछ सेकंड की GPS लोकेशन Redis में जाती है; पूरा इतिहास बाद में batch में Cassandra/S3 में।

---

## 🟠 My Stack Example

### Node.js — video view counter with write-back
```js
// fast path: on each view
app.post('/api/v1/videos/:id/view', async (req, res) => {
  const id = req.params.id;
  await redis.multi()
    .incr(`views:total:${id}`)          // live value for reads (seeded from DB on first use)
    .hIncrBy('views:delta', id, 1)      // pending delta to flush
    .exec();
  res.status(202).end();
});

// flusher (separate worker process / cron every 5s)
async function flushViews() {
  // atomically take the current delta hash and start a fresh one
  const tmp = `views:delta:flushing:${Date.now()}`;
  try { await redis.rename('views:delta', tmp); } catch { return; }   // no key → nothing to flush
  const deltas = await redis.hGetAll(tmp);
  const ids = Object.keys(deltas);
  if (ids.length) {
    await pool.query(
      `UPDATE videos v SET views = v.views + d.delta
       FROM (SELECT unnest($1::bigint[]) AS id, unnest($2::bigint[]) AS delta) d
       WHERE v.id = d.id`,
      [ids, ids.map((i) => Number(deltas[i]))]);
  }
  await redis.del(tmp);
  // if the DB write fails, tmp key remains → a recovery job retries keys matching views:delta:flushing:*
}
setInterval(flushViews, 5000);
process.on('SIGTERM', async () => { await flushViews(); process.exit(0); });   // flush on shutdown
```

### Safer version: durable stream + batch consumer
```js
// producer
await redis.xAdd('events:views', '*', { videoId: id, userId: uid ?? '', ts: Date.now().toString() });

// consumer group aggregates 1000 events → one batched DB write → XACK
// survives worker crashes (pending entries list), can be replayed
```

### FastAPI — "last seen" write-back
```python
@app.middleware("http")
async def track_last_seen(request, call_next):
    resp = await call_next(request)
    if (uid := getattr(request.state, "user_id", None)):
        await r.hset("last_seen:pending", uid, int(time.time()))   # overwrite = coalescing
    return resp

async def flush_last_seen():          # every 30s
    data = await r.hgetall("last_seen:pending")
    if not data: return
    await r.hdel("last_seen:pending", *data.keys())
    await db.execute(text("""
        UPDATE users u SET last_seen_at = to_timestamp(v.ts)
        FROM (SELECT unnest(:ids)::bigint AS id, unnest(:ts)::bigint AS ts) v WHERE u.id = v.id
    """), {"ids": list(map(int, data.keys())), "ts": list(map(int, data.values()))})
```

### Redis durability settings for write-back data
```conf
appendonly yes
appendfsync everysec        # at most ~1s of loss on crash
# + replica with automatic failover (ElastiCache Multi-AZ)
```

### Mobile angle
- The React Native app can also do client-side write-back: batch analytics events locally (MMKV/SQLite) and send them every 30 s or when back online, instead of one request per event. That saves battery and data.

---

## ⚫ Interview Questions + Answers

**Q1: What is write-back caching and how is it different from write-through?**
A1: Write-back writes only to the cache and acknowledges immediately, then persists to the DB asynchronously, in batches and coalesced. Write-through writes to the cache and the DB synchronously before acknowledging. Write-back gives the lowest write latency and much lower DB load, but the DB lags behind and unflushed data can be lost if the cache fails. Write-through is consistent and durable but slower on writes.

**Q2: When would you use write-back?**
A2: For very high-volume, low-criticality writes where losing a few seconds of updates is acceptable and eventual DB consistency is fine: view, like and play counters, last-seen timestamps, telemetry and location pings, analytics events, game scores, rate-limit counters. Never for payments, orders, inventory reservations or anything legally or financially critical.

**Q3: How do you reduce data-loss risk in write-back?**
A3: Persist the cache (Redis AOF with fsync every second) and replicate it with automatic failover. Flush frequently and on shutdown. Make the "read and reset" of pending deltas atomic. Better still, write events to a durable log (Kafka, Redis Streams) and aggregate from there, so data can be replayed after a crash. Make flushes idempotent and monitor flush lag and backlog.

**Q4: How would you design a view counter for a viral video receiving 1M views per minute?**
A4: Don't update one DB row per view. Increment an in-memory counter (Redis INCR, possibly sharded into N keys to avoid a hot key, summed on read) and also append events to Kafka if per-view analytics or fraud filtering is needed. A worker flushes aggregated deltas to the DB every few seconds in a single batched update. Display the count from Redis, possibly approximated. Reconcile periodically from the event log, and deduplicate bot or repeated views in the stream pipeline.

**Q5: What happens to reads in a write-back system?**
A5: Reads should come from the cache, which has the latest state. Reading from the DB returns slightly stale data, which is acceptable for analytics and reports. If the cache entry is evicted before a flush, you lose pending updates unless they're tracked separately, so dirty entries must not be evicted (or must be flushed first), or deltas should be kept in a structure that isn't evicted (maxmemory policies, separate Redis instance with noeviction).

---

## 🔷 Trade-offs
✅ Advantages:
- Lowest write latency; massive DB offload via batching/coalescing; absorbs bursts.

❌ Disadvantages:
- Possible data loss on cache failure; DB lags (eventual consistency).
- Complex: flushers, atomic swaps, retries, shutdown handling, monitoring.
- Not suitable for critical data.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Write-back / Write-behind | Write cache now, DB later | अभी cache, बाद में DB |
| Flush | Persist pending changes | जमा बदलाव DB में लिखना |
| Dirty key | Changed but not yet persisted | बदला पर अभी DB में नहीं |
| Coalescing | Merging many updates into one | कई updates एक में |
| Batching | Writing many rows together | कई rows एक साथ |
| AOF | Redis append-only file persistence | Redis का log |
| Eventual consistency | DB catches up later | बाद में DB बराबर होगा |

---

## ⚡ 3-Line Summary
**English:**
1. Write-back acknowledges writes after updating only the cache, flushing to DB later in batches.
2. Best for high-volume, low-criticality data (views, likes, last-seen, telemetry); never for money.
3. Mitigate loss with atomic delta swaps, frequent/shutdown flushes, AOF/replicas, or a durable stream.

**Hindi:**
1. Write-back = सिर्फ़ cache में लिखकर OK, DB में बाद में batch में।
2. Views, likes, last seen, telemetry के लिए बढ़िया; पैसे के लिए कभी नहीं।
3. Atomic swap, बार-बार flush, AOF/replica या durable stream से डेटा खोने का ख़तरा घटाओ।

---

## ➡️ Next Topic Suggestion
**48. Cache TTL + Invalidation** — All patterns depend on knowing when cached data is no longer valid. Next: choosing TTLs, invalidation strategies (event, version, tag-based), and keeping CDN, Redis and client caches consistent.
