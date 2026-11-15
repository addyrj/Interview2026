# 227. Azure Cache for Redis
# AWS: ElastiCache for Redis / MemoryDB
# Azure: Azure Cache for Redis (successor: Azure Managed Redis)
# हिंदी में: तेज़ in-memory कैश और session स्टोर

---

## 🔵 Simple Definition (2 lines)
A managed in-memory Redis service used for caching, sessions, rate limits and pub/sub, with tiers from Basic to Enterprise.
हिंदी: बार-बार पढ़े जाने वाले डेटा को मेमोरी में रखकर DB का लोड घटाता है।

---

## 🔴 Why it Exists (2 lines)
Database round trips are slow and expensive for hot data.
Managed Redis gives sub-millisecond reads with patching and replication handled.

---

## 🟢 How it Works
```
Request -> API -> GET key in Redis -- hit --> return
                       | miss
                       v
                   Database -> SET key EX 300 -> return
Tiers: Basic (no SLA) | Standard (replica) | Premium (cluster, VNet, persistence)
       | Enterprise (Redis modules)
Port 6380 = TLS (non-TLS 6379 disabled by default)
Note: Microsoft has announced Azure Managed Redis as the successor; check current docs for retirement dates.
```

---

## 💻 Code / Config Example
```bash
az redis create --name myapp-redis --resource-group rg-app --location centralindia \
  --sku Standard --vm-size c1
az redis list-keys --name myapp-redis --resource-group rg-app
```
```javascript
// Node.js cache-aside with ioredis over TLS
const Redis = require("ioredis");
const redis = new Redis({
  host: "myapp-redis.redis.cache.windows.net", port: 6380,
  password: process.env.REDIS_KEY, tls: { servername: "myapp-redis.redis.cache.windows.net" },
});

async function getUser(id, loadFromDb) {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);
  const user = await loadFromDb(id);
  await redis.set(`user:${id}`, JSON.stringify(user), "EX", 300); // TTL avoids stale forever
  return user;
}
module.exports = { getUser };
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | ElastiCache (Redis/Valkey) | Azure Cache for Redis / Managed Redis |
| Durable Redis | MemoryDB | Premium persistence / Enterprise |
| Clustering | Cluster mode | Premium/Enterprise clustering |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Caching without TTL or invalidation.
✅ Correct: Always set TTL and delete/update keys on writes.

❌ Mistake: Using Basic tier in production.
✅ Correct: Use Standard or higher for a replica and SLA.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is cache-aside?
A1: App checks cache first, on miss reads DB and fills cache.

Q2: [Medium] Redis eviction policy?
A2: When memory is full, policy (e.g. volatile-lru, allkeys-lru) decides what is removed; set it intentionally.

Q3: [Hard] Cache stampede?
A3: Many requests miss together after expiry. Use jittered TTLs, request coalescing/locks, or refresh-ahead.

---

## ✅ Quick Checklist
□ TLS on, keys in Key Vault
□ TTL on all keys, eviction policy set
□ Standard+ tier for production

---

## ⚡ 1-Line Summary
Managed Redis for sub-ms caching | सब-मिलीसेकंड कैशिंग के लिए मैनेज्ड Redis

## ➡️ Next: Azure Synapse Analytics

---
