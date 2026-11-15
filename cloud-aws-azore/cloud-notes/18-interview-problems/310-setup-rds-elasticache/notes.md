# 310. Setup RDS + Elasticache
# AWS: RDS PostgreSQL (Multi-AZ) + ElastiCache for Redis
# Azure: Azure Database for PostgreSQL Flexible Server + Azure Cache for Redis
# हिंदी में: RDS में स्थायी डेटा, ElastiCache Redis में तेज़ कैश ताकि DB पर लोड कम हो

---

## 🔵 Simple Definition
RDS is the system of record; Redis holds hot, rebuildable data with a TTL, using cache-aside.
हिंदी: असली डेटा RDS में, बार-बार पढ़े जाने वाला डेटा Redis कैश में।

## 🔴 Why it Exists
Cuts read latency from milliseconds to sub-millisecond and protects the DB from read spikes.

## 🟢 How it Works
```
App --GET user:42--> Redis hit? -> return
                     miss -> SELECT from RDS -> SET user:42 EX ttl -> return
Write: UPDATE RDS -> DEL user:42
Both in isolated subnets; SG allows 5432 / 6379 only from the app SG
RDS Multi-AZ standby (sync) ; Redis primary + replica in another AZ (auto failover)
```

## 💻 Code / Config Example
`main.tf` (SGs, subnet groups, force-SSL parameter group, Multi-AZ Postgres with managed secret, Redis replication group with TLS and at-rest encryption; provider ~> 5.x, not applied here) and `cache-aside.js` (node-postgres + ioredis; syntax-checked only, not run against real services).

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| SQL | RDS / Aurora | Flexible Server |
| Cache | ElastiCache (Redis/Valkey) | Azure Cache for Redis |
| HA | Multi-AZ | zone-redundant HA |
| Secrets | Secrets Manager managed password | Key Vault / Entra auth |
| Pricing | instance-hours + storage (approximate - check current docs) | similar |

## 💰 Cost / HA / Security
- Cost: Graviton `t4g`/`r7g` classes, reserved instances for steady DBs, avoid oversized caches; storage autoscaling cap.
- HA: Multi-AZ DB, Redis replica with failover; app must reconnect on failover (retry, DNS TTL).
- Security: private subnets, TLS everywhere, encryption at rest, no hard-coded passwords, deletion protection.

## ⚠️ Common Mistakes
❌ Caching without TTL or invalidation.
✅ TTL plus delete-on-write.

❌ Treating Redis as the only copy.
✅ Cache is rebuildable; DB is the source of truth.

## ⚫ Interview Q&A
Q1 [Easy]: What is cache-aside?
A1: App checks the cache first, loads from DB on miss, then populates the cache.

Q2 [Medium]: What is a cache stampede and the fix?
A2: Many requests recompute a hot key after expiry; use TTL jitter, request coalescing/locks, or stale-while-revalidate.

Q3 [Hard]: Multi-AZ vs read replica?
A3: Multi-AZ is synchronous standby for failover, not readable (for classic RDS instance Multi-AZ); read replicas are asynchronous, scale reads and can lag.

## ✅ Quick Checklist
□ SG-to-SG access only
□ TLS + encryption at rest
□ TTL and invalidation defined

## ⚡ 1-Line Summary
RDS stores truth, Redis serves hot reads. | RDS सच्चा डेटा रखता है, Redis तेज़ रीड देता है।

## ➡️ Next: 311. Write GitHub Actions → AWS
