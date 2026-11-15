# 77. ELASTICACHE - REDIS + MEMCACHED
# AWS: Amazon ElastiCache (Redis OSS / Valkey / Memcached)
# Azure: Azure Cache for Redis / Azure Managed Redis
# हिंदी में: ElastiCache यानी मैनेज्ड कैश

---

## 🔵 Simple Definition (2 lines)
ElastiCache is a managed in-memory data store: Redis/Valkey (rich data types, persistence, replication) or Memcached (simple multi-threaded cache).
हिंदी: ElastiCache मैनेज्ड इन-मेमोरी स्टोर है: Redis/Valkey (समृद्ध फ़ीचर) या Memcached (सरल कैश)।

---

## 🔴 Why it Exists (2 lines)
Hitting the database for every request is slow and expensive.
A cache returns hot data in sub-millisecond time and also serves sessions, rate limits and queues.

---

## 🟢 How it Works
```
NestJS / FastAPI --> GET key in cache --hit--> return
                        | miss
                        v
                    query RDS -> SET key EX 300 -> return   (cache-aside)
Redis/Valkey : strings, hashes, lists, sets, sorted sets, pub/sub, TTL,
               replication + Multi-AZ failover, snapshots
Memcached    : plain key-value, multi-threaded, no persistence, no replication
```

---

## 💻 Code / Config Example
```javascript
// Node.js cache-aside with ioredis
const Redis = require("ioredis");
const redis = new Redis({ host: process.env.REDIS_HOST, port: 6379, tls: {} });

async function getUser(id, db) {
  const key = `user:${id}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);
  const user = await db.findUser(id);          // DB call on miss
  await redis.set(key, JSON.stringify(user), "EX", 300);
  return user;
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Redis | ElastiCache Redis OSS / Valkey | Azure Cache for Redis / Azure Managed Redis |
| Memcached | Yes | N/A (not offered); use Redis |
| Serverless option | ElastiCache Serverless | Azure Managed Redis tiers |
| Pricing | Node-hours (approximate - check current docs) | Tier-based (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: No TTL, so cache grows and serves stale data forever.
✅ Correct: Always set an expiry and an eviction policy.

❌ Mistake: Treating cache as the source of truth.
✅ Correct: The DB is the truth; the cache must be rebuildable.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Redis vs Memcached?
A1: Redis has data structures, persistence, replication; Memcached is simple and multi-threaded.

Q2: [Medium] What is cache-aside?
A2: App checks cache, on miss reads DB and fills the cache.

Q3: [Hard] Prevent a cache stampede on a hot key expiry.
A3: Use request coalescing/locks, jittered TTLs, or refresh-ahead so one worker repopulates.

---

## ✅ Quick Checklist
□ TTL on every key
□ In-transit encryption (TLS) on
□ Private subnet, SG only from app

---

## ⚡ 1-Line Summary
ElastiCache = managed Redis/Memcached to cut DB load and latency. | ElastiCache = DB लोड और लेटेंसी घटाने वाला मैनेज्ड Redis/Memcached।

## ➡️ Next: ElastiCache Redis Setup

---
