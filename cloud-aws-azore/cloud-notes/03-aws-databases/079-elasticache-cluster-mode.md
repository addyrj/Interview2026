# 79. ELASTICACHE CLUSTER MODE
# AWS: ElastiCache Redis Cluster Mode Enabled (sharding)
# Azure: Azure Cache for Redis Premium clustering
# हिंदी में: Redis क्लस्टर मोड यानी डेटा को शार्ड्स में बाँटना

---

## 🔵 Simple Definition (2 lines)
Cluster mode enabled splits data across multiple shards (each a primary plus replicas) using 16384 hash slots.
हिंदी: क्लस्टर मोड में डेटा 16384 हैश स्लॉट के ज़रिए कई शार्ड्स में बँटता है।

---

## 🔴 Why it Exists (2 lines)
One Redis primary is limited by one node's memory and write throughput.
Sharding scales memory and writes horizontally.

---

## 🟢 How it Works
```
key --CRC16--> slot (0..16383) --> shard
 Shard 1: slots 0-5460      primary + replica(s)
 Shard 2: slots 5461-10922  primary + replica(s)
 Shard 3: slots 10923-16383 primary + replica(s)
Client must be cluster-aware (follows MOVED redirects) -> configuration endpoint
Multi-key ops need same slot -> use hash tags: {user:1}:cart , {user:1}:profile
Cluster mode disabled = 1 shard, simple, up to 5 replicas
```

---

## 💻 Code / Config Example
```javascript
// Node.js ioredis Cluster client
const Redis = require("ioredis");
const cluster = new Redis.Cluster(
  [{ host: process.env.REDIS_CONFIG_ENDPOINT, port: 6379 }],
  {
    dnsLookup: (addr, cb) => cb(null, addr),
    redisOptions: { tls: {} },
  }
);
// Same slot via hash tag, so MGET/transactions work:
// await cluster.set("{user:1}:cart", "..."); await cluster.set("{user:1}:profile", "...");
```
```bash
# Create a 3-shard, 1-replica cluster (AWS CLI v2)
aws elasticache create-replication-group \
  --replication-group-id app-redis-cluster \
  --replication-group-description "sharded redis" \
  --engine redis --cache-node-type cache.t4g.small \
  --num-node-groups 3 --replicas-per-node-group 1 \
  --automatic-failover-enabled --transit-encryption-enabled
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Sharding | Cluster mode enabled | Premium tier clustering (and Enterprise/Managed Redis) |
| Online resharding | Yes | Yes (scale shards) |
| Client | Cluster-aware client | Cluster-aware client |
| Pricing | Per node, shards x nodes (approximate - check current docs) | Per shard (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using multi-key commands across slots (CROSSSLOT error).
✅ Correct: Use hash tags so related keys share a slot.

❌ Mistake: Non-cluster client against cluster mode.
✅ Correct: Use `Redis.Cluster` / `RedisCluster`.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] How many hash slots?
A1: 16384.

Q2: [Medium] Cluster mode enabled vs disabled?
A2: Enabled shards data across nodes for scale; disabled is one shard with replicas, simpler.

Q3: [Hard] You get CROSSSLOT errors on a Lua script. Fix?
A3: Ensure all keys the script touches share a hash tag so they map to the same slot.

---

## ✅ Quick Checklist
□ Cluster-aware client
□ Hash tags for multi-key ops
□ Shard count sized for memory and writes

---

## ⚡ 1-Line Summary
Cluster mode shards Redis over 16384 slots to scale memory and writes. | क्लस्टर मोड 16384 स्लॉट में Redis को बाँटकर मेमोरी और राइट स्केल करता है।

## ➡️ Next: DocumentDB (MongoDB compatible)

---
