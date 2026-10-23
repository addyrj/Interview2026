# 44. Redis Data Structures
# हिंदी में: Redis Data Structures — Redis के अलग-अलग डेटा ढाँचे (String, Hash, List, Set, Sorted Set, Stream, Geo...) और हर एक से बनने वाले फ़ीचर

---

## 🔵 Simple Definition (English)
Redis values aren't just strings. Redis provides **native data structures** with atomic operations on the server: **String, Hash, List, Set, Sorted Set (ZSET), Stream, Geo, Bitmap, HyperLogLog, Bloom filters (module)**. Choosing the right one turns complex features (leaderboards, queues, rate limiters, "nearby drivers") into one or two commands.

## 🔵 सरल परिभाषा (Hindi)
Redis में सिर्फ़ string नहीं, कई डेटा ढाँचे हैं — Hash (object), List (क़तार), Set (unique लिस्ट), Sorted Set (score वाली लिस्ट), Stream, Geo आदि।
सही ढाँचा चुनने से leaderboard, queue, rate limiter, "पास के ड्राइवर" जैसे फ़ीचर 1-2 commands में बन जाते हैं।

---

## 🔴 Problem it Solves
Without server-side structures, you'd:
- Fetch a JSON blob, modify it in your app, write it back → **race conditions** between concurrent requests.
- Sort leaderboards in app memory → slow, not shared across instances.
- Build queues, counters and geo-search yourself on top of SQL → slow and complex.

Redis data structures give **atomic, O(1)/O(log n) operations in memory**, shared by all app instances.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ string हो तो JSON निकालकर ऐप में बदलो और वापस लिखो — एक साथ दो requests में डेटा बिगड़ता है। Leaderboard, queue, geo-search ख़ुद बनाना धीमा और जटिल है।
Redis के ढाँचे सर्वर पर ही atomic और तेज़ operations देते हैं, जो सारे app instances साझा करते हैं।

---

## 🟢 How it Works — Step by Step

### Cheat sheet: structure → use case

```
┌──────────────┬───────────────────────────────┬──────────────────────────────────────────┐
│ Structure    │ Think of it as                │ Real use                                 │
├──────────────┼───────────────────────────────┼──────────────────────────────────────────┤
│ String       │ value / number / blob         │ cache JSON, counters (INCR), OTP, locks  │
│ Hash         │ object / map of fields        │ user profile, cart {item: qty}, sessions │
│ List         │ linked list (push/pop ends)   │ simple queues, recent N items, timeline  │
│ Set          │ unique unordered members      │ tags, followers, online users, dedupe    │
│ Sorted Set   │ unique members + score, sorted│ leaderboards, top-N, rate limit windows, │
│ (ZSET)       │                               │ delayed jobs (score = run time), feeds   │
│ Stream       │ append-only log + consumer    │ event streams, reliable queues, activity │
│              │ groups                        │ logs, chat (mini-Kafka)                  │
│ Geo          │ sorted set of lat/lng         │ nearby drivers/restaurants               │
│ Bitmap       │ array of bits                 │ daily active users, feature flags per id │
│ HyperLogLog  │ approx. unique count (12 KB)  │ unique visitors per page/day             │
│ Bloom filter │ "maybe in set" / "definitely  │ "username taken?", seen-before checks    │
│ (RedisBloom) │ not"                          │                                          │
│ Pub/Sub      │ fire-and-forget broadcast     │ WebSocket fan-out, cache invalidation    │
└──────────────┴───────────────────────────────┴──────────────────────────────────────────┘
```

### 1. String
```
SET otp:+9198xxxx 482913 EX 300 NX     → OTP, only if not exists, expires 5 min
GET otp:+9198xxxx
INCR api:calls:2024-10-18              → atomic counter
SET lock:order:9001 <token> NX PX 10000 → simple distributed lock (Topic 88)
```

### 2. Hash
```
HSET cart:42 item:7 2 item:9 1          → cart = {item:7: 2, item:9: 1}
HINCRBY cart:42 item:7 1                → atomic +1 qty (no read-modify-write race)
HGETALL cart:42
HDEL cart:42 item:9
EXPIRE cart:42 604800                   → cart expires in 7 days
✅ update one field without rewriting the whole object
```

### 3. List
```
LPUSH notifications:42 "{...}"          → newest first
LTRIM notifications:42 0 49             → keep only latest 50
LRANGE notifications:42 0 9             → latest 10
BRPOP jobs 0                            → blocking pop (simple worker queue)
⚠️ LINDEX/LINSERT in middle are O(n); lists are for ends
```

### 4. Set
```
SADD online_users 42 77 13
SISMEMBER online_users 42      → 1
SCARD online_users             → count
SINTER followers:42 followers:77   → mutual followers
SADD processed_events evt_123  → returns 0 if already there → idempotency/dedupe
```

### 5. Sorted Set (most asked in interviews)
```
ZADD leaderboard 1500 "user:42" 2300 "user:77"
ZINCRBY leaderboard 50 "user:42"
ZREVRANGE leaderboard 0 9 WITHSCORES     → top 10   O(log n + 10)
ZREVRANK leaderboard "user:42"           → my rank
ZRANGEBYSCORE delayed_jobs -inf <now>    → jobs due now (score = timestamp)
Sliding window rate limit: ZADD rl:42 <now_ms> <uuid>; ZREMRANGEBYSCORE rl:42 0 <now-60s>; ZCARD rl:42
Internally: skip list + hash table → O(log n) inserts/rank queries
```

### 6. Stream (Redis 5+)
```
XADD orders * orderId 9001 status PLACED          → append event, auto ID
XGROUP CREATE orders notifier $ MKSTREAM
XREADGROUP GROUP notifier w1 COUNT 10 BLOCK 5000 STREAMS orders >
XACK orders notifier <id>                         → mark processed
XPENDING / XAUTOCLAIM                             → recover messages from dead consumers
✅ persistent, consumer groups, acks → reliable queue (lighter than Kafka)
```

### 7. Geo
```
GEOADD drivers:mumbai 72.8777 19.0760 driver:77
GEOSEARCH drivers:mumbai FROMLONLAT 72.88 19.07 BYRADIUS 3 km ASC COUNT 10 WITHDIST
```

### 8. Bitmap & HyperLogLog
```
SETBIT dau:2024-10-18 42 1          → user 42 active today (1 bit per user id!)
BITCOUNT dau:2024-10-18             → daily active users
BITOP AND active_both dau:2024-10-17 dau:2024-10-18   → retained users
(100M users → 12.5 MB per day)

PFADD uv:page:home user42 user77    → unique visitors (approx, ±0.81%)
PFCOUNT uv:page:home                → count, always ≤ 12 KB memory
```

### Atomicity: MULTI/EXEC & Lua
```
MULTI; DECRBY stock:7 1; LPUSH orders:pending 9001; EXEC   → executed together
Lua (EVAL) → run check-and-set logic atomically on server (e.g. "decrement only if > 0")
```

### Memory tips
```
- Small hashes/zsets use compact encodings (listpack) → store many small objects as hash fields
- Always set TTLs for cache keys; avoid giant keys (> 1 MB) and huge collections (> 1M members)
- Use SCAN (not KEYS *) in production — KEYS blocks the single thread
```

## 🟢 कैसे काम करता है? (Hindi)
1. String: cache, OTP, counter (`INCR`), lock (`SET NX`)।
2. Hash: object जैसे cart/profile — एक field बदलो बिना पूरा object दोबारा लिखे।
3. List: latest 50 notifications, simple queue; Set: unique चीज़ें — online users, followers, duplicate जाँच।
4. Sorted Set: score के साथ sorted — leaderboard, top-N, rate limiter, delayed jobs।
5. Stream: भरोसेमंद event queue (consumer groups + ACK); Geo: पास के ड्राइवर; Bitmap/HyperLogLog: DAU और unique visitors कम memory में।

---

## 🟡 Real World Example

**Gaming leaderboards (Dream11, MPL)** — live contest leaderboards with millions of entries use sorted sets: `ZINCRBY` on every score update and `ZREVRANGE` for the top 100. Ranks are O(log n) even with millions of players.

**Uber / Ola / Rapido** — nearby-driver lookup is geo-indexed in memory. Redis GEO or similar geo-hash structures answer "drivers within 2 km" in milliseconds.

**Twitter timelines** — Redis lists of tweet IDs per user (fan-out on write), trimmed to the latest ~800 entries.

**Rate limiting at GitHub / Stripe** — counters and sorted sets in Redis implement per-user, per-endpoint limits shared across all API servers.

**Daily active users** — bitmaps are a well-known trick (popularized by Spool, later used widely) for computing DAU and retention for millions of users in milliseconds.

## 🟡 Real Example Hindi में
Dream11/MPL के live leaderboard में लाखों खिलाड़ी Sorted Set में होते हैं — हर score पर `ZINCRBY`, और top 100 तुरंत।
Uber/Rapido "2 km के अंदर ड्राइवर" Geo structure से ms में ढूँढते हैं; GitHub/Stripe rate limiting Redis counters से करते हैं।

---

## 🟠 My Stack Example

### Cart with Hash (Node)
```js
await redis.hIncrBy(`cart:${uid}`, `item:${itemId}`, qty);
await redis.expire(`cart:${uid}`, 7 * 86400);
const cart = await redis.hGetAll(`cart:${uid}`);       // { 'item:7': '2', 'item:9': '1' }
```

### Leaderboard with Sorted Set
```js
await redis.zIncrBy(`lb:contest:${cid}`, points, `user:${uid}`);
const top = await redis.zRangeWithScores(`lb:contest:${cid}`, 0, 9, { REV: true });
const myRank = await redis.zRevRank(`lb:contest:${cid}`, `user:${uid}`);   // 0-based
```

### Sliding-window rate limiter with Sorted Set + MULTI
```js
async function allow(userId, limit = 100, windowMs = 60_000) {
  const key = `rl:${userId}`, now = Date.now();
  const [, , count] = await redis.multi()
    .zRemRangeByScore(key, 0, now - windowMs)
    .zAdd(key, { score: now, value: `${now}-${Math.random()}` })
    .zCard(key)
    .pExpire(key, windowMs)
    .exec();
  return count <= limit;
}
```

### Atomic stock decrement with Lua (flash sale)
```js
const DECR_IF_AVAILABLE = `
  local s = tonumber(redis.call('GET', KEYS[1]) or '0')
  if s >= tonumber(ARGV[1]) then return redis.call('DECRBY', KEYS[1], ARGV[1]) else return -1 end`;
const left = await redis.eval(DECR_IF_AVAILABLE, { keys: [`stock:${sku}`], arguments: ['1'] });
if (left < 0) throw new AppError(409, 'SOLD_OUT');
// then enqueue order creation; DB remains source of truth (reconcile)
```

### Nearby delivery partners with Geo (FastAPI)
```python
await r.geoadd("partners:blr", (lng, lat, f"p:{pid}"))
nearby = await r.geosearch("partners:blr", longitude=u_lng, latitude=u_lat,
                           radius=3, unit="km", sort="ASC", count=10, withdist=True)
```

### Reliable job queue with Streams
```js
await redis.xAdd('jobs:email', '*', { to: 'a@x.com', template: 'receipt', orderId: '9001' });

// worker
await redis.xGroupCreate('jobs:email', 'mailers', '0', { MKSTREAM: true }).catch(() => {});
while (true) {
  const res = await redis.xReadGroup('mailers', `w-${process.pid}`, { key: 'jobs:email', id: '>' }, { COUNT: 10, BLOCK: 5000 });
  for (const msg of res?.[0]?.messages ?? []) {
    await sendEmail(msg.message);
    await redis.xAck('jobs:email', 'mailers', msg.id);
  }
}
```
(For most Node apps, **BullMQ** wraps Redis into a full job queue with retries, delays and dashboards.)

### Online presence with Set + TTL heartbeat
```js
// on WebSocket heartbeat every 30s
await redis.set(`presence:${uid}`, '1', { EX: 60 });
const online = await redis.exists(`presence:${friendId}`);
```

### DAU with Bitmap
```js
await redis.setBit(`dau:${today}`, userIdNumber, 1);
const dau = await redis.bitCount(`dau:${today}`);
```

---

## ⚫ Interview Questions + Answers

**Q1: Which Redis data structure would you use for a leaderboard and why?**
A1: A sorted set (ZSET). Members are user IDs and scores are points. `ZINCRBY` updates a score atomically in O(log n), `ZREVRANGE 0 9 WITHSCORES` returns the top 10, and `ZREVRANK` gives a user's rank, all efficient even with millions of members, thanks to the skip list + hash table implementation. For multiple time windows (daily or weekly), use separate keys with TTL, or `ZUNIONSTORE` to aggregate.

**Q2: How would you implement a rate limiter in Redis?**
A2: Fixed window: `INCR rl:user:minute` with `EXPIRE 60`, and reject if the count exceeds the limit. Simple, but bursty at window edges. Sliding window log: a sorted set of request timestamps, removing old entries with `ZREMRANGEBYSCORE`, counting with `ZCARD`, and adding the new one, wrapped in MULTI or Lua for atomicity. Token bucket: store tokens and last refill time in a hash, updated by a Lua script. Redis is shared across all API instances, so the limit is global (Topics 59–62).

**Q3: Redis List vs Stream for a job queue?**
A3: Lists (`LPUSH`/`BRPOP`) are simple, but a message popped by a worker that then crashes is lost unless you use `BLMOVE` to a processing list and handle recovery yourself. Streams provide consumer groups, per-message IDs, acknowledgements (`XACK`), a pending list and reclaiming of stuck messages (`XAUTOCLAIM`), plus history and replay, giving at-least-once delivery. Use Streams (or BullMQ, or a real broker) when you need reliability.

**Q4: How do you count unique visitors efficiently for millions of users?**
A4: HyperLogLog: `PFADD uv:page:date userId` and `PFCOUNT`. It uses a fixed ~12 KB per key with about 0.81% standard error, and HLLs can be merged (`PFMERGE`) for weekly or monthly counts. If you need exact counts or set operations with numeric IDs, bitmaps (`SETBIT`/`BITCOUNT`) are compact (1 bit per user ID). Avoid storing millions of IDs in a Set if approximate counts are acceptable.

**Q5: Why should you avoid the KEYS command in production, and what are other Redis pitfalls?**
A5: `KEYS *` scans the whole keyspace in one blocking O(n) command, freezing the single-threaded server for every client. Use `SCAN` with a cursor instead. Other pitfalls: big keys (huge values or collections) cause latency spikes and slow deletes (use `UNLINK`), keys without TTLs grow memory, hot keys overload one cluster shard, `FLUSHALL` and other dangerous commands should be renamed or ACL-restricted, and Pub/Sub messages are lost if subscribers are disconnected (use Streams for durability).

---

## 🔷 Trade-offs
✅ Advantages:
- Atomic server-side operations eliminate race conditions; very fast; shared state.
- One tool covers caching, counters, queues, leaderboards, geo, presence.

❌ Disadvantages:
- Memory-bound and costly at large scale; complex structures can create big keys.
- Single-threaded: one slow command (KEYS, huge ZRANGE) blocks everyone.
- Durability weaker than a DB (unless configured carefully); not a replacement for Kafka at massive scale.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hash | Field-value map in one key | एक key में object |
| List | Ordered list, push/pop | क्रम वाली लिस्ट |
| Set | Unique unordered members | unique सदस्य |
| Sorted Set (ZSET) | Members ordered by score | score से sorted लिस्ट |
| Stream | Append-only log with consumer groups | event log + consumers |
| Geo | Location index | लोकेशन index |
| Bitmap | Bits per id | हर id का एक bit |
| HyperLogLog | Approximate unique count | अनुमानित unique गिनती |
| Lua script | Atomic server-side logic | सर्वर पर atomic logic |
| Consumer group | Workers sharing a stream | stream बाँटने वाले workers |

---

## ⚡ 3-Line Summary
**English:**
1. Redis offers String, Hash, List, Set, Sorted Set, Stream, Geo, Bitmap, HyperLogLog — each with atomic, fast ops.
2. Map features to structures: cart → Hash, leaderboard/rate-limit → ZSET, queue → Stream, nearby → Geo, DAU → Bitmap/HLL.
3. Use MULTI/Lua for atomic multi-step logic; avoid KEYS, big keys and missing TTLs.

**Hindi:**
1. Redis में String, Hash, List, Set, Sorted Set, Stream, Geo, Bitmap, HyperLogLog — सब तेज़ और atomic।
2. Cart → Hash, leaderboard → ZSET, queue → Stream, पास के ड्राइवर → Geo, DAU → Bitmap।
3. कई कदम atomic करने हों तो MULTI/Lua; KEYS, बड़ी keys और बिना TTL की keys से बचो।

---

## ➡️ Next Topic Suggestion
**45. Cache-Aside Pattern** — Now, HOW should the app and cache work together? Next: the most common caching pattern, cache-aside (lazy loading), its flow, pitfalls and production-grade implementation.
