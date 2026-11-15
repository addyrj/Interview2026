---

# Q154. Sharding — Horizontal Partitioning
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (concept; routing demo verified on MySQL 9.1 — real multi-server sharding was NOT run)

---

## ❓ Question
Your `users` table no longer fits on one server. Explain sharding, choose a shard key, show how a row is routed to a shard, why modulo-by-server-count is dangerous when you add servers, and what you lose (joins, transactions, global unique ids).

---

## 💡 Quick Concept (2 lines only)
Sharding splits rows of one logical table across multiple independent database servers using a shard key; the application (or a proxy) routes each query. Unlike partitioning, each shard is a separate server with its own CPU, RAM and disk.
हिंदी: Sharding = एक table की rows अलग-अलग servers पर बांटना (shard key से); partitioning एक ही server के अंदर होती है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (single MySQL instance simulating the routing logic)
-- ============================================

-- Directory: many LOGICAL shards (4) mapped onto few PHYSICAL hosts (2).
CREATE TABLE shard_map (
  logical_shard INT PRIMARY KEY,
  physical_host VARCHAR(50) NOT NULL
);
INSERT INTO shard_map VALUES (0,'db-a'),(1,'db-a'),(2,'db-b'),(3,'db-b');

CREATE TABLE users (id INT PRIMARY KEY, email VARCHAR(100));
INSERT INTO users VALUES
  (1,'a@x.com'),(2,'b@x.com'),(3,'c@x.com'),(4,'d@x.com'),
  (5,'e@x.com'),(6,'f@x.com'),(7,'g@x.com'),(8,'h@x.com');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: hash the shard key -> logical shard -> physical host
SELECT u.id, CRC32(u.id) % 4 AS logical_shard, m.physical_host
FROM users u JOIN shard_map m ON m.logical_shard = CRC32(u.id) % 4
ORDER BY u.id;

-- Result (MySQL CRC32; PgSQL has no CRC32, hashtext() gives different numbers):
-- id | logical_shard | physical_host
-- 1  | 3 | db-b
-- 2  | 1 | db-a
-- 3  | 3 | db-b
-- 4  | 0 | db-a
-- 5  | 2 | db-b
-- 6  | 0 | db-a
-- 7  | 2 | db-b
-- 8  | 3 | db-b

-- Step 2: check the distribution (hot-shard detection)
SELECT CRC32(u.id) % 4 AS logical_shard, COUNT(*) AS users_cnt
FROM users u GROUP BY 1 ORDER BY 1;
-- 0 -> 2 | 1 -> 1 | 2 -> 2 | 3 -> 3        (uneven with only 8 rows; evens out with volume)

-- Step 3: why "id % number_of_servers" breaks when you go from 2 to 3 servers
SELECT SUM((id % 2) <> (id % 3)) AS moved, COUNT(*) AS total FROM users;
-- moved | total
-- 5     | 8         -> 5 of 8 rows (62%) must migrate to another server!

-- Step 4: the fix — fixed number of logical shards + a directory table.
-- Adding a server = copy some logical shards and UPDATE shard_map. Rows never get re-hashed:
UPDATE shard_map SET physical_host = 'db-c' WHERE logical_shard = 3;   -- move shard 3 only
```

---

## 🔍 Why This Works (3 lines max)
Hashing the shard key spreads rows evenly, and routing through many logical shards decouples "which shard" from "how many servers". Resizing then moves whole logical shards rather than re-hashing every row. A good shard key (tenant_id, user_id) keeps most queries on a single shard.
हिंदी: Hash से rows बराबर बंटती हैं; logical shards + directory से server जोड़ने पर सिर्फ पूरा shard move होता है, हर row नहीं।

---

## ⚡ Alternative Solution

```sql
-- Other routing strategies
-- Range sharding : user_id 1-1M -> shard1, 1M-2M -> shard2   (easy range scans, hot last shard)
-- Directory/lookup: tenant_id -> shard in a lookup table      (flexible, lookup is a SPOF/cache)
-- Consistent hashing (Cassandra, many proxies): adding a node moves only ~1/N of keys.

-- Global unique ids across shards (no shared AUTO_INCREMENT):
--   * Snowflake-style 64-bit id = timestamp | shard_id | sequence
--   * MySQL trick: auto_increment_increment = number_of_shards, auto_increment_offset = shard_no
--   * UUIDv7 (time-ordered) — see Q160

-- Ready-made tooling (not run here): Vitess / ProxySQL for MySQL, Citus for PostgreSQL
--   Citus example:  SELECT create_distributed_table('users', 'id');

-- Cross-shard query = scatter-gather: run on every shard, merge in the app.
-- Cross-shard transaction = 2PC / saga; avoid by choosing a shard key that keeps related rows together.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: sharding too early. Exhaust indexes, query tuning, caching, read replicas, partitioning,
--    and a bigger machine first; sharding makes every feature harder.

-- ❌ Wrong: shard key with low cardinality or skew (country, status) -> one hot shard
-- ❌ Wrong: shard_no = id % server_count   (see Step 3: resharding moves most of the data)
-- ❌ Wrong: queries that don't include the shard key -> scatter-gather on every shard
SELECT * FROM orders WHERE status = 'pending';       -- hits all shards
-- ✅ Include the key:   WHERE user_id = ? AND status = 'pending'
-- ❌ Wrong: JOIN across tables with different shard keys. Co-locate related tables on the same key.
```

---

## 🎯 Interview Tip (1 line)
Say: "Sharding is a last resort: I'd first use indexes, caching, read replicas and partitioning; if I must shard I pick a high-cardinality key that co-locates related data (e.g. tenant_id), use many logical shards with a directory for easy rebalancing, and plan for global ids and no cross-shard joins/transactions."

---

## 🔗 Related Questions
→ Q241 (Sharding when to use) | Q153 (Partitioning) | Q155 (Read replicas) | Q147 (Multi-tenancy) | Q160 (UUID vs BIGINT)
