---

# Q241. What Is Sharding and When to Use It?
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: Both

---

## ❓ Question
What is sharding, how are rows routed to shards, what breaks when you add a shard, and when should you NOT shard? Demonstrate routing and single-node hash partitioning.

---

## 💡 Quick Concept (2 lines only)
Sharding splits one logical dataset horizontally across multiple independent database servers using a shard key (e.g. user_id); each shard holds a subset of rows. Use it only when one primary (even after indexing, caching, read replicas, partitioning) cannot handle the write volume or data size.
हिंदी: Sharding = data को कई servers पर shard key से बाँटना; पहले index, cache, replica आज़माओ, फिर shard करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE users (user_id INT PRIMARY KEY, email VARCHAR(100));
INSERT INTO users VALUES
  (1,'a@x.com'),(2,'b@x.com'),(3,'c@x.com'),(4,'d@x.com'),(5,'e@x.com'),
  (6,'f@x.com'),(7,'g@x.com'),(8,'h@x.com'),(9,'i@x.com'),(10,'j@x.com');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: modulo routing - the application (or proxy like Vitess/Citus) computes the shard
SELECT user_id, user_id % 4 AS shard_id,
       CONCAT('orders_db_', user_id % 4) AS target_db      -- PostgreSQL: 'orders_db_' || (user_id % 4)
FROM users ORDER BY user_id;

-- Result (same on MySQL 9.1 and PostgreSQL):
-- user_id | shard_id | target_db
-- 1       | 1        | orders_db_1
-- 2       | 2        | orders_db_2
-- 3       | 3        | orders_db_3
-- 4       | 0        | orders_db_0
-- 5       | 1        | orders_db_1
-- 6       | 2        | orders_db_2
-- 7       | 3        | orders_db_3
-- 8       | 0        | orders_db_0
-- 9       | 1        | orders_db_1
-- 10      | 2        | orders_db_2

-- Step 2: why naive modulo hurts - changing 4 shards to 5 relocates most rows
SELECT COUNT(*) AS users_that_must_move FROM users WHERE user_id % 4 <> user_id % 5;
-- Result: 7 (of 10 rows must move). Use consistent hashing / a lookup (directory) table / many
-- virtual shards (e.g. 1024 logical shards mapped to a few servers) to avoid this.

-- Step 3: single-node HASH partitioning (NOT sharding: one server, but same idea + pruning)
-- MySQL:
CREATE TABLE orders (
  order_id BIGINT NOT NULL,
  user_id  INT NOT NULL,
  amount   DECIMAL(10,2),
  PRIMARY KEY (order_id, user_id)          -- partition key must be part of every unique key
) PARTITION BY HASH (user_id) PARTITIONS 4;

INSERT INTO orders VALUES (1,1,10),(2,2,20),(3,3,30),(4,4,40),(5,5,50),(6,6,60),(7,8,80),(8,8,90);

SELECT PARTITION_NAME, TABLE_ROWS FROM information_schema.PARTITIONS
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'orders' ORDER BY PARTITION_ORDINAL_POSITION;
-- p0 | 3     (user 4, 8, 8)
-- p1 | 2     (user 1, 5)
-- p2 | 2     (user 2, 6)
-- p3 | 1     (user 3)
-- (TABLE_ROWS is an InnoDB estimate; it was exact on this tiny table)

EXPLAIN SELECT * FROM orders WHERE user_id = 8;
-- partitions: p0  <- partition pruning: only 1 of 4 partitions is read

-- PostgreSQL equivalent (declarative hash partitioning):
-- CREATE TABLE orders (order_id BIGINT NOT NULL, user_id INT NOT NULL, amount NUMERIC(10,2),
--                      PRIMARY KEY (order_id, user_id)) PARTITION BY HASH (user_id);
-- CREATE TABLE orders_p0 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 0);  -- repeat p1..p3
-- SELECT tableoid::regclass AS partition_name, COUNT(*) FROM orders GROUP BY tableoid;
-- Observed on PGlite: orders_p0=1, orders_p1=4, orders_p2=1, orders_p3=2
--   (PostgreSQL uses its own hash function, not user_id % 4, so distribution differs from MySQL)
-- EXPLAIN (COSTS OFF) ... WHERE user_id = 8 -> "Seq Scan on orders_p1 orders" (only one partition touched)

-- NOT RUN (needs several servers): real cross-server sharding, Vitess/Citus/ProxySQL setup,
-- cross-shard joins/transactions (2PC), online resharding.
```

---

## 🔍 Why This Works (3 lines max)
A deterministic function of the shard key picks the target, so each query touching one key hits one shard and writes scale out linearly. Cross-shard joins, unique constraints, transactions and resharding become hard, which is the price paid.
हिंदी: Shard key से तय होता है कि row किस server पर जाएगी; cross-shard join और resharding महँगे हैं।

---

## ⚡ Alternative Solution

```sql
-- Before sharding, try in this order:
-- 1. Fix queries/indexes (EXPLAIN)   2. Cache (Redis)   3. Read replicas for reads
-- 4. Table partitioning on one server (above)   5. Archive/purge old data   6. Vertical split by service
-- Then shard. Strategies: hash (even spread), range (hot-spot risk on newest range), directory/lookup
-- table (flexible, extra hop), geo/tenant-based (data residency, big-tenant skew).
-- Tools: MySQL -> Vitess / ProxySQL; PostgreSQL -> Citus / pg partitions + postgres_fdw; or app-level.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Bad shard key: created_at / auto-increment id with range sharding -> all new writes hit the last shard
-- ❌ Low-cardinality key (country) -> hot shards;  ❌ shard key not in WHERE -> scatter-gather to all shards
-- ❌ user_id % N hard-coded in app, then adding a shard with no migration plan
-- ✅ High-cardinality key present in most queries (user_id / tenant_id), virtual shards, global ID generator
--    (snowflake) instead of per-shard AUTO_INCREMENT
```

---

## 🎯 Interview Tip (1 line)
Say: "Sharding is a last resort after indexing, caching, replicas and partitioning; I choose a high-cardinality shard key that appears in most queries, use many logical shards or consistent hashing to make resharding cheap, and accept losing cross-shard joins, transactions and global unique constraints."

---

## 🔗 Related Questions
→ Q240 (Multi-tenant design) | Q245 (Zero-downtime migration) | Q231 (Primary key vs unique key) | Q237 (Covering index)
