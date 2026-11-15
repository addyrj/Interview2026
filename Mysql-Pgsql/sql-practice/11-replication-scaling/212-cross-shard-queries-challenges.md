---

# Q212. Cross-Shard Queries — Challenges
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: Both

---

## ❓ Question
After sharding, what breaks for queries that span shards (aggregates, joins, ORDER BY/LIMIT, transactions, unique constraints)? Show a correct scatter-gather aggregation and the classic "average of averages" bug.

---

## 💡 Quick Concept (2 lines only)
A query without the shard key must be sent to every shard (scatter-gather) and the partial results merged in the app or router; only decomposable aggregates (SUM, COUNT, MIN, MAX) merge safely.
हिंदी: Shard key के बिना query सब shards पर जाती है और नतीजे merge होते हैं; सिर्फ SUM/COUNT/MIN/MAX आसानी से merge होते हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP: two tables simulate two shards (run on MySQL 9.1.0; same SQL on PostgreSQL)
-- ============================================
CREATE TABLE s1 (order_id INT PRIMARY KEY, user_id INT, amount DECIMAL(10,2));
CREATE TABLE s2 LIKE s1;                       -- PgSQL: CREATE TABLE s2 (LIKE s1 INCLUDING ALL);

INSERT INTO s1 VALUES (1, 2, 100), (2, 4, 50), (3, 2, 30);   -- shard 1: 3 rows
INSERT INTO s2 VALUES (4, 1, 10);                            -- shard 2: 1 row

-- ============================================
-- WRONG: average of per-shard averages
-- ============================================
SELECT AVG(a) AS wrong_avg
FROM (SELECT AVG(amount) AS a FROM s1
      UNION ALL
      SELECT AVG(amount) FROM s2) t;
-- wrong_avg
-- 35.0000000000     ((60 + 10) / 2 -- ignores that shard 1 has 3x the rows)

-- ============================================
-- RIGHT: ship SUM and COUNT from each shard, divide at the coordinator
-- ============================================
SELECT SUM(s) / SUM(c) AS right_avg
FROM (SELECT SUM(amount) AS s, COUNT(*) AS c FROM s1
      UNION ALL
      SELECT SUM(amount), COUNT(*) FROM s2) t;
-- right_avg
-- 47.500000         (190 / 4)

-- ============================================
-- Top-N across shards: each shard returns its own top N, coordinator re-sorts
-- ============================================
-- (Per-shard GROUP BY first only works when a user lives on ONE shard.
--  If the same user can appear on both shards, merge SUMs by user before ranking.)
SELECT user_id, SUM(s) AS total
FROM (SELECT user_id, SUM(amount) AS s FROM s1 GROUP BY user_id
      UNION ALL
      SELECT user_id, SUM(amount)        FROM s2 GROUP BY user_id) t
GROUP BY user_id
ORDER BY total DESC LIMIT 2;
-- user_id | total
-- 2       | 130.00
-- 4       | 50.00
-- (Per-shard LIMIT 2 is safe only if each shard returns >= the global N it might contribute;
--  pushing LIMIT down before merging a re-grouped sum can drop a winning user.)

-- ============================================
-- Challenge list (what to say)
-- ============================================
-- 1. Joins        : cross-shard JOIN = fetch both sides to coordinator. Fix: co-locate
--                   by same shard key; replicate small reference tables to all shards.
-- 2. Aggregates   : decompose (SUM/COUNT); AVG = SUM/COUNT; COUNT(DISTINCT) needs
--                   sketches (HLL) or a shuffle; percentiles are not mergeable.
-- 3. ORDER BY/LIMIT/OFFSET: deep OFFSET pages fetch N+offset rows from every shard.
-- 4. Transactions : atomic across shards needs 2PC / sagas; most systems avoid it.
-- 5. Uniqueness   : UNIQUE(email) is per shard only; need a global lookup table.
-- 6. Auto-increment: ids collide across shards -> Snowflake/UUIDv7/range-allocated ids.
-- 7. Latency      : p99 of a scatter query = slowest of N shards.
-- 8. Schema change: DDL must roll out to every shard consistently.
```

---

## 🔍 Why This Works (3 lines max)
Only partial states that can be combined (sum, count) are shipped back, so the coordinator reproduces the exact global result. AVG of AVGs is wrong whenever the shards hold different row counts, as the 35.0 vs 47.5 output shows.
हिंदी: हर shard से SUM और COUNT लाओ, coordinator पर भाग दो। AVG के AVG से गलत नतीजा आता है (35.0 बनाम 47.5)।

---

## ⚡ Alternative Solution

```sql
-- Avoid the problem: route by shard key so a query hits ONE shard.
--   SELECT ... FROM orders WHERE user_id = 2;   -- router sends to shard(user_id)

-- Denormalized global index / read model: stream every shard's changes (CDC) into
-- an analytics DB (ClickHouse, Postgres warehouse) and run cross-shard reports there.

-- PostgreSQL: postgres_fdw can query remote shards as foreign tables (pushdown
-- of simple filters/aggregates); Citus (Q214) does this transparently. NOT RUN here.
-- CREATE FOREIGN TABLE s2_orders (...) SERVER shard2 OPTIONS (table_name 'orders');
```

---

## ⚠️ Common Mistake

```sql
-- ❌ AVG(avg) across shards (shown above): 35.0 instead of 47.5.
-- ❌ SELECT ... ORDER BY x LIMIT 10 OFFSET 100000 over all shards: every shard sorts
--    100010 rows and ships them. Use keyset pagination (WHERE id > last_seen).
-- ❌ Assuming a foreign key / unique constraint holds across shards. It does not.
-- ✅ Make shard-local queries the norm; move cross-shard analytics to a warehouse.
```

---

## 🎯 Interview Tip (1 line)
Say: "Cross-shard reads are scatter-gather with the p99 of the slowest shard, so I design the shard key to keep hot-path queries single-shard, decompose aggregates into sum and count, avoid cross-shard transactions with sagas or idempotent outbox events, and push reporting to a separate analytical store."

---

## 🔗 Related Questions
→ Q210 (shard key) | Q211 (consistent hashing) | Q213 (Vitess) | Q214 (Citus)
