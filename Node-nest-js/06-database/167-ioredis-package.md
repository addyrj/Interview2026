# 167. ioredis Package
# हिंदी में: ioredis Package — Advanced Redis Client

---

## 🔵 Simple Definition (English)
**`ioredis`** is a full-featured, high-performance Redis client for Node.js, offering everything the basic `redis` package does plus built-in **Cluster** support, **Sentinel** (automatic failover for high availability), transparent reconnection, **pipelining** (batching commands for fewer round trips), Lua scripting helpers, and a Promise-based API with excellent TypeScript support.

## 🔵 सरल परिभाषा (Hindi)
**`ioredis`** Node.js के लिए एक full-featured, high-performance Redis client है, जो basic `redis` package के सारे features के साथ built-in **Cluster** support, **Sentinel** (automatic failover), transparent reconnection, **pipelining** (fewer round trips के लिए commands batch करना), Lua scripting helpers, और Promise-based API देता है।

---

## 🔴 Problem it Solves
A single Redis instance is a single point of failure and a scaling bottleneck for very high-throughput or high-availability systems. Production Redis deployments often use **Cluster mode** (data sharded across multiple nodes) or **Sentinel** (automatic master failover for replicas) — these require a client smart enough to discover topology, redirect commands to the right shard, and reconnect automatically during failover. `ioredis` handles all of this transparently, so application code just calls `redis.get(key)` without worrying about which physical node holds that key.

## 🔴 यह क्यों बना? (Hindi)
Single Redis instance high-throughput या high-availability systems के लिए single point of failure और scaling bottleneck है। Production deployments अक्सर **Cluster mode** या **Sentinel** इस्तेमाल करते — इनके लिए client को topology discover करना, commands सही shard पर redirect करना, failover के दौरान automatically reconnect करना चाहिए। `ioredis` ये सब transparently handle करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Install: `npm install ioredis`. Simple usage: `new Redis(port, host)` or `new Redis(redisUrl)` — connects automatically (no explicit `.connect()` needed, unlike `redis` v4).
Step 2 → For Cluster: `new Redis.Cluster([{ host, port }, ...])` — ioredis discovers all nodes and shards/routes commands automatically based on key hashing.
Step 3 → For Sentinel (HA failover): `new Redis({ sentinels: [...], name: 'mymaster' })` — ioredis asks Sentinel for the current master and reconnects automatically if a failover occurs.
Step 4 → **Pipelining**: `redis.pipeline().set('a', 1).set('b', 2).exec()` — batches multiple commands into ONE network round trip instead of N separate ones.
Step 5 → **Lua scripting**: `redis.defineCommand('myScript', { numberOfKeys: 1, lua: '...' })` — runs atomic, server-side logic that can't be expressed as a single command.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Install करो: `npm install ioredis`। `new Redis(port, host)` से auto-connect होता है।
Step 2 → Cluster के लिए: `new Redis.Cluster([...])` — ioredis सारे nodes discover करता है, commands auto-route करता है।
Step 3 → Sentinel (HA) के लिए: `new Redis({ sentinels, name })` — current master पूछता है, failover पर auto-reconnect करता है।
Step 4 → **Pipelining**: multiple commands को ONE network round trip में batch करना।
Step 5 → **Lua scripting**: atomic, server-side logic जो एक single command से express नहीं हो सकता।

---

## 🟡 Real World Example
**Amazon India's inventory-reservation service** uses `ioredis` with a Redis Cluster deployment to handle flash-sale traffic spread across multiple shards for horizontal scalability. During checkout, it uses a Lua script (atomic server-side execution) to check-and-decrement stock count in ONE atomic operation (`GET` + conditional `DECR`), preventing overselling even with thousands of concurrent requests hitting the same product — a plain `GET` then `DECR` from the app would have a race condition window; the Lua script eliminates it entirely.

## 🟡 Real Example Hindi mein
**Amazon India की inventory-reservation service** `ioredis` के साथ Redis Cluster इस्तेमाल करती है flash-sale traffic के लिए horizontal scalability के साथ। Checkout पर एक Lua script stock count को एक ही atomic operation में check-and-decrement करती है, overselling से बचाव — plain `GET` फिर `DECR` में race condition window होता, Lua script उसे पूरी तरह खत्म करती है।

---

## 💻 Code Example — Basic

```javascript
// ioredis-basic.js
// npm install ioredis
const Redis = require('ioredis');

// Connects automatically — no explicit .connect() call needed (unlike `redis` v4)
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

async function main() {
  // Basic string operations
  await redis.set('city', 'Bengaluru');
  const city = await redis.get('city');
  console.log('City:', city);

  // Set with TTL — shorthand "EX" flag style
  await redis.set('otp:9999', '123456', 'EX', 300); // expires in 5 minutes
  console.log('OTP TTL:', await redis.ttl('otp:9999'));

  // Hash operations for structured data
  await redis.hset('user:1', { name: 'Vikas', age: 29 });
  const user = await redis.hgetall('user:1');
  console.log('User hash:', user); // { name: 'Vikas', age: '29' } — note: all hash values are strings

  // Sorted set for a leaderboard
  await redis.zadd('leaderboard', 100, 'player1', 250, 'player2', 180, 'player3');
  const top = await redis.zrevrange('leaderboard', 0, 2, 'WITHSCORES'); // top 3, highest score first
  console.log('Leaderboard top 3:', top);

  await redis.quit();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// ioredis-advanced.js — pipelining, Lua scripting, cluster-ready pattern
const Redis = require('ioredis');
const redis = new Redis(process.env.REDIS_URL);

// ─── 1. PIPELINING — batch many commands into ONE round trip ────────────────
async function bulkCacheWarm(products) {
  const pipeline = redis.pipeline(); // queue commands, don't send yet
  products.forEach((p) => {
    pipeline.set(`product:${p.id}`, JSON.stringify(p), 'EX', 300);
  });
  const results = await pipeline.exec(); // sends ALL commands in one network round trip
  console.log(`Warmed cache for ${results.length} products in one round trip`);
}

// ─── 2. LUA SCRIPT for atomic check-and-decrement (prevents overselling) ────
// defineCommand registers a custom command backed by a Lua script, run atomically on the server
redis.defineCommand('reserveStock', {
  numberOfKeys: 1,
  lua: `
    local current = tonumber(redis.call('GET', KEYS[1]) or 0)
    local requested = tonumber(ARGV[1])
    if current >= requested then
      redis.call('DECRBY', KEYS[1], requested)
      return 1
    else
      return 0
    end
  `,
});

async function reserveProductStock(productId, quantity) {
  // This entire check-and-decrement runs as ONE atomic operation on the Redis server —
  // no other command can interleave between the GET and the DECRBY, eliminating race conditions.
  const success = await redis.reserveStock(`stock:${productId}`, quantity);
  return success === 1;
}

// ─── 3. CLUSTER-READY CONNECTION (would be used in production multi-node setup) ──
function createClusterClient() {
  return new Redis.Cluster([
    { host: 'redis-node-1', port: 6379 },
    { host: 'redis-node-2', port: 6379 },
    { host: 'redis-node-3', port: 6379 },
  ], {
    redisOptions: { password: process.env.REDIS_PASSWORD },
  });
  // ioredis automatically discovers the full cluster topology and routes
  // each command to the correct shard based on the key's hash slot.
}

async function run() {
  await redis.set('stock:p1', 50);

  const reserved1 = await reserveProductStock('p1', 20);
  console.log('Reserved 20 units:', reserved1); // true, stock now 30

  const reserved2 = await reserveProductStock('p1', 100); // more than available
  console.log('Reserved 100 units:', reserved2); // false, stock unchanged

  await bulkCacheWarm([{ id: 'a', name: 'Item A' }, { id: 'b', name: 'Item B' }]);

  await redis.quit();
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express app using ioredis for atomic stock reservation during checkout
const express = require('express');
const Redis = require('ioredis');

const app = express();
app.use(express.json());
const redis = new Redis(process.env.REDIS_URL);

redis.defineCommand('reserveStock', {
  numberOfKeys: 1,
  lua: `
    local current = tonumber(redis.call('GET', KEYS[1]) or 0)
    if current >= tonumber(ARGV[1]) then
      redis.call('DECRBY', KEYS[1], ARGV[1])
      return 1
    end
    return 0
  `,
});

app.post('/api/checkout', async (req, res) => {
  const { productId, quantity } = req.body;
  const success = await redis.reserveStock(`stock:${productId}`, quantity);
  if (!success) return res.status(409).json({ error: 'Insufficient stock' });
  res.json({ message: 'Stock reserved successfully' });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Looping individual commands instead of using pipelining for bulk operations
```javascript
// Wrong — N network round trips for N keys
for (const item of items) { await redis.set(item.key, item.value); }

// Right — batch into one pipeline, one round trip
const pipeline = redis.pipeline();
items.forEach((item) => pipeline.set(item.key, item.value));
await pipeline.exec();
```

❌ Mistake 2: Using `GET` then `SET`/`DECR` separately for operations that MUST be atomic
✅ Correct: Separate `GET` + `DECR` calls have a race-condition window between them under concurrent requests. Use atomic single commands (`DECRBY`, `INCR`) or a Lua script via `defineCommand` when the logic needs to check-and-modify as ONE indivisible step.

---

## 🧠 Tricky Interview Question

```javascript
const pipeline = redis.pipeline();
pipeline.set('a', 1);
pipeline.get('nonexistent-key-that-errors-on-wrong-type'); // suppose this throws a type error
pipeline.set('b', 2);
const results = await pipeline.exec();
console.log(results);
```
Answer: Unlike a single command that would reject the whole call on error, `pipeline.exec()` returns an ARRAY of `[error, result]` PAIRS for EACH command, even if one command failed — it does NOT abort the remaining commands in the pipeline. So `results` looks like `[[null, 'OK'], [TypeError, null], [null, 'OK']]` — the `set('a', 1)` and `set('b', 2)` still succeed even though the middle command errored. Developers must check each `[error, result]` pair individually rather than assuming a single try/catch around `exec()` covers per-command failures.

---

## ⚫ Interview Questions + Answers

Q1: What are the main advantages of `ioredis` over the basic `redis` package?
A1: Built-in support for Redis Cluster (automatic sharding/routing) and Sentinel (automatic failover for high availability), native pipelining and transaction (MULTI/EXEC) chaining with a fluent API, `defineCommand` for registering custom Lua scripts as regular-feeling methods, and historically more mature/battle-tested handling of complex production topologies. The basic `redis` client has closed much of this gap in v4+, but `ioredis` remains popular for cluster/sentinel-heavy deployments.

Q2: What is pipelining, and how does it improve performance?
A2: Pipelining batches multiple Redis commands and sends them together in ONE network round trip, rather than waiting for each command's response before sending the next. This amortizes network latency across many commands — instead of N round trips (each with its own latency cost), you pay for roughly ONE round trip's latency for the whole batch, dramatically speeding up bulk operations like cache warming or bulk key reads.

Q3: How does `ioredis` handle Redis Cluster mode differently from a single-instance connection?
A3: `new Redis.Cluster([...seed nodes...])` tells ioredis to discover the full cluster topology (which node owns which hash slots) from the seed nodes. For every subsequent command, ioredis computes the key's hash slot and routes the command DIRECTLY to the node responsible for it — transparently to application code. If the cluster topology changes (node added/removed, failover), ioredis automatically refreshes its routing table.

Q4: Why would you use a Lua script instead of separate Redis commands for some operations?
A4: Redis guarantees that a Lua script executes ATOMICALLY and IN ISOLATION on the server — no other command can interleave in the middle of it, even under heavy concurrency. This is essential for "check-then-act" logic (like checking stock before decrementing) where separate GET+DECR commands from the application would have a race-condition window between the two network calls. A Lua script performs the whole check-and-modify as one indivisible server-side operation.

Q5: What happens to in-flight commands if a `ioredis` connection drops (e.g., during a Sentinel failover)?
A5: `ioredis` has built-in automatic reconnection logic — by default it queues commands issued while disconnected (configurable via `enableOfflineQueue`) and retries/reconnects according to a configurable retry strategy. During a Sentinel-managed failover, `ioredis` detects the new master (by querying Sentinel) and transparently reconnects and resumes sending commands to the new master, without requiring application code to handle the failover manually.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running Redis in Cluster or Sentinel (HA) mode in production
- You need pipelining for bulk operations or Lua scripting for atomic multi-step logic
- You want a mature, widely-adopted client with strong community support for complex deployments

❌ Avoid when:
- You only need a single Redis instance with basic GET/SET caching — the simpler official `redis` package may suffice and has a smaller footprint
- Team familiarity/standardization already favors the official `redis` client across other services — consistency matters more than marginal feature differences for simple use cases

---

## 📊 Visual Diagram
```
ioredis FEATURES
──────────────────────────────────────────────
  Single instance:  new Redis(url)
  Cluster mode:     new Redis.Cluster([node1, node2, node3])
                          │
                          ▼
                    auto hash-slot routing
                    key → correct shard

  Sentinel (HA):    new Redis({ sentinels: [...], name: 'mymaster' })
                          │
                          ▼
                    auto master discovery + failover reconnect

  Pipelining:
    pipeline().set().get().set().exec()
                          │
                          ▼
                    ONE network round trip for all commands

  Lua script (defineCommand):
    GET + DECRBY as ONE atomic server-side operation
    (no race condition between the check and the modify)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cluster | Sharded Redis across nodes | Nodes में sharded Redis |
| Sentinel | Automatic failover system | Automatic failover system |
| Pipelining | Batch commands, 1 round trip | Commands batch, 1 round trip |
| Lua script | Atomic server-side logic | Atomic server-side logic |
| defineCommand | Register custom Lua command | Custom Lua command register करना |
| hash slot | Cluster's key-to-node mapping | Cluster का key-to-node mapping |
| offline queue | Buffers commands during disconnect | Disconnect के दौरान commands buffer |

---

## ⚡ 3-Line Summary
English:
1. `ioredis` adds Cluster and Sentinel support, pipelining, and Lua scripting on top of basic Redis client functionality.
2. Pipelining batches many commands into one network round trip — essential for bulk operations.
3. Use Lua scripts (`defineCommand`) for atomic check-then-act logic that would otherwise have a race condition across separate commands.

Hindi:
1. `ioredis` basic Redis client functionality के ऊपर Cluster, Sentinel support, pipelining, Lua scripting add करता है।
2. Pipelining कई commands को एक network round trip में batch करता है — bulk operations के लिए essential।
3. Atomic check-then-act logic के लिए Lua scripts (`defineCommand`) इस्तेमाल करो, वर्ना separate commands में race condition आएगी।

---

## ➡️ Next Topic
**168. Redis Caching in Node** — Cache invalidation strategies, cache-aside vs write-through, and avoiding stale data bugs.
