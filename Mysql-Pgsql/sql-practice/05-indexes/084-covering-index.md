---

# Q084. Covering Index — What It Is and How to Use It
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
What is a covering index? How does it differ from a regular index? Show before/after EXPLAIN output and when to add vs avoid one.

---

## 💡 Quick Concept (2 lines only)
A covering index contains ALL columns the query needs — the database answers the query entirely from the index without touching the actual table rows. MySQL EXPLAIN shows "Using index" (not "Using index condition"). PgSQL shows "Index Only Scan".
हिंदी: Covering index में query के सभी columns होते हैं — table rows touch नहीं होते। MySQL: "Using index", PgSQL: "Index Only Scan"।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE orders (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id    INT NOT NULL,
  status     VARCHAR(20) NOT NULL,
  amount     DECIMAL(10,2),
  created_at DATETIME NOT NULL
);

-- Insert sample data (imagine 1M rows)

-- ============================================
-- PROBLEM: REGULAR INDEX (still touches table)
-- ============================================

-- Regular index on user_id only:
CREATE INDEX idx_user ON orders(user_id);

-- Query: how much did user 42 spend?
SELECT user_id, status, SUM(amount)
FROM orders
WHERE user_id = 42
GROUP BY user_id, status;

-- EXPLAIN output (MySQL):
-- type: ref | key: idx_user | rows: 250 | Extra: Using index condition
-- "Using index condition" means: index used for WHERE, but must fetch rows for status + amount
-- Each of 250 matching rows requires a lookup back to the clustered index (double lookup!)

-- EXPLAIN ANALYZE (PgSQL):
-- Index Scan using idx_user on orders (rows=250)
-- → "Index Scan" (not "Index Only Scan") = table heap must be consulted

-- ============================================
-- SOLUTION: COVERING INDEX
-- ============================================

-- Drop the narrow index, create a covering one:
DROP INDEX idx_user ON orders;

-- MySQL: include all columns needed by the query
CREATE INDEX idx_user_covering ON orders(user_id, status, amount);
--  ↑ user_id: WHERE filter (leftmost)
--  ↑ status:  needed in SELECT + GROUP BY
--  ↑ amount:  needed in SUM(amount)

-- PgSQL: same composite index, OR use INCLUDE (PG11+):
CREATE INDEX idx_user_covering ON orders(user_id, status) INCLUDE (amount);
--  INCLUDE adds amount to leaf nodes without making it a sort key
--  Useful when amount is only in SELECT but not in WHERE/ORDER BY

-- Now EXPLAIN (MySQL):
-- type: ref | key: idx_user_covering | rows: 250 | Extra: Using index ← !!!
-- "Using index" = query answered ENTIRELY from index — no table access!

-- PgSQL:
-- Index Only Scan using idx_user_covering on orders (rows=250)
-- Heap Fetches: 0  ← no table access needed!

-- Why faster?
-- Without covering index: 250 index lookups + 250 heap/clustered-index lookups = 500 I/O
-- With covering index:    250 index lookups only = 250 I/O
-- At scale (1M rows, 1000 users each): 50% fewer I/O operations!

-- ============================================
-- MYSQL InnoDB: AUTOMATIC SECONDARY INDEX COVERAGE
-- ============================================

-- InnoDB secondary indexes already include the primary key automatically:
CREATE INDEX idx_status ON orders(status);
-- Leaf node: [status | id]  ← id included automatically!

-- Query using both status AND id:
SELECT id FROM orders WHERE status = 'pending' ORDER BY id;
-- EXPLAIN Extra: "Using index" ← covering! (status + id both in index leaf)

-- Query using status + any other column (not PK):
SELECT id, amount FROM orders WHERE status = 'pending';
-- EXPLAIN Extra: "Using index condition" ← NOT covering (amount not in index)
-- Must fetch row from clustered index for amount

-- ============================================
-- PgSQL: INCLUDE CLAUSE (PG11+)
-- ============================================

-- INCLUDE adds columns to leaf nodes only (not to internal B-tree nodes):
-- Benefits: smaller index (fewer levels), columns not usable for filtering/sorting
-- but available for SELECT without heap access

CREATE INDEX idx_user_status ON orders(user_id, status) INCLUDE (amount, created_at);

-- Queries that benefit:
SELECT user_id, status, amount, created_at FROM orders WHERE user_id = 42;
-- → Index Only Scan (all 4 columns in leaf!) 

-- Queries that don't use INCLUDE for filtering:
SELECT * FROM orders WHERE amount > 100 AND user_id = 42;
-- amount is in INCLUDE but NOT in the indexed key → can't filter on it via index
-- Use WHERE user_id = 42 (index key) → THEN filter amount from INCLUDE

-- ============================================
-- WHEN TO ADD A COVERING INDEX
-- ============================================

/*
Good candidates:
  ✅ High-frequency read queries (reports, dashboards, APIs)
  ✅ Query selects a small, fixed set of columns
  ✅ WHERE + SELECT columns together are < 5-10 columns
  ✅ Table is large and full scans are costly
  ✅ The query runs thousands of times per minute

When NOT to add:
  ❌ Write-heavy tables (every INSERT/UPDATE/DELETE maintains the covering index)
  ❌ Query selects SELECT * (can't cover all columns)
  ❌ Table is small (< 10K rows) — full scan is fine
  ❌ Columns are large (TEXT, BLOB) — huge index size, worse cache efficiency
  ❌ Columns in SELECT change frequently — maintenance overhead
*/

-- ============================================
-- IDENTIFY QUERIES NEEDING COVERING INDEX
-- ============================================

-- MySQL: Find queries with "Using index condition" or "Using filesort":
EXPLAIN SELECT user_id, status, SUM(amount)
FROM orders
WHERE user_id = 42
GROUP BY status;
-- If Extra: "Using index condition; Using temporary; Using filesort" → needs covering index!

-- PgSQL: Find "Heap Fetches > 0" in Index Only Scan:
EXPLAIN (ANALYZE, BUFFERS) SELECT user_id, status, SUM(amount)
FROM orders WHERE user_id = 42 GROUP BY status;
-- "Heap Fetches: 5000" → not fully covered → add missing columns to index

-- Check index usage (PgSQL):
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE relname = 'orders'
ORDER BY idx_scan DESC;
-- idx_tup_fetch >> 0: fetching rows beyond index (not covering)
-- idx_tup_fetch = 0: pure index-only access (fully covering)
```

---

## 🔍 Why This Works (3 lines max)
A covering index stores all needed column values in the index's leaf nodes — when MySQL or PgSQL finds a matching key, it has all the data needed for SELECT and GROUP BY right there in the index page, with no need to jump to the actual table. This eliminates the "double lookup" in InnoDB (secondary index → clustered index) and the heap fetch in PgSQL. The trade-off is larger index size and slower writes.
हिंदी: Covering index leaf nodes में सभी required columns होते हैं। Table access नहीं = double lookup नहीं। Trade-off: बड़ा index, slower writes।

---

## ⚡ Alternative Solution

```sql
-- Materialized view as an alternative to covering index for complex aggregations:
-- PgSQL:
CREATE MATERIALIZED VIEW user_order_summary AS
SELECT user_id, status, SUM(amount) AS total, COUNT(*) AS cnt
FROM orders GROUP BY user_id, status;

CREATE UNIQUE INDEX ON user_order_summary(user_id, status);

-- Query hits materialized view instead:
SELECT * FROM user_order_summary WHERE user_id = 42;
-- Precomputed! Zero scan of orders table.
-- Trade-off: must REFRESH MATERIALIZED VIEW CONCURRENTLY periodically
-- Good for reports with tolerable staleness (refresh every 5 minutes)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Covering index column order (wrong leftmost column)
CREATE INDEX idx_bad ON orders(amount, user_id, status);
-- Query: WHERE user_id = 42 → can't use this index efficiently (amount is leftmost!)
-- ✅ Fix: leftmost column must match WHERE filter
CREATE INDEX idx_good ON orders(user_id, status, amount);

-- ❌ Wrong: Adding covering index for SELECT * queries
-- SELECT * requires all columns — index can never cover this
-- ✅ Fix: either narrow the SELECT or accept that * always needs table access

-- ❌ Wrong: Using covering index on low-write-frequency assumption
-- A covering index with 5 columns on a table with 10,000 inserts/sec
-- = 10,000 index updates/sec → significant write overhead!
-- ✅ Measure write impact: check insert latency before/after adding index

-- ❌ Wrong (PgSQL): Using INCLUDE column in WHERE clause expecting index benefit
CREATE INDEX idx ON orders(user_id) INCLUDE (amount);
SELECT * FROM orders WHERE user_id = 42 AND amount > 500;
-- amount is in INCLUDE but NOT usable for filtering!
-- The WHERE amount > 500 is applied AFTER fetching from index — still fast
-- but you must add amount to the indexed key if you want index-based filtering:
CREATE INDEX idx ON orders(user_id, amount) INCLUDE (status);  -- amount now filterable
```

---

## 🎯 Interview Tip (1 line)
Say: "A covering index answers the query purely from the index — MySQL shows 'Using index' in EXPLAIN Extra, PgSQL shows 'Index Only Scan'. I create one by including all columns from WHERE, SELECT, and ORDER BY in the index — but only for high-frequency read queries, since adding columns increases write overhead."

---

## 🔗 Related Questions
→ Q081 (B-Tree internals) | Q083 (composite index order) | Q086 (EXPLAIN output) | Q088 (functional indexes)
