---

# Q106. Optimize COUNT(*) on a Large Table
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
`SELECT COUNT(*) FROM events` is slow on a 300M-row table. Why (MVCC), and what are the options: exact vs approximate counts, counter tables, covering indexes?

---

## 💡 Quick Concept (2 lines only)
InnoDB and PostgreSQL use MVCC, so each transaction may see a different row count and the engine must scan (the smallest index or the heap) - there is no stored exact count like MyISAM. Options: scan the smallest index, use planner estimates, or maintain a counter/summary table.
हिंदी: MVCC की वजह से exact count के लिए rows गिननी ही पड़ती हैं; अनुमान चलेगा तो statistics से लो, exact चाहिए तो counter table रखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0, 300,000 rows)
-- ============================================

CREATE TABLE events (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id    INT NOT NULL,
  event_type VARCHAR(20) NOT NULL,
  payload    VARCHAR(200) NOT NULL,
  created_at DATETIME NOT NULL,
  KEY idx_user (user_id)
);
SET SESSION cte_max_recursion_depth = 300000;
INSERT INTO events (user_id, event_type, payload, created_at)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 300000)
SELECT i % 10000 + 1, ELT(i % 3 + 1, 'click','view','purchase'), REPEAT('x',150),
       TIMESTAMP('2024-01-01') + INTERVAL i SECOND FROM n;
ANALYZE TABLE events;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: exact count - how does MySQL do it?
EXPLAIN SELECT COUNT(*) FROM events;
EXPLAIN ANALYZE SELECT COUNT(*) FROM events;

-- Step 2: filtered count with no index -> scan; with an index -> covering index count
EXPLAIN SELECT COUNT(*) FROM events WHERE event_type = 'purchase';
ALTER TABLE events ADD KEY idx_type (event_type);
ANALYZE TABLE events;
EXPLAIN SELECT COUNT(*) FROM events WHERE event_type = 'purchase';

-- Step 3: approximate (instant) count
SELECT table_rows FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'events';
SELECT COUNT(*) FROM events;      -- exact, for comparison

-- Step 4: exact + instant = maintained counter (trigger shown; use app-level/Redis counters at high write rates)
CREATE TABLE row_counters (table_name VARCHAR(64) PRIMARY KEY, row_count BIGINT NOT NULL);
INSERT INTO row_counters SELECT 'events', COUNT(*) FROM events;
CREATE TRIGGER trg_events_ai AFTER INSERT ON events FOR EACH ROW
  UPDATE row_counters SET row_count = row_count + 1 WHERE table_name = 'events';
CREATE TRIGGER trg_events_ad AFTER DELETE ON events FOR EACH ROW
  UPDATE row_counters SET row_count = row_count - 1 WHERE table_name = 'events';
INSERT INTO events (user_id, event_type, payload, created_at) VALUES (1, 'click', 'p', NOW());
DELETE FROM events WHERE id IN (1, 2);
SELECT row_count FROM row_counters WHERE table_name = 'events';
SELECT COUNT(*) FROM events;

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0)
-- ============================================
-- Step 1: type=index, key=idx_user (smallest secondary index), rows=296219, Extra: Using index
--         ANALYZE: "Count rows in events (actual time=19.3 ms)"   <- MySQL 9.1 reports a dedicated "Count rows" node
-- Step 2: before index: type=ALL, Using where, rows=296219 | after: type=ref, key=idx_type, Using index
-- Step 3: table_rows = 296219 (estimate)  vs  COUNT(*) = 300000 (exact)
-- Step 4: row_count = 299999  and  COUNT(*) = 299999   (+1 insert, -2 deletes)
-- Also: COUNT(1) = same plan as COUNT(*) (Using index); COUNT(payload) -> type=ALL (must check NULLs in a non-indexed column)
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6)
-- ============================================
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF) SELECT COUNT(*) FROM events;
-- Aggregate -> Seq Scan on events (actual rows=300000)       <- before VACUUM
VACUUM events;            -- builds the visibility map
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF) SELECT COUNT(*) FROM events;
-- Aggregate -> Index Only Scan using idx_user  Heap Fetches: 0   <- visibility map makes it index-only

SELECT reltuples::bigint AS estimate FROM pg_class WHERE relname = 'events';   -- 300000 (after ANALYZE/autovacuum)
-- Large tables: planner estimate of a filtered count (not run here):
--   EXPLAIN (FORMAT JSON) SELECT 1 FROM events WHERE user_id = 77;   -> read "Plan Rows"
-- Counter table + trigger (plpgsql) verified: after +1 insert, -2 deletes -> counter 299999 = COUNT(*) 299999
-- Caveat: a single counter row serializes concurrent writers (row lock hot spot).
```

---

## 🔍 Why This Works (3 lines max)
COUNT(*) only needs row presence, so the engine reads the narrowest index (fewer pages) instead of the clustered table; statistics (`table_rows`, `reltuples`) give an O(1) estimate; a counter turns the count into a point lookup at the price of extra write work.
हिंदी: सबसे छोटा index scan करो, अनुमान चाहिए तो statistics लो, और exact + तेज़ चाहिए तो counter table maintain करो।

---

## ⚡ Alternative Solution

```sql
-- Batched / sharded counters to avoid a hot row:
CREATE TABLE row_counters_sharded (table_name VARCHAR(64), slot TINYINT, row_count BIGINT, PRIMARY KEY (table_name, slot));
-- writers: UPDATE ... WHERE slot = FLOOR(RAND()*16);  readers: SELECT SUM(row_count) ...     (not run)
-- Time-bucketed summaries (hourly counts) answer most dashboard questions without touching the base table.
-- PostgreSQL: pg_stat_user_tables.n_live_tup (cheap, approximate); extension-free HLL for distinct counts via postgresql-hll (not core).
-- MySQL: nothing equals Postgres's visibility-map trick; keep a narrow index so the count scan is small.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ COUNT(*) on every page load for "Total results: N" - scans the table each time
-- ❌ Believing COUNT(1) is faster than COUNT(*): same plan (verified)
-- ❌ COUNT(column) when you mean rows: counts only NON-NULL values and may force a scan
-- ❌ Trusting information_schema.table_rows as exact: 296219 vs real 300000 (~1.3% off)
-- ✅ Estimate for UI, exact only when needed; cap with LIMIT:  SELECT COUNT(*) FROM (SELECT 1 FROM events WHERE ... LIMIT 10001) t;
```

---

## 🎯 Interview Tip (1 line)
Say: "Exact counts are O(n) under MVCC, so I decide whether the product really needs exact: estimates from statistics for UI, a maintained counter or summary table for exact-and-fast, and a narrow index (plus visibility map in Postgres) to make unavoidable scans cheap."

---

## 🔗 Related Questions
→ Q084 (Covering index) | Q107 (Pagination on large table) | Q114 (Statistics / ANALYZE) | Q115 (VACUUM / ANALYZE PgSQL)
