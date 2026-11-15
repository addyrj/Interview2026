---

# Q114. Statistics / ANALYZE — When to Run
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both

---

## ❓ Question
The optimizer picks a bad plan right after a big data load. Explain what table statistics are, what `ANALYZE` does in PostgreSQL and MySQL, when you must run it manually, and how to confirm it fixed the estimate.

---

## 💡 Quick Concept (2 lines only)
The planner chooses plans from statistics (row counts, distinct values, most-common values, histograms). Stale stats give wrong row estimates, and wrong estimates give wrong join order and scan type; `ANALYZE` refreshes them.
हिंदी: Optimizer plan statistics देखकर बनाता है; बड़ा data load/बदलाव के बाद stats पुराने हों तो plan गलत बनता है, `ANALYZE` से ठीक होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (PostgreSQL; verified on PGlite 18.6)
-- ============================================

CREATE TABLE events (
  id      SERIAL PRIMARY KEY,
  user_id INT,
  kind    TEXT
);
CREATE INDEX idx_events_kind ON events (kind);
ANALYZE events;                     -- stats captured while the table is EMPTY

-- Bulk load: 50,000 clicks + 50 purchases (stats are now stale)
INSERT INTO events (user_id, kind) SELECT g, 'click'    FROM generate_series(1, 50000) g;
INSERT INTO events (user_id, kind) SELECT g, 'purchase' FROM generate_series(1, 50)    g;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: what does the planner believe?
SELECT reltuples::bigint AS est_rows, relpages FROM pg_class WHERE relname = 'events';
EXPLAIN SELECT * FROM events WHERE kind = 'purchase';

-- Step 2: refresh statistics
ANALYZE events;

-- Step 3: check again
SELECT reltuples::bigint AS est_rows, relpages FROM pg_class WHERE relname = 'events';
EXPLAIN SELECT * FROM events WHERE kind = 'purchase';

-- Step 4: look at what ANALYZE collected
SELECT attname, n_distinct, most_common_vals::text, most_common_freqs::text
FROM pg_stats WHERE tablename = 'events' AND attname = 'kind';

-- Step 5: skewed column? collect more detail (default target is 100)
ALTER TABLE events ALTER COLUMN kind SET STATISTICS 500;
ANALYZE events;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Before ANALYZE (stale: planner thinks table is empty):
-- est_rows | relpages
-- 0        | 0
-- Bitmap Heap Scan on events  (cost=5.55..253.84 rows=163 width=40)    <- guessed 163 rows
--   ->  Bitmap Index Scan on idx_events_kind  (cost=0.00..5.51 rows=163 width=0)
--
-- After ANALYZE:
-- est_rows | relpages
-- 50050    | 271
-- Index Scan using idx_events_kind on events  (cost=0.29..9.20 rows=52 width=14)   <- ~52 (real: 50)
--
-- pg_stats:
-- kind | n_distinct 2 | {click,purchase} | {0.9989667,0.0010333334}
-- (sampled values, may differ slightly on a real server)
--
-- Defaults: default_statistics_target = 100, autovacuum_analyze_scale_factor = 0.1,
--           autovacuum_analyze_threshold = 50
```

---

## 🔍 Why This Works (3 lines max)
`ANALYZE` samples the table and stores row count, distinct counts, most-common values and histograms; the planner turns these into selectivity. Autovacuum re-analyzes when about 10% of rows (+50) changed, which is too slow right after a bulk load or a big delete, so you run it yourself.
हिंदी: `ANALYZE` table का sample लेकर stats बदल देता है; bulk load के तुरंत बाद autovacuum का इंतज़ार मत करो, खुद चलाओ।

---

## ⚡ Alternative Solution

```sql
-- MySQL (verified on 9.1.0). InnoDB stats are persistent and auto-recalc after ~10% change.
ANALYZE TABLE events;                         -- re-samples index cardinality
SELECT INDEX_NAME, CARDINALITY FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'q114' AND TABLE_NAME = 'events';
--  before ANALYZE (after bulk insert): idx_kind = 1,  PRIMARY = 11   (stale, real output)
--  after  ANALYZE:                     idx_kind = 2,  PRIMARY = 5010 (real output)

-- MySQL 8.0+ histograms: stats for NON-indexed or skewed columns
ANALYZE TABLE events UPDATE HISTOGRAM ON kind WITH 16 BUCKETS;
--  Msg: Histogram statistics created for column 'kind'.  (type = singleton)
ANALYZE TABLE events DROP HISTOGRAM ON kind;

-- Defaults seen: innodb_stats_persistent = 1, innodb_stats_auto_recalc = 1,
--                innodb_stats_persistent_sample_pages = 20

-- PostgreSQL extras
ANALYZE;                                     -- whole database
VACUUM (ANALYZE) events;                     -- reclaim dead rows AND refresh stats (Q115)
CREATE STATISTICS st_cs (dependencies) ON city, zip FROM addresses;  -- correlated columns (not run)
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Loading millions of rows and immediately running reports: autovacuum has not analyzed yet,
--    planner thinks the table is tiny -> nested loops / seq scans on huge data.
-- ❌ Running ANALYZE on a partitioned table parent only: in PostgreSQL autovacuum does NOT
--    analyze the parent of a partitioned table - run ANALYZE parent_table yourself.
-- ❌ Believing ANALYZE changes data or blocks writes: it takes only a light lock; cheap to run.
-- ✅ ANALYZE after bulk loads, big deletes, restores from pg_dump/pg_upgrade, creating
--    expression indexes; raise SET STATISTICS for skewed columns.
```

---

## 🎯 Interview Tip (1 line)
Say: "When a plan suddenly looks wrong I compare estimated vs actual rows in EXPLAIN ANALYZE; a big gap means stale or insufficient stats, so I ANALYZE after bulk loads, raise the statistics target on skewed columns, and use extended statistics or MySQL histograms for correlated or unindexed columns."

---

## 🔗 Related Questions
→ Q115 (VACUUM ANALYZE / bloat) | Q113 (Plan caching) | Q109 (Slow query diagnosis) | Q119 (Function on indexed column)
