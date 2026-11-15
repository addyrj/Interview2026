---

# Q210. Horizontal Sharding — Shard Key Selection
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: Both

---

## ❓ Question
You must shard an `orders` table across 4 shards. How do you choose the shard key? Show how to test candidate keys for skew (hot shards) and explain hash vs range sharding trade-offs.

---

## 💡 Quick Concept (2 lines only)
A good shard key has high cardinality, even distribution, and appears in most queries (so each query hits one shard); it is very hard to change later.
हिंदी: Shard key ऐसी चुनो जिसमें values बहुत हों, load बराबर बँटे, और ज़्यादातर queries में हो — बाद में बदलना बहुत मुश्किल है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run on MySQL 9.1.0 -- same SQL works on PostgreSQL)
-- ============================================
CREATE TABLE orders (
  order_id  INT PRIMARY KEY,
  user_id   INT,
  tenant_id INT,
  amount    DECIMAL(10,2)
);

INSERT INTO orders VALUES
  (1,101,1,10),(2,101,1,20),(3,102,1,30),(4,103,1,40),(5,104,1,50),(6,105,1,60),
  (7,106,2,70),(8,107,2,80),(9,108,3,90),(10,109,4,15),(11,110,5,25),(12,111,6,35);
-- tenant 1 is a "whale" customer with 6 of 12 rows

-- ============================================
-- SOLUTION: measure distribution of each candidate key
-- ============================================

-- Candidate A: tenant_id (natural for multi-tenant SaaS)
SELECT tenant_id AS k, COUNT(*) AS rows_cnt FROM orders GROUP BY tenant_id ORDER BY k;
-- k | rows_cnt
-- 1 | 6        <- one tenant = 50% of data: hot shard
-- 2 | 2
-- 3 | 1
-- 4 | 1
-- 5 | 1
-- 6 | 1

-- Candidate B: user_id % 4 (modulo)
SELECT user_id % 4 AS shard, COUNT(*) AS rows_cnt FROM orders GROUP BY user_id % 4 ORDER BY shard;
-- shard | rows_cnt
-- 0     | 2
-- 1     | 4
-- 2     | 3
-- 3     | 3

-- Candidate C: tenant_id % 4 (low-cardinality key, modulo)
SELECT tenant_id % 4 AS shard, COUNT(*) AS rows_cnt FROM orders GROUP BY tenant_id % 4 ORDER BY shard;
-- shard | rows_cnt
-- 0     | 1
-- 1     | 7        <- 58% of rows on shard 1
-- 2     | 3
-- 3     | 1

-- Candidate D: hash of user_id (MySQL CRC32; PostgreSQL: abs(hashtext(user_id::text)) % 4)
SELECT CRC32(CAST(user_id AS CHAR)) % 4 AS shard, COUNT(*) AS rows_cnt
FROM orders GROUP BY 1 ORDER BY 1;
-- shard | rows_cnt
-- 0     | 4
-- 1     | 3
-- 2     | 2
-- 3     | 3

-- Verdict: user_id (or hash(user_id)) distributes best here.
-- Trade-off: queries by tenant_id become scatter-gather (Q212).
-- Numbers above are from a 12-row toy table; use millions of rows in reality.

-- ============================================
-- Checklist (interview answer)
-- ============================================
-- 1. Cardinality   : millions of distinct values, not status/country
-- 2. Distribution  : no whale tenant, no monotonically increasing hot tail
-- 3. Query locality: most reads/writes carry the key (WHERE user_id = ?)
-- 4. Co-location   : child tables (order_items) shard by the SAME key
-- 5. Immutable     : the key value never changes after insert
-- 6. Growth        : resharding plan (consistent hashing / virtual shards, Q211)
```

---

## 🔍 Why This Works (3 lines max)
Counting rows per candidate bucket exposes skew before you commit. Hash sharding spreads load evenly but kills range scans; range sharding keeps range queries cheap but creates hot spots for increasing keys (timestamps, auto-increment ids).
हिंदी: Candidate key से GROUP BY करके skew पहले ही दिख जाता है। Hash = बराबर load, range = range queries आसान पर hot spot का खतरा।

---

## ⚡ Alternative Solution

```sql
-- Directory/lookup-table sharding: explicit map, lets you move a whale tenant alone.
CREATE TABLE shard_map (
  tenant_id INT PRIMARY KEY,
  shard_id  INT NOT NULL
);
INSERT INTO shard_map VALUES (1, 4), (2, 1), (3, 2);   -- whale tenant 1 gets own shard 4
SELECT shard_id FROM shard_map WHERE tenant_id = 1;
-- shard_id
-- 4
-- Cost: lookup on every request (cache it) and the map is a critical component.

-- PostgreSQL native hash partitioning shows the same idea inside one server
-- (verified on PGlite 18.6: 20 rows, tenant = id % 5 -> partitions got 12 / 8):
-- CREATE TABLE ev (id int, tenant int) PARTITION BY HASH (tenant);
-- CREATE TABLE ev_0 PARTITION OF ev FOR VALUES WITH (MODULUS 2, REMAINDER 0);
-- Real result: ev_0 = 12 rows, ev_1 = 8 rows (5 tenants cannot split evenly into 2).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Shard by created_at / auto-increment id: all new writes hit the last shard.
-- ❌ Shard by country or status: low cardinality, 3 values for 16 shards.
-- ❌ Shard key not in the PK/unique indexes: global uniqueness can't be enforced.
-- ❌ Using plain "% N" with no plan: changing N from 3 to 4 moves most keys (Q211).
--    Measured on 1000 keys: 752 of 1000 keys change shard when mod 3 -> mod 4.
-- ✅ Use many virtual shards (e.g. 1024) mapped to few servers, or consistent hashing.
```

---

## 🎯 Interview Tip (1 line)
Say: "I shard last, after read replicas, caching and partitioning are exhausted; then I pick the key by query patterns (usually tenant or user id), verify skew with real data, co-locate related tables on the same key, and use virtual shards so I can rebalance without rehashing everything."

---

## 🔗 Related Questions
→ Q211 (consistent hashing) | Q212 (cross-shard queries) | Q213 (Vitess) | Q214 (Citus)
